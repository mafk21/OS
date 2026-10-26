import json
from pathlib import Path
import subprocess
import threading
import time
from unittest.mock import Mock

import pytest

from actions.brag_video import brag_video, TOOL
from core import brag_video as video


@pytest.fixture
def project(tmp_path, monkeypatch):
    source = tmp_path / "project"
    source.mkdir()
    (source / "README.md").write_text("# Orbit\n\nOrganize projects without losing context.\nKeep notes close to your work.\n")
    monkeypatch.setattr(video, "OUTPUT_ROOT", tmp_path / "videos")
    return source


def request(project, **overrides):
    return {"project_path": str(project), "duration": 5, "quality": "draft", "hook": "Keep your work in orbit.",
            "highlights": ["Organize projects in one place.", "Keep notes close to your work."], **overrides}


def await_terminal(job_id, timeout=90):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        state = video.status(job_id)
        if state["status"] not in ("queued", "running"):
            return state
        time.sleep(.05)
    pytest.fail("Video job failed to reach a terminal state")


def test_inspection_does_not_crawl_secrets_or_execute_source(project):
    (project / ".env").write_text("SECRET=do-not-read")
    (project / "config.json").write_text('"private"')
    data = video.inspect_project(str(project))
    assert data["title"] == "Orbit" and data["sources"] == ["README.md"]
    assert "do-not-read" not in json.dumps(data)


def test_ignored_readme_is_not_read(project, monkeypatch):
    monkeypatch.setattr(video.subprocess, "run", lambda *a, **k: Mock(returncode=0))
    assert video.inspect_project(str(project))["sources"] == []


def test_symlink_readme_is_not_read(project, tmp_path):
    (project / "README.md").unlink()
    private = tmp_path / "secret.txt"
    private.write_text("private source")
    try:
        (project / "README.md").symlink_to(private)
    except OSError:
        pytest.skip("Symlink unavailable")
    assert video.inspect_project(str(project))["sources"] == []


@pytest.mark.parametrize("field,value", [("duration", 0), ("duration", float("nan")), ("duration", 31), ("format", "bad"),
                                         ("tone", "bad"), ("quality", "bad"), ("voice", "false"), ("highlights", "not a list")])
def test_invalid_options_fail_before_job_creation(project, field, value):
    with pytest.raises((ValueError, TypeError)):
        video.validate_request(request(project, **{field: value}))
    assert not video.OUTPUT_ROOT.exists()


def test_no_output_path_traversal(project):
    with pytest.raises(ValueError):
        video.status("../../credentials")
    with pytest.raises(ValueError):
        video.validate_request(request(project, image_paths=["../private.png"]))


def test_redacts_public_copy(project):
    (project / "README.md").write_text("# Orbit\nEmail me@example.org, secret sk-abcdefghijklmnopqrst and https://internal.example/key")
    data = video.inspect_project(str(project))
    assert "me@example.org" not in data["excerpt"]
    assert "sk-abcdef" not in data["excerpt"]
    assert "internal.example" not in data["excerpt"]


def test_interrupted_job_never_reports_completion(project):
    folder = video.OUTPUT_ROOT / ("a"*16)
    folder.mkdir(parents=True)
    video._atomic(folder/"job.json", {"job_id":"a"*16, "status":"running"})
    assert video.status("a"*16)["status"] == "interrupted"


def test_background_render_failure_is_truthful_and_visible(project, monkeypatch):
    monkeypatch.setattr(video, "doctor", lambda: {"ready":True})
    monkeypatch.setattr(video, "render", Mock(side_effect=RuntimeError("encode failed")))
    done = threading.Event()
    results = []
    def notify(data, _):
        if data["status"] == "failed":
            results.append(data)
            done.set()
    job = video.start(request(project), notify=notify)
    assert job["status"] == "queued"
    assert done.wait(5)
    assert results[0]["status"] == "failed"
    assert not (Path(job["directory"])/"brag.mp4").exists()


def test_cancellation_and_no_autoplay_for_partial_file(project, monkeypatch):
    monkeypatch.setattr(video, "doctor", lambda: {"ready":True})
    started = threading.Event()
    def renderer(spec, folder, event, progress):
        started.set()
        assert event.wait(5)
        video._check(event)
    monkeypatch.setattr(video, "render", renderer)
    job = video.start(request(project))
    assert started.wait(5)
    assert video.cancel(job["job_id"])["status"] == "cancellation_requested"
    assert await_terminal(job["job_id"])["status"] == "cancelled"


def test_missing_dependency_does_not_claim_started(project, monkeypatch):
    monkeypatch.setattr(video, "doctor", lambda: {"ready":False, "error":"missing ffmpeg"})
    assert "not started" in brag_video(request(project))
    assert not video.OUTPUT_ROOT.exists()


