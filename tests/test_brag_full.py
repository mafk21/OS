"""Real Hyperframes gate/render tests are opt-in; provider responses stay fixtures.

Set JARVIS_TEST_HYPERFRAMES=1 and JARVIS_BRAG_RUNTIME / browser overrides to run.
No paid model/voice call or publication occurs in the tests.
"""
import json
import os
from pathlib import Path
import threading
from unittest.mock import Mock

import pytest

from core import brag_full as full
from core import brag_video as video


@pytest.fixture
def project(tmp_path):
    root = tmp_path/"project"
    root.mkdir()
    (root/"README.md").write_text("# Orbit\nOrganize projects. Keep notes close to your work.")
    (root/"index.html").write_text('<main><h1>Orbit projects</h1><p>Keep notes close to your work.</p></main>')
    return root


def spec(project, **extra):
    return video.validate_request({"project_path":str(project), "engine":"full", "duration":5,
        "music":True, "sfx":False, "quality":"draft", **extra})


def plan():
    return {"rubric":["Orbit projects"]*9, "angle":"A workspace that keeps notes visible",
        "storyboard":[{"duration":2.5,"description":"entry","copy":"Orbit projects"},
                      {"duration":2.5,"description":"result","copy":"Keep notes close to your work."}],
        "music":"music/happy-beats-business-moves-vol-10-by-ende-dot-app.mp3", "sfx":[],
        "share_copy":"Orbit projects. Keep notes close to your work.", "poster_time":3.8}


def files():
    root = '''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#101827;color:#fff;font-family:Inter}#root{position:relative;width:1920px;height:1080px;overflow:hidden}
</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="5" data-width="1920" data-height="1080">
<div id="entry" data-composition-id="entry" data-composition-src="compositions/entry.html" data-start="0" data-duration="2.5" data-track-index="1" data-width="1920" data-height="1080"></div>
<div id="result" data-composition-id="result" data-composition-src="compositions/result.html" data-start="2.5" data-duration="2.5" data-track-index="2" data-width="1920" data-height="1080"></div>
<audio id="score" class="clip" src="assets/brag/music/happy-beats-business-moves-vol-10-by-ende-dot-app.mp3" data-start="0" data-duration="5" data-volume="0.15" data-fade-in="0.1" data-fade-out="0.4"></audio>
</div><script src="assets/gsap.min.js"></script><script>window.__timelines=window.__timelines||{};window.__timelines.main=gsap.timeline({paused:true}).to({x:0},{x:1,duration:5});</script></body></html>'''
    entry = '''<template><style>#root{position:absolute;inset:0;background:#101827;color:white;font-family:Inter}#entry-title{position:absolute;left:160px;top:200px;font-size:110px;margin:0}#entry-sub{position:absolute;left:160px;top:460px;font-size:60px}</style>
<div id="root" data-composition-id="entry" data-width="1920" data-height="1080"><div class="clip" data-start="0" data-duration="2.5"><h1 id="entry-title">Orbit projects</h1><p id="entry-sub">Organize projects.</p></div></div>
<script>const tl=gsap.timeline({paused:true});tl.fromTo('#entry-title',{x:120},{x:0,duration:1.1,ease:'power4.out'},0).fromTo('#entry-sub',{y:50},{y:0,duration:1,ease:'power3.out'},0.4);window.__timelines.entry=tl;</script></template>'''
    result = '''<template><style>#root{position:absolute;inset:0;background:#101827;color:white;font-family:Inter}#result-panel{position:absolute;left:150px;top:150px;width:1500px;height:650px;background:#172a45;border-radius:30px;padding:60px}h1{font-size:70px;margin:0}p{font-size:56px}#result-bar{background:#67e8f9;height:12px;transform-origin:left}</style>
<div id="root" data-composition-id="result" data-width="1920" data-height="1080"><div class="clip" data-start="0" data-duration="2.5"><div id="result-panel"><h1>Orbit projects</h1><p>Keep notes close to your work.</p><div id="result-bar"></div></div></div></div>
<script>const tl=gsap.timeline({paused:true});tl.fromTo('#result-panel',{y:90},{y:0,duration:1.1,ease:'power4.out'},0).fromTo('#result-bar',{scaleX:0.1},{scaleX:1,duration:1.6,ease:'power2.inOut'},0.3);window.__timelines.result=tl;</script></template>'''
    return {"index.html":root,"compositions/entry.html":entry,"compositions/result.html":result}


