"""Phase 3 — Productivity Core — offline unit tests."""
import pathlib, tempfile, os

def test_tasks_crud():
    import memory.productivity as prod
    # isolate: use temp DB path via monkeypatch not available, so test against real DB but clean up
    t = prod.add_task(title="Test task phase3", due="tomorrow", priority="high")
    assert t["id"] > 0
    tid = t["id"]
    lst = prod.list_tasks(status="open")
    assert any(x["id"] == tid for x in lst["tasks"])
    s = prod.search_tasks("phase3")
    assert any(x["id"] == tid for x in s["tasks"])
    prod.complete_task(tid)
    lst2 = prod.list_tasks(status="done")
    assert any(x["id"] == tid for x in lst2["tasks"])
    prod.reopen_task(tid)
    prod.archive_task(tid, True)
    prod.archive_task(tid, False)
    prod.delete_task(tid)
    # verify deleted
    lst3 = prod.search_tasks("phase3")
    assert not any(x["id"] == tid for x in lst3["tasks"])

def test_notes_crud():
    import memory.productivity as prod
    n = prod.add_note(title="Test note", content="hello phase3 content", tags="test")
    nid = n["id"]
    lst = prod.list_notes()
    assert any(x["id"] == nid for x in lst["notes"])
    s = prod.search_notes("phase3")
    assert any(x["id"] == nid for x in s["notes"])
    one = prod.get_note(nid)
    assert one and one["id"] == nid
    prod.archive_note(nid, True)
    prod.archive_note(nid, False)
    prod.delete_note(nid)

def test_routines_crud():
    import memory.productivity as prod
    r = prod.add_routine(name="TestRoutine", trigger="test trigger", steps=["step1","step2"])
    assert r["name"] == "TestRoutine"
    lst = prod.list_routines()
    assert any(x["name"] == "TestRoutine" for x in lst)
    got = prod.get_routine_by_trigger("test trigger")
    assert got and got["name"] == "TestRoutine"
    prod.delete_routine("TestRoutine")
    assert not prod.get_routine_by_trigger("test trigger")

def test_checkpoints_crud():
    import memory.productivity as prod, tempfile, pathlib
    tmp = tempfile.mkdtemp()
    cp = prod.create_checkpoint(name="TestCP", paths=[tmp], note="test")
    cid = cp["id"]
    lst = prod.list_checkpoints()
    assert any(x["id"] == cid for x in lst)
    got = prod.get_checkpoint(cid)
    assert got and got["name"] == "TestCP"
    res = prod.restore_checkpoint(cid, dry_run=True)
    assert res["checkpoint"]["id"] == cid
    prod.delete_checkpoint(cid)

def test_lecture_capture():
    import memory.productivity as prod
    # start, append, status, stop
    s = prod.lecture_start("Test Lecture")
    assert "session_id" in s
    st = prod.lecture_status()
    assert st["active"] is True
    prod.lecture_append("Hello lecture line 1")
    prod.lecture_append("Line 2")
    res = prod.lecture_stop(summarize=False)
    assert res["transcript_chars"] > 0
    st2 = prod.lecture_status()
    assert st2["active"] is False

def test_actions_exist():
    for name in ["productivity_tasks.py","productivity_notes.py","productivity_routines.py","productivity_checkpoints.py","lecture_notes.py"]:
        assert (pathlib.Path(f"actions/{name}")).exists()
    import actions.productivity_tasks as at
    assert hasattr(at, "TOOL") and at.TOOL["name"] == "manage_tasks"
