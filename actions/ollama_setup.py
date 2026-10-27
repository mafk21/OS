"""No-extra-approval local Ollama setup requested by the user."""
import json


def ollama_setup(parameters=None, player=None, speak=None, **_):
    from core import ollama_setup as setup
    p = parameters or {}
    action = str(p.get("action") or "setup").lower()
    try:
        if action == "doctor":
            return json.dumps(setup.doctor())
        if action == "status":
            return json.dumps(setup.status(p.get("job_id")))
        if action == "cancel":
            return json.dumps(setup.cancel(p.get("job_id")))
        if action != "setup":
            return "Use setup, status, cancel or doctor."
        def notify(data):
            text = json.dumps(data)
            terminal = data["status"] in ("completed", "failed", "cancelled")
            if player is not None:
                try:
                    player.show_content("OLLAMA SETUP", text)
                except Exception:
                    pass
                if terminal:
                    try:
                        player.write_log("SYS: Ollama setup result: "+text)
                    except Exception:
                        pass
            if terminal and callable(speak):
                try:
                    speak("Report the actual Ollama setup result. Only completed means a local inference passed. "
                          "Do not claim cloud voice was replaced or request another approval. Result: "+text)
                except Exception:
                    pass
        return json.dumps(setup.start(p.get("model", "auto"), p.get("activate", False), notify))
    except Exception as exc:
        return f"Ollama setup not started: {type(exc).__name__}: {exc}"


TOOL = {
    "name":"ollama_setup",
    "description":("Install/connect Ollama when the user requests local AI setup. No additional JARVIS approval: "
        "uses SHA-256-verified official portable release, starts loopback HTTP server, chooses a hardware-fit "
        "Qwen3 model, downloads it and tests actual inference before saving local settings. Model downloads "
        "can be multi-GB. Auto is a conservative hardware heuristic, not a universal best-model claim. "
        "Runs background with HUD completion; queued is not ready. No sudo/UAC bypass or arbitrary shell. "
        "Default preserves cloud voice/provider and enables local offline fallback. Set activate=true only "
        "when asked to select local text provider; this does NOT replace live voice/STT/TTS. Use status/cancel/doctor."),
    "parameters":{"type":"OBJECT", "properties":{
        "action":{"type":"STRING", "enum":["setup","status","cancel","doctor"]},
        "model":{"type":"STRING", "enum":["auto","qwen3:0.6b","qwen3:1.7b","qwen3:4b","qwen3:8b","qwen3:14b","qwen3:30b-a3b"]},
        "activate":{"type":"BOOLEAN", "description":"Explicitly select local text provider after successful inference. Default false preserves cloud provider/voice."},
        "job_id":{"type":"STRING", "description":"ID returned by setup for status/cancel."}
    }},
    "handler":ollama_setup,
    "behavior":"NON_BLOCKING",
    "scheduling":"WHEN_IDLE"
}