def test_full_is_default_and_no_simple_substitution(project, monkeypatch, tmp_path):
    assert spec(project)["engine"] == "full"
    monkeypatch.setattr(video, "OUTPUT_ROOT", tmp_path/"outputs")
    monkeypatch.setattr(full, "doctor", lambda **_: {"ready":False,"error":"missing actual runtime"})
    simple = Mock(side_effect=AssertionError("Must never downgrade"))
    monkeypatch.setattr(video, "render", simple)
    with pytest.raises(RuntimeError, match="missing actual runtime"):
        video.start({"project_path":str(project)})
    simple.assert_not_called()


def test_plan_contract(project):
    full.validate_plan(plan(), spec(project))
    bad = plan()
    bad["storyboard"][0]["duration"] = 10
    with pytest.raises(ValueError, match="durations"):
        full.validate_plan(bad, spec(project))


@pytest.mark.parametrize("name,body", [("../escape.py","pass"), ("package.json","{}"),
    ("assets/gsap.min.js","broken"), ("index.html","<head></head><script>fetch('https://evil.invalid')</script>")])
def test_model_cannot_write_shell_or_network_files(tmp_path, name, body):
    with pytest.raises(ValueError):
        full.write_files({"index.html":"<html><head></head></html>",name:body}, tmp_path)


def test_zero_coverage_or_skipped_browser_never_passes():
    for report in ({"ok":True}, {"ok":True,"contrast":{"enabled":True,"ok":True,"checked":0}},
                   {"ok":True,"browserSkipped":True,"contrast":{"enabled":True,"ok":True,"checked":12}}):
        with pytest.raises(ValueError):
            full.require_contrast(report)
    full.require_contrast({"ok":True,"contrast":{"enabled":True,"ok":True,"checked":8}})


def test_source_context_preserves_brand_markup_but_excludes_configuration(project):
    (project/"secrets.css").write_text("secret")
    result = full.source_context(spec(project))
    assert "<h1>Orbit projects</h1>" in result["index.html"]
    with pytest.raises(ValueError):
        full.source_context(spec(project, source_files=["secrets.css"]))


def test_no_usable_provider_response_is_explicit_failure(monkeypatch):
    from core import gemini
    monkeypatch.setattr(gemini, "as_json", lambda *a, **kw: None)
    with pytest.raises(RuntimeError, match="No simple renderer"):
        full.model_json("build")


def test_check_parser_handles_actual_cli_notices():
    text = '[INFO] startup\n'+json.dumps({"ok":True,"contrast":{"enabled":True,"ok":True,"checked":2}})
    full.require_contrast(full.check_report(text))


