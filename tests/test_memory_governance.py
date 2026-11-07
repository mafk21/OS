from datetime import datetime, timezone
from memory import memory_governance as gov
from memory import memory_manager as mm


def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory.json")


def test_conflicting_fact_is_quarantined_from_prompt(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    mm.remember("city", "Riyadh", "identity", manual=True)
    mm.remember("city", "Jeddah", "identity", manual=True)
    entry = mm.load_memory()["identity"]["city"]
    assert entry["status"] == "conflicted"
    assert entry["confidence"] == 0.5
    assert "Jeddah" not in mm.format_memory_for_prompt(mm.load_memory())
    assert gov.conflicts()[0]["alternatives"][0]["value"] == "Riyadh"


def test_user_resolution_restores_authoritative_fact(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    mm.remember("city", "Riyadh", "identity", manual=True)
    mm.remember("city", "Jeddah", "identity", manual=True)
    assert "Resolved" in gov.resolve("identity", "city", "Hafar Al-Batin")
    entry = mm.load_memory()["identity"]["city"]
    assert entry["status"] == "active" and entry["confidence"] == 1.0
    assert entry["provenance"][-1]["source"] == "explicit_user_resolution"


def test_user_retention_expiry_is_enforced(monkeypatch, tmp_path):
    isolate(monkeypatch, tmp_path)
    mm.remember("temporary", "value", manual=True)
    gov.set_expiry("notes", "temporary", "2020-01-01T00:00:00+00:00")
    assert gov.enforce_explicit_retention(datetime.now(timezone.utc)) == ["notes/temporary"]
    assert "temporary" not in mm.load_memory()["notes"]
