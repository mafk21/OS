from __future__ import annotations

import json
import time
from pathlib import Path

from core import long_tasks as lt


def manager(tmp_path, monkeypatch):
    notices = []
    monkeypatch.setattr(lt, "desktop_notify", lambda title, message: notices.append((title, message)) or True)
    mgr = lt.LongTaskManager(tmp_path / "long_tasks.json", poll_seconds=60)
    mgr.add_notifier(lambda task: notices.append((task["id"], task["status"])))
    return mgr, notices


def test_media_task_requires_real_matching_ended_event_and_deduplicates(tmp_path, monkeypatch):
    mgr, notices = manager(tmp_path, monkeypatch)
    video = {
        "id": "vid-1", "title": "Launch Film", "webpage_url": "https://example/video",
        "playlist_url": "", "queue_total": 0,
    }
    rec = mgr.create_media(video, notify_message="The film is done.")
    mgr.stop()
    assert mgr.get(rec["id"])["status"] == "waiting"
    assert mgr.signal_media_ended({"video_id": "wrong", "terminal": True}) == []
    assert notices == []

    assert mgr.signal_media_ended({"video_id": "vid-1", "webpage_url": "https://example/video", "terminal": True}) == [rec["id"]]
    done = mgr.get(rec["id"])
    assert done["status"] == "completed"
    assert "player reported" in done["completion_evidence"].lower()
    assert done["notified_at"]
    assert len(notices) == 2  # one desktop delivery + one app callback
    assert mgr.signal_media_ended({"video_id": "vid-1", "terminal": True}) == []
    assert len(notices) == 2


def test_playlist_waits_for_final_item(tmp_path, monkeypatch):
    mgr, _ = manager(tmp_path, monkeypatch)
    rec = mgr.create_media({
        "id": "first", "title": "One", "playlist_title": "My Mix",
        "playlist_url": "https://example/list", "queue_total": 3,
    }, scope="queue")
    mgr.stop()
    event = {"video_id": "second", "playlist_url": "https://example/list", "terminal": False}
    assert mgr.signal_media_ended(event) == []
    assert mgr.get(rec["id"])["status"] == "waiting"
    event["terminal"] = True
    assert mgr.signal_media_ended(event) == [rec["id"]]


def test_deadline_and_file_monitors_survive_manager_restart(tmp_path, monkeypatch):
    mgr, _ = manager(tmp_path, monkeypatch)
    future = time.time() + 20
    deadline = mgr.create_deadline(future, title="Tea")
    target = tmp_path / "render.mp4"
    file_task = mgr.create_file(str(target))
    mgr.stop()

    restored, notices = manager(tmp_path, monkeypatch)
    assert {x["id"] for x in restored.list(include_finished=False)} == {deadline["id"], file_task["id"]}
    target.write_bytes(b"real output")
    completed = restored.tick_once(now=future + 1)
    assert set(completed) == {deadline["id"], file_task["id"]}
    assert all(restored.get(task_id)["status"] == "completed" for task_id in completed)
    assert len(notices) == 4


def test_file_change_uses_real_stat_change_and_cancel_is_terminal(tmp_path, monkeypatch):
    mgr, _ = manager(tmp_path, monkeypatch)
    path = tmp_path / "build.log"
    path.write_text("start")
    changed = mgr.create_file(str(path), changed=True)
    cancelled = mgr.create_deadline(time.time() + 50, title="Cancel me")
    mgr.stop()
    assert mgr.tick_once() == []
    path.write_text("finished")
    assert mgr.tick_once() == [changed["id"]]
    assert mgr.cancel(cancelled["id"])
    assert mgr.get(cancelled["id"])["status"] == "cancelled"
    assert not mgr.cancel(cancelled["id"])
    assert mgr.remove(cancelled["id"])


def test_expiry_never_claims_completion_or_notifies(tmp_path, monkeypatch):
    mgr, notices = manager(tmp_path, monkeypatch)
    rec = mgr.create_media({"id": "v", "title": "Never ends"}, max_wait_hours=1)
    mgr.stop()
    mgr.tick_once(now=rec["expires_at"] + 1)
    expired = mgr.get(rec["id"])
    assert expired["status"] == "expired"
    assert "expired" in expired["completion_evidence"].lower()
    assert notices == []


def test_completed_notification_retries_when_no_delivery_channel_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(lt, "desktop_notify", lambda *_: False)
    mgr = lt.LongTaskManager(tmp_path / "long_tasks.json", poll_seconds=60)
    rec = mgr.create_deadline(time.time() + 10, title="Retry notice")
    mgr.stop()
    mgr.tick_once(now=time.time() + 11)
    assert mgr.get(rec["id"])["status"] == "completed"
    assert mgr.get(rec["id"])["notified_at"] is None
    delivered = []
    mgr.add_notifier(lambda task: delivered.append(task["id"]))
    mgr.deliver_pending_notifications()
    assert delivered == [rec["id"]]
    assert mgr.get(rec["id"])["notification_channel"] == "app"


def test_action_contract_and_hud_event_wiring_are_discoverable():
    from actions.long_task import TOOL
    assert TOOL["name"] == "long_task"
    assert "actual ended event" in TOOL["description"]
    hud = Path("apex_ui/components/HudVideoModal.tsx").read_text()
    bridge = Path("core/apex_bridge.py").read_text()
    assert 'action: "video_ended"' in hud
    assert "onEnded" in hud and "reportEnded();" in hud
    assert 'if action == "video_ended":' in bridge
    assert "signal_media_ended" in bridge


