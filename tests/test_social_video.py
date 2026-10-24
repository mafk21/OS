from __future__ import annotations

from pathlib import Path
import time
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from actions.social_video import social_video
from actions.video_player import video_player
from actions.youtube_video import youtube_video
from core.action_loader import discover_actions
from core.apex_bridge import ApexHudBridge
import core.media_engine as me

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_platform_detection_direct_url_guard_and_clipboard(monkeypatch):
    assert me.detect_platform("https://www.instagram.com/reel/C9xYz123/") == "Instagram"
    assert me.detect_platform("https://youtu.be/dQw4w9WgXcQ") == "YouTube"
    assert me.detect_platform("https://www.youtube.com/shorts/abc123def45") == "YouTube"
    assert me.detect_platform("https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYa2") == "Snapchat"
    assert me.detect_platform("https://vm.tiktok.com/ZMh12345/") == "TikTok"
    assert me.detect_platform("https://x.com/NASA/status/1234567890") == "X"
    assert me.detect_platform("https://v.redd.it/987654321") == "Reddit"
    assert me.detect_platform("https://fb.watch/abc123/") == "Facebook"
    assert me.detect_platform("https://vimeo.com/12345678") == "Vimeo"

    # Social pages are NEVER treated as raw direct .mp4 files
    assert me.is_direct_media_url("https://www.instagram.com/reel/C9xYz123/") is False
    assert me.is_direct_media_url("https://www.snapchat.com/spotlight/abc") is False
    assert me.is_direct_media_url("https://cdn.example.org/clips/demo.mp4") is True

    # Clipboard fallback when user says "download this video"
    monkeypatch.setattr("pyperclip.paste", lambda: "Check this out https://www.instagram.com/reel/Clip999/ !")
    extracted = me.extract_url_from_text_or_clipboard("", allow_clipboard=True)
    assert extracted == "https://www.instagram.com/reel/Clip999/"


def test_resolve_stream_instagram_snapchat_and_youtube_dash_plus_cookie_retry():
    # 1. Instagram progressive MP4 with CDN Referer header
    insta_info = {
        "title": "Sunset Skate Reel",
        "uploader": "skater_pro",
        "webpage_url": "https://www.instagram.com/reel/Sun123/",
        "duration": 19,
        "http_headers": {"Referer": "https://www.instagram.com/"},
        "formats": [
            {
                "url": "https://scontent.cdninstagram.com/v/t50/reel.mp4",
                "ext": "mp4",
                "vcodec": "avc1.64001f",
                "acodec": "mp4a.40.2",
                "height": 1080,
                "tbr": 2400,
            }
        ],
    }
    with patch.object(me, "_extract_with_ytdlp", return_value=insta_info):
        s = me.resolve_playable_stream("https://www.instagram.com/reel/Sun123/")
        assert s.ok is True
        assert s.platform == "Instagram"
        assert s.video_url.endswith("reel.mp4")
        assert s.audio_url == ""
        assert s.http_headers.get("Referer") == "https://www.instagram.com/"

    # 2. YouTube split DASH chooses original language track over auto-dub
    yt_info = {
        "title": "Deep Space Documentary",
        "uploader": "AstroChannel",
        "webpage_url": "https://www.youtube.com/watch?v=abc123def45",
        "duration": 240,
        "formats": [
            {
                "url": "https://rr1.googlevideo.com/video_720.mp4",
                "ext": "mp4",
                "protocol": "https",
                "vcodec": "avc1.4d401f",
                "acodec": "none",
                "height": 720,
                "tbr": 1800,
            },
            {
                "url": "https://rr1.googlevideo.com/audio_dub_es.m4a",
                "ext": "m4a",
                "protocol": "https",
                "vcodec": "none",
                "acodec": "mp4a.40.2",
                "language": "es",
                "language_preference": -1,
                "abr": 130.0,
            },
            {
                "url": "https://rr1.googlevideo.com/audio_orig_en.m4a",
                "ext": "m4a",
                "protocol": "https",
                "vcodec": "none",
                "acodec": "mp4a.40.2",
                "language": "en",
                "language_preference": 10,
                "abr": 128.0,
            },
        ],
    }
    with patch.object(me, "_extract_with_ytdlp", return_value=yt_info):
        sy = me.resolve_playable_stream("https://www.youtube.com/watch?v=abc123def45", max_height=720)
        assert sy.ok is True
        assert sy.platform == "YouTube"
        assert sy.video_url.endswith("video_720.mp4")
        assert sy.audio_url.endswith("audio_orig_en.m4a")


