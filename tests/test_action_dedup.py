from __future__ import annotations

import json
import threading

from core import action_dedup, action_safety


def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(action_dedup, "STORE_PATH", tmp_path / "guard.json")
    monkeypatch.setattr(action_dedup, "KEY_PATH", tmp_path / ".key")
    monkeypatch.setattr(action_safety, "AUDIT_PATH", tmp_path / "audit.jsonl")


def policy(**changes):
    values = dict(risk="high", permission="external_service", confirmation="none",
                  side_effect=True, reversible=False, verification="observed", idempotency="window")
    values.update(changes)
    return action_safety.ActionPolicy(**values)


def test_matching_consequential_action_requires_human_confirmation(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    calls = []
    params = {"receiver": "private-person", "message_text": "private-message"}
    assert action_safety.execute("send", params, policy(), lambda: calls.append(1) or "sent") == "sent"

    staged = []
    monkeypatch.setattr(action_safety.confirm, "request", lambda key, title, detail, run: staged.append((title, detail, run)) or "pending")
    assert action_safety.execute("send", params, policy(), lambda: calls.append(2) or "sent") == "pending"
    assert calls == [1]
    assert staged[0][0] == "Repeat send?"

    assert staged[0][2]() == "sent"
    assert calls == [1, 2]


def test_guard_store_contains_no_parameter_values_or_results(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    private = "never-store-this-message"
    action_safety.execute("send", {"receiver": "secret-recipient", "message": private}, policy(), lambda: "private-result")

    raw = action_dedup.STORE_PATH.read_text(encoding="utf-8")
    assert private not in raw
    assert "secret-recipient" not in raw
    assert "private-result" not in raw
    row = json.loads(raw)["records"][0]
    assert set(row) == {"fingerprint", "state", "at"}


def test_atomic_reservation_blocks_racing_duplicate(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    token = action_dedup.fingerprint("pay", {"invoice": "42"})
    barrier = threading.Barrier(3)
    outcomes = []

    def claim():
        barrier.wait()
        outcomes.append(action_dedup.reserve(token))

    threads = [threading.Thread(target=claim) for _ in range(2)]
    for thread in threads: thread.start()
    barrier.wait()
    for thread in threads: thread.join()
    assert sorted(outcomes) == [False, True]


def test_uncertain_outcome_is_not_automatically_replayed(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    params = {"target": "remote-job"}
    try:
        action_safety.execute("launch", params, policy(), lambda: (_ for _ in ()).throw(RuntimeError("lost response")))
    except RuntimeError:
        pass

    staged = []
    monkeypatch.setattr(action_safety.confirm, "request", lambda key, title, detail, run: staged.append(detail) or "pending")
    assert action_safety.execute("launch", params, policy(), lambda: "done") == "pending"
    assert "recently uncertain" in staged[0]


def test_corrupt_or_keyless_store_blocks_instead_of_replaying(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    action_dedup.STORE_PATH.write_text("not-json", encoding="utf-8")
    try:
        action_dedup.inspect("pay", {"invoice": "42"})
        raise AssertionError("corruption must fail closed")
    except RuntimeError as exc:
        assert "blocked" in str(exc)
    action_dedup.STORE_PATH.write_text('{"version":1,"records":[]}', encoding="utf-8")
    action_dedup.KEY_PATH.unlink(missing_ok=True)
    try:
        action_dedup.fingerprint("pay", {})
        raise AssertionError("missing key with existing ledger must fail closed")
    except RuntimeError as exc:
        assert "blocked" in str(exc)


def test_low_risk_read_only_actions_are_not_suppressed(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    calls = []
    read_policy = action_safety.ActionPolicy()
    for _ in range(2):
        assert action_safety.execute("read", {"query": "same"}, read_policy, lambda: calls.append(1) or "result") == "result"
    assert len(calls) == 2
    assert not action_dedup.STORE_PATH.exists()
