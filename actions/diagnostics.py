"""Diagnostics Health Window — Phase 5.4: audio, keys, network, storage, skills & DB checks."""

from __future__ import annotations

import pathlib
import shutil


def _check_api_key() -> tuple[str, str]:
    try:
        import memory.config_manager as cm
        gk = cm.get_gemini_key() or ""
        ok = cm.get_openai_key() or ""
        parts = []
        if gk and len(gk) > 15:
            parts.append("Gemini configured")
        if ok and len(ok) > 15:
            parts.append("OpenAI configured")
        if cm.get_anthropic_key():
            parts.append("Anthropic configured")
        if parts:
            # Diagnostics must never disclose credential prefixes. Prefixes are
            # still credential material and do not help users repair settings.
            return ("ok", " | ".join(parts))
        return ("missing", "—")
    except Exception as e:
        return ("error", str(e))


def _check_mic() -> tuple[str, str]:
    try:
        import sounddevice as sd
        devs = sd.query_devices()
        default_in = (
            sd.default.device[0]
            if isinstance(sd.default.device, (list, tuple))
            else sd.default.device
        )
        return ("ok", f"{len(devs)} devices, default in={default_in}")
    except Exception as e:
        return ("missing", f"sounddevice: {e}")


def _check_speaker() -> tuple[str, str]:
    try:
        import sounddevice as sd
        return ("ok", f"default out={sd.default.device}")
    except Exception as e:
        return ("missing", str(e))


def _check_connectivity() -> tuple[str, str]:
    try:
        import requests
        import memory.config_manager as cm
        engine = cm.resolve_cloud_engine()
        url = (
            cm.get_openai_cfg().get("base_url", "https://api.openai.com/v1")
            if engine == "openai"
            else "https://generativelanguage.googleapis.com"
        )
        r = requests.get(url, timeout=5)
        return ("ok", f"{engine} HTTP {r.status_code}")
    except Exception as e:
        return ("offline", str(e)[:80])


def _check_camera() -> tuple[str, str]:
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ok = cap.isOpened()
        cap.release()
        return ("ok" if ok else "no camera", "0" if ok else "not found")
    except Exception as e:
        return ("missing", str(e)[:80])


def _check_ollama() -> tuple[str, str]:
    try:
        import requests
        import memory.config_manager as cm
        url = cm.get_local_llm_cfg().get("url", "http://localhost:11434").rstrip("/")
        r = requests.get(f"{url}/api/tags", timeout=3)
        return ("ok" if r.status_code == 200 else "offline", url)
    except Exception as e:
        return ("offline", str(e)[:80])


def _check_storage() -> tuple[str, str]:
    try:
        usage = shutil.disk_usage(pathlib.Path.cwd())
        free_gb = usage.free / (1024 ** 3)
        pct_free = (usage.free / usage.total) * 100.0 if usage.total else 0.0
        status = "ok" if free_gb >= 1.0 else "low"
        return (status, f"{free_gb:.1f} GB free ({pct_free:.0f}%)")
    except Exception as e:
        return ("error", str(e)[:80])


def _check_skills() -> tuple[str, str]:
    try:
        from core.skill_loader import discover_skills
        base = pathlib.Path(__file__).resolve().parent.parent
        reg = discover_skills(base / "skills", logger=lambda _: None)
        return ("ok", f"{len(reg)} active skill(s) in skills/")
    except Exception as e:
        return ("error", str(e)[:80])


_ALL_CHECKS = {
    "api_key": _check_api_key,
    "mic": _check_mic,
    "speaker": _check_speaker,
    "connectivity": _check_connectivity,
    "storage": _check_storage,
    "skills": _check_skills,
    "camera": _check_camera,
    "ollama": _check_ollama,
}

_GROUPS = {
    "audio": ("mic", "speaker"),
    "network": ("api_key", "connectivity", "ollama"),
    "storage": ("storage", "skills"),
    "skills": ("skills",),
}

_HINTS = {
    "api_key": "→ Set gemini_api_key in config/api_keys.json (aistudio.google.com)",
    "mic": "→ Check Audio Devices in ⚙, or plug in headset",
    "speaker": "→ Check Audio Devices in ⚙",
    "connectivity": "→ Check internet/VPN; offline fallback uses local LLM",
    "storage": "→ Free disk space (run safe-file-organizer skill on Downloads)",
    "skills": "→ Verify SKILL.md frontmatter in skills/",
    "camera": "→ Allow camera in OS privacy settings",
    "ollama": "→ Optional offline LLM: ollama serve && ollama pull llama3.2",
}


def diagnostics_check(parameters: dict, player=None, **_) -> str:
    action = str((parameters or {}).get("action", "full") or "full").strip().lower()
    if action == "repair":
        from core.system_repair import request_repair
        return request_repair(str((parameters or {}).get("repair") or ""))
    if action in {"system", "identity", "report"}:
        from core.system_doctor import run_doctor, write_support_report
        report = run_doctor()
        identity = report["installation"]
        lines = [
            f"JARVIS System Doctor — {str(report['overall']).upper()}",
            f"  Installation: {identity['installation_id']} ({identity['install_type']}, {identity['revision']})",
            f"  Runtime: Python {identity['python']} on {identity['platform']}",
        ]
        for item in report["results"]:
            icon = "✓" if item["status"] == "ok" else ("!" if item["status"] == "warning" else "✗")
            lines.append(f"  {icon} {item['check']}: {item['summary']}")
            if item["remediation"]:
                lines.append(f"    → {item['remediation']}")
        if action == "report":
            try:
                lines.append(f"  Redacted report: {write_support_report()}")
            except Exception as exc:
                lines.append(f"  ✗ Report export failed safely ({type(exc).__name__}).")
        out = "\n".join(lines)
        if player and hasattr(player, "show_content"):
            player.show_content("SYSTEM DOCTOR", out)
        if player and hasattr(player, "write_log"):
            player.write_log(f"[System Doctor] {report['counts']}")
        return out

    selected = _GROUPS.get(action, tuple(_ALL_CHECKS.keys()))

    results = {}
    for name in selected:
        fn = _ALL_CHECKS[name]
        try:
            results[name] = fn()
        except Exception as e:
            results[name] = ("error", str(e))

    lines = [f"Diagnostics ({action}) — what works / how to fix:"]
    for k, (status, detail) in results.items():
        icon = "✓" if status == "ok" else ("✗" if status in ("missing", "offline", "error", "low") else "–")
        lines.append(f"  {icon} {k}: {status} — {detail}")
        if status != "ok" and k in _HINTS:
            lines.append(f"    {_HINTS[k]}")

    out = "\n".join(lines)
    if player:
        if hasattr(player, "show_content"):
            player.show_content("DIAGNOSTICS", out)
        if hasattr(player, "write_log"):
            player.write_log(f"[Diagnostics] Checked {len(results)} subsystem(s)")
    return out


TOOL = {
    "name": "diagnostics_check",
    "description": (
        "Diagnostics Health Window: checks API key, microphone, speaker, "
        "connectivity, disk storage, installed skills, camera, and local LLM "
        "(Ollama) with actionable fix hints. System Doctor also reports the exact "
        "running installation and core product health without exposing credentials. "
        "Actions: full | system | identity | report | repair | audio | network | storage | skills. "
        "Repair requires an allowlisted repair name and always opens a human confirmation."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "full | system | identity | report | repair | audio | network | storage | skills",
            },
            "repair": {
                "type": "STRING",
                "description": "For action=repair: shortcut | permissions | dependencies | hud | hud_port | soul_backup",
            },
        },
    },
    "required": [],
    "handler": diagnostics_check,
}
