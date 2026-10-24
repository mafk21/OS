"""
Recurring Automations Engine — Phase 4.

Local cron/interval & on-demand multi-step automation runner stored in
`memory/automations.json`. Supports:
  • Interval schedules (`every_minutes`) and daily wall-clock schedules (`daily_at` "HH:MM")
  • Pause / Resume / Delete / 1-click Run Now
  • Multi-step execution across built-in JARVIS actions (`cloud_integrations`,
    `web_search`, `custom_connector`, `brain_control`, etc.)
  • Full execution history (`runs`) + automatic Brain Outputs archiving
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from core.action_loader import discover_actions
from memory import timeline

BASE_DIR = Path(__file__).resolve().parent.parent
AUTOMATIONS_FILE = BASE_DIR / "memory" / "automations.json"
ACTIONS_DIR = BASE_DIR / "actions"

_LOCK = threading.RLock()


def _load() -> list[dict[str, Any]]:
    with _LOCK:
        if not AUTOMATIONS_FILE.exists():
            return []
        try:
            raw = json.loads(AUTOMATIONS_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("automations"), list):
                return list(raw["automations"])
            return list(raw) if isinstance(raw, list) else []
        except Exception:
            return []


def _save(items: list[dict[str, Any]]) -> None:
    with _LOCK:
        AUTOMATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = AUTOMATIONS_FILE.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"automations": items}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(AUTOMATIONS_FILE)


def list_automations() -> list[dict[str, Any]]:
    return _load()


def save_automation(data: dict[str, Any]) -> dict[str, Any]:
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("Automation 'name' is required.")

    schedule_type = str(data.get("schedule_type") or "interval").strip().lower()
    if schedule_type not in ("interval", "daily", "manual"):
        schedule_type = "interval"
    every_minutes = max(1, int(data.get("every_minutes") or 60))
    daily_at = str(data.get("daily_at") or "09:00").strip()[:5]

    raw_steps = data.get("steps")
    if isinstance(raw_steps, list) and raw_steps:
        steps = [
            {
                "tool": str(s.get("tool") or "").strip(),
                "params": s.get("params") if isinstance(s.get("params"), dict) else {},
            }
            for s in raw_steps
            if isinstance(s, dict) and str(s.get("tool") or "").strip()
        ]
    else:
        tool_name = str(data.get("tool") or "web_search").strip()
        tool_params = data.get("params") if isinstance(data.get("params"), dict) else {}
        steps = [{"tool": tool_name, "params": tool_params}]

    if not steps:
        raise ValueError("Automation requires at least one tool step.")

    aid = str(data.get("id") or "").strip() or f"auto-{uuid.uuid4().hex[:8]}"
    with _LOCK:
        items = _load()
        prev_runs: list[dict[str, Any]] = []
        last_run_ts = 0.0
        last_daily_date = ""
        enabled = bool(data.get("enabled", True))
        for ex in items:
            if ex.get("id") == aid:
                prev_runs = list(ex.get("runs") or [])
                last_run_ts = float(ex.get("last_run_ts") or 0.0)
                last_daily_date = str(ex.get("last_daily_date") or "")
                if "enabled" not in data:
                    enabled = bool(ex.get("enabled", True))
                break

        rec = {
            "id": aid,
            "name": name[:80],
            "enabled": enabled,
            "schedule_type": schedule_type,
            "every_minutes": every_minutes,
            "daily_at": daily_at,
            "steps": steps,
            "last_run_ts": last_run_ts,
            "last_daily_date": last_daily_date,
            "runs": prev_runs[-15:],
        }
        items = [x for x in items if x.get("id") != aid] + [rec]
        _save(items)
    return rec


def toggle_automation(automation_id: str, enabled: bool | None = None) -> dict[str, Any] | None:
    with _LOCK:
        items = _load()
        for it in items:
            if it.get("id") == automation_id:
                it["enabled"] = (not bool(it.get("enabled", True))) if enabled is None else bool(enabled)
                _save(items)
                return dict(it)
    return None


def delete_automation(automation_id: str) -> bool:
    with _LOCK:
        items = _load()
        before = len(items)
        items = [x for x in items if x.get("id") != automation_id]
        if len(items) != before:
            _save(items)
            return True
    return False


def run_automation_now(
    automation_id: str,
    on_log: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    items = _load()
    target = next((x for x in items if x.get("id") == automation_id), None)
    if target is None:
        raise ValueError(f"Automation '{automation_id}' not found.")

    t0 = time.monotonic()
    reg = discover_actions(ACTIONS_DIR)
    step_outputs: list[str] = []
    status = "success"

    for idx, step in enumerate(target.get("steps") or [], 1):
        tool = str(step.get("tool") or "").strip()
        params = dict(step.get("params") or {})
        try:
            if reg.has(tool):
                res = str(reg.run(tool, params, {"player": None, "speak": None}) or "Done.")
            else:
                res = f"Unknown tool '{tool}'"
                status = "error"
        except Exception as exc:
            res = f"Error in {tool}: {exc}"
            status = "error"
        step_outputs.append(f"Step {idx} ({tool}): {res[:800]}")

    combined = "\n\n".join(step_outputs)
    dur_ms = int((time.monotonic() - t0) * 1000)
    run_rec = {
        "id": f"run-{uuid.uuid4().hex[:8]}",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "duration_ms": dur_ms,
        "output": combined[:2400],
    }

    with _LOCK:
        fresh = _load()
        for it in fresh:
            if it.get("id") == automation_id:
                it["last_run_ts"] = time.time()
                it["last_daily_date"] = time.strftime("%Y-%m-%d")
                runs = list(it.get("runs") or [])
                runs.append(run_rec)
                it["runs"] = runs[-15:]
                break
        _save(fresh)

    try:
        timeline.record_output(
            f"AUTOMATION — {target['name']}", combined, category="automation"
        )
    except Exception:
        pass
    if callable(on_log):
        on_log(f"SYS: Automation '{target['name']}' finished ({status}, {dur_ms}ms).")
    return run_rec


class AutomationScheduler:
    """Lightweight background daemon checking due automations every 20 seconds."""

    def __init__(self, on_log: Callable[[str], None] | None = None):
        self._on_log = on_log
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="JarvisAutomations")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def tick_once(self, now_ts: float | None = None) -> list[str]:
        now = now_ts if now_ts is not None else time.time()
        lt = time.localtime(now)
        hhmm = time.strftime("%H:%M", lt)
        today = time.strftime("%Y-%m-%d", lt)
        fired: list[str] = []

        for it in _load():
            if not it.get("enabled", True):
                continue
            stype = it.get("schedule_type", "interval")
            due = False
            if stype == "interval":
                mins = max(1, int(it.get("every_minutes") or 60))
                last_ts = float(it.get("last_run_ts") or 0.0)
                if last_ts > 0 and (now - last_ts) >= mins * 60:
                    due = True
                elif last_ts == 0.0:
                    # Seed initial timestamp so interval starts counting from creation
                    with _LOCK:
                        cur = _load()
                        for x in cur:
                            if x.get("id") == it.get("id") and not x.get("last_run_ts"):
                                x["last_run_ts"] = now
                        _save(cur)
            elif stype == "daily":
                if hhmm == str(it.get("daily_at") or "09:00") and it.get("last_daily_date") != today:
                    due = True

            if due:
                try:
                    run_automation_now(str(it["id"]), on_log=self._on_log)
                    fired.append(str(it["id"]))
                except Exception:
                    pass
        return fired

    def _loop(self) -> None:
        while not self._stop.wait(20.0):
            try:
                self.tick_once()
            except Exception:
                pass
