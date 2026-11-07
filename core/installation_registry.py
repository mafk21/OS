"""Machine-local registry for explicit JARVIS installation lifecycle.

The registry never searches user folders. Installations register themselves when
running. A private marker travels with portable installations, allowing a move
to retain identity while a copied live installation receives a fresh identity.
"""
from __future__ import annotations

import json
import os
import platform
import threading
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MARKER = ROOT / "config" / "installation.json"
_LOCK = threading.RLock()
_SCHEMA = 1


def registry_path() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        return base / "JARVIS" / "installations.json"
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "JARVIS" / "installations.json"
    base = Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state"))
    return base / "jarvis" / "installations.json"


def _read(path: Path | None = None) -> dict[str, Any]:
    source = path or registry_path()
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
        if value.get("schema_version") == _SCHEMA and isinstance(value.get("installations"), dict):
            return value
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        pass
    return {"schema_version": _SCHEMA, "active_id": "", "installations": {}}


def _write(value: dict[str, Any], path: Path | None = None) -> None:
    destination = path or registry_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    temporary.replace(destination)


def _marker_id(marker: Path = MARKER) -> str:
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
        candidate = str(value.get("installation_id") or "")
        uuid.UUID(candidate)
        return candidate
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        marker.parent.mkdir(parents=True, exist_ok=True)
        candidate = str(uuid.uuid4())
        temporary = marker.with_suffix(".tmp")
        temporary.write_text(json.dumps({"schema_version": 1, "installation_id": candidate}, indent=2), encoding="utf-8")
        temporary.replace(marker)
        return candidate


def ensure_current(*, install_type: str, revision: str, executable: str, root: Path = ROOT) -> dict[str, Any]:
    """Register this running installation and return its registry record."""
    with _LOCK:
        marker = root / "config" / "installation.json"
        identifier = _marker_id(marker)
        root = str(root.resolve())
        data = _read()
        existing = data["installations"].get(identifier)
        if existing and os.path.normcase(str(existing.get("root", ""))) != os.path.normcase(root):
            old_root = Path(str(existing.get("root", "")))
            if old_root.exists():
                # This is a copy, not a move. Give it a separate identity.
                identifier = str(uuid.uuid4())
                temporary = marker.with_suffix(".tmp")
                temporary.write_text(json.dumps({"schema_version": 1, "installation_id": identifier}, indent=2), encoding="utf-8")
                temporary.replace(marker)
        record = {
            "installation_id": identifier, "root": root, "install_type": install_type,
            "revision": revision, "executable": str(Path(executable).resolve()),
            "platform": platform.system() or "Unknown", "last_seen": int(time.time()),
        }
        data["installations"][identifier] = record
        active_id = str(data.get("active_id") or "")
        active_record = data["installations"].get(active_id, {})
        active_root = Path(str(active_record.get("root") or "")) if active_record else None
        # Recover from a moved/deleted active checkout without scanning: only
        # the path that checkout registered is inspected.
        if not active_id or (active_id != identifier and active_root is not None and not active_root.exists()):
            data["active_id"] = identifier
        _write(data)
        return {**record, "active": data.get("active_id") == identifier}


def status(current_id: str) -> dict[str, Any]:
    with _LOCK:
        data = _read()
        records = list(data["installations"].values())
        return {
            "active_id": str(data.get("active_id") or ""),
            "current_id": current_id,
            "is_active": data.get("active_id") == current_id,
            "installations": records,
            "other_count": sum(row.get("installation_id") != current_id for row in records),
        }


def make_active(current_id: str) -> dict[str, Any]:
    with _LOCK:
        data = _read()
        if current_id not in data["installations"]:
            raise ValueError("Current installation is not registered")
        data["active_id"] = current_id
        _write(data)
        return status(current_id)


def activate_and_refresh_shortcut(current_id: str) -> str:
    """Make current installation active, then atomically refresh its shortcut."""
    previous = status(current_id)["active_id"]
    make_active(current_id)
    try:
        from core.system_repair import execute_repair
        repaired = execute_repair("shortcut")
        if not repaired.ok or not repaired.verified:
            raise RuntimeError("shortcut verification failed")
    except Exception:
        if previous and previous in _read()["installations"]:
            make_active(str(previous))
        raise
    return "This installation is now active and its Desktop shortcut was verified."


def request_make_active(current_id: str) -> str:
    from core import confirm
    current = status(current_id)
    if current["is_active"]:
        return "This is already the active JARVIS installation."
    return confirm.request(
        "jarvis-make-installation-active",
        "Make this the active JARVIS installation?",
        "The shared Desktop shortcut will be backed up and replaced with one targeting this installation.",
        lambda: activate_and_refresh_shortcut(current_id),
    )


def request_unregister(current_id: str) -> str:
    from core import confirm
    return confirm.request(
        "jarvis-unregister-installation",
        "Unregister this JARVIS installation?",
        "Only machine-local registry metadata will be removed. No repository or user data will be deleted.",
        lambda: "Installation registration removed." if unregister(current_id) else "Installation was not registered.",
    )


def unregister(current_id: str) -> bool:
    """Forget registry metadata only; never delete an installation or user data."""
    with _LOCK:
        data = _read()
        removed = data["installations"].pop(current_id, None) is not None
        if data.get("active_id") == current_id:
            data["active_id"] = ""
        _write(data)
        return removed