@pytest.mark.parametrize("format,duration", [("landscape",5),("landscape",20),("vertical",5),("square",5)])
def test_real_hyperframes_full_pipeline_with_fixture_director(project, tmp_path, monkeypatch, format, duration):
    if os.environ.get("JARVIS_TEST_HYPERFRAMES") != "1":
        pytest.skip("Set JARVIS_TEST_HYPERFRAMES=1 for actual Hyperframes check/snapshot/render integration")
    folder = tmp_path/"render"
    folder.mkdir()
    calls = []
    def director(prompt, pictures=()):
        calls.append((prompt[:80], len(pictures)))
        if "Return JSON {rubric:" in prompt:
            data = plan()
            for scene in data["storyboard"]:
                scene["duration"] = duration/2
            return data
        if "Return JSON {files:" in prompt:
            width,height = video.FORMATS[format]
            output = {k:v.replace('data-width="1920"',f'data-width="{width}"').replace('data-height="1080"',f'data-height="{height}"')
                .replace('width:1920px;height:1080px',f'width:{width}px;height:{height}px')
                .replace('left:150px;top:150px;width:1500px;height:650px;',f'left:90px;top:150px;width:{width-300}px;height:650px;')
                .replace('data-duration="2.5"',f'data-duration="{duration/2}"').replace('data-start="2.5"',f'data-start="{duration/2}"')
                .replace('data-duration="5"',f'data-duration="{duration}"').replace('duration:5}',f'duration:{duration}}}') for k,v in files().items()}
            return {"files":output}
        return {"approved":True,"issues":[],"poster_time":duration*.75}
    monkeypatch.setattr(full,"model_json",director)
    stages = []
    result = full.render(spec(project, format=format, duration=duration), folder, threading.Event(), lambda stage, _: stages.append(stage))
    assert result["engine"] == "full"
    assert Path(result["video"]).stat().st_size > 10000
    assert (folder/"CREDITS.txt").is_file()
    assert "CC BY 4.0" in (folder/"CREDITS.txt").read_text()
    assert "hyperframes_check" in stages and "visual_review" in stages and "hyperframes_render" in stages
    assert any(n>0 for _,n in calls), "Actual snapshot images did not reach the visual reviewer"
    full.require_contrast(full.check_report((folder/"work"/"check-0.json").read_text()))
    report = full._probe(Path(result["video"]), full.environment())
    assert abs(float(report["format"]["duration"])-duration)<.15
    assert any(s["codec_type"]=="audio" for s in report["streams"])


def test_setup_uses_real_gate_without_running_installer(monkeypatch):
    from core import confirm
    monkeypatch.setattr(full,"_node",lambda: "node")
    monkeypatch.setattr(confirm,"_show_cb",None)
    run = Mock(side_effect=AssertionError("Must require a human approval"))
    monkeypatch.setattr(full.subprocess,"run",run)
    assert "not done" in full.setup()
    run.assert_not_called()


def test_symlink_to_private_source_is_rejected(project):
    (project/"credentials.tsx").write_text("PRIVATE")
    (project/"page.tsx").symlink_to(project/"credentials.tsx")
    with pytest.raises(ValueError, match="Symlink"):
        full.source_context(spec(project,source_files=["page.tsx"]))


def test_common_inline_credentials_scrubbed(project):
    (project/"App.tsx").write_text('const api_key = "private-example"; const mail="owner@example.com";')
    result = full.source_context(spec(project,source_files=["App.tsx"]))
    assert "private-example" not in result["App.tsx"]
    assert "owner@example.com" not in result["App.tsx"]


def test_svg_namespace_is_not_a_remote_request(tmp_path):
    full.write_files({"index.html":'<html><head></head><body><svg xmlns="http://www.w3.org/2000/svg"></svg></body></html>'},tmp_path)
    assert "Content-Security-Policy" in (tmp_path/"index.html").read_text()
    with pytest.raises(ValueError,match="canonical"):
        full.write_files({"index.html":"<head></head>","index.html/":"<head></head>"},tmp_path)


def test_audio_flags_and_nonmute_are_enforced(project, tmp_path):
    composition=tmp_path/"comp"
    composition.mkdir()
    (composition/"index.html").write_text(files()["index.html"])
    full.require_audio(composition,spec(project))
    with pytest.raises(ValueError,match="violates"):
        full.require_audio(composition,spec(project,music=False))
    (composition/"index.html").write_text(files()["index.html"].replace('data-volume="0.15"','data-volume="0"'))
    with pytest.raises(ValueError,match="non-muted"):
        full.require_audio(composition,spec(project))


