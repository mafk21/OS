"""Brag launch videos through JARVIS's existing action/skill registries."""
import json

from core import brag_video as engine


def brag_video(parameters=None, player=None, speak=None, **_):
    params = parameters or {}
    action = str(params.get("action") or "generate").lower()
    try:
        if action == "doctor":
            return json.dumps(engine.doctor(params.get("engine", "full"), voice=params.get("voice", False)), ensure_ascii=False)
        if action == "setup":
            from core.brag_full import setup
            def setup_result(text):
                if player is not None:
                    try:
                        player.show_content("BRAG SETUP", text)
                        player.write_log("SYS: " + text)
                    except Exception:
                        pass
            return setup(notify=setup_result)
        if action == "inspect":
            return json.dumps(engine.inspect_project(str(params.get("project_path") or engine.BASE)), ensure_ascii=False)
        if action in ("preview", "stop_preview"):
            from core.brag_full import preview
            return json.dumps(preview(str(params.get("job_id") or ""), stop=action=="stop_preview"), ensure_ascii=False)
        if action == "status":
            return json.dumps(engine.status(params.get("job_id")), ensure_ascii=False)
        if action == "cancel":
            return json.dumps(engine.cancel(params.get("job_id")), ensure_ascii=False)
        if action not in ("generate", "revise"):
            return "Unknown brag_video action. Use inspect, generate, doctor, setup, status, cancel, revise, preview, or stop_preview."
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
        result = engine.revise(str(params.get("job_id") or ""), params.get("revision"), notify=notify) if action == "revise" else engine.start(params, notify=notify)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return f"Brag video not started: {type(exc).__name__}: {exc}"


TOOL = {
    "name": "brag_video",
    "description": "Create a full Brag launch/promo video using JARVIS's configured model and real Hyperframes: custom HTML/GSAP scenes, upstream music/SFX, iterative check/repair, visual frame review, render, poster and share copy. Default engine=full; never silently downgrade to simple cards. Inspect first. Setup requires real approval for pinned runtime install; doctor checks Node/Chrome/FFprobe. Generation uses the configured model and can incur provider cost. Queued is not completed. No publishing.",
    "parameters": {"type": "OBJECT", "properties": {
        "action": {"type": "STRING", "enum": ["inspect", "generate", "doctor", "setup", "status", "cancel", "revise", "preview", "stop_preview"]},
        "engine": {"type":"STRING", "enum":["full","simple"], "description":"Default full: real Brag/Hyperframes. Simple is explicit lightweight card mode only."},
        "url": {"type":"STRING", "description":"Explicit user-selected public HTTP(S) website to capture as editable product UI; never browse an unrelated site."},
        "asset_paths": {"type":"ARRAY", "items":{"type":"STRING"}, "description":"Explicit public product media/fonts inside project (images, SVG, woff/woff2/ttf, mp4/webm)."},
        "revision": {"type":"STRING", "description":"Requested changes for action=revise. Creates a new independently checked/reviewed/rendered job; preserves the original."},
        "source_files": {"type":"ARRAY", "items":{"type":"STRING"}, "description":"Public UI HTML/CSS/TSX/JSX source paths relative to project. Selected files are sent as context to the configured JARVIS provider."},
        "creative_direction": {"type":"STRING", "description":"Freeform product-film direction in addition to the tone preset."},
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
        "image_paths": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Optional user-selected product screenshots/images inside project; Full mode uses these as visual references and local assets; simple mode without images makes source-copy motion cards."},
        "music": {"type": "BOOLEAN", "description": "Full mode: licensed upstream music (CC BY 4.0, supplied credit); simple: synthesized. Default true."},
        "sfx": {"type": "BOOLEAN", "description": "Full mode: upstream CC0 motion-matched SFX; simple: synthesized. Default true."},
        "voice": {"type": "BOOLEAN", "description": "Off by default. Full mode uses upstream Hyperframes Kokoro (explicit dependencies/model setup); simple mode uses OpenAI-compatible speech. No silent substitution."},
        "autoplay": {"type": "BOOLEAN", "description": "Play verified MP4 in JARVIS HUD after render, default false."}
    }},
    "handler": brag_video,
}
