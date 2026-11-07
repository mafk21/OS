"""Structured, privacy-safe health checks for the running JARVIS installation.

The doctor observes before it repairs. Checks never mutate application state,
scan unrelated user folders, or include credentials in reports. This module is
kept UI-independent so Classic UI, APEX, voice tools, and support exports can
consume the same evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
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

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


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
                            remediation="Open Settings and configure a provider.")
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
        state = desktop_shortcut.status()
    except Exception as exc:
        return DoctorResult("shortcut", "error", "Shortcut status could not be inspected.",
                            evidence=type(exc).__name__,
                            remediation="Use Settings to recreate the Desktop shortcut.")
    if state.get("exists"):
        return DoctorResult("shortcut", "ok", "A Desktop shortcut exists.",
                            evidence=str(state.get("path", "")))
    return DoctorResult("shortcut", "warning", "No Desktop shortcut exists.",
                        remediation="Create one from Settings or ask JARVIS to add it.")


_CHECKS: tuple[Callable[[], DoctorResult], ...] = (
    _installation_check, _runtime_check, _storage_check, _config_check, _shortcut_check,
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
