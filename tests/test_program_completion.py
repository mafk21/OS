import json
from pathlib import Path
from core import provider_routing, proactive_permissions, reliability_evaluation, skill_governance
from memory import memory_governance, memory_manager


def test_provider_routing_preferences_are_durable(monkeypatch, tmp_path):
    from core import provider_preferences
    from memory import config_manager as cfg
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config.json")
    assert provider_preferences.save("lowest", "fastest")["cost_priority"] == "lowest"
    assert provider_preferences.get()["latency_priority"] == "fastest"


def test_provider_cost_latency_and_user_override():
    available = {"gemini", "openai", "local"}
    low = provider_routing.ProviderRequest(cost_priority="lowest")
    assert provider_routing.route("auto", low, available)[0] == "local"
    override = provider_routing.ProviderRequest(provider_override="openai")
    assert provider_routing.route("auto", override, available) == ["openai"]


def test_memory_inspect_edit_pin_export_delete(monkeypatch, tmp_path):
    monkeypatch.setattr(memory_manager, "MEMORY_PATH", tmp_path / "memory.json")
    memory_manager.remember("project", "alpha", manual=True)
    assert memory_governance.edit("notes", "project", "beta").startswith("Edited")
    assert memory_governance.pin("notes", "project").startswith("Pinned")
    assert memory_governance.inspect()[0]["pinned"] is True
    assert memory_governance.export()["memories"][0]["value"] == "beta"
    assert memory_governance.delete("notes", "project").startswith("Forgotten")


def test_explicit_memory_fact_outranks_later_inference(monkeypatch, tmp_path):
    monkeypatch.setattr(memory_manager, "MEMORY_PATH", tmp_path / "memory.json")
    memory_manager.remember("city", "Hafar Al-Batin", "identity", manual=True)
    memory_manager.remember("city", "Riyadh", "identity", manual=False)
    entry = memory_manager.load_memory()["identity"]["city"]
    assert entry["value"] == "Hafar Al-Batin" and entry["status"] == "active"
    assert entry["contradictions"][0]["value"] == "Riyadh"


def test_proactive_topic_allow_and_deny():
    policy = proactive_permissions.ProactivePolicy(use_monitors=True, allowed_topics=("weather", "travel"), blocked_topics=("travel",))
    _, topics, _ = proactive_permissions.filter_context({}, ["weather", "travel", "finance"], [], policy)
    assert topics == ["weather"]


def test_skill_proposal_approval_rollback_and_reliability(monkeypatch, tmp_path):
    skill = tmp_path / "demo"; skill.mkdir(); current = skill / "SKILL.md"; current.write_text("old", encoding="utf-8")
    monkeypatch.setattr(skill_governance, "BACKUPS", tmp_path / "backups")
    monkeypatch.setattr(skill_governance, "STATE", tmp_path / "state.json")
    skill_governance.propose(skill, "new")
    backup = skill_governance.approve(skill)
    assert current.read_text() == "new"
    skill_governance.rollback(skill, Path(backup)); assert current.read_text() == "old"
    skill_governance.record_outcome("demo", True); skill_governance.record_outcome("demo", False)
    assert skill_governance.reliability("demo") == {"verified": 1, "failed": 1, "score": 0.5, "sample_size": 2}


def test_evaluation_matrix_and_truthful_release_comparison(monkeypatch, tmp_path):
    monkeypatch.setattr(reliability_evaluation, "RESULTS", tmp_path / "eval.json")
    reliability_evaluation.record("1", "adversarial", "duplicate_action", False, "test-id")
    reliability_evaluation.record("2", "adversarial", "duplicate_action", True, "test-id")
    report = reliability_evaluation.report("2", "1")
    assert report["delta"] == 1.0
    assert report["coverage"]["covered"] == 1
    assert report["claim"] == "measured_only_no_absolute_reliability_claim"
