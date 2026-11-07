"""Structured, privacy-safe health checks for the running JARVIS installation.

The doctor observes before it repairs. Checks never mutate application state,
scan unrelated user folders, or include credentials in reports. This module is
kept UI-independent so Classic UI, APEX, voice tools, and support exports can
consume the same evidence.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_PYTHON = {(3, 11), (3, 12)}


@dataclass(frozen=True)
class InstallationIdentity:
    installation_id: str
    root: str
    executable: str
    entrypoint: str
    install_type: str
    revision: str
    platform: str
    python: str


@dataclass(frozen=True)
class DoctorResult:
    check: str
    status: str  # ok | warning | error
    summary: str
    evidence: str = ""
    remediation: str = ""
    state: str = ""
    code: str = ""

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["code"] = self.code or f"JARVIS-{self.check.upper().replace('_', '-')}-{self.status.upper()}"
        data["state"] = self.state or {
            "ok": "healthy", "warning": "degraded", "error": "unavailable",
        }.get(self.status, "unavailable")
        return data


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        timeout=5, check=False, env=env,
    )


def _revision() -> str:
    if not (ROOT / ".git").exists():
        return "packaged"
    try:
        result = _git("rev-parse", "--short=12", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def installation_identity() -> InstallationIdentity:
    """Describe this exact installation without a machine-specific registry."""
    root = ROOT.resolve()
    executable = Path(sys.executable).resolve()
    install_type = "packaged" if getattr(sys, "frozen", False) else (
        "git" if (root / ".git").exists() else "source"
    )
    # The path is intentionally hashed, not exposed as a globally correlatable
    # hardware identifier. Two checkouts on one machine get different IDs.
    material = f"jarvis-installation-v1\0{os.path.normcase(str(root))}".encode("utf-8")
    return InstallationIdentity(
        installation_id=hashlib.sha256(material).hexdigest()[:16],
        root=str(root), executable=str(executable),
        entrypoint=str((root / "main.py").resolve()), install_type=install_type,
        revision=_revision(), platform=platform.system() or "Unknown",
        python=platform.python_version(),
    )


def _runtime_check() -> DoctorResult:
    version = sys.version_info[:2]
    if version in SUPPORTED_PYTHON:
        return DoctorResult("runtime", "ok", f"Python {platform.python_version()} is supported.",
                            evidence=str(Path(sys.executable).resolve()))
    return DoctorResult(
        "runtime", "error", f"Python {platform.python_version()} is not supported.",
        evidence=str(Path(sys.executable).resolve()),
        remediation="Install Python 3.11 or 3.12 and run JARVIS with that interpreter.",
    )


def _installation_check() -> DoctorResult:
    identity = installation_identity()
    entrypoint = Path(identity.entrypoint)
    if not entrypoint.is_file():
        return DoctorResult("installation", "error", "The JARVIS entry point is missing.",
                            evidence=identity.root,
                            remediation="Repair or reinstall this JARVIS checkout.")
    return DoctorResult(
        "installation", "ok", f"Installation {identity.installation_id} is identifiable.",
        evidence=f"{identity.install_type}; revision={identity.revision}; root={identity.root}",
    )


def _storage_check() -> DoctorResult:
    usage = shutil.disk_usage(ROOT)
    free_gb = usage.free / (1024 ** 3)
    if free_gb < 1.0:
        return DoctorResult("storage", "warning", f"Only {free_gb:.1f} GB is free.",
                            remediation="Free at least 1 GB before updates or model downloads.")
    return DoctorResult("storage", "ok", f"{free_gb:.1f} GB is free.")


def _config_check() -> DoctorResult:
    path = ROOT / "config" / "api_keys.json"
    if not path.exists():
        return DoctorResult("configuration", "warning", "Provider configuration has not been created.",
                            remediation="Open Settings and configure a provider.", state="not_configured")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("root is not an object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return DoctorResult("configuration", "error", "Provider configuration cannot be read.",
                            evidence=type(exc).__name__,
                            remediation="Restore the configuration backup or save Settings again.")
    return DoctorResult("configuration", "ok", "Provider configuration is readable.")


def _shortcut_check() -> DoctorResult:
    try:
        from core import desktop_shortcut
        state = desktop_shortcut.verify()
    except Exception as exc:
        return DoctorResult("shortcut", "error", "Shortcut status could not be inspected.",
                            evidence=type(exc).__name__,
                            remediation="Use Settings to recreate the Desktop shortcut.")
    if state.get("valid"):
        return DoctorResult("shortcut", "ok", "The Desktop shortcut targets this installation.",
                            evidence=str(state.get("path", "")))
    if state.get("reason") == "missing":
        return DoctorResult("shortcut", "warning", "No Desktop shortcut exists.",
                            remediation="Create one from Settings or ask JARVIS to add it.")
    return DoctorResult("shortcut", "error", "The Desktop shortcut does not target this installation.",
                        evidence=str(state.get("reason", "invalid")),
                        remediation="Recreate it from this installation's Settings panel.")


def _dependencies_check() -> DoctorResult:
    required = ("fastapi", "uvicorn", "httpx", "requests", "cryptography")
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        return DoctorResult(
            "dependencies", "error", "Required runtime dependencies are missing.",
            evidence=", ".join(missing),
            remediation="Run the supported installer to repair application dependencies.",
        )
    return DoctorResult("dependencies", "ok", "Core runtime dependencies are importable.")


def _hud_check() -> DoctorResult:
    hud = ROOT / "apex_ui" / "static_hud" / "index.html"
    if not hud.is_file() or hud.stat().st_size < 100:
        return DoctorResult("hud", "error", "The built APEX HUD is missing or incomplete.",
                            evidence=str(hud),
                            remediation="Restore the release assets or rebuild apex_ui.")
    probe_script = (
        "import asyncio,uvicorn\n"
        "async def app(scope,receive,send):\n"
        " await send({'type':'http.response.start','status':204,'headers':[]})\n"
        " await send({'type':'http.response.body','body':b''})\n"
        "async def check():\n"
        " s=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=0,log_level='critical'))\n"
        " t=asyncio.create_task(s.serve())\n"
        " for _ in range(100):\n"
        "  if s.started: break\n"
        "  if t.done(): raise RuntimeError('server exited')\n"
        "  await asyncio.sleep(.02)\n"
        " if not s.started: raise RuntimeError('startup timeout')\n"
        " s.should_exit=True; await asyncio.wait_for(t,2)\n"
        "asyncio.run(check())\n"
    )
    try:
        result = subprocess.run([sys.executable, "-c", probe_script], capture_output=True,
                                text=True, timeout=6, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return DoctorResult("hud", "error", "The HUD server startup probe failed.",
                            evidence=type(exc).__name__,
                            remediation="Repair FastAPI/Uvicorn or local networking permissions.")
    if result.returncode != 0:
        return DoctorResult("hud", "error", "The HUD server cannot complete startup.",
                            evidence=f"exit={result.returncode}",
                            remediation="Repair FastAPI/Uvicorn or local networking permissions.")
    return DoctorResult("hud", "ok", "APEX HUD assets and a controlled server startup are healthy.")


def _port_check() -> DoctorResult:
    preferred = int(os.environ.get("JARVIS_HUD_PORT", "8765") or "8765")
    if not 1 <= preferred <= 65535:
        return DoctorResult("hud_port", "error", "The configured HUD port is invalid.",
                            evidence=str(preferred), remediation="Remove or correct JARVIS_HUD_PORT.")
    available = None
    for port in range(preferred, min(preferred + 20, 65536)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(("127.0.0.1", port))
            available = port
            break
        except OSError:
            continue
    if available is None:
        return DoctorResult("hud_port", "error", "No HUD port is available in the fallback range.",
                            evidence=f"{preferred}-{min(preferred + 19, 65535)}",
                            remediation="Close stale local servers or select another HUD port.")
    if available != preferred:
        return DoctorResult("hud_port", "warning", "The preferred HUD port is occupied; fallback is available.",
                            evidence=f"preferred={preferred}; fallback={available}")
    return DoctorResult("hud_port", "ok", "The preferred HUD port is available.", evidence=str(preferred))


def _browser_check() -> DoctorResult:
    candidates = ("msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser")
    found = next((shutil.which(name) for name in candidates if shutil.which(name)), None)
    if platform.system() == "Windows" and not found:
        roots = [os.environ.get("PROGRAMFILES(X86)"), os.environ.get("PROGRAMFILES"), os.environ.get("LOCALAPPDATA")]
        for root in filter(None, roots):
            candidate = Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
            if candidate.is_file():
                found = str(candidate)
                break
    if found:
        return DoctorResult("browser", "ok", "A compatible HUD browser is available.", evidence=found)
    return DoctorResult("browser", "warning", "No supported Chromium browser was detected.",
                        remediation="Install Microsoft Edge, Chrome, or Chromium; Classic UI remains available.")


def _memory_check() -> DoctorResult:
    failures: list[str] = []
    checked = 0
    for name in ("long_term.json", "soul.json", "routines.json", "automations.json",
                 "taste_profile.json", "accounts.json", "companions.json"):
        path = ROOT / "memory" / name
        if not path.exists():
            continue
        checked += 1
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, (dict, list)):
                failures.append(name)
        except (OSError, UnicodeError, json.JSONDecodeError):
            failures.append(name)
    if failures:
        return DoctorResult("memory", "error", "One or more memory stores are unreadable.",
                            evidence=", ".join(failures),
                            remediation="Preserve the files and restore a validated backup; do not overwrite them.")
    parent = ROOT / "memory"
    if not os.access(parent, os.W_OK):
        return DoctorResult("memory", "error", "The memory directory is not writable.",
                            evidence=str(parent), remediation="Restore write permission for this installation.")
    return DoctorResult("memory", "ok", f"{checked} existing JSON memory store(s) are readable.")


def _audio_check() -> DoctorResult:
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        inputs = sum(int(item.get("max_input_channels", 0)) > 0 for item in devices)
        outputs = sum(int(item.get("max_output_channels", 0)) > 0 for item in devices)
    except Exception as exc:
        return DoctorResult("audio", "error", "Audio devices cannot be enumerated.",
                            evidence=type(exc).__name__,
                            remediation="Check OS audio permissions and the selected devices.")
    if not inputs or not outputs:
        return DoctorResult("audio", "warning", "An input or output audio device is unavailable.",
                            evidence=f"inputs={inputs}; outputs={outputs}",
                            remediation="Connect and select a microphone and speaker.")
    return DoctorResult("audio", "ok", "Microphone and speaker devices are available.",
                        evidence=f"inputs={inputs}; outputs={outputs}")


def _voice_controls_check() -> DoctorResult:
    try:
        from core.hotkey import PushToTalk
        from core import wake_word
        from memory import config_manager as cfg
        wake = cfg.get_wake_word_enabled()
        detector = PushToTalk(lambda _held: None)
        scope = detector.start()
        detector.stop()
    except Exception as exc:
        return DoctorResult("voice_controls", "warning", "Voice control readiness cannot be verified.",
                            evidence=type(exc).__name__)
    if wake and not wake_word.is_ready():
        return DoctorResult("voice_controls", "warning", "Wake word is enabled but its local model is not ready.",
                            evidence=f"push_to_talk_scope={scope}",
                            remediation="Install the wake-word model or disable wake word; push-to-talk remains available.")
    return DoctorResult("voice_controls", "ok", "Wake word and push-to-talk readiness were verified.",
                        evidence=f"wake_word_enabled={bool(wake)}; push_to_talk_scope={scope}")


def _backup_check() -> DoctorResult:
    state = ROOT / "memory" / "soul.json"
    backup = ROOT / "memory" / "soul.backup.json"
    if state.exists() and not backup.exists():
        return DoctorResult("backups", "warning", "Soul state exists without a last-known-good backup.",
                            remediation="A backup will be created on the next validated Soul mutation.")
    if backup.exists():
        try:
            value = json.loads(backup.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("backup root")
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            return DoctorResult("backups", "error", "The Soul backup is unreadable.",
                                evidence=backup.name,
                                remediation="Preserve it and create a new validated backup from healthy state.")
        return DoctorResult("backups", "ok", "The Soul backup is readable.")
    return DoctorResult("backups", "ok", "No Soul backup is required before first persisted state.")


def _database_check() -> DoctorResult:
    import sqlite3
    failures: list[str] = []
    checked = 0
    for path in (ROOT / "memory").glob("*.db"):
        checked += 1
        try:
            uri = f"file:{path.resolve().as_posix()}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=2) as connection:
                result = connection.execute("PRAGMA quick_check").fetchone()
            if not result or result[0] != "ok":
                failures.append(path.name)
        except sqlite3.Error:
            failures.append(path.name)
    if failures:
        return DoctorResult("databases", "error", "A local database failed its integrity check.",
                            evidence=", ".join(failures),
                            remediation="Preserve the database and restore a validated backup.")
    return DoctorResult("databases", "ok", f"{checked} local database(s) passed integrity checks.")


def _permissions_check() -> DoctorResult:
    unwritable = [str(path.relative_to(ROOT)) for path in (ROOT / "config", ROOT / "memory")
                  if path.exists() and not os.access(path, os.W_OK)]
    if unwritable:
        return DoctorResult("permissions", "error", "Required local data directories are not writable.",
                            evidence=", ".join(unwritable),
                            remediation="Restore write access for the current user.")
    return DoctorResult("permissions", "ok", "Required local data directories are writable.")


def _provider_check() -> DoctorResult:
    """Probe model-list endpoints; never generate content or spend inference tokens."""
    try:
        from memory import config_manager as cfg
        provider = cfg.get_provider()
        key = {"gemini": cfg.get_gemini_key, "openai": cfg.get_openai_key,
               "anthropic": cfg.get_anthropic_key}.get(provider, lambda: None)()
        local = cfg.get_local_llm_cfg()
    except Exception as exc:
        return DoctorResult("provider", "error", "Provider settings cannot be read.",
                            evidence=type(exc).__name__)
    if provider != "ollama" and not key:
        return DoctorResult("provider", "warning", f"The selected provider ({provider}) is not configured.",
                            remediation="Configure it in Settings or select an available provider.",
                            state="not_configured")
    try:
        if provider == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + urllib.parse.quote(str(key))
            request = urllib.request.Request(url)
            selected = ""
        elif provider == "anthropic":
            url = "https://api.anthropic.com/v1/models?limit=100"
            request = urllib.request.Request(url, headers={"x-api-key": str(key), "anthropic-version": "2023-06-01"})
            selected = str(cfg.get_anthropic_cfg().get("model") or "")
        elif provider == "ollama":
            url = str(local.get("url") or "http://127.0.0.1:11434").rstrip("/") + "/api/tags"
            request = urllib.request.Request(url)
            selected = str(local.get("model") or "")
        else:
            openai = cfg.get_openai_cfg()
            url = str(openai.get("base_url") or "https://api.openai.com/v1").rstrip("/") + "/models"
            request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
            selected = str(openai.get("model") or "")
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read(2_000_000).decode("utf-8"))
        rows = payload.get("models") if provider in {"gemini", "ollama"} else payload.get("data")
        if not isinstance(rows, list):
            raise ValueError("invalid model list")
        names = {str(row.get("name") or row.get("id") or "").removeprefix("models/")
                 for row in rows if isinstance(row, dict)}
        if selected and selected not in names and not any(name.endswith(selected) for name in names):
            return DoctorResult("provider", "warning", "The provider is reachable but the selected model was not listed.",
                                evidence=f"provider={provider}; models={len(names)}",
                                remediation="Choose an available model in Settings.")
        return DoctorResult("provider", "ok", "The provider endpoint and model listing are available.",
                            evidence=f"provider={provider}; models={len(names)}; no inference request")
    except Exception as exc:
        return DoctorResult("provider", "error", "The selected provider endpoint could not be verified.",
                            evidence=f"provider={provider}; error={type(exc).__name__}",
                            remediation="Check the key, endpoint, selected model, internet connection, or local server.")


def _source_state_check() -> DoctorResult:
    if not (ROOT / ".git").exists():
        return DoctorResult("updates", "ok", "This packaged/source installation has no Git checkout state.")
    try:
        branch = _git("rev-parse", "--abbrev-ref", "HEAD")
        status = _git("status", "--porcelain", "--untracked-files=normal")
    except (OSError, subprocess.SubprocessError) as exc:
        return DoctorResult("updates", "warning", "Git installation state could not be inspected.",
                            evidence=type(exc).__name__)
    if branch.returncode or status.returncode:
        return DoctorResult("updates", "warning", "Git installation state could not be inspected.")
    if status.stdout.strip():
        return DoctorResult("updates", "warning", "This checkout contains local changes.",
                            evidence=f"branch={branch.stdout.strip()}",
                            remediation="Back up or commit intentional work before applying updates.")
    return DoctorResult("updates", "ok", "The Git checkout is clean.",
                        evidence=f"branch={branch.stdout.strip()}; revision={_revision()}")


_CHECKS: tuple[Callable[[], DoctorResult], ...] = (
    _installation_check, _runtime_check, _dependencies_check, _storage_check,
    _config_check, _provider_check, _permissions_check, _memory_check,
    _backup_check, _database_check, _audio_check, _voice_controls_check, _hud_check,
    _port_check, _browser_check, _shortcut_check, _source_state_check,
)


def run_doctor(checks: Iterable[Callable[[], DoctorResult]] | None = None) -> dict[str, object]:
    """Run read-only checks; contain individual failures and return JSON-safe data."""
    results: list[DoctorResult] = []
    for check in checks or _CHECKS:
        try:
            results.append(check())
        except Exception as exc:
            results.append(DoctorResult(
                getattr(check, "__name__", "unknown").removeprefix("_").removesuffix("_check"),
                "error", "The health check failed safely.", evidence=type(exc).__name__,
            ))
    counts = {status: sum(item.status == status for item in results)
              for status in ("ok", "warning", "error")}
    overall = "error" if counts["error"] else ("warning" if counts["warning"] else "ok")
    return {
        "schema_version": 1,
        "overall": overall,
        "counts": counts,
        "installation": asdict(installation_identity()),
        "results": [item.to_dict() for item in results],
    }


def write_support_report(directory: Path | None = None) -> Path:
    """Write a bounded, credential-free report and return its exact path."""
    report = run_doctor()
    destination_dir = (directory or (ROOT / "config" / "diagnostics")).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "system_doctor.json"
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if len(payload.encode("utf-8")) > 128_000:
        raise RuntimeError("System Doctor report exceeded its safe size limit")
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(payload, encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(destination)
    return destination
