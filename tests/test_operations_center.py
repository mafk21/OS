import json
from core import operations_center as ops


def test_snapshot_is_aggregate_and_privacy_bounded(monkeypatch, tmp_path):
    monkeypatch.setattr(ops, "ROOT", tmp_path)
    config = tmp_path / "config"; config.mkdir()
    private = "private-message-body"
    (config / "action_audit.jsonl").write_text(json.dumps({"stage": "report", "outcome": "unverified", "private": private}) + "\n", encoding="utf-8")
    snap = ops.snapshot()
    assert snap["actions"] == {"unverified": 1}
    assert snap["privacy"] == "aggregate_metadata_only"
    assert private not in json.dumps(snap)
    assert set(snap) == {"ok", "tasks", "actions", "timeline", "memory_conflicts", "providers", "local_voice", "owner_auth", "proactive", "privacy"}