def test_social_video_download_instagram_snapchat_and_youtube(tmp_path):
    def _fake_extract(url, opts, *, download=False, cookies_browser=""):
        assert download is True
        outtmpl = opts["outtmpl"]
        stage_dir = Path(outtmpl).parent
        ext = "mp3" if any(
            p.get("preferredcodec") == "mp3" for p in (opts.get("postprocessors") or [])
        ) else "mp4"
        staged = stage_dir / f"sample.{ext}"
        staged.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"x" * 4096)
        return {
            "id": "xyz987",
            "title": "Amazing Desert Drone Shot",
            "uploader": "desert_flyer",
            "duration": 34,
            "webpage_url": url,
        }

    cards: list[tuple[str, str]] = []
    dummy_player = SimpleNamespace(
        write_log=lambda _m: None,
        show_content=lambda title, body: cards.append((title, body)),
    )

    with patch.object(me, "_extract_with_ytdlp", side_effect=_fake_extract):
        # Snapchat Spotlight download
        out_snap = social_video(
            {
                "action": "download",
                "url": "https://www.snapchat.com/spotlight/W7_DesertClip",
                "destination": str(tmp_path),
            },
            player=dummy_player,
        )
        assert "Downloaded Snapchat video" in out_snap
        saved_snap = [p for p in tmp_path.glob("*.mp4") if "[Snapchat]" in p.name]
        assert len(saved_snap) == 1
        assert saved_snap[0].stat().st_size > 1000
        assert cards and "Snapchat Download Complete" in cards[-1][0]

        # Instagram Reel download
        out_ig = social_video(
            {
                "action": "download",
                "url": "https://www.instagram.com/reel/C88Reel/",
                "destination": str(tmp_path),
            },
            player=dummy_player,
        )
        assert "Downloaded Instagram video" in out_ig
        saved_ig = [p for p in tmp_path.glob("*.mp4") if "[Instagram]" in p.name]
        assert len(saved_ig) == 1

        # YouTube MP3 audio download
        out_yt_mp3 = social_video(
            {
                "action": "download",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "audio_only": True,
                "destination": str(tmp_path),
            },
            player=dummy_player,
        )
        assert "Downloaded YouTube audio" in out_yt_mp3
        saved_mp3 = [p for p in tmp_path.glob("*.mp3") if "[YouTube]" in p.name]
        assert len(saved_mp3) == 1


def test_video_player_supports_instagram_and_hud_media_range_streaming(tmp_path):
    sample_mp4 = tmp_path / "local_clip.mp4"
    payload = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 64
    sample_mp4.write_bytes(payload)

    bridge = ApexHudBridge(None)
    app = bridge._build_app()

    with TestClient(app) as client:
        bridge.push_video(
            str(sample_mp4),
            title="Instagram: Night Timelapse",
            muted=True,
            webpage_url="https://www.instagram.com/reel/Night99/",
            platform="Instagram",
        )
        assert bridge.video_is_playing() is True

        snap = client.get("/api/hud/bootstrap").json()
        assert snap["video"] is not None
        assert snap["video"]["platform"] == "Instagram"
        media_url = snap["video"]["video_url"]

        # Verify HTTP 206 Partial Content Range streaming
        r_range = client.get(media_url, headers={"Range": "bytes=0-15"})
        assert r_range.status_code == 206
        assert r_range.content == payload[:16]
        assert r_range.headers["content-range"] == f"bytes 0-15/{len(payload)}"

        # Unmute & close via HUD actions
        r_mute = client.post("/api/hud/action", json={"action": "video_mute", "muted": False})
        assert r_mute.status_code == 200
        assert bridge._video["muted"] is False

        r_close = client.post("/api/hud/action", json={"action": "video_close"})
        assert r_close.status_code == 200
        assert bridge.video_is_playing() is False


def test_video_player_routes_non_youtube_social_urls_through_ytdlp():
    shown: list[tuple[str, str, str]] = []

    class FakePlayer:
        def video_is_playing(self):
            return False

        def show_video(self, src, title="", muted=True, audio_source="", headers=None, webpage_url="", platform=""):
            shown.append((src, title, platform))

    fake_stream = me.ResolvedStream(
        ok=True,
        video_url="https://cdn.snapchat.com/stream/spot123.mp4",
        title="City Lights",
        platform="Snapchat",
        webpage_url="https://www.snapchat.com/spotlight/spot123",
        http_headers={"Referer": "https://www.snapchat.com/"},
    )
    fp = FakePlayer()
    with patch("actions.video_player.resolve_playable_stream", return_value=fake_stream):
        res = video_player(
            {"action": "play", "source": "https://www.snapchat.com/spotlight/spot123"},
            player=fp,
        )
        assert res.startswith("status=opening")
        deadline = time.time() + 1.5
        while not shown and time.time() < deadline:
            time.sleep(0.02)

    assert len(shown) == 1
    assert shown[0][0] == "https://cdn.snapchat.com/stream/spot123.mp4"
    assert shown[0][2] == "Snapchat"