@pytest.mark.parametrize("fmt,music,sfx", [("landscape", True, True), ("vertical", False, False), ("square", False, True)])
def test_real_end_to_end_mp4_render_decode_and_deliverables(project, fmt, music, sfx):
    assert video.doctor()["ready"]
    job = video.start(request(project, format=fmt, music=music, sfx=sfx))
    result = await_terminal(job["job_id"])
    assert result["status"] == "completed", result
    folder = Path(job["directory"])
    for name in ("brag.mp4", "brag.jpg", "brag-plan.md", "composition-brief.md", "share-copy.txt", "plan.json"):
        assert (folder/name).is_file()
    assert (result["width"],result["height"]) == tuple(v//2 for v in video.FORMATS[fmt])
    # Independent full decode, not a mocked provider success.
    proc = subprocess.run([video.ffmpeg_path(), "-v", "error", "-xerror", "-i", result["video"], "-f", "null", "-"], capture_output=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    assert result["progress"] == 100


def test_tool_and_skill_are_discoverable():
    from core.action_loader import discover_actions
    from core.skill_loader import discover_skills
    actions = discover_actions(video.BASE / "actions", logger=lambda _:None)
    assert actions.has("brag_video")
    registry = discover_skills(video.BASE / "skills", logger=lambda _:None)
    assert "brag" in registry.names()
    assert TOOL["parameters"]["properties"]["voice"]["type"] == "BOOLEAN"


def test_opt_in_narration_is_rendered_not_silently_dropped(project, monkeypatch):
    import sys
    from types import SimpleNamespace
    tts = Mock(return_value=b"\0\0"*24000)
    monkeypatch.setitem(sys.modules, "core.openai_compat", SimpleNamespace(openai_tts_pcm24k=tts))
    job = video.start(request(project, voice=True))
    result = await_terminal(job["job_id"])
    assert result["status"] == "completed", result
    tts.assert_called_once()
    assert (Path(job["directory"])/"work"/"narration.wav").is_file()


def test_requested_voice_failure_does_not_fall_back_to_silent_success(project, monkeypatch):
    import sys
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules, "core.openai_compat", SimpleNamespace(openai_tts_pcm24k=lambda _: b""))
    job = video.start(request(project, voice=True))
    result = await_terminal(job["job_id"])
    assert result["status"] == "failed"
    assert "Narration requested" in result["error"]
    assert not (Path(job["directory"])/"brag.mp4").exists()


def test_actual_product_image_used_and_poster_is_nonblank(project):
    from PIL import Image
    image = project / "product.png"
    Image.new("RGB", (200,100), "#ff0000").save(image)
    spec = video.validate_request(request(project, image_paths=["product.png"]))
    frame = video.make_frame(spec, .5, (960,540), [Image.open(image).convert("RGB")])
    import numpy as np
    pixels = np.asarray(frame)
    assert int(((pixels[:,:,0]>200) & (pixels[:,:,1]<50) & (pixels[:,:,2]<50)).sum()) > 5000


def test_completed_job_callback_and_autoplay_use_existing_hud(project, monkeypatch):
    from types import SimpleNamespace
    player = SimpleNamespace(write_log=Mock(), show_content=Mock())
    done = threading.Event()
    monkeypatch.setattr(video, "doctor", lambda: {"ready":True})
    def render(spec, folder, event, progress):
        return {"video":"verified-test.mp4"}
    monkeypatch.setattr(video, "render", render)
    spoken = []
    def speak(text):
        spoken.append(text)
        done.set()
    job = json.loads(brag_video(request(project), player=player, speak=speak))
    assert done.wait(5)
    assert '"status": "completed"' in spoken[0]
    player.write_log.assert_called_once()
    assert job["status"] == "queued"


def test_cancellation_terminates_media_subprocess_promptly():
    import sys
    event = threading.Event()
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    event.set()
    with pytest.raises(video.Cancelled):
        video._wait_process(process, event, 120)
    assert process.poll() is not None


def test_real_final_quality_twenty_second_render(project):
    job = video.start(request(project, duration=20, quality="final"))
    result = await_terminal(job["job_id"], timeout=120)
    assert result["status"] == "completed", result
    assert (result["width"], result["height"]) == (1920,1080)
    probe = subprocess.run([video.ffmpeg_path(), "-hide_banner", "-i", result["video"], "-f", "null", "-"],
                           capture_output=True, timeout=30)
    assert probe.returncode == 0
    assert b"00:00:20" in probe.stderr
    assert b"Audio: aac" in probe.stderr
