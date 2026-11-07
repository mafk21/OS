from __future__ import annotations

import json
import threading
import time

from core import long_tasks as lt


def manager(tmp_path, monkeypatch):
    monkeypatch.setattr(lt, "desktop_notify", lambda *_: True)
    return lt.LongTaskManager(tmp_path / "tasks.json", poll_seconds=60)


def wait_for(mgr, task_id, statuses, timeout=3):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        row = mgr.get(task_id)
        if row and row.get("status") in statuses:
            return row
        time.sleep(.01)
    raise AssertionError(mgr.get(task_id))


def test_pause_checkpoint_revise_and_resume(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    entered, release = threading.Event(), threading.Event()
    calls = []
    def execute(tool, params):
        calls.append((tool, params))
        if tool == "first":
            entered.set(); release.wait(2)
        return "verified"
    mgr.set_executor(execute)
    rec = mgr.create_workflow([
        {"tool": "first", "params": {}},
        {"tool": "old", "params": {"value": 1}},
    ])
    assert entered.wait(1)
    assert mgr.pause(rec["id"])
    release.set()
    paused = wait_for(mgr, rec["id"], {"paused"})
    assert paused["target"]["steps"][0]["status"] == "completed"
    assert paused["target"]["steps"][1]["status"] == "queued"
    assert mgr.revise_step(rec["id"], 2, {"tool": "new", "params": {"value": 2}, "timeout_seconds": 5})
    assert mgr.resume(rec["id"])
    done = wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert calls == [("first", {}), ("new", {"value": 2})]
    assert any(event["type"] == "step_revised" for event in done["events"])


def test_timeout_becomes_uncertain_and_propagates_cancellation(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    cancelled = []
    blocker = threading.Event()
    mgr.set_cancel_executor(cancelled.append)
    mgr.set_executor(lambda *_: blocker.wait(5) or "late")
    rec = mgr.create_workflow([{"tool": "slow_side_effect", "params": {}, "timeout_seconds": 1}])
    uncertain = wait_for(mgr, rec["id"], {"uncertain"}, timeout=2.5)
    blocker.set(); mgr.stop()
    assert cancelled
    assert uncertain["target"]["steps"][0]["status"] == "uncertain"
    assert "may have occurred" in uncertain["completion_evidence"]
    assert any(event["type"] == "step_timed_out" for event in uncertain["events"])


def test_cancel_propagates_running_execution_id(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    entered, release = threading.Event(), threading.Event()
    propagated = []
    mgr.set_cancel_executor(propagated.append)
    mgr.set_executor(lambda *_: entered.set() or release.wait(2) or "late")
    rec = mgr.create_workflow([{"tool": "child_process", "params": {}}])
    assert entered.wait(1)
    assert mgr.cancel(rec["id"])
    release.set(); mgr.stop()
    assert propagated and propagated[0].startswith("exec-")
    assert mgr.get(rec["id"])["status"] == "cancelled"


def test_executor_receives_cooperative_cancellation_context(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    entered, observed = threading.Event(), threading.Event()
    def execute(_tool, _params, context):
        entered.set()
        if context["cancellation_event"].wait(2): observed.set()
        return "stopped"
    mgr.set_executor(execute)
    rec = mgr.create_workflow([{"tool": "cooperative", "params": {}}])
    assert entered.wait(1)
    assert mgr.cancel(rec["id"])
    assert observed.wait(1)
    mgr.stop()


def test_verified_failure_selects_predeclared_safe_alternative(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    calls = []
    def execute(tool, _params):
        calls.append(tool)
        return "Error: primary unavailable" if tool == "primary" else "verified fallback"
    mgr.set_executor(execute)
    rec = mgr.create_workflow([{
        "tool": "primary", "params": {}, "fallback_safe": True,
        "alternatives": [{"tool": "fallback", "params": {}}],
    }])
    done = wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert calls == ["primary", "fallback"]
    assert done["target"]["steps"][0]["strategy_index"] == 1
    assert any(event["type"] == "alternative_strategy_selected" for event in done["events"])


def test_v2_store_migrates_states_and_step_defaults(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({"version": 2, "tasks": [{
        "id": "old", "condition": "workflow", "status": "needs_review",
        "target": {"steps": [{"index": 1, "tool": "x", "params": {}, "status": "uncertain"}]},
    }]}), encoding="utf-8")
    row = lt.LongTaskManager(path).get("old")
    assert row["status"] == "uncertain"
    assert row["target"]["steps"][0]["timeout_seconds"] == 300
    assert row["target"]["steps"][0]["strategies"] == []
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 3
