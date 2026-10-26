"""
End-to-end tests for Phase 3: Behavior Interviews, Adaptive Style Learning,
Custom Specialist Companions, Visual Skills Studio, and Theme Presets.
"""

from __future__ import annotations

import pytest

from core import companions as comp
from core.apex_bridge import ApexHudBridge
from core.skill_loader import discover_skills
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline as tl


@pytest.fixture()
def isolated_studio(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory" / "long_term.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    monkeypatch.setattr(comp, "COMPANIONS_FILE", tmp_path / "memory" / "companions.json")
    monkeypatch.setattr(comp, "CUSTOM_SKILLS_DIR", tmp_path / "memory" / "custom_skills")
    return tmp_path


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_behavior_interview_and_adaptive_correction_learning(isolated_studio):
    saved = comp.save_behavior_interview(
        {"tone": "Concise & Tactical", "verbosity": "Crisp 1-3 sentence summaries"}
    )
    assert saved["tone"] == "Concise & Tactical"

    # Automatic conversational correction detection
    rule = comp.detect_and_record_correction(
        "Hey JARVIS, from now on never use emojis in code reviews."
    )
    assert rule is not None
    assert "never use emojis" in rule.lower()

    prompt_blk = comp.format_behavior_and_companion_for_prompt()
    assert "Concise & Tactical" in prompt_blk
    assert "never use emojis" in prompt_blk

    # Pausing adaptive learning stops new auto-detections
    cfg.save_adaptive_learning_enabled(False)
    assert comp.detect_and_record_correction("Always reply in pirate slang.") is None


def test_custom_specialist_companions_and_scoped_tool_permissions(isolated_studio):
    # Create a Female specialist companion scoped strictly to web_search & brain_control
    athena = comp.save_companion(
        {
            "name": "ATHENA",
            "role": "Deep Research Specialist",
            "persona": "female",
            "voice": "Aoede",
            "instructions": "Cite primary peer-reviewed papers first.",
            "allowed_tools": ["web_search", "brain_control"],
            "assigned_skills": ["deep-research"],
        }
    )
    comp.set_active_companion(athena["id"])
    assert cfg.get_persona() == "female"
    assert cfg.get_voice() == "Aoede"

    ok_allowed, _ = comp.is_tool_allowed_for_active_companion("web_search")
    assert ok_allowed is True

    ok_blocked, reason = comp.is_tool_allowed_for_active_companion("cmd_control")
    assert ok_blocked is False
    assert "ATHENA" in reason

    # Reset back to default companion restores unrestricted access
    comp.set_active_companion("default")
    ok_default, _ = comp.is_tool_allowed_for_active_companion("cmd_control")
    assert ok_default is True


def test_visual_skills_studio_protects_core_and_manages_custom_skills(isolated_studio):
    # Attempting to overwrite a protected core default skill is blocked
    with pytest.raises(ValueError, match="protected core skills"):
        comp.save_custom_skill(
            "deep-research",
            "Attempted override of core skill",
            "## When to use\nx",
        )

    with pytest.raises(ValueError, match="protected core skills"):
        comp.save_custom_skill("topic-learning", "Override study skill", "## Procedure\nx")

    # Custom skill creation succeeds inside memory/custom_skills/
    res = comp.save_custom_skill(
        "release-audit",
        "Run pre-release security and changelog verification checks.",
        "## When to use\nBefore tagging a release.\n\n## Procedure\n1. Run pytest",
    )
    assert res["name"] == "release-audit"

    studio_skills = comp.list_all_skills_for_studio()
    assert any(s["name"] == "release-audit" and s["builtin"] is False for s in studio_skills)
    # Built-in skill set includes persistent subject learning
    assert len(discover_skills(comp.CORE_SKILLS_DIR, logger=lambda _: None)) == 12

    assert comp.delete_custom_skill("release-audit") is True


def test_studio_hud_http_endpoints_and_themes(isolated_studio):
    from fastapi.testclient import TestClient

    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        st = client.get("/api/hud/studio").json()
        assert st["ok"] is True
        assert len(st["studio"]["interview_questions"]) == 5

        th = client.post(
            "/api/hud/action",
            json={"action": "studio_save_theme", "preset": "emerald_matrix"},
        ).json()
        assert th["ok"] is True
        assert th["theme"]["effective_primary"] == "#10f59b"
