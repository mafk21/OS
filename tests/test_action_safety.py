from __future__ import annotations

import json

from core import action_safety
from core.action_loader import ActionRecord, ActionRegistry
from core.plugin_loader import PluginRecord, PluginRegistry


def audit_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_every_action_runs_shared_lifecycle_without_logging_values(monkeypatch, tmp_path):
    audit = tmp_path / "audit.jsonl"
    monkeypatch.setattr(action_safety, "AUDIT_PATH", audit)
    private = "private-message-body"

    result = action_safety.execute(
        "read_only", {"query": private}, action_safety.ActionPolicy(), lambda: "observed",
    )

    assert result == "observed"
    rows = audit_rows(audit)
    assert [row["stage"] for row in rows] == ["understand", "plan", "execute", "verify", "report"]
    assert private not in audit.read_text(encoding="utf-8")
    assert rows[0]["parameter_keys"] == ["query"]


def test_high_risk_action_cannot_execute_before_human_confirmation(monkeypatch, tmp_path):
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    staged, calls = {}, []
    def request(key, title, detail, run):
        staged.update(key=key, title=title, detail=detail, run=run)
        return "[CONFIRMATION_PENDING]"
    monkeypatch.setattr(action_safety.confirm, "request", request)
    policy = action_safety.ActionPolicy("high", "external_communication", "required", True, False, "verified")

    response = action_safety.execute(
        "send_message", {"receiver": "Alex", "message_text": "private"},
        policy, lambda: calls.append("sent") or {"ok": True, "verified": True, "evidence": "message id"},
    )

    assert response == "[CONFIRMATION_PENDING]"
    assert calls == []
    assert "private" not in staged["detail"]
    staged["run"]()
    assert calls == ["sent"]


def test_missing_external_destination_fails_before_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    called = []
    policy = action_safety.ActionPolicy("high", "external_communication", "required", True)
    result = action_safety.execute("send_message", {"message_text": "hello"}, policy,
                                   lambda: called.append(True))
    assert "explicit recipient" in result
    assert called == []


def test_sensitive_parameter_elevates_to_confirmation(monkeypatch, tmp_path):
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    staged = []
    monkeypatch.setattr(action_safety.confirm, "request", lambda *args: staged.append(args) or "pending")
    result = action_safety.execute("configure", {"api_key": "secret-value"},
                                   action_safety.ActionPolicy(), lambda: "saved")
    assert result == "pending"
    assert staged
    assert "secret-value" not in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")


def test_unverified_result_is_not_reported_as_success(monkeypatch, tmp_path):
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    policy = action_safety.ActionPolicy(verification="verified")
    result = action_safety.execute("external", {}, policy, lambda: "probably done")
    assert "unverified" in result
    assert "Do not claim success" in result


def test_reversible_action_records_undo_availability(monkeypatch, tmp_path):
    from core import undo
    undo.clear()
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    def change():
        undo.push_undo("restore setting", lambda: "restored")
        return "changed"
    policy = action_safety.ActionPolicy("medium", "device_settings", "none", True, True)

    assert action_safety.execute("setting", {}, policy, change) == "changed"
    rows = audit_rows(tmp_path / "audit.jsonl")
    assert any(row["stage"] == "undo" and row["outcome"] == "available" for row in rows)
    undo.clear()


def test_action_registry_enforces_declared_safety(monkeypatch, tmp_path):
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    staged = []
    monkeypatch.setattr(action_safety.confirm, "request", lambda *args: staged.append(args) or "pending")
    rec = ActionRecord(
        name="send", description="send", parameters={"type": "OBJECT", "properties": {}},
        handler=lambda parameters: "sent", valid=True,
        safety={"risk": "high", "permission": "external_communication", "confirmation": "required"},
    )
    registry = ActionRegistry({"send": rec}, logger=lambda _msg: None)

    result = registry.run("send", {"receiver": "Alex"})

    assert result == "pending"
    assert staged


def test_plugin_registry_uses_same_safety_boundary(monkeypatch, tmp_path):
    import core.plugin_loader as loader
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(loader, "get_plugin_enabled", lambda _name: True)
    record = PluginRecord(
        name="sample_plugin", description="sample", parameters={"type": "OBJECT", "properties": {}},
        run=lambda parameters: "done", valid=True,
    )
    registry = PluginRegistry({"sample_plugin": record}, logger=lambda _msg: None)

    assert registry.run("sample_plugin", {}) == "done"
    assert {row["stage"] for row in audit_rows(tmp_path / "audit.jsonl")} == {
        "understand", "plan", "execute", "verify", "report",
    }
