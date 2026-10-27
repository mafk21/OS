"""Durable, evidence-driven long-term task monitoring.

Unlike a conversational promise, these tasks are persisted to disk and finish
only after an observable condition occurs: HUD media emits an ``ended`` event,
a deadline passes, or a file appears/changes. Completion is delivered through
an OS desktop notification and any registered in-app listeners. Pending tasks
survive JARVIS restarts.
"""
from __future__ import annotations

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
        self._executor: Callable[[str, dict[str, Any]], str] | None = None

    def _load(self) -> list[dict[str, Any]]:
        with self._lock:
            if not self.path.exists():
                return []
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                rows = raw.get("tasks", []) if isinstance(raw, dict) else raw
                return [dict(x) for x in rows if isinstance(x, dict)] if isinstance(rows, list) else []
            except Exception:
                return []

    def _save(self, rows: list[dict[str, Any]]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps({"version": 1, "tasks": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.path)

    def add_listener(self, callback: Callable[[], None]) -> None:
        if callable(callback) and callback not in self._listeners:
            self._listeners.append(callback)

    def add_notifier(self, callback: Callable[[dict[str, Any]], None]) -> None:
        if callable(callback) and callback not in self._notifiers:
            self._notifiers.append(callback)

    def set_executor(self, callback: Callable[[str, dict[str, Any]], str]) -> None:
        """Bind the app's real action registry for durable workflow steps."""
        if callable(callback):
            self._executor = callback
            self._launch_pending_workflows()

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
             notify_message: str, expires_at: float) -> dict[str, Any]:
        now = time.time()
        rec = {
            "id": f"long-{uuid.uuid4().hex[:10]}",
            "kind": "long_task",
            "title": str(title or "Long-term task").strip()[:120],
            "condition": condition,
            "target": target,
            "notify_message": str(notify_message or "Task completed.").strip()[:500],
            "status": "waiting",
            "created_at": now,
            "updated_at": now,
            "created_iso": _now_iso(now),
            "expires_at": float(expires_at),
            "completed_at": None,
            "completion_evidence": None,
            "notified_at": None,
            "notification_channel": None,
            "events": [],
        }
        with self._lock:
            rows = self._load()
            rows.append(rec)
            self._save(rows[-200:])
        self.start()
        self._changed()
        return dict(rec)

    def create_media(self, video: dict[str, Any], *, scope: str = "item",
                     notify_message: str = "", max_wait_hours: float = 24.0) -> dict[str, Any]:
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
        )

    def create_deadline(self, run_at: float, *, title: str = "Scheduled task",
                        notify_message: str = "", max_wait_hours: float = 24 * 365) -> dict[str, Any]:
        run_at = float(run_at)
        if run_at <= time.time():
            raise ValueError("The completion time must be in the future.")
        return self._new(
            title=title, condition="time", target={"run_at": run_at, "run_at_iso": _now_iso(run_at)},
            notify_message=notify_message or f"{title} is due.",
            expires_at=run_at + max(1.0, max_wait_hours) * 3600,
        )

    def create_file(self, path: str, *, changed: bool = False, title: str = "",
                    notify_message: str = "", max_wait_hours: float = 24 * 7) -> dict[str, Any]:
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
        )

    def create_workflow(self, steps: list[dict[str, Any]], *, title: str = "Long-running workflow",
                        notify_message: str = "", max_wait_hours: float = 24 * 7) -> dict[str, Any]:
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
            normalized.append({
                "index": index, "tool": tool, "params": params,
                "status": "queued", "attempts": 0,
                "started_at": None, "completed_at": None,
                "output": None, "error": None, "execution_id": None,
            })
        rec = self._new(
            title=title, condition="workflow",
            target={"steps": normalized, "current_step": 0},
            notify_message=notify_message or f"Workflow finished: {title}",
            expires_at=time.time() + max(1.0, min(max_wait_hours, 24 * 365)) * 3600,
        )
        self._launch_workflow(str(rec["id"]))
        return self.get(str(rec["id"])) or rec

    def list(self, include_finished: bool = True) -> list[dict[str, Any]]:
        rows = self._load()
        if not include_finished:
            rows = [x for x in rows if x.get("status") not in _TERMINAL]
        return sorted(rows, key=lambda x: float(x.get("created_at") or 0), reverse=True)

    def get(self, task_id: str) -> dict[str, Any] | None:
        return next((x for x in self._load() if x.get("id") == task_id), None)

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
                "status": "in_progress" if status == "waiting" else status,
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
                    rec["status"] = "needs_review"
                    rec["completion_evidence"] = interrupted["error"]
                    rec["updated_at"] = time.time()
                    changed = True
                elif rec.get("status") in ("running", "waiting"):
                    rec["status"] = "waiting"
                    changed = True
            if changed:
                self._save(rows)
        if changed:
            self._changed()

    def _launch_pending_workflows(self) -> None:
        for rec in self.list(include_finished=False):
            if rec.get("condition") == "workflow" and rec.get("status") == "waiting":
                self._launch_workflow(str(rec.get("id") or ""))

    def _launch_workflow(self, task_id: str) -> bool:
        if not task_id or self._executor is None:
            return False
        with self._lock:
            if task_id in self._workflow_threads:
                return False
            rec = self.get(task_id)
            if not rec or rec.get("condition") != "workflow" or rec.get("status") != "waiting":
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

    def _default_execute(self, tool: str, params: dict[str, Any]) -> str:
        from core.action_loader import discover_actions
        registry = discover_actions(BASE_DIR / "actions", logger=lambda _msg: None)
        if not registry.has(tool):
            raise ValueError(f"Tool '{tool}' is not a discoverable durable action.")
        return str(registry.run(tool, params, {"player": None, "speak": None}) or "Done.")

    def _run_workflow(self, task_id: str) -> None:
        try:
            while not self._stop.is_set():
                with self._lock:
                    rows = self._load()
                    rec = next((x for x in rows if x.get("id") == task_id), None)
                    if not rec or rec.get("status") in _TERMINAL or rec.get("status") == "needs_review":
                        return
                    target = rec.get("target") or {}
                    steps = target.get("steps") or []
                    queued = next((s for s in steps if s.get("status") == "queued"), None)
                    if queued is None:
                        break
                    completed = [dict(s) for s in steps if s.get("status") == "completed"]
                    queued["status"] = "running"
                    queued["attempts"] = int(queued.get("attempts") or 0) + 1
                    queued["started_at"] = time.time()
                    queued["execution_id"] = f"exec-{uuid.uuid4().hex[:10]}"
                    rec["status"] = "running"
                    rec["updated_at"] = time.time()
                    target["current_step"] = int(queued.get("index") or 1)
                    self._save(rows)  # checkpoint BEFORE any side effect
                    tool = str(queued.get("tool") or "")
                    params = self._resolve_workflow_params(dict(queued.get("params") or {}), completed)
                    execution_id = str(queued["execution_id"])
                self._changed()

                try:
                    executor = self._executor or self._default_execute
                    result = str(executor(tool, params) or "Done.")
                    result_low = result.strip().lower()
                    confirmation_pending = "[confirmation_pending]" in result_low
                    failed = result_low.startswith((
                        "tool '", "action '", "error", "failed", "could not", "unable to",
                    ))
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
                    step["completed_at"] = now
                    if confirmation_pending:
                        step["status"] = "uncertain"
                        step["error"] = result[:4000]
                        rec["status"] = "needs_review"
                        rec["completion_evidence"] = (
                            f"Step {step.get('index')} ({tool}) is waiting for the HUD confirmation. "
                            "After approving or rejecting it, resume with mark_done or retry."
                        )
                    elif failed:
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
                    rec["updated_at"] = now
                    self._save(rows)
                self._changed()
                if failed or confirmation_pending:
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

    def resolve_uncertain(self, task_id: str, resolution: str) -> bool:
        """Human recovery after a crash: retry explicitly or acknowledge done."""
        resolution = str(resolution or "").strip().lower()
        if resolution not in ("retry", "mark_done"):
            return False
        with self._lock:
            rows = self._load()
            rec = next((x for x in rows if x.get("id") == task_id), None)
            if not rec or rec.get("status") != "needs_review":
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

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            rows = self._load()
            found = False
            for rec in rows:
                if rec.get("id") == task_id and rec.get("status") not in _TERMINAL:
                    rec["status"] = "cancelled"
                    rec["updated_at"] = time.time()
                    rec["events"] = (list(rec.get("events") or []) + [{"ts": time.time(), "type": "cancelled"}])[-20:]
                    found = True
                    break
            if found:
                self._save(rows)
        if found:
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
                if rec.get("id") == task_id and rec.get("status") in ("waiting", "running"):
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
                    if rec.get("id") in expired and rec.get("status") == "waiting":
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
