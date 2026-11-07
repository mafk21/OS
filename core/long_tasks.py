"""Durable, evidence-driven long-term task monitoring.

Unlike a conversational promise, these tasks are persisted to disk and finish
only after an observable condition occurs: HUD media emits an ``ended`` event,
a deadline passes, or a file appears/changes. Completion is delivered through
an OS desktop notification and any registered in-app listeners. Pending tasks
survive JARVIS restarts.
"""
from __future__ import annotations

import inspect
import json
import os
import platform
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_FILE = BASE_DIR / "memory" / "long_tasks.json"
_TERMINAL = {"completed", "cancelled", "expired", "failed"}
_ACTIVE = {"planned", "active", "waiting", "paused", "retrying", "blocked", "uncertain"}
_MAX_TASKS = 200
_MAX_ACTIVE_TASKS = 100
_STORE_VERSION = 3


def _now_iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts if ts is not None else time.time()).astimezone().isoformat(timespec="seconds")


def desktop_notify(title: str, message: str) -> bool:
    """Best-effort immediate native notification without shell interpolation."""
    title = str(title or "JARVIS").strip()[:80]
    message = str(message or "Task completed.").strip()[:500]
    try:
        from plyer import notification  # type: ignore
        notification.notify(title=title, message=message, timeout=15)
        return True
    except Exception:
        pass
    system = platform.system()
    try:
        if system == "Darwin" and shutil.which("osascript"):
            # Values are argv, but AppleScript source still needs string escaping.
            esc_title = title.replace("\\", "\\\\").replace('"', '\\"')
            esc_message = message.replace("\\", "\\\\").replace('"', '\\"')
            result = subprocess.run(
                ["osascript", "-e", f'display notification "{esc_message}" with title "{esc_title}"'],
                capture_output=True, timeout=8,
            )
            return result.returncode == 0
        if system == "Linux" and shutil.which("notify-send"):
            result = subprocess.run(
                ["notify-send", "--urgency=normal", "--expire-time=15000", title, message],
                capture_output=True, timeout=8,
            )
            return result.returncode == 0
        if system == "Windows":
            # Avoid PowerShell/script interpolation. msg.exe is plain argv and is
            # available on standard Windows editions; the HUD log is the fallback.
            msg = shutil.which("msg") or shutil.which("msg.exe")
            if msg:
                result = subprocess.run(
                    [msg, "*", "/TIME:30", f"{title}: {message}"],
                    capture_output=True, timeout=8,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                return result.returncode == 0
    except Exception:
        pass
    return False


class LongTaskManager:
    """Atomic persistent task registry plus a lightweight condition poller."""

    def __init__(self, path: Path = TASKS_FILE, poll_seconds: float = 2.0):
        self.path = Path(path)
        self.poll_seconds = max(0.05, float(poll_seconds))
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._listeners: list[Callable[[], None]] = []
        self._notifiers: list[Callable[[dict[str, Any]], None]] = []
        self._delivering: set[str] = set()
        self._workflow_threads: set[str] = set()
        self._executor: Callable[[str, dict[str, Any]], Any] | None = None
        self._cancel_executor: Callable[[str], None] | None = None
        self._cancel_events: dict[str, threading.Event] = {}

    @staticmethod
    def _migrate_row(row: dict[str, Any]) -> dict[str, Any]:
        """Normalize v1/v2 workflow states without losing persisted evidence."""
        migrated = dict(row)
        migrated["status"] = {
            "running": "active", "needs_review": "uncertain",
        }.get(str(migrated.get("status") or "waiting"), str(migrated.get("status") or "waiting"))
        target = migrated.get("target")
        if isinstance(target, dict) and isinstance(target.get("steps"), list):
            for step in target["steps"]:
                if not isinstance(step, dict):
                    continue
                step.setdefault("timeout_seconds", 300.0)
                step.setdefault("strategies", [])
                step.setdefault("strategy_index", 0)
                step.setdefault("deadline_at", None)
        migrated.setdefault("paused_at", None)
        migrated.setdefault("blocked_reason", None)
        return migrated

    @staticmethod
    def _decode_store(text: str) -> list[dict[str, Any]]:
        raw = json.loads(text)
        rows = raw.get("tasks", []) if isinstance(raw, dict) else raw
        if not isinstance(rows, list) or any(not isinstance(item, dict) for item in rows):
            raise ValueError("long-task store has an invalid tasks collection")
        return [LongTaskManager._migrate_row(dict(item)) for item in rows]

    def _load(self) -> list[dict[str, Any]]:
        """Load persisted tasks without ever treating corruption as an empty store."""
        with self._lock:
            if not self.path.exists():
                return []
            try:
                text = self.path.read_text(encoding="utf-8")
                raw = json.loads(text)
                rows = self._decode_store(text)
                version = int(raw.get("version", 1)) if isinstance(raw, dict) else 1
                if version < _STORE_VERSION:
                    self._save(rows)
                elif version > _STORE_VERSION:
                    raise ValueError("long-task store uses an unsupported future version")
                return rows
            except (OSError, ValueError, json.JSONDecodeError) as primary_error:
                backup = self.path.with_suffix(self.path.suffix + ".bak")
                if backup.exists():
                    try:
                        return self._decode_store(backup.read_text(encoding="utf-8"))
                    except (OSError, ValueError, json.JSONDecodeError):
                        pass
                raise RuntimeError(
                    f"Long-task storage is unreadable at {self.path}; the file was preserved. "
                    "Restore its .bak copy or repair the JSON before creating more tasks."
                ) from primary_error

    def _save(self, rows: list[dict[str, Any]]) -> None:
        """Atomically persist and fsync tasks, retaining the last valid snapshot."""
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            backup = self.path.with_suffix(self.path.suffix + ".bak")
            payload = json.dumps(
                {"version": _STORE_VERSION, "tasks": rows}, indent=2, ensure_ascii=False
            )
            with tmp.open("w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if self.path.exists():
                try:
                    # Never replace a good backup with a corrupt primary file.
                    self._decode_store(self.path.read_text(encoding="utf-8"))
                    shutil.copy2(self.path, backup)
                except (OSError, ValueError, json.JSONDecodeError):
                    pass
            os.replace(tmp, self.path)
            try:
                directory_fd = os.open(str(self.path.parent), os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            except OSError:
                # Directory fsync is unavailable on some Windows/filesystem combinations.
                pass

    def add_listener(self, callback: Callable[[], None]) -> None:
        if callable(callback) and callback not in self._listeners:
            self._listeners.append(callback)

    def add_notifier(self, callback: Callable[[dict[str, Any]], None]) -> None:
        if callable(callback) and callback not in self._notifiers:
            self._notifiers.append(callback)

    def set_executor(self, callback: Callable[[str, dict[str, Any]], Any]) -> None:
        """Bind the app's real action registry for durable workflow steps."""
        if callable(callback):
            self._executor = callback
            with self._lock:
                rows = self._load()
                changed = False
                for rec in rows:
                    if rec.get("condition") == "workflow" and rec.get("status") == "blocked" and rec.get("blocked_reason") == "executor_unavailable":
                        rec["status"] = "waiting"
                        rec["blocked_reason"] = None
                        rec["updated_at"] = time.time()
                        changed = True
                if changed:
                    self._save(rows)
            self._launch_pending_workflows()

    def set_cancel_executor(self, callback: Callable[[str], None]) -> None:
        """Bind cancellation propagation for executors that own child work."""
        if callable(callback):
            self._cancel_executor = callback

    def _changed(self) -> None:
        for callback in list(self._listeners):
            try:
                callback()
            except Exception:
                pass

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            self._launch_pending_workflows()
            return
        self._stop.clear()
        self._recover_interrupted_workflows()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="JarvisLongTasks")
        self._thread.start()
        # Deliver a completion that was persisted immediately before a crash.
        self.deliver_pending_notifications()
        self._launch_pending_workflows()

    def stop(self) -> None:
        self._stop.set()

    def _new(self, *, title: str, condition: str, target: dict[str, Any],
             notify_message: str, expires_at: float,
             idempotency_key: str = "", initial_status: str = "waiting") -> dict[str, Any]:
        now = time.time()
        key = str(idempotency_key or "").strip()[:160]
        with self._lock:
            rows = self._load()
            if key:
                existing = next((row for row in rows if row.get("idempotency_key") == key), None)
                if existing:
                    return dict(existing)
            active_count = sum(1 for row in rows if row.get("status") not in _TERMINAL)
            if active_count >= _MAX_ACTIVE_TASKS:
                raise ValueError(
                    f"The active long-task limit ({_MAX_ACTIVE_TASKS}) has been reached. "
                    "Finish or cancel existing tasks before adding another."
                )
            rec = {
                "id": f"long-{uuid.uuid4().hex[:10]}",
                "kind": "long_task",
                "title": str(title or "Long-term task").strip()[:120],
                "condition": condition,
                "target": target,
                "notify_message": str(notify_message or "Task completed.").strip()[:500],
                "idempotency_key": key or None,
                "status": initial_status if initial_status in _ACTIVE else "waiting",
                "created_at": now,
                "updated_at": now,
                "created_iso": _now_iso(now),
                "expires_at": float(expires_at),
                "completed_at": None,
                "completion_evidence": None,
                "notified_at": None,
                "notification_channel": None,
                "events": [{"ts": now, "type": "created"}],
            }
            rows.append(rec)
            if len(rows) > _MAX_TASKS:
                # Retention may prune old terminal history, never active work.
                terminal = sorted(
                    (row for row in rows if row.get("status") in _TERMINAL),
                    key=lambda row: float(row.get("updated_at") or row.get("created_at") or 0),
                )
                removable = {id(row) for row in terminal[:len(rows) - _MAX_TASKS]}
                rows = [row for row in rows if id(row) not in removable]
            self._save(rows)
        self.start()
        self._changed()
        return dict(rec)

    def create_media(self, video: dict[str, Any], *, scope: str = "item",
                     notify_message: str = "", max_wait_hours: float = 24.0,
                     idempotency_key: str = "") -> dict[str, Any]:
        if not isinstance(video, dict) or not str(video.get("id") or "").strip():
            raise ValueError("No active HUD video is playing. Start the video first.")
        scope = "queue" if scope in ("queue", "playlist", "mix") else "item"
        title = str(
            (video.get("playlist_title") if scope == "queue" else video.get("title"))
            or video.get("title") or "media"
        ).strip()
        target = {
            "scope": scope,
            "video_id": str(video.get("id") or ""),
            "webpage_url": str(video.get("webpage_url") or ""),
            "playlist_url": str(video.get("playlist_url") or ""),
            "queue_total": int(video.get("queue_total") or 0),
        }
        msg = notify_message or f"Finished watching {title}."
        return self._new(
            title=f"Watch until finished — {title}", condition="media_end", target=target,
            notify_message=msg, expires_at=time.time() + max(1.0, min(max_wait_hours, 24 * 30)) * 3600,
            idempotency_key=idempotency_key,
        )

    def create_deadline(self, run_at: float, *, title: str = "Scheduled task",
                        notify_message: str = "", max_wait_hours: float = 24 * 365,
                        idempotency_key: str = "") -> dict[str, Any]:
        run_at = float(run_at)
        if run_at <= time.time():
            raise ValueError("The completion time must be in the future.")
        return self._new(
            title=title, condition="time", target={"run_at": run_at, "run_at_iso": _now_iso(run_at)},
            notify_message=notify_message or f"{title} is due.",
            expires_at=run_at + max(1.0, max_wait_hours) * 3600,
            idempotency_key=idempotency_key,
        )

    def create_file(self, path: str, *, changed: bool = False, title: str = "",
                    notify_message: str = "", max_wait_hours: float = 24 * 7,
                    idempotency_key: str = "") -> dict[str, Any]:
        file_path = Path(path).expanduser().resolve()
        initial = None
        if file_path.exists():
            stat = file_path.stat()
            initial = {"mtime_ns": stat.st_mtime_ns, "size": stat.st_size}
        if not changed and initial is not None:
            raise ValueError("That file already exists; there is nothing to wait for.")
        if changed and initial is None:
            raise ValueError("File-change monitoring requires an existing file.")
        label = title or (f"Wait for {file_path.name} to change" if changed else f"Wait for {file_path.name}")
        return self._new(
            title=label, condition="file_changed" if changed else "file_exists",
            target={"path": str(file_path), "initial": initial},
            notify_message=notify_message or f"{file_path.name} is ready.",
            expires_at=time.time() + max(1.0, min(max_wait_hours, 24 * 365)) * 3600,
            idempotency_key=idempotency_key,
        )

    def create_workflow(self, steps: list[dict[str, Any]], *, title: str = "Long-running workflow",
                        notify_message: str = "", max_wait_hours: float = 24 * 7,
                        idempotency_key: str = "") -> dict[str, Any]:
        """Persist and execute sequential real actions, checkpointing every step."""
        if not isinstance(steps, list) or not steps:
            raise ValueError("A workflow requires at least one tool step.")
        if len(steps) > 25:
            raise ValueError("A workflow is limited to 25 steps; split larger jobs into stages.")
        normalized = []
        for index, raw in enumerate(steps, 1):
            if not isinstance(raw, dict):
                raise ValueError(f"Workflow step {index} must be an object.")
            tool = str(raw.get("tool") or "").strip()
            if not tool or tool == "long_task":
                raise ValueError(f"Workflow step {index} has an invalid tool.")
            params = raw.get("params", {})
            if isinstance(params, str):
                try:
                    params = json.loads(params or "{}")
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Workflow step {index} params are not valid JSON: {exc}") from exc
            if not isinstance(params, dict):
                raise ValueError(f"Workflow step {index} params must be a JSON object.")
            max_attempts = int(raw.get("max_attempts") or 1)
            retry_delay = float(raw.get("retry_delay_seconds") or 0)
            retry_safe = bool(raw.get("retry_safe", False))
            if max_attempts < 1 or max_attempts > 5:
                raise ValueError(f"Workflow step {index} max_attempts must be between 1 and 5.")
            if retry_delay < 0 or retry_delay > 3600:
                raise ValueError(f"Workflow step {index} retry_delay_seconds must be between 0 and 3600.")
            if max_attempts > 1 and not retry_safe:
                raise ValueError(
                    f"Workflow step {index} requests automatic retries but is not marked retry_safe. "
                    "Side-effecting steps require manual review instead of blind repetition."
                )
            timeout_seconds = float(raw.get("timeout_seconds") or 300)
            if timeout_seconds < 1 or timeout_seconds > 3600:
                raise ValueError(f"Workflow step {index} timeout_seconds must be between 1 and 3600.")
            alternatives = raw.get("alternatives") or []
            if not isinstance(alternatives, list) or len(alternatives) > 3:
                raise ValueError(f"Workflow step {index} alternatives must be a list of at most 3 strategies.")
            strategies = [{"tool": tool, "params": params}]
            for alt in alternatives:
                if not isinstance(alt, dict) or not str(alt.get("tool") or "").strip():
                    raise ValueError(f"Workflow step {index} has an invalid alternative strategy.")
                alt_tool = str(alt["tool"]).strip()
                alt_params = alt.get("params", {})
                if alt_tool == "long_task" or not isinstance(alt_params, dict):
                    raise ValueError(f"Workflow step {index} has an invalid alternative strategy.")
                strategies.append({"tool": alt_tool, "params": alt_params})
            if len(strategies) > 1 and not bool(raw.get("fallback_safe", False)):
                raise ValueError(f"Workflow step {index} alternatives require fallback_safe=true.")
            normalized.append({
                "index": index, "tool": tool, "params": params,
                "status": "queued", "attempts": 0,
                "max_attempts": max_attempts, "retry_delay_seconds": retry_delay,
                "retry_safe": retry_safe, "next_attempt_at": None,
                "timeout_seconds": timeout_seconds, "deadline_at": None,
                "strategies": strategies, "strategy_index": 0,
                "started_at": None, "completed_at": None,
                "output": None, "error": None, "execution_id": None,
            })
        rec = self._new(
            title=title, condition="workflow",
            target={"steps": normalized, "current_step": 0},
            notify_message=notify_message or f"Workflow finished: {title}",
            expires_at=time.time() + max(1.0, min(max_wait_hours, 24 * 365)) * 3600,
            idempotency_key=idempotency_key, initial_status="planned",
        )
        self._launch_workflow(str(rec["id"]))
        return self.get(str(rec["id"])) or rec

    def list(self, include_finished: bool = True) -> list[dict[str, Any]]:
        rows = self._load()
        if not include_finished:
            rows = [x for x in rows if x.get("status") not in _TERMINAL]
        return sorted(rows, key=lambda x: float(x.get("created_at") or 0), reverse=True)

    def get(self, task_id: str) -> dict[str, Any] | None:
        rec = next((x for x in self._load() if x.get("id") == task_id), None)
        # A status reader is also an opportunity to finish a persisted delivery
        # that lost the race with completion or survived an application crash.
        if rec and rec.get("status") == "completed" and not rec.get("notified_at"):
            self._deliver(rec)
            rec = next((x for x in self._load() if x.get("id") == task_id), rec)
        return rec

    def list_detailed(self) -> list[dict[str, Any]]:
        now = time.time()
        out = []
        for rec in self.list()[:50]:
            status = str(rec.get("status") or "waiting")
            target = rec.get("target") or {}
            evidence = rec.get("completion_evidence") or ""
            workflow_steps = target.get("steps") or [] if rec.get("condition") == "workflow" else []
            activity_steps = ([{
                "step": int(step.get("index") or index),
                "action": str(step.get("tool") or "tool"),
                "result": str(step.get("output") or step.get("error") or step.get("status") or "queued")[:500],
                "ts": step.get("completed_at") or step.get("started_at") or rec.get("updated_at"),
            } for index, step in enumerate(workflow_steps, 1)] if workflow_steps else [{
                "step": 1, "action": str(rec.get("condition") or "monitor"),
                "result": evidence or self._target_summary(str(rec.get("condition") or ""), target),
                "ts": rec.get("updated_at"),
            }])
            out.append({
                "id": rec.get("id"), "kind": "long_task", "title": rec.get("title"),
                "goal": rec.get("title"),
                "status": (
                    "in_progress" if status in {"planned", "active", "waiting", "retrying"}
                    else "needs_review" if status in {"paused", "blocked", "uncertain"}
                    else status
                ),
                "tools": [str(step.get("tool")) for step in workflow_steps] or ["long_task"],
                "nodes": ["planner"], "steps": activity_steps[-12:],
                "step_count": sum(1 for step in workflow_steps if step.get("status") == "completed") if workflow_steps else 1,
                "max_steps": len(workflow_steps) if workflow_steps else 1,
                "result": evidence if status == "completed" else None,
                "error": evidence if status in ("failed", "expired") else None,
                "created_at": rec.get("created_at"), "updated_at": rec.get("updated_at"),
                "elapsed_s": round(max(0.0, (float(rec.get("completed_at") or now) - float(rec.get("created_at") or now))), 1),
            })
        return out

    @staticmethod
    def _target_summary(condition: str, target: dict[str, Any]) -> str:
        if condition == "media_end":
            return "Waiting for the player to report real playback completion."
        if condition == "time":
            return f"Waiting until {target.get('run_at_iso', 'scheduled time')}."
        if condition == "file_changed":
            return f"Watching for a real file change: {target.get('path', '')}"
        if condition == "file_exists":
            return f"Watching for file creation: {target.get('path', '')}"
        if condition == "workflow":
            steps = target.get("steps") or []
            done = sum(1 for step in steps if step.get("status") == "completed")
            return f"Executing durable workflow steps: {done}/{len(steps)} complete."
        return "Monitoring an observable completion condition."

    def _recover_interrupted_workflows(self) -> None:
        """Never blindly repeat a side effect whose result was lost in a crash."""
        with self._lock:
            rows = self._load()
            changed = False
            for rec in rows:
                if rec.get("condition") != "workflow" or rec.get("status") in _TERMINAL:
                    continue
                steps = (rec.get("target") or {}).get("steps") or []
                interrupted = next((s for s in steps if s.get("status") == "running"), None)
                if interrupted:
                    interrupted["status"] = "uncertain"
                    interrupted["error"] = (
                        "JARVIS stopped while this step was running. Its side effect may have happened; "
                        "choose retry or mark_done explicitly."
                    )
                    rec["status"] = "uncertain"
                    rec["completion_evidence"] = interrupted["error"]
                    rec["updated_at"] = time.time()
                    changed = True
                elif rec.get("status") in ("active", "waiting", "retrying", "planned"):
                    rec["status"] = "waiting"
                    changed = True
            if changed:
                self._save(rows)
        if changed:
            self._changed()

    def _launch_pending_workflows(self) -> None:
        for rec in self.list(include_finished=False):
            if rec.get("condition") == "workflow" and rec.get("status") in {"planned", "waiting", "retrying"}:
                self._launch_workflow(str(rec.get("id") or ""))

    def _launch_workflow(self, task_id: str) -> bool:
        if not task_id:
            return False
        if self._executor is None:
            with self._lock:
                rows = self._load()
                rec = next((row for row in rows if row.get("id") == task_id), None)
                if rec and rec.get("condition") == "workflow" and rec.get("status") in {"planned", "waiting", "retrying"}:
                    rec["status"] = "blocked"
                    rec["blocked_reason"] = "executor_unavailable"
                    rec["updated_at"] = time.time()
                    self._save(rows)
            self._changed()
            return False
        with self._lock:
            if task_id in self._workflow_threads:
                return False
            rec = self.get(task_id)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") not in {"planned", "waiting", "retrying"}:
                return False
            self._workflow_threads.add(task_id)
        thread = threading.Thread(
            target=self._run_workflow, args=(task_id,), daemon=True,
            name=f"JarvisLongWorkflow-{task_id[-6:]}",
        )
        thread.start()
        return True

    @staticmethod
    def _resolve_workflow_params(value: Any, completed: list[dict[str, Any]]) -> Any:
        """Allow later steps to consume `${previous.output}` / `${step.N.output}`."""
        if isinstance(value, dict):
            return {k: LongTaskManager._resolve_workflow_params(v, completed) for k, v in value.items()}
        if isinstance(value, list):
            return [LongTaskManager._resolve_workflow_params(v, completed) for v in value]
        if not isinstance(value, str):
            return value
        out = value
        previous = str(completed[-1].get("output") or "") if completed else ""
        out = out.replace("${previous.output}", previous)
        for step in completed:
            out = out.replace(f"${{step.{step.get('index')}.output}}", str(step.get("output") or ""))
        return out

    def _default_execute(self, tool: str, params: dict[str, Any]) -> Any:
        from core.action_loader import discover_actions
        registry = discover_actions(BASE_DIR / "actions", logger=lambda _msg: None)
        if not registry.has(tool):
            raise ValueError(f"Tool '{tool}' is not a discoverable durable action.")
        return registry.run(tool, params, {"player": None, "speak": None})

    def _execute_with_timeout(self, tool: str, params: dict[str, Any], execution_id: str,
                              timeout_seconds: float) -> tuple[Any, bool]:
        """Bound a step without pretending a timed-out side effect did not happen."""
        finished = threading.Event()
        cancelled = self._cancel_events.setdefault(execution_id, threading.Event())
        outcome: list[tuple[bool, Any]] = []

        def invoke() -> None:
            try:
                executor = self._executor or self._default_execute
                try:
                    supports_context = len(inspect.signature(executor).parameters) >= 3
                except (TypeError, ValueError):
                    supports_context = False
                context = {"execution_id": execution_id, "cancellation_event": cancelled}
                outcome.append((True, executor(tool, params, context) if supports_context else executor(tool, params)))
            except BaseException as exc:
                outcome.append((False, exc))
            finally:
                finished.set()
                # Keep the token while work is active so cancel() can propagate;
                # remove it only after the executor has actually returned.
                self._cancel_events.pop(execution_id, None)

        threading.Thread(target=invoke, daemon=True, name=f"LongTaskStep-{execution_id[-6:]}").start()
        if not finished.wait(max(1.0, min(float(timeout_seconds), 3600.0))):
            cancelled.set()
            if self._cancel_executor:
                try:
                    self._cancel_executor(execution_id)
                except Exception:
                    pass
            return "Step timed out; its external side effect may have occurred.", True
        self._cancel_events.pop(execution_id, None)
        ok, value = outcome[0]
        if not ok:
            raise value
        return value, False

    @staticmethod
    def _normalize_execution_result(value: Any) -> tuple[str, bool, bool]:
        """Interpret structured action results before falling back to legacy text signals."""
        if isinstance(value, dict):
            status = str(value.get("status") or "").strip().lower()
            confirmation = bool(value.get("confirmation_pending")) or status in {
                "confirmation_pending", "pending_confirmation", "needs_confirmation",
            }
            explicit_failure = value.get("ok") is False or value.get("success") is False
            failed = explicit_failure or status in {"failed", "failure", "error"}
            return json.dumps(value, ensure_ascii=False, default=str), failed, confirmation
        if value is False:
            return "Action returned false.", True, False
        result = str(value if value is not None else "Done.")
        result_low = result.strip().lower()
        confirmation = "[confirmation_pending]" in result_low
        failed = result_low.startswith((
            "tool '", "action '", "error", "failed", "could not", "unable to",
        ))
        return result, failed, confirmation

    def _run_workflow(self, task_id: str) -> None:
        try:
            while not self._stop.is_set():
                with self._lock:
                    rows = self._load()
                    rec = next((x for x in rows if x.get("id") == task_id), None)
                    if not rec or rec.get("status") in _TERMINAL or rec.get("status") in {"uncertain", "paused", "blocked"}:
                        return
                    target = rec.get("target") or {}
                    steps = target.get("steps") or []
                    if float(rec.get("expires_at") or 0) and time.time() >= float(rec["expires_at"]):
                        rec["status"] = "expired"
                        rec["updated_at"] = time.time()
                        rec["completion_evidence"] = "Workflow deadline expired before all steps completed."
                        rec["events"] = (list(rec.get("events") or []) + [{
                            "ts": time.time(), "type": "expired",
                        }])[-50:]
                        self._save(rows)
                        self._changed()
                        return
                    queued = next((s for s in steps if s.get("status") == "queued"), None)
                    if queued is None:
                        break
                    next_attempt = float(queued.get("next_attempt_at") or 0)
                    wait_seconds = max(0.0, min(next_attempt - time.time(), 1.0))
                    if not wait_seconds:
                        completed = [dict(s) for s in steps if s.get("status") == "completed"]
                        queued["status"] = "running"
                        queued["next_attempt_at"] = None
                        queued["attempts"] = int(queued.get("attempts") or 0) + 1
                        queued["started_at"] = time.time()
                        queued["execution_id"] = f"exec-{uuid.uuid4().hex[:10]}"
                        queued["deadline_at"] = queued["started_at"] + float(queued.get("timeout_seconds") or 300)
                        rec["status"] = "active"
                        rec["updated_at"] = time.time()
                        target["current_step"] = int(queued.get("index") or 1)
                        rec["events"] = (list(rec.get("events") or []) + [{
                            "ts": rec["updated_at"], "type": "step_started",
                            "step": queued.get("index"), "tool": queued.get("tool"),
                            "attempt": queued.get("attempts"),
                        }])[-50:]
                        self._save(rows)  # checkpoint BEFORE any side effect
                        strategies = queued.get("strategies") or [{"tool": queued.get("tool"), "params": queued.get("params") or {}}]
                        strategy_index = min(int(queued.get("strategy_index") or 0), len(strategies) - 1)
                        strategy = strategies[strategy_index]
                        tool = str(strategy.get("tool") or "")
                        params = self._resolve_workflow_params(dict(strategy.get("params") or {}), completed)
                        execution_id = str(queued["execution_id"])
                        timeout_seconds = float(queued.get("timeout_seconds") or 300)
                if wait_seconds:
                    self._stop.wait(wait_seconds)
                    continue
                self._changed()

                timed_out = False
                try:
                    raw_result, timed_out = self._execute_with_timeout(
                        tool, params, execution_id, timeout_seconds
                    )
                    result, failed, confirmation_pending = self._normalize_execution_result(raw_result)
                except Exception as exc:
                    result = f"{type(exc).__name__}: {exc}"
                    failed = True
                    confirmation_pending = False

                with self._lock:
                    rows = self._load()
                    rec = next((x for x in rows if x.get("id") == task_id), None)
                    if not rec or rec.get("status") in _TERMINAL:
                        return
                    steps = (rec.get("target") or {}).get("steps") or []
                    step = next((s for s in steps if s.get("execution_id") == execution_id), None)
                    if not step:
                        return
                    now = time.time()
                    retry_scheduled = False
                    step["completed_at"] = now
                    if timed_out:
                        step["status"] = "uncertain"
                        step["error"] = result[:4000]
                        rec["status"] = "uncertain"
                        rec["completion_evidence"] = (
                            f"Step {step.get('index')} ({tool}) exceeded its timeout. Its side effect may have occurred; "
                            "review evidence before retrying or marking it complete."
                        )
                        rec["events"] = (list(rec.get("events") or []) + [{
                            "ts": now, "type": "step_timed_out", "step": step.get("index"),
                            "execution_id": execution_id,
                        }])[-50:]
                    elif confirmation_pending:
                        step["status"] = "uncertain"
                        step["error"] = result[:4000]
                        rec["status"] = "uncertain"
                        rec["completion_evidence"] = (
                            f"Step {step.get('index')} ({tool}) is waiting for the HUD confirmation. "
                            "After approving or rejecting it, resume with mark_done or retry."
                        )
                    elif failed:
                        attempts = int(step.get("attempts") or 0)
                        max_attempts = int(step.get("max_attempts") or 1)
                        strategies = step.get("strategies") or []
                        strategy_index = int(step.get("strategy_index") or 0)
                        if strategy_index + 1 < len(strategies):
                            step["strategy_index"] = strategy_index + 1
                            step["status"] = "queued"
                            step["error"] = result[:4000]
                            step["execution_id"] = None
                            step["next_attempt_at"] = now
                            rec["status"] = "retrying"
                            rec["completion_evidence"] = None
                            retry_scheduled = True
                            rec["events"] = (list(rec.get("events") or []) + [{
                                "ts": now, "type": "alternative_strategy_selected",
                                "step": step.get("index"), "strategy_index": strategy_index + 1,
                            }])[-50:]
                        elif bool(step.get("retry_safe")) and attempts < max_attempts:
                            delay = float(step.get("retry_delay_seconds") or 0)
                            # Exponential backoff is bounded by the declared delay and attempt count.
                            retry_at = now + min(3600.0, delay * (2 ** max(0, attempts - 1)))
                            step["status"] = "queued"
                            step["error"] = result[:4000]
                            step["execution_id"] = None
                            step["next_attempt_at"] = retry_at
                            rec["status"] = "retrying"
                            rec["completion_evidence"] = None
                            retry_scheduled = True
                            rec["events"] = (list(rec.get("events") or []) + [{
                                "ts": now, "type": "step_retry_scheduled",
                                "step": step.get("index"), "attempt": attempts,
                                "next_attempt_at": retry_at,
                            }])[-50:]
                        else:
                            step["status"] = "failed"
                            step["error"] = result[:4000]
                            rec["status"] = "failed"
                            rec["completion_evidence"] = f"Step {step.get('index')} ({tool}) failed: {result[:500]}"
                    else:
                        step["status"] = "completed"
                        step["output"] = result[:12000]
                        step["error"] = None
                        rec["status"] = "waiting"
                        rec["completion_evidence"] = None
                    paused_now = False
                    if rec.get("pause_requested") and rec.get("status") in {"waiting", "retrying"}:
                        rec["status"] = "paused"
                        rec["pause_requested"] = False
                        rec["paused_at"] = now
                        paused_now = True
                        rec["events"] = (list(rec.get("events") or []) + [{
                            "ts": now, "type": "paused",
                        }])[-50:]
                    rec["updated_at"] = now
                    if not retry_scheduled and not paused_now:
                        rec["events"] = (list(rec.get("events") or []) + [{
                            "ts": now,
                            "type": f"step_{step.get('status')}",
                            "step": step.get("index"), "tool": tool,
                            "attempt": step.get("attempts"),
                        }])[-50:]
                    self._save(rows)
                self._changed()
                if confirmation_pending or timed_out or paused_now or (failed and not retry_scheduled):
                    return

            rec = self.get(task_id)
            if rec and rec.get("status") not in _TERMINAL:
                steps = (rec.get("target") or {}).get("steps") or []
                summary = "Workflow completed: " + "; ".join(
                    f"{s.get('index')}. {s.get('tool')}" for s in steps
                )
                self._complete(task_id, summary)
        finally:
            with self._lock:
                self._workflow_threads.discard(task_id)

    def pause(self, task_id: str) -> bool:
        """Pause before the next step; a running step is checkpointed first."""
        with self._lock:
            rows = self._load()
            rec = next((row for row in rows if row.get("id") == task_id), None)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") in _TERMINAL | {"paused", "uncertain"}:
                return False
            now = time.time()
            if rec.get("status") == "active":
                rec["pause_requested"] = True
                event_type = "pause_requested"
            else:
                rec["status"] = "paused"
                rec["paused_at"] = now
                event_type = "paused"
            rec["updated_at"] = now
            rec["events"] = (list(rec.get("events") or []) + [{"ts": now, "type": event_type}])[-50:]
            self._save(rows)
        self._changed()
        return True

    def resume(self, task_id: str) -> bool:
        with self._lock:
            rows = self._load()
            rec = next((row for row in rows if row.get("id") == task_id), None)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") not in {"paused", "blocked"}:
                return False
            if rec.get("status") == "blocked" and self._executor is None:
                return False
            now = time.time()
            rec["status"] = "waiting"
            rec["paused_at"] = None
            rec["blocked_reason"] = None
            rec["updated_at"] = now
            rec["events"] = (list(rec.get("events") or []) + [{"ts": now, "type": "resumed"}])[-50:]
            self._save(rows)
        self._changed()
        self._launch_workflow(task_id)
        return True

    def revise_step(self, task_id: str, step_index: int, patch: dict[str, Any]) -> bool:
        """Revise only a not-yet-run step while execution is safely paused."""
        if not isinstance(patch, dict):
            return False
        allowed = {"tool", "params", "timeout_seconds"}
        if set(patch) - allowed:
            return False
        with self._lock:
            rows = self._load()
            rec = next((row for row in rows if row.get("id") == task_id), None)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") not in {"paused", "blocked"}:
                return False
            steps = (rec.get("target") or {}).get("steps") or []
            step = next((item for item in steps if int(item.get("index") or 0) == int(step_index)), None)
            if not step or step.get("status") != "queued":
                return False
            if "tool" in patch:
                tool = str(patch["tool"] or "").strip()
                if not tool or tool == "long_task": return False
                step["tool"] = tool
            if "params" in patch:
                if not isinstance(patch["params"], dict): return False
                step["params"] = patch["params"]
            if "timeout_seconds" in patch:
                timeout = float(patch["timeout_seconds"])
                if timeout < 1 or timeout > 3600: return False
                step["timeout_seconds"] = timeout
            step["strategies"] = [{"tool": step["tool"], "params": step.get("params") or {}}]
            step["strategy_index"] = 0
            now = time.time()
            rec["updated_at"] = now
            rec["events"] = (list(rec.get("events") or []) + [{
                "ts": now, "type": "step_revised", "step": step_index,
            }])[-50:]
            self._save(rows)
        self._changed()
        return True

    def resolve_uncertain(self, task_id: str, resolution: str) -> bool:
        """Human recovery after a crash: retry explicitly or acknowledge done."""
        resolution = str(resolution or "").strip().lower()
        if resolution not in ("retry", "mark_done"):
            return False
        with self._lock:
            rows = self._load()
            rec = next((x for x in rows if x.get("id") == task_id), None)
            if not rec or rec.get("status") != "uncertain":
                return False
            steps = (rec.get("target") or {}).get("steps") or []
            step = next((s for s in steps if s.get("status") == "uncertain"), None)
            if not step:
                return False
            if resolution == "retry":
                step["status"] = "queued"
                step["error"] = None
                step["execution_id"] = None
            else:
                step["status"] = "completed"
                step["output"] = "Marked complete by the user after restart review."
                step["completed_at"] = time.time()
            rec["status"] = "waiting"
            rec["completion_evidence"] = None
            rec["updated_at"] = time.time()
            self._save(rows)
        self._changed()
        self._launch_workflow(task_id)
        return True

    def retry_failed(self, task_id: str) -> bool:
        """Explicitly retry the failed workflow step; never automatic for unsafe steps."""
        with self._lock:
            rows = self._load()
            rec = next((row for row in rows if row.get("id") == task_id), None)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") != "failed":
                return False
            steps = (rec.get("target") or {}).get("steps") or []
            step = next((item for item in steps if item.get("status") == "failed"), None)
            if not step:
                return False
            step["status"] = "queued"
            step["error"] = None
            step["execution_id"] = None
            step["next_attempt_at"] = None
            step["completed_at"] = None
            step["strategy_index"] = 0
            rec["status"] = "waiting"
            rec["completion_evidence"] = None
            rec["updated_at"] = time.time()
            rec["events"] = (list(rec.get("events") or []) + [{
                "ts": time.time(), "type": "failed_step_retry_requested",
                "step": step.get("index"),
            }])[-50:]
            self._save(rows)
        self._changed()
        self._launch_workflow(task_id)
        return True

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            rows = self._load()
            found = False
            execution_id = ""
            for rec in rows:
                if rec.get("id") == task_id and rec.get("status") not in _TERMINAL:
                    steps = (rec.get("target") or {}).get("steps") or []
                    running = next((step for step in steps if step.get("status") == "running"), None)
                    execution_id = str((running or {}).get("execution_id") or "")
                    rec["status"] = "cancelled"
                    rec["updated_at"] = time.time()
                    rec["events"] = (list(rec.get("events") or []) + [{"ts": time.time(), "type": "cancelled"}])[-20:]
                    found = True
                    break
            if found:
                self._save(rows)
        if found:
            if execution_id:
                event = self._cancel_events.get(execution_id)
                if event:
                    event.set()
                if self._cancel_executor:
                    try:
                        self._cancel_executor(execution_id)
                    except Exception:
                        pass
            self._changed()
        return found

    def remove(self, task_id: str) -> bool:
        with self._lock:
            rows = self._load()
            target = next((x for x in rows if x.get("id") == task_id), None)
            if not target or target.get("status") not in _TERMINAL:
                return False
            self._save([x for x in rows if x.get("id") != task_id])
        self._changed()
        return True

    def clear_finished(self) -> int:
        with self._lock:
            rows = self._load()
            kept = [x for x in rows if x.get("status") not in _TERMINAL]
            removed = len(rows) - len(kept)
            if removed:
                self._save(kept)
        if removed:
            self._changed()
        return removed

    def _complete(self, task_id: str, evidence: str) -> bool:
        with self._lock:
            rows = self._load()
            completed = None
            for rec in rows:
                if rec.get("id") == task_id and rec.get("status") in ("waiting", "active"):
                    now = time.time()
                    rec["status"] = "completed"
                    rec["completed_at"] = now
                    rec["updated_at"] = now
                    rec["completion_evidence"] = str(evidence)[:600]
                    rec["events"] = (list(rec.get("events") or []) + [{"ts": now, "type": "completed", "evidence": str(evidence)[:300]}])[-20:]
                    completed = dict(rec)
                    break
            if completed is None:
                return False
            self._save(rows)
        self._changed()
        self._deliver(completed)
        return True

    def signal_media_ended(self, event: dict[str, Any]) -> list[str]:
        """Complete matching media monitors from a real HTMLMediaElement ended event."""
        event_id = str(event.get("video_id") or "")
        webpage = str(event.get("webpage_url") or "")
        playlist = str(event.get("playlist_url") or "")
        terminal = bool(event.get("terminal", False))
        matched: list[str] = []
        for rec in self.list(include_finished=False):
            if rec.get("condition") != "media_end":
                continue
            target = rec.get("target") or {}
            scope = target.get("scope", "item")
            if scope == "queue":
                same = bool(target.get("playlist_url") and target.get("playlist_url") == playlist)
                same = same or (not target.get("playlist_url") and target.get("video_id") == event_id)
                ready = same and terminal
                evidence = "Player reported the final playlist item ended."
            else:
                same = target.get("video_id") == event_id
                same = same or bool(target.get("webpage_url") and target.get("webpage_url") == webpage)
                ready = same
                evidence = "Player reported the watched media ended."
            if ready and self._complete(str(rec.get("id")), evidence):
                matched.append(str(rec.get("id")))
        return matched

    def tick_once(self, now: float | None = None) -> list[str]:
        now = float(now if now is not None else time.time())
        completed: list[str] = []
        expired: list[str] = []
        for rec in self.list(include_finished=False):
            task_id = str(rec.get("id") or "")
            if float(rec.get("expires_at") or 0) and now >= float(rec.get("expires_at") or 0):
                expired.append(task_id)
                continue
            condition = rec.get("condition")
            target = rec.get("target") or {}
            evidence = ""
            if condition == "time" and now >= float(target.get("run_at") or 0):
                evidence = f"Scheduled time reached at {_now_iso(now)}."
            elif condition in ("file_exists", "file_changed"):
                path = Path(str(target.get("path") or ""))
                if condition == "file_exists" and path.is_file():
                    evidence = f"Observed file creation: {path}"
                elif condition == "file_changed" and path.is_file():
                    stat = path.stat()
                    initial = target.get("initial") or {}
                    if stat.st_mtime_ns != int(initial.get("mtime_ns") or -1) or stat.st_size != int(initial.get("size") or -1):
                        evidence = f"Observed file change: {path}"
            if evidence and self._complete(task_id, evidence):
                completed.append(task_id)
        if expired:
            with self._lock:
                rows = self._load()
                changed = False
                for rec in rows:
                    if rec.get("id") in expired and rec.get("status") in _ACTIVE:
                        rec["status"] = "expired"
                        rec["updated_at"] = now
                        rec["completion_evidence"] = "Monitoring deadline expired before completion was observed."
                        changed = True
                if changed:
                    self._save(rows)
            self._changed()
        self.deliver_pending_notifications()
        self._launch_pending_workflows()
        return completed

    def _deliver(self, rec: dict[str, Any]) -> None:
        task_id = str(rec.get("id") or "")
        if rec.get("notified_at") or not task_id:
            return
        with self._lock:
            if task_id in self._delivering:
                return
            self._delivering.add(task_id)
        try:
            message = str(rec.get("notify_message") or "Task completed.")
            native = desktop_notify("JARVIS · Task complete", message)
            app_delivered = False
            for callback in list(self._notifiers):
                try:
                    callback(dict(rec))
                    app_delivered = True
                except Exception:
                    pass
            # If neither channel exists yet, keep this completion pending and
            # retry when a HUD listener or OS notifier becomes available.
            if not native and not app_delivered:
                return
            with self._lock:
                rows = self._load()
                for row in rows:
                    if row.get("id") == task_id and not row.get("notified_at"):
                        row["notified_at"] = time.time()
                        row["notification_channel"] = (
                            "desktop+app" if native and app_delivered else "desktop" if native else "app"
                        )
                        break
                self._save(rows)
            self._changed()
        finally:
            with self._lock:
                self._delivering.discard(task_id)

    def deliver_pending_notifications(self) -> None:
        for rec in self.list():
            if rec.get("status") == "completed" and not rec.get("notified_at"):
                self._deliver(rec)

    def _loop(self) -> None:
        while not self._stop.wait(self.poll_seconds):
            try:
                self.tick_once()
            except Exception:
                pass


_MANAGER: LongTaskManager | None = None


def get_long_task_manager() -> LongTaskManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = LongTaskManager()
    return _MANAGER
