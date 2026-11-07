"""Privacy-bounded operational snapshot for APEX."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def snapshot() -> dict[str, Any]:
    task_states: Counter[str] = Counter()
    timeline: list[dict[str, Any]] = []
    try:
        from core.long_tasks import get_long_task_manager
        for row in get_long_task_manager()._load():
            state = str(row.get("status") or "unknown")
            task_states[state] += 1
            timeline.append({"kind": "task", "state": state, "at": float(row.get("updated_at") or 0)})
    except Exception:
        task_states["unavailable"] += 1
    action_outcomes: Counter[str] = Counter()
    audit = ROOT / "config" / "action_audit.jsonl"
    try:
        for line in audit.read_text(encoding="utf-8").splitlines()[-200:]:
            row = json.loads(line)
            if row.get("stage") == "report":
                outcome = str(row.get("outcome") or "unknown")
                action_outcomes[outcome] += 1
                timeline.append({"kind": "action", "action": str(row.get("action") or "")[:64],
                                 "state": outcome, "at": float(row.get("timestamp") or 0)})
    except (OSError, ValueError):
        pass
    try:
        from memory.memory_governance import conflicts
        conflict_count = len(conflicts())
    except Exception:
        conflict_count = -1
    try:
        from core.proactive_permissions import load
        proactive = load()
        proactive_state = {"enabled": proactive.enabled, "memory_scope": proactive.use_memory,
                           "monitor_scope": proactive.use_monitors, "daily_limit": proactive.daily_limit}
    except Exception:
        proactive_state = {"enabled": False, "unavailable": True}
    try:
        from core.provider_routing import _FAILURES
        provider_health = {name: {"failures": count} for name, (count, _at) in _FAILURES.items()}
    except Exception:
        provider_health = {}
    timeline.sort(key=lambda event: event["at"], reverse=True)
    return {"ok": True, "tasks": dict(task_states), "actions": dict(action_outcomes),
            "timeline": timeline[:100], "memory_conflicts": conflict_count, "providers": provider_health,
            "proactive": proactive_state, "privacy": "aggregate_metadata_only"}
