"""Brag launch videos through JARVIS's existing action/skill registries."""
import json

from core import brag_video as engine


def brag_video(parameters=None, player=None, speak=None, **_):
    params = parameters or {}
    action = str(params.get("action") or "generate").lower()
    try:
        if action == "doctor":
            return json.dumps(engine.doctor(), ensure_ascii=False)
        if action == "inspect":
            return json.dumps(engine.inspect_project(str(params.get("project_path") or engine.BASE)), ensure_ascii=False)
        if action == "status":
            return json.dumps(engine.status(params.get("job_id")), ensure_ascii=False)
        if action == "cancel":
            return json.dumps(engine.cancel(params.get("job_id")), ensure_ascii=False)
        if action != "generate":
            return "Unknown brag_video action. Use inspect, generate, doctor, status, or cancel."
        def notify(data, autoplay):
            text = json.dumps(data, ensure_ascii=False)
            if player is not None:
                updates = [("show_content", ("BRAG VIDEO — " + data["status"], text))]
                if data["status"] in ("completed", "failed", "cancelled"):
                    updates.append(("write_log", ("SYS: Brag video result: " + text,)))
                for method, args in updates:
                    try:
                        getattr(player, method)(*args)
                    except Exception:
                        pass
                if autoplay and data["status"] == "completed":
                    try:
                        from actions.video_player import video_player
                        video_player({"action": "play", "source": data["video"]}, player=player)
                    except Exception:
                        pass
            if callable(speak) and data["status"] in ("completed", "failed", "cancelled"):
                try:
                    speak("Report this actual video-render result accurately. Only status completed means a verified MP4 exists. Do not claim upload/publishing. Result: " + text)
                except Exception:
                    pass
        return json.dumps(engine.start(params, notify=notify), ensure_ascii=False)
    except Exception as exc:
        return f"Brag video not started: {type(exc).__name__}: {exc}"


TOOL = {
    "name": "brag_video",
    "description": "Create a local Brag-style project launch video (MP4, poster, storyboard, share copy). Use for /brag, make a launch/demo/promo video, show off this project. Inspect public project copy first, then supply factual hook/highlights. Starts a background render; queued is NOT completed. No Hyperframes, Claude subscription, publishing, software installs or arbitrary source execution. Use doctor/status/cancel for dependencies and jobs.",
    "parameters": {"type": "OBJECT", "properties": {
        "action": {"type": "STRING", "enum": ["inspect", "generate", "doctor", "status", "cancel"]},
        "project_path": {"type": "STRING", "description": "Existing local project directory. Default: JARVIS project."},
        "job_id": {"type": "STRING", "description": "ID returned by generate; required for status/cancel."},
        "title": {"type": "STRING"},
        "hook": {"type": "STRING", "description": "Short factual opening, grounded in the inspected project."},
        "highlights": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "1–3 short, factual product highlights. No invented metrics/testimonials."},
        "outro": {"type": "STRING"},
        "tone": {"type": "STRING", "enum": sorted(engine.TONES)},
        "format": {"type": "STRING", "enum": list(engine.FORMATS)},
        "duration": {"type": "NUMBER", "description": "5–30 seconds, default 20. Brag normally uses 15–25."},
        "quality": {"type": "STRING", "enum": ["draft", "final"]},
        "image_paths": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Optional user-selected product screenshots/images inside project; without them render source-copy motion cards, not a captured app demo."},
        "music": {"type": "BOOLEAN", "description": "Original synthesized score, default true."},
        "sfx": {"type": "BOOLEAN", "description": "Soft original scene cues, default true."},
        "voice": {"type": "BOOLEAN", "description": "Opt-in narration using configured OpenAI-compatible speech adapter, default false. Fails explicitly if unavailable or too long."},
        "autoplay": {"type": "BOOLEAN", "description": "Play verified MP4 in JARVIS HUD after render, default false."}
    }},
    "handler": brag_video,
}
