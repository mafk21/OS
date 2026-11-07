"""Durable least-privilege policy for unsolicited proactive behavior."""
from __future__ import annotations
import json, os, threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "config" / "proactive_permissions.json"
USAGE_PATH = Path(__file__).resolve().parent.parent / "config" / "proactive_usage.json"
_LOCK = threading.Lock()

@dataclass(frozen=True)
class ProactivePolicy:
    enabled: bool = True
    use_memory: bool = False
    use_monitors: bool = False
    use_recent_conversation: bool = True
    quiet_start: int = 23
    quiet_end: int = 7
    daily_limit: int = 6


def load() -> ProactivePolicy:
    try:
        raw = json.loads(PATH.read_text(encoding="utf-8"))
        allowed = {k: raw[k] for k in asdict(ProactivePolicy()) if k in raw}
        return ProactivePolicy(**allowed)
    except (OSError, ValueError, TypeError):
        return ProactivePolicy()


def save(policy: ProactivePolicy) -> None:
    PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(asdict(policy), indent=2), encoding="utf-8")
    os.replace(temp, PATH)


def allowed(policy: ProactivePolicy | None = None, now: datetime | None = None) -> bool:
    p = policy or load(); current = now or datetime.now()
    if not p.enabled or p.daily_limit <= 0: return False
    try:
        usage = json.loads(USAGE_PATH.read_text(encoding="utf-8"))
        count = int(usage.get("count", 0)) if usage.get("date") == current.date().isoformat() else 0
    except (OSError, ValueError, TypeError):
        count = 0
    if count >= p.daily_limit: return False
    hour = current.hour
    if p.quiet_start > p.quiet_end:
        return not (hour >= p.quiet_start or hour < p.quiet_end)
    return not (p.quiet_start <= hour < p.quiet_end)


def record(now: datetime | None = None) -> None:
    current = now or datetime.now(); day = current.date().isoformat()
    with _LOCK:
        try: usage = json.loads(USAGE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError): usage = {}
        count = int(usage.get("count", 0)) + 1 if usage.get("date") == day else 1
        USAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp = USAGE_PATH.with_suffix(".tmp")
        temp.write_text(json.dumps({"date": day, "count": count}), encoding="utf-8")
        os.replace(temp, USAGE_PATH)


def filter_context(memory: dict, monitors: list[str] | None, recent: list[str] | None,
                   policy: ProactivePolicy | None = None):
    p = policy or load()
    return (memory if p.use_memory else {}, monitors if p.use_monitors else None,
            recent if p.use_recent_conversation else None)