def _wait_for(mgr, task_id, statuses, timeout=3):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        rec = mgr.get(task_id)
        if rec and rec.get("status") in statuses:
            return rec
        time.sleep(0.01)
    raise AssertionError(f"task {task_id} did not reach {statuses}: {mgr.get(task_id)}")


def test_durable_workflow_executes_real_steps_checkpoints_and_chains_output(tmp_path, monkeypatch):
    mgr, notices = manager(tmp_path, monkeypatch)
    calls = []
    def execute(tool, params):
        calls.append((tool, params))
        return "alpha" if tool == "first" else f"received={params['value']}"
    mgr.set_executor(execute)
    rec = mgr.create_workflow([
        {"tool": "first", "params": {"query": "go"}},
        {"tool": "second", "params": {"value": "${previous.output}"}},
    ], title="Real workflow")
    done = _wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert calls == [("first", {"query": "go"}), ("second", {"value": "alpha"})]
    steps = done["target"]["steps"]
    assert [s["status"] for s in steps] == ["completed", "completed"]
    assert all(s["execution_id"] and s["started_at"] and s["completed_at"] for s in steps)
    assert steps[1]["output"] == "received=alpha"
    assert done["notified_at"] and len(notices) == 2


def test_workflow_failure_is_real_and_stops_later_steps(tmp_path, monkeypatch):
    mgr, notices = manager(tmp_path, monkeypatch)
    calls = []
    mgr.set_executor(lambda tool, params: calls.append(tool) or ("Tool 'bad' failed: real failure" if tool == "bad" else "should not run"))
    rec = mgr.create_workflow([
        {"tool": "bad", "params": {}}, {"tool": "later", "params": {}},
    ])
    failed = _wait_for(mgr, rec["id"], {"failed"})
    mgr.stop()
    assert calls == ["bad"]
    assert failed["target"]["steps"][0]["status"] == "failed"
    assert failed["target"]["steps"][1]["status"] == "queued"
    assert notices == []  # failure is not misreported as successful completion


def test_confirmation_pending_pauses_workflow_instead_of_claiming_success(tmp_path, monkeypatch):
    mgr, notices = manager(tmp_path, monkeypatch)
    calls = []
    mgr.set_executor(lambda tool, params: calls.append(tool) or "[CONFIRMATION_PENDING] Approve this in the HUD.")
    rec = mgr.create_workflow([
        {"tool": "dangerous", "params": {}}, {"tool": "later", "params": {}},
    ])
    review = _wait_for(mgr, rec["id"], {"uncertain"})
    mgr.stop()
    assert calls == ["dangerous"]
    assert review["target"]["steps"][0]["status"] == "uncertain"
    assert review["target"]["steps"][1]["status"] == "queued"
    assert notices == []


def test_restart_does_not_repeat_uncertain_side_effect_without_user_resolution(tmp_path, monkeypatch):
    mgr, _ = manager(tmp_path, monkeypatch)
    rec = mgr.create_workflow([{"tool": "send_something", "params": {"to": "person"}}])
    mgr.stop()
    # Simulate a process crash after the pre-side-effect checkpoint.
    rows = mgr._load()
    rows[0]["status"] = "running"
    rows[0]["target"]["steps"][0].update({"status": "running", "execution_id": "exec-crashed"})
    mgr._save(rows)

    restored, _ = manager(tmp_path, monkeypatch)
    calls = []
    restored.set_executor(lambda tool, params: calls.append(tool) or "sent")
    restored.start()
    review = restored.get(rec["id"])
    assert review["status"] == "uncertain"
    assert review["target"]["steps"][0]["status"] == "uncertain"
    assert calls == []
    assert restored.resolve_uncertain(rec["id"], "mark_done")
    done = _wait_for(restored, rec["id"], {"completed"})
    restored.stop()
    assert calls == []
    assert done["status"] == "completed"


def test_workflow_waits_for_app_executor_instead_of_running_without_context(tmp_path, monkeypatch):
    mgr, _ = manager(tmp_path, monkeypatch)
    rec = mgr.create_workflow([{"tool": "needs_ui", "params": {}}])
    time.sleep(0.03)
    assert mgr.get(rec["id"])["status"] == "blocked"
    calls = []
    mgr.set_executor(lambda tool, params: calls.append(tool) or "done")
    done = _wait_for(mgr, rec["id"], {"completed"})
    mgr.stop()
    assert calls == ["needs_ui"] and done["status"] == "completed"


def test_bridge_end_to_end_completes_bound_media_monitor(tmp_path, monkeypatch):
    from core.apex_bridge import ApexHudBridge
    monkeypatch.setattr(lt, "desktop_notify", lambda *_: True)
    durable = lt.LongTaskManager(tmp_path / "long_tasks.json", poll_seconds=60)
    monkeypatch.setattr(lt, "_MANAGER", durable)
    bridge = ApexHudBridge(ui_ref=None)
    bridge.push_video("https://cdn.example/video.mp4", title="Observed", webpage_url="https://example/watch")
    video = bridge.current_video_snapshot()
    rec = durable.create_media(video)
    durable.stop()
    result = bridge.handle_action({
        "action": "video_ended", "video_id": video["id"],
        "webpage_url": video["webpage_url"], "terminal": True,
    })
    assert result == {"ok": True, "completed_tasks": [rec["id"]]}
    assert durable.get(rec["id"])["status"] == "completed"
    assert any("LONG TASK COMPLETE" in line for line in bridge._logs)


def test_storage_is_private_runtime_data():
    ignored = __import__("subprocess").run(
        ["git", "check-ignore", "--no-index", "memory/long_tasks.json"],
        capture_output=True, text=True,
    )
    assert ignored.returncode == 0
