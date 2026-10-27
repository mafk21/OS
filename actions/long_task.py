"""Durable long-term completion monitoring exposed to voice and text."""
from __future__ import annotations

import json
import time
from datetime import datetime

from core.long_tasks import get_long_task_manager


def _active_video() -> dict:
    try:
        from core.apex_bridge import get_active_bridge
        bridge = get_active_bridge()
        if bridge is not None:
            return bridge.current_video_snapshot() or {}
    except Exception:
        pass
    return {}


def _format(rec: dict) -> str:
    target = rec.get("target") or {}
    detail = ""
    if rec.get("condition") == "time":
        detail = str(target.get("run_at_iso") or "")
    elif rec.get("condition", "").startswith("file_"):
        detail = str(target.get("path") or "")
    elif rec.get("condition") == "media_end":
        detail = str(target.get("scope") or "item")
    evidence = str(rec.get("completion_evidence") or "")
    return (
        f"[{rec.get('id')}] {rec.get('status')} — {rec.get('title')}"
        + (f" ({detail})" if detail else "")
        + (f"\n  Evidence: {evidence}" if evidence else "")
    )


def long_task(parameters: dict, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = str(params.get("action") or "create").strip().lower().replace("-", "_")
    manager = get_long_task_manager()
    try:
        if action in ("watch_until_end", "watch_media", "media_end"):
            video = _active_video()
            scope = str(params.get("scope") or ("queue" if video.get("queue_total", 0) > 1 else "item")).lower()
            rec = manager.create_media(
                video,
                scope=scope,
                notify_message=str(params.get("notify_message") or ""),
                max_wait_hours=float(params.get("max_wait_hours") or 24),
            )
            return (
                f"Long-term task armed: {rec['id']}. I will rely on the player's real ended event "
                f"and notify you when the {'whole queue' if scope in ('queue','playlist','mix') else 'current video'} finishes."
            )

        if action in ("at_time", "time", "deadline"):
            delay = float(params.get("delay_seconds") or 0)
            run_at_raw = str(params.get("run_at") or "").strip()
            if delay > 0:
                run_at = time.time() + delay
            elif run_at_raw:
                run_at = datetime.fromisoformat(run_at_raw.replace("Z", "+00:00")).timestamp()
            else:
                return "long_task: provide run_at (ISO date/time) or delay_seconds."
            rec = manager.create_deadline(
                run_at,
                title=str(params.get("title") or "Scheduled notification"),
                notify_message=str(params.get("notify_message") or ""),
            )
            return f"Long-term task armed: {_format(rec)}"

        if action in ("file_exists", "file_ready", "file_changed"):
            path = str(params.get("path") or "").strip()
            if not path:
                return "long_task: provide the file path to monitor."
            rec = manager.create_file(
                path,
                changed=action == "file_changed",
                title=str(params.get("title") or ""),
                notify_message=str(params.get("notify_message") or ""),
                max_wait_hours=float(params.get("max_wait_hours") or 24 * 7),
            )
            return f"Long-term task armed: {_format(rec)}"

        if action in ("workflow", "run_workflow", "long_workflow"):
            raw_steps = params.get("steps")
            if isinstance(raw_steps, str):
                try:
                    raw_steps = json.loads(raw_steps)
                except json.JSONDecodeError as exc:
                    return f"long_task: steps must be a JSON array: {exc}"
            rec = manager.create_workflow(
                raw_steps if isinstance(raw_steps, list) else [],
                title=str(params.get("title") or "Long-running workflow"),
                notify_message=str(params.get("notify_message") or ""),
                max_wait_hours=float(params.get("max_wait_hours") or 24 * 7),
            )
            return (
                f"Durable workflow started: {rec['id']} with "
                f"{len((rec.get('target') or {}).get('steps') or [])} checkpointed steps."
            )

        if action == "resume":
            task_id = str(params.get("task_id") or "").strip()
            resolution = str(params.get("resolution") or "").strip()
            if not resolution:
                return "long_task resume: choose resolution='retry' or 'mark_done' after reviewing the uncertain step."
            return (
                f"Resumed {task_id} with resolution {resolution}."
                if manager.resolve_uncertain(task_id, resolution)
                else f"Could not resume '{task_id}'; it is not waiting for crash review or the resolution is invalid."
            )

        if action == "list":
            rows = manager.list(include_finished=bool(params.get("include_finished", True)))
            return "No long-term tasks." if not rows else "Long-term tasks:\n" + "\n".join(_format(x) for x in rows[:30])

        if action == "status":
            task_id = str(params.get("task_id") or "").strip()
            rec = manager.get(task_id)
            return _format(rec) if rec else f"Long-term task '{task_id}' was not found."

        if action == "cancel":
            task_id = str(params.get("task_id") or "").strip()
            return f"Cancelled long-term task {task_id}." if manager.cancel(task_id) else f"Could not cancel '{task_id}'; it may already be finished."

        if action == "remove":
            task_id = str(params.get("task_id") or "").strip()
            return f"Removed long-term task {task_id}." if manager.remove(task_id) else f"Could not remove '{task_id}'; only finished tasks can be removed."

        return "long_task actions: workflow | watch_until_end | at_time | file_exists | file_changed | list | status | resume | cancel | remove"
    except (ValueError, OSError) as exc:
        return f"long_task: {exc}"


TOOL = {
    "name": "long_task",
    "description": (
        "Run and manage REAL durable long tasks. Use workflow for a long multi-tool job: each action "
        "step is persisted before and after execution, outputs can feed later steps, progress survives "
        "restarts, and a crash during a possibly non-repeatable side effect pauses for explicit review "
        "instead of silently repeating it. Use watch_until_end when the user says 'watch this until the "
        "end and notify me'; it waits for the active player's actual ended event. Also supports future "
        "times and file creation/change. Tasks appear in Activity, can be cancelled between steps, and "
        "send desktop + in-app completion notices."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "workflow | watch_until_end | at_time | file_exists | file_changed | list | status | resume | cancel | remove"},
            "task_id": {"type": "STRING", "description": "Task ID for status/resume/cancel/remove"},
            "steps": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "tool": {"type": "STRING", "description": "Discoverable action name"},
                        "params": {"type": "STRING", "description": "JSON object string of tool parameters; may use ${previous.output} or ${step.N.output}"},
                    },
                    "required": ["tool", "params"],
                },
                "description": "workflow: ordered durable tool steps",
            },
            "resolution": {"type": "STRING", "description": "resume after crash review: retry or mark_done"},
            "scope": {"type": "STRING", "description": "For media: item or queue. Defaults to queue when a playlist is active."},
            "run_at": {"type": "STRING", "description": "ISO local date/time for at_time"},
            "delay_seconds": {"type": "NUMBER", "description": "Alternative relative delay for at_time"},
            "path": {"type": "STRING", "description": "Absolute or ~ path for file_exists/file_changed"},
            "title": {"type": "STRING", "description": "Short task label"},
            "notify_message": {"type": "STRING", "description": "Message delivered only after observed completion"},
            "max_wait_hours": {"type": "NUMBER", "description": "Expiry guard; default 24 for media, 168 for files, maximum 720/8760"},
            "include_finished": {"type": "BOOLEAN", "description": "list: include completed/cancelled/expired tasks"},
        },
        "required": ["action"],
    },
    "handler": long_task,
}