def test_summarize_media_and_action_discovery_all_valid():
    vtt = "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nWelcome to Khobar corniche.\n00:00:02.000 --> 00:00:05.000\nSunset view over the water.\n"
    cleaned = me._clean_subtitle_payload(vtt)
    assert cleaned == "Welcome to Khobar corniche. Sunset view over the water."

    fake_info = {
        "title": "Khobar Walk",
        "uploader": "traveler",
        "duration": 25,
        "description": "Evening walk clip",
        "webpage_url": "https://www.instagram.com/reel/Khobar1/",
        "subtitles": {},
        "automatic_captions": {},
    }
    with patch.object(me, "_extract_with_ytdlp", return_value=fake_info), patch.object(
        me, "_transcribe_short_video_audio", return_value="Welcome to the corniche at sunset."
    ), patch("core.gemini.call", return_value=SimpleNamespace(text="Overview: Sunset walk along Khobar corniche.")):
        s_res = me.summarize_media("https://www.instagram.com/reel/Khobar1/")
        assert s_res["ok"] is True
        assert s_res["platform"] == "Instagram"
        assert "Khobar" in s_res["summary"]

        # youtube_video summarize also handles explicit `url` parameter without tkinter dialog
        yt_sum = youtube_video(
            {"action": "summarize", "url": "https://www.instagram.com/reel/Khobar1/"}
        )
        assert "Khobar" in yt_sum

    # Verify action_loader discovers social_video, video_player, and youtube_video cleanly
    reg = discover_actions(REPO_ROOT / "actions")
    names = {d["name"] for d in reg.get_tool_declarations()}
    assert {"social_video", "video_player", "youtube_video"}.issubset(names)

    # Verify Web HUD video modal is wired
    hud_modal = (REPO_ROOT / "apex_ui" / "components" / "HudVideoModal.tsx").read_text(encoding="utf-8")
    overlays = (REPO_ROOT / "apex_ui" / "components" / "JarvisHudOverlays.tsx").read_text(encoding="utf-8")
    assert 'data-testid="hud-video-player"' in hud_modal
    assert "<HudVideoModal />" in overlays


def test_watch_media_extracts_real_visual_frames_and_watches_active_hud_video(tmp_path):
    import subprocess
    from PIL import Image

    ff = me.resolve_ffmpeg_path()
    assert ff is not None

    # Generate a real 2-second MP4 video (red scene -> blue scene) using bundled ffmpeg
    real_mp4 = tmp_path / "two_scenes.mp4"
    subprocess.run(
        [
            ff,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:s=320x240:d=1",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=320x240:d=1",
            "-filter_complex",
            "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map",
            "[v]",
            "-pix_fmt",
            "yuv420p",
            str(real_mp4),
        ],
        check=True,
        timeout=20,
    )
    assert real_mp4.is_file() and real_mp4.stat().st_size > 500

    frames = me.extract_video_frames(real_mp4, max_frames=4, max_dim=320, duration_hint=2.0)
    assert len(frames) >= 2
    assert all(isinstance(im, Image.Image) for _, im in frames)
    # First frame center pixel should be predominantly red, last frame predominantly blue
    r0, _g0, b0 = frames[0][1].getpixel((160, 120))
    rn, _gn, bn = frames[-1][1].getpixel((160, 120))
    assert r0 > b0
    assert bn > rn

    captured_contents: list[object] = []

    def _fake_vision_call(contents, **_kwargs):
        captured_contents.extend(contents if isinstance(contents, list) else [contents])
        return SimpleNamespace(
            text="At 00:00 the screen is bright red, then at 00:01 it transitions to deep blue."
        )

    # Also verify active HUD video fallback when user asks "can you see it?" with no URL
    dummy_player = SimpleNamespace(
        write_log=lambda _m: None,
        show_content=lambda _t, _b: None,
        current_video_source=lambda: str(real_mp4),
    )

    with patch("core.gemini.call", side_effect=_fake_vision_call):
        out = social_video(
            {"action": "watch", "focus": "What colors appear in the video?"},
            player=dummy_player,
        )

    assert "keyframes inspected" in out
    assert "bright red" in out and "deep blue" in out
    # Confirm real PIL.Image frames were passed to the multimodal model!
    pil_passed = [x for x in captured_contents if isinstance(x, Image.Image)]
    assert len(pil_passed) >= 2