@pytest.mark.parametrize("gate", ["check","visual"])
def test_unresolved_real_gates_never_reach_render(project,tmp_path,monkeypatch,gate):
    from PIL import Image
    package=tmp_path/"runtime"
    vendor=package/"dist"/"vendor"/"npm"/"gsap@fake"/"dist"
    vendor.mkdir(parents=True)
    (vendor/"gsap.min.js").write_text("// fixture")
    monkeypatch.setattr(full,"_runtime",lambda:(package,package))
    monkeypatch.setattr(full,"doctor",lambda **kw:{"ready":True})
    monkeypatch.setattr(full,"environment",lambda:{})
    monkeypatch.setattr(full,"guidance",lambda:"fixture")
    def director(prompt,pictures=()):
        if "Return JSON {rubric:" in prompt:
            return plan()
        if "Return JSON {files:" in prompt:
            return {"files":files()}
        return {"approved":False,"issues":["UI must be readable"],"poster_time":3.8}
    monkeypatch.setattr(full,"model_json",director)
    commands=[]
    def command(args,cwd,event,log,timeout=180):
        commands.append(args[0])
        assert args[0] != "render", "Rejected composition reached delivery render"
        if args[0]=="snapshot":
            snaps=Path(args[args.index("--output")+1]);snaps.mkdir(exist_ok=True)
            Image.new("RGB",(32,32),"white").save(snaps/"3.8.png")
        return 0,json.dumps({"ok":gate!="check","contrast":{"enabled":True,"ok":True,"checked":4}})
    monkeypatch.setattr(full,"command",command)
    folder=tmp_path/"out";folder.mkdir()
    with pytest.raises(RuntimeError,match="three author/repair attempts"):
        full.render(spec(project),folder,threading.Event(),lambda *a:None)
    assert commands.count("check")==3
    assert not (folder/"brag.mp4").exists()


def test_revision_preserves_original_and_passes_edit_context(project,tmp_path,monkeypatch):
    monkeypatch.setattr(video,"OUTPUT_ROOT",tmp_path/"jobs")
    job="a"*16
    folder=video.OUTPUT_ROOT/job;folder.mkdir(parents=True)
    (folder/"job.json").write_text(json.dumps({"job_id":job,"status":"completed","engine":"full"}))
    (folder/"plan.json").write_text(json.dumps(spec(project)))
    start=Mock(return_value={"status":"queued"})
    monkeypatch.setattr(video,"start",start)
    video.revise(job,"Slow the product reveal")
    request=start.call_args.args[0]
    assert request["project_path"]==str(project)
    assert request["revision_of"]==job and request["revision"]=="Slow the product reveal"
    assert json.loads((folder/"job.json").read_text())["status"]=="completed"


def test_url_capture_never_inherits_jarvis_product_claims():
    request=video.validate_request({"url":"https://example.com/product"})
    assert request["title"]=="example.com"
    assert request["source"]["sources"]==[]
    assert "JARVIS" not in request["source"]["excerpt"]
    for url in ("https://user:pass@example.com", "https://example.com/?token=secret", "file:///etc/passwd"):
        with pytest.raises(ValueError):
            video.validate_request({"url":url})


def test_blocked_capture_fails_without_substituting_local_project(project,tmp_path,monkeypatch):
    monkeypatch.setattr(full,"doctor",lambda **kw:{"ready":True})
    monkeypatch.setattr(full,"environment",lambda:{})
    command=Mock(return_value=(1,'{"ok":false,"error":"Website capture blocked"}'))
    monkeypatch.setattr(full,"command",command)
    local=Mock(side_effect=AssertionError("No unrelated project fallback"))
    monkeypatch.setattr(full,"source_context",local)
    folder=tmp_path/"out";folder.mkdir()
    with pytest.raises(RuntimeError,match="could not be captured"):
        full.render(spec(project,url="https://example.com"),folder,threading.Event(),lambda *a:None)
    local.assert_not_called()
    assert not (folder/"brag.mp4").exists()


def test_cancel_kills_hyperframes_children_and_parent(tmp_path,monkeypatch):
    import psutil
    monkeypatch.setattr(full,"_runtime",lambda:(tmp_path,tmp_path))
    monkeypatch.setattr(full,"environment",lambda:{})
    monkeypatch.setattr(full,"_node",lambda:"node")
    process=Mock(pid=12345)
    process.poll.return_value=None
    monkeypatch.setattr(full.subprocess,"Popen",Mock(return_value=process))
    child=Mock()
    parent=Mock()
    parent.children.return_value=[child]
    monkeypatch.setattr(psutil,"Process",lambda pid:parent)
    monkeypatch.setattr(psutil,"wait_procs",Mock())
    event=threading.Event();event.set()
    with pytest.raises(video.Cancelled):
        full.command(["check","--json"],tmp_path,event,tmp_path/"cancel.log")
    child.kill.assert_called_once()
    process.kill.assert_called_once()
