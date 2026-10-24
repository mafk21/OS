"""
Tests for Voice/Live-Session Tool Parity (`companion_os` + `manage_accounts`)
across Automations, Specialist Companions, Guest Portals, and Audit Chain.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from actions.accounts_center import manage_accounts
from actions.companion_os import TOOL as COMP_TOOL, companion_os
from core import automations, companions, security_vault
from core.action_loader import discover_actions
from core.apex_bridge import map_tool_to_nodes
from memory import accounts
from memory import config_manager as cfg
from memory import timeline as tl


@pytest.fixture()
def isolated_voice_os(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    monkeypatch.setattr(companions, "COMPANIONS_FILE", tmp_path / "memory" / "companions.json")
    monkeypatch.setattr(automations, "AUTOMATIONS_FILE", tmp_path / "memory" / "automations.json")
    monkeypatch.setattr(security_vault, "VAULT_KEY_FILE", tmp_path / "config" / ".vault.key")
    monkeypatch.setattr(security_vault, "AUDIT_DB_PATH", tmp_path / "memory" / "security_audit.db")
    return tmp_path


def test_companion_os_voice_automations_companions_and_portals(isolated_voice_os):
    # 1. Create & run automation by voice tool
    saved = companion_os(
        {
            "action": "automation_save",
            "name": "Morning Status Sweep",
            "schedule_type": "daily",
            "daily_at": "08:30",
            "tool": "cloud_integrations",
            "tool_params": {"action": "status"},
        }
    )
    assert "Morning Status Sweep" in saved

    ran = companion_os({"action": "automation_run", "name": "Morning Status"})
    assert "finished (success)" in ran

    # 2. Create & activate specialist companion by voice
    created_comp = companion_os(
        {
            "action": "companion_create",
            "name": "NOVA",
            "role": "Security Specialist",
            "persona": "female",
            "voice": "Aoede",
            "allowed_tools": ["companion_os", "brain_control"],
        }
    )
    assert "NOVA" in created_comp

    switched = companion_os({"action": "companion_activate", "name": "NOVA"})
    assert "NOVA" in switched
    assert cfg.get_persona() == "female"

    # 3. Create Guest Portal automatically from latest Brain Output, then shut off all
    tl.record_output("Weekly Sprint Digest", "All 6 Operating Companion phases shipped.")
    portal_msg = companion_os({"action": "portal_create"})
    assert "/portal/" in portal_msg
    assert "Weekly Sprint Digest" in portal_msg

    revoked = companion_os({"action": "portal_revoke_all"})
    assert "1 active" in revoked

    verified = companion_os({"action": "audit_verify"})
    assert "verified" in verified.lower()


def test_companion_os_and_accounts_center_discovery(isolated_voice_os):
    reg = discover_actions(Path(__file__).resolve().parent.parent / "actions")
    names = {d["name"] for d in reg.get_tool_declarations()}
    assert "companion_os" in names
    assert COMP_TOOL["name"] == "companion_os"
    assert "chief_of_staff" in map_tool_to_nodes("companion_os")

    acc_msg = manage_accounts({"action": "list"})
    for svc in ("linear", "outlook", "dropbox", "hubspot", "calendly"):
        assert svc in acc_msg
