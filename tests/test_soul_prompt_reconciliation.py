"""Phase 13 tests for single-authority personality prompt composition."""
from pathlib import Path

import pytest

from core.soul.service import reconcile_legacy_prompt


PROMPT = Path("core/prompt.txt").read_text(encoding="utf-8")


def test_legacy_path_keeps_personality_but_never_marker_syntax():
    rendered = reconcile_legacy_prompt(PROMPT, "")
    assert "most experienced person in the room" in rendered
    assert "Humour is dry understatement" in rendered
    assert "LEGACY_PERSONALITY" not in rendered


def test_soul_path_removes_only_legacy_personality_and_keeps_operations():
    rendered = reconcile_legacy_prompt(PROMPT, "[CONSTITUTION]\nSoul active")
    assert "most experienced person in the room" not in rendered
    assert "Humour is dry understatement" not in rendered
    for required in ("[WHAT YOU CAN DO]", "[SKILLS]", "[INTERRUPTIONS]", "[EXECUTION]", "[LANGUAGE]"):
        assert required in rendered
    assert "{assistant_name}" in rendered and "{capabilities}" in rendered


def test_reconciliation_rejects_malformed_or_nested_markers():
    with pytest.raises(ValueError, match="unterminated"):
        reconcile_legacy_prompt("[[LEGACY_PERSONALITY_START]]\ntext", "soul")
    with pytest.raises(ValueError, match="unmatched"):
        reconcile_legacy_prompt("[[LEGACY_PERSONALITY_END]]", "")
    with pytest.raises(ValueError, match="nested"):
        reconcile_legacy_prompt("[[LEGACY_PERSONALITY_START]]\n[[LEGACY_PERSONALITY_START]]", "soul")


def test_main_reconciles_both_live_and_offline_base_prompts():
    source = Path("main.py").read_text(encoding="utf-8")
    assert source.count("reconcile_legacy_prompt(system_prompt, soul_ctx)") == 1
    assert source.count("reconcile_legacy_prompt(sys_prompt, soul_ctx)") == 1
