"""Allowlisted, confirmation-gated repairs for System Doctor findings.

Diagnosis and repair are deliberately separate. Every repair backs up affected
state when applicable, verifies its postcondition, and restores the backup when
verification fails. No LLM-provided command is ever executed.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import time
import threading
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from core import confirm, desktop_shortcut, system_doctor

ROOT = Path(__file__).resolve().parent.parent
BACKUP_ROOT = ROOT / "config" / "repair_backups"
_RESULT_LOCK = threading.Lock()
_LAST_RESULT: RepairResult | None = None


@dataclass(frozen=True)
class RepairResult:
    repair: str
    ok: bool
    verified: bool
    message: str
    backup: str = ""
    rolled_back: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _backup_dir(repair: str) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = BACKUP_ROOT / f"{stamp}-{repair}-{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _repair_shortcut() -> RepairResult:
    destination = desktop_shortcut.shortcut_path()
    backup_dir = _backup_dir("shortcut")
    backup = backup_dir / destination.name
    had_original = destination.is_file()
    if had_original:
        shutil.copy2(destination, backup)
    try:
        desktop_shortcut.create()
        verified = bool(desktop_shortcut.verify().get("valid"))
        if not verified:
            raise RuntimeError("shortcut postcondition failed")
        return RepairResult("shortcut", True, True, "Desktop shortcut repaired and verified.",
                            str(backup) if had_original else "")
    except Exception:
        rolled_back = False
        try:
            if had_original:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, destination)
            else:
                destination.unlink(missing_ok=True)
            rolled_back = True
        except OSError:
            pass
        return RepairResult("shortcut", False, False,
                            "Desktop shortcut repair failed; the previous state was restored when possible.",
                            str(backup) if had_original else "", rolled_back)


def _repair_permissions() -> RepairResult:
    targets = (ROOT / "config", ROOT / "memory")
    backup_dir = _backup_dir("permissions")
    modes: dict[str, int | None] = {}
    try:
        for path in targets:
            modes[str(path)] = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
        (backup_dir / "modes.json").write_text(json.dumps(modes, indent=2), encoding="utf-8")
        for path in targets:
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(path.stat().st_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        verified = all(os.access(path, os.W_OK) for path in targets)
        if not verified:
            raise RuntimeError("permission postcondition failed")
        return RepairResult("permissions", True, True, "Local data-directory permissions repaired and verified.",
                            str(backup_dir / "modes.json"))
    except Exception:
        rolled_back = True
        for raw, mode in modes.items():
            try:
                path = Path(raw)
                if mode is None:
                    path.rmdir()
                else:
                    path.chmod(mode)
            except OSError:
                rolled_back = False
        return RepairResult("permissions", False, False,
                            "Permission repair failed; previous modes were restored when possible.",
                            str(backup_dir / "modes.json"), rolled_back)


def _repair_dependencies() -> RepairResult:
    installer = ROOT / "install_jarvis.py"
    if not installer.is_file():
        return RepairResult("dependencies", False, False, "The supported installer is missing.")
    try:
        result = subprocess.run(
            [sys.executable, str(installer), "--install"], cwd=str(ROOT),
            capture_output=True, text=True, timeout=900, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return RepairResult("dependencies", False, False, "Dependency repair did not complete.")
    verified = result.returncode == 0
    return RepairResult("dependencies", verified, verified,
                        "Dependencies repaired through the supported installer." if verified
                        else "The supported installer reported a dependency repair failure.")


def _repair_hud_port() -> RepairResult:
    import socket
    previous = os.environ.get("JARVIS_HUD_PORT")
    preferred = 8765
    for port in range(preferred, preferred + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(("127.0.0.1", port))
            os.environ["JARVIS_HUD_PORT"] = str(port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as verify:
                verify.bind(("127.0.0.1", port))
            return RepairResult("hud_port", True, True,
                                f"Selected and verified HUD port {port} for the next HUD start.")
        except OSError:
            continue
    if previous is None:
        os.environ.pop("JARVIS_HUD_PORT", None)
    else:
        os.environ["JARVIS_HUD_PORT"] = previous
    return RepairResult("hud_port", False, False,
                        "No safe local HUD port was available; the previous setting was retained.",
                        rolled_back=True)


def _repair_hud() -> RepairResult:
    hud = ROOT / "apex_ui" / "static_hud"
    package = ROOT / "apex_ui" / "package-lock.json"
    if not package.is_file() or not shutil.which("npm"):
        return RepairResult("hud", False, False, "Node.js/npm or the locked APEX package is unavailable.")
    backup_dir = _backup_dir("hud")
    backup = backup_dir / "static_hud"
    if hud.exists():
        shutil.copytree(hud, backup)
    try:
        install = subprocess.run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
                                 cwd=str(ROOT / "apex_ui"), capture_output=True, text=True,
                                 timeout=600, check=False)
        build = subprocess.run(["npm", "run", "build"], cwd=str(ROOT / "apex_ui"),
                               capture_output=True, text=True, timeout=600, check=False) if install.returncode == 0 else install
        verified = build.returncode == 0 and (hud / "index.html").is_file()
        if not verified:
            raise RuntimeError("HUD postcondition failed")
        return RepairResult("hud", True, True, "APEX HUD rebuilt and verified.", str(backup) if backup.exists() else "")
    except Exception:
        rolled_back = False
        try:
            if backup.exists():
                if hud.exists(): shutil.rmtree(hud)
                shutil.copytree(backup, hud)
            rolled_back = True
        except OSError:
            pass
        return RepairResult("hud", False, False, "HUD repair failed; previous assets were restored when possible.",
                            str(backup) if backup.exists() else "", rolled_back)


def _repair_soul_backup() -> RepairResult:
    state = ROOT / "memory" / "soul.json"
    backup = ROOT / "memory" / "soul.backup.json"
    if not backup.is_file():
        return RepairResult("soul_backup", False, False, "No Soul backup is available; nothing was changed.")
    repair_backup = _backup_dir("soul") / "soul.before-repair.json"
    if state.exists():
        shutil.copy2(state, repair_backup)
    try:
        from core.soul.migrations import migrate_raw
        raw = json.loads(backup.read_text(encoding="utf-8"))
        validated = migrate_raw(raw).state
        temporary = state.with_suffix(".repair.tmp")
        temporary.write_text(json.dumps(validated.to_dict(), indent=2), encoding="utf-8")
        temporary.replace(state)
        json.loads(state.read_text(encoding="utf-8"))
        return RepairResult("soul_backup", True, True, "Soul state restored from its validated backup.",
                            str(repair_backup) if repair_backup.exists() else "")
    except Exception:
        rolled_back = False
        try:
            if repair_backup.exists(): shutil.copy2(repair_backup, state)
            rolled_back = True
        except OSError:
            pass
        return RepairResult("soul_backup", False, False,
                            "Soul restoration failed; the previous state was restored when possible.",
                            str(repair_backup) if repair_backup.exists() else "", rolled_back)


_REPAIRS: dict[str, tuple[str, str, Callable[[], RepairResult]]] = {
    "shortcut": ("Repair JARVIS Desktop shortcut?", "Back up the existing shortcut, replace it, and verify its installation target.", _repair_shortcut),
    "permissions": ("Repair JARVIS data permissions?", "Back up current modes, grant this user required local access, and verify it.", _repair_permissions),
    "dependencies": ("Repair JARVIS dependencies?", "Run only the repository's supported locked installer. This may download packages.", _repair_dependencies),
    "hud": ("Rebuild the APEX HUD?", "Back up existing HUD assets, run the locked npm build, verify it, and roll back on failure.", _repair_hud),
    "hud_port": ("Select a safe HUD port?", "Find and verify an available loopback port for the next HUD start without closing other applications.", _repair_hud_port),
    "soul_backup": ("Restore Soul from validated backup?", "Preserve current state, validate the last-known-good backup, restore it, and verify it.", _repair_soul_backup),
}


def available_repairs() -> list[str]:
    return sorted(_REPAIRS)


def execute_repair(repair: str) -> RepairResult:
    """Execute only an allowlisted repair. UI callers must use request_repair."""
    key = str(repair).strip().lower()
    if key not in _REPAIRS:
        raise ValueError("Unsupported System Doctor repair")
    result = _REPAIRS[key][2]()
    global _LAST_RESULT
    with _RESULT_LOCK:
        _LAST_RESULT = result
    return result


def repair_status() -> dict[str, object] | None:
    with _RESULT_LOCK:
        return _LAST_RESULT.to_dict() if _LAST_RESULT is not None else None


def request_repair(repair: str) -> str:
    """Stage an allowlisted repair behind the non-forgeable UI confirmation gate."""
    key = str(repair).strip().lower()
    if key not in _REPAIRS:
        return "That System Doctor repair is not supported. Nothing was changed."
    title, detail, _operation = _REPAIRS[key]
    return confirm.request(
        f"system-repair-{key}", title, detail,
        lambda: execute_repair(key).message,
    )
