from __future__ import annotations

import json
import time

import pytest

from core import long_tasks as lt


def _manager(tmp_path, monkeypatch):
    monkeypatch.setattr(lt, "desktop_notify", lambda *_: True)
    return lt.LongTaskManager(tmp_path / "long_tasks.json", poll_seconds=60)


def _wait_for(mgr, task_id, statuses, timeout=3):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        rec = mgr.get(task_id)
        if rec and rec.get("status") in statuses:
            return rec
        time.sleep(0.01)
    raise AssertionError(f"task {task_id} did not reach {statuses}: {mgr.get(task_id)}")


def test_corrupt_store_is_never_silently_replaced(tmp_path, monkeypatch):
    path = tmp_path / "long_tasks.json"
    path.write_text("{ definitely broken", encoding="utf-8")
    mgr = lt.LongTaskManager(path)

    with pytest.raises(RuntimeError, match="storage is unreadable"):
        mgr.create_deadline(time.time() + 60, title="must not overwrite")

    assert path.read_text(encoding="utf-8") == "{ definitely broken"


def test_last_valid_backup_recovers_readable_tasks(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    first = mgr.create_deadline(time.time() + 60, title="first")
    mgr.stop()
    second = mgr.create_deadline(time.time() + 120, title="second")
    mgr.stop()
    assert mgr.path.with_suffix(".json.bak").exists()

    mgr.path.write_text("not json", encoding="utf-8")
    recovered = lt.LongTaskManager(mgr.path)
    rows = recovered.list()
    assert [row["id"] for row in rows] == [first["id"]]
    assert all(row["id"] != second["id"] for row in rows)


def test_idempotency_key_prevents_duplicate_workflows(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    steps = [{"tool": "safe", "params": {}}]
    one = mgr.create_workflow(steps, idempotency_key="request-42")
    two = mgr.create_workflow(steps, idempotency_key="request-42")
    mgr.stop()

    assert one["id"] == two["id"]
    assert len(mgr.list()) == 1


def test_automatic_retry_requires_explicit_retry_safe_and_uses_backoff(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="not marked retry_safe"):
        mgr.create_workflow([{"tool": "send", "params": {}, "max_attempts": 2}])

    calls = []
    def execute(tool, params):
        calls.append(tool)
        if len(calls) == 1:
            return "Error: temporary failure"
        return "verified output"

    mgr.set_executor(execute)
    rec = mgr.create_workflow([{
        "tool": "read_only_check", "params": {}, "max_attempts": 2,
        "retry_safe": True, "retry_delay_seconds": 0,
    }])
    done = _wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()

    step = done["target"]["steps"][0]
    assert calls == ["read_only_check", "read_only_check"]
    assert step["attempts"] == 2
    assert step["status"] == "completed"
    assert any(event["type"] == "step_retry_scheduled" for event in done["events"])


def test_failed_workflow_can_be_retried_only_by_explicit_request(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    outcomes = iter(["Failed: first attempt", "completed with evidence"])
    mgr.set_executor(lambda *_: next(outcomes))
    rec = mgr.create_workflow([{"tool": "manual_step", "params": {}}])
    failed = _wait_for(mgr, rec["id"], {"failed"})
    assert failed["target"]["steps"][0]["status"] == "failed"

    assert mgr.retry_failed(rec["id"])
    done = _wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert done["target"]["steps"][0]["attempts"] == 2
    assert any(event["type"] == "failed_step_retry_requested" for event in done["events"])


def test_retention_prunes_terminal_history_but_never_active_tasks(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    now = time.time()
    active = [{
        "id": f"active-{i}", "status": "waiting", "created_at": now + i,
        "updated_at": now + i, "condition": "time", "target": {},
    } for i in range(4)]
    terminal = [{
        "id": f"done-{i}", "status": "completed", "created_at": i,
        "updated_at": i, "condition": "time", "target": {},
    } for i in range(lt._MAX_TASKS - 3)]
    mgr._save(active + terminal)

    created = mgr.create_deadline(now + 60, title="new active")
    mgr.stop()
    rows = mgr.list()
    ids = {row["id"] for row in rows}
    assert len(rows) == lt._MAX_TASKS
    assert {row["id"] for row in active}.issubset(ids)
    assert created["id"] in ids
    assert "done-0" not in ids


def test_structured_executor_failure_is_not_misreported_as_success(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    mgr.set_executor(lambda *_: {"ok": False, "error": "provider rejected request"})
    rec = mgr.create_workflow([{"tool": "structured", "params": {}}])
    failed = _wait_for(mgr, rec["id"], {"failed"})
    mgr.stop()
    assert failed["target"]["steps"][0]["status"] == "failed"
    assert "provider rejected" in failed["completion_evidence"]


def test_store_writes_current_schema_version(tmp_path, monkeypatch):
    mgr = _manager(tmp_path, monkeypatch)
    mgr.create_deadline(time.time() + 60, title="schema")
    mgr.stop()
    payload = json.loads(mgr.path.read_text(encoding="utf-8"))
    assert payload["version"] == lt._STORE_VERSION
