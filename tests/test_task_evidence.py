from __future__ import annotations

import threading
import time

from core import long_tasks as lt
from core import task_evidence as evidence


def manager(tmp_path, monkeypatch):
    monkeypatch.setattr(lt, "desktop_notify", lambda *_: True)
    return lt.LongTaskManager(tmp_path / "tasks.json", poll_seconds=60)


def wait_for(mgr, task_id, states, timeout=2):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        row = mgr.get(task_id)
        if row and row.get("status") in states:
            return row
        time.sleep(.01)
    raise AssertionError(mgr.get(task_id))


def test_external_side_effect_requires_verified_evidence(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    mgr.set_executor(lambda *_: "message probably sent")
    rec = mgr.create_workflow([{"tool": "send_message", "params": {}}])

    uncertain = wait_for(mgr, rec["id"], {"uncertain"})
    mgr.stop()

    step = uncertain["target"]["steps"][0]
    assert step["evidence_requirement"] == "verified"
    assert step["verification_state"] == "observed"
    assert "did not satisfy" in uncertain["completion_evidence"]


def test_structured_verified_result_completes_external_step(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    mgr.set_executor(lambda *_: {
        "ok": True, "verified": True, "authoritative": True,
        "evidence": "Provider returned message identifier.", "evidence_reference": "message:42",
    })
    rec = mgr.create_workflow([{"tool": "send_message", "params": {}}])

    done = wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()

    step = done["target"]["steps"][0]
    assert step["verification_state"] == "verified"
    assert step["evidence"]["reference"] == "message:42"
    assert "[verified]" in done["completion_evidence"]


def test_authoritative_failure_overrides_success_wording():
    record = evidence.from_result(
        {"ok": False, "summary": "successfully sent"}, tool="send_message", started_at=time.time() - 1
    )
    assert record.state == "contradicted"
    assert record.authoritative is True
    assert "successfully sent" not in record.summary


def test_stale_evidence_is_rejected():
    started = time.time()
    record = evidence.from_result(
        {"ok": True, "verified": True, "verified_at": started - 30, "evidence": "old"},
        tool="send_message", started_at=started,
    )
    assert record.state == "uncertain"
    assert not evidence.satisfies(record, "verified")


def test_deterministic_postcondition_can_verify_result(tmp_path, monkeypatch):
    output = tmp_path / "result.txt"
    mgr = manager(tmp_path, monkeypatch)
    def execute(*_):
        output.write_text("done", encoding="utf-8")
        return "created"
    mgr.set_executor(execute)
    rec = mgr.create_workflow([{
        "tool": "code_helper", "params": {}, "evidence_requirement": "verified",
        "postcondition": {"type": "file_exists", "path": str(output)},
    }])

    done = wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert done["target"]["steps"][0]["evidence"]["source"] == "postcondition"


def test_observable_monitor_completion_has_authoritative_evidence_record(tmp_path, monkeypatch):
    mgr = manager(tmp_path, monkeypatch)
    watched = tmp_path / "ready.txt"
    rec = mgr.create_file(str(watched))
    watched.write_text("ready", encoding="utf-8")
    mgr.tick_once()
    done = mgr.get(rec["id"])
    assert done["status"] == "completed"
    assert done["completion_evidence_record"]["state"] == "verified"
    assert done["completion_evidence_record"]["authoritative"] is True
