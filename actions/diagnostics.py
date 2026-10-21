"""Diagnostics Health Window — Phase 5.4: what works/how to fix, mic/speaker/key/connectivity checks."""
import platform, pathlib, json, sys

def _check_api_key():
    try:
        import memory.config_manager as cm
        k=cm.get_gemini_key() or ""
        return ("ok" if k and len(k)>15 else "missing", k[:6]+"…" if k else "—")
    except Exception as e: return ("error", str(e))

def _check_mic():
    try:
        import sounddevice as sd
        devs=sd.query_devices()
        default_in=sd.default.device[0] if isinstance(sd.default.device, (list,tuple)) else sd.default.device
        return ("ok", f"{len(devs)} devices, default in={default_in}")
    except Exception as e: return ("missing", f"sounddevice: {e}")

def _check_speaker():
    try:
        import sounddevice as sd
        return ("ok", f"default out={sd.default.device}")
    except Exception as e: return ("missing", str(e))

def _check_connectivity():
    try:
        import requests
        r=requests.get("https://generativelanguage.googleapis.com", timeout=5)
        return ("ok", f"HTTP {r.status_code}")
    except Exception as e: return ("offline", str(e)[:80])

def _check_camera():
    try:
        import cv2
        cap=cv2.VideoCapture(0)
        ok=cap.isOpened()
        cap.release()
        return ("ok" if ok else "no camera", "0" if ok else "not found")
    except Exception as e: return ("missing", str(e)[:80])

def _check_ollama():
    try:
        import requests, memory.config_manager as cm
        url=cm.get_local_llm_cfg().get("url","http://localhost:11434").rstrip("/")
        r=requests.get(f"{url}/api/tags", timeout=3)
        return ("ok" if r.status_code==200 else "offline", url)
    except Exception as e: return ("offline", str(e)[:80])

def diagnostics_check(parameters: dict, player=None, **_):
    action=str(parameters.get("action","full")).strip().lower()
    checks={
        "api_key": _check_api_key,
        "mic": _check_mic,
        "speaker": _check_speaker,
        "connectivity": _check_connectivity,
        "camera": _check_camera,
        "ollama": _check_ollama,
    }
    results={}
    for name, fn in checks.items():
        try: results[name]=fn()
        except Exception as e: results[name]=("error", str(e))
    lines=["Diagnostics — what works / how to fix:"]
    for k,(status, detail) in results.items():
        icon="✓" if status=="ok" else ("✗" if status in ("missing","offline","error") else "–")
        lines.append(f"  {icon} {k}: {status} — {detail}")
        if status!="ok":
            hints={
                "api_key": "→ Set gemini_api_key in config/api_keys.json (aistudio.google.com)",
                "mic": "→ Check Audio Devices in ⚙, or plug in headset",
                "speaker": "→ Check Audio Devices in ⚙",
                "connectivity": "→ Check internet/VPN; offline fallback uses local LLM",
                "camera": "→ Allow camera in OS privacy settings",
                "ollama": "→ Run: ollama serve && ollama pull llama3.2",
            }
            if k in hints: lines.append(f"    {hints[k]}")
    out="\n".join(lines)
    if player:
        player.show_content("DIAGNOSTICS", out)
        player.write_log("[Diagnostics] Checked 6 subsystems")
    return out

TOOL={
    "name":"diagnostics_check",
    "description":"Diagnostics Health Window: what works/how to fix — checks API key, microphone, speaker, connectivity, camera, local LLM (ollama). Actions: full.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"full"}}},"required":[],"handler":diagnostics_check
}
