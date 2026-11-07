"""Privacy-safe replay suppression for consequential actions.

Only keyed fingerprints and bounded lifecycle metadata are persisted. Parameter
values and action results never enter this store. A machine-local random key
makes offline guessing of recipients, paths, or message content impractical.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STORE_PATH = ROOT / "config" / "action_replay_guard.json"
KEY_PATH = ROOT / "config" / ".action_replay.key"
WINDOW_SECONDS = 10 * 60
PENDING_SECONDS = 2 * 60
MAX_RECORDS = 256
_LOCK = threading.Lock()


def _canonical(value: Any, depth: int = 0) -> Any:
    if depth >= 5:
        return "<bounded>"
    if isinstance(value, dict):
        return {str(k)[:80]: _canonical(v, depth + 1) for k, v in sorted(value.items(), key=lambda item: str(item[0]))[:80]
                if str(k) not in {"allow_repeat", "confirmed"}}
    if isinstance(value, (list, tuple)):
        return [_canonical(v, depth + 1) for v in value[:80]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value if not isinstance(value, str) else value[:20_000]
    return f"<{type(value).__name__}>"


def _key() -> bytes:
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        value = KEY_PATH.read_bytes()
        if len(value) == 32:
            return value
    except OSError:
        pass
    value = os.urandom(32)
    temporary = KEY_PATH.with_suffix(".tmp")
    temporary.write_bytes(value)
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    os.replace(temporary, KEY_PATH)
    return value


def fingerprint(action: str, parameters: dict[str, Any]) -> str:
    payload = json.dumps({"action": str(action), "parameters": _canonical(parameters)}, sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hmac.new(_key(), payload, hashlib.sha256).hexdigest()


def _load(now: float) -> list[dict[str, Any]]:
    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        rows = raw.get("records", []) if isinstance(raw, dict) else []
    except (OSError, ValueError):
        rows = []
    return [row for row in rows if isinstance(row, dict) and now - float(row.get("at", 0)) <= WINDOW_SECONDS]


def _save(rows: list[dict[str, Any]]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = STORE_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps({"version": 1, "records": rows[-MAX_RECORDS:]}, separators=(",", ":")), encoding="utf-8")
    os.replace(temporary, STORE_PATH)


def inspect(action: str, parameters: dict[str, Any], now: float | None = None) -> tuple[str, str]:
    """Return (fingerprint, prior state), where state is new/pending/completed/uncertain."""
    stamp = time.time() if now is None else now
    token = fingerprint(action, parameters)
    with _LOCK:
        rows = _load(stamp)
        match = next((row for row in reversed(rows) if hmac.compare_digest(str(row.get("fingerprint", "")), token)), None)
    if not match:
        return token, "new"
    state = str(match.get("state") or "uncertain")
    if state == "pending" and stamp - float(match.get("at", 0)) > PENDING_SECONDS:
        return token, "uncertain"
    return token, state


def reserve(token: str, *, force: bool = False, now: float | None = None) -> bool:
    stamp = time.time() if now is None else now
    with _LOCK:
        rows = _load(stamp)
        exists = any(hmac.compare_digest(str(row.get("fingerprint", "")), token) for row in rows)
        if exists and not force:
            return False
        if force:
            rows = [row for row in rows if not hmac.compare_digest(str(row.get("fingerprint", "")), token)]
        rows.append({"fingerprint": token, "state": "pending", "at": stamp})
        _save(rows)
    return True


def finish(token: str, state: str, now: float | None = None) -> None:
    stamp = time.time() if now is None else now
    bounded_state = state if state in {"completed", "uncertain"} else "uncertain"
    with _LOCK:
        rows = _load(stamp)
        rows = [row for row in rows if not hmac.compare_digest(str(row.get("fingerprint", "")), token)]
        rows.append({"fingerprint": token, "state": bounded_state, "at": stamp})
        _save(rows)


def release(token: str) -> None:
    with _LOCK:
        rows = _load(time.time())
        rows = [row for row in rows if not hmac.compare_digest(str(row.get("fingerprint", "")), token)]
        _save(rows)
