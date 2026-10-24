"""
End-to-end tests for Phase 6: Authenticated Credential Vault, Key Rotation,
Tamper-Evident Hash-Chained Action Audit Log, Revocable Guest Portals, and
1-Click Native Installer.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

import install_jarvis
from core import security_vault as sv
from core.apex_bridge import ApexHudBridge
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline as tl


@pytest.fixture()
def isolated_sec(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory" / "long_term.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    monkeypatch.setattr(sv, "VAULT_KEY_FILE", tmp_path / "config" / ".vault.key")
    monkeypatch.setattr(sv, "AUDIT_DB_PATH", tmp_path / "memory" / "security_audit.db")
    return tmp_path


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_accounts_encrypted_at_rest_tamper_detection_and_key_rotation(isolated_sec):
    accounts.connect_account("notion", token="ntn_super_secret_token_999")
    raw_disk = accounts.ACCOUNTS_FILE.read_text(encoding="utf-8")
    # Plaintext secret must NEVER appear on disk
    assert "ntn_super_secret_token_999" not in raw_disk
    assert "enc:v1:" in raw_disk

    # Transparent decryption in memory
    assert accounts.get_account("notion")["token"] == "ntn_super_secret_token_999"

    # Strict api_keys.json encryption round-trip
    cfg.save_api_keys("AIzaSyDummyGeminiKey1234567890")
    cfg.set_strict_config_encryption(True)
    raw_cfg = cfg.CONFIG_FILE.read_text(encoding="utf-8")
    assert "AIzaSyDummyGeminiKey1234567890" not in raw_cfg
    assert "enc:v1:" in raw_cfg
    assert cfg.get_gemini_key() == "AIzaSyDummyGeminiKey1234567890"

    # Rotate 256-bit master key and verify secrets still decrypt cleanly
    rot = sv.rotate_vault_master_key(accounts.ACCOUNTS_FILE, cfg.CONFIG_FILE)
    assert rot["ok"] is True
    assert rot["reencrypted_count"] >= 2
    assert accounts.get_account("notion")["token"] == "ntn_super_secret_token_999"
    assert cfg.get_gemini_key() == "AIzaSyDummyGeminiKey1234567890"

    # Tampering with ciphertext must raise authentication mismatch
    ct = sv.encrypt_secret("top-secret")
    tampered = ct[:-4] + ("AAAA" if not ct.endswith("AAAA") else "BBBB")
    with pytest.raises(ValueError, match="mismatch|Malformed|Truncated"):
        sv.decrypt_secret(tampered)


def test_hash_chained_audit_log_redaction_and_tamper_verification(isolated_sec):
    sv.log_audit_event(
        "jarvis",
        "cloud_integrations",
        {"action": "slack_send", "token": "xoxb-secret-leak"},
        "Sent Slack message",
    )
    sv.log_audit_event("jarvis", "web_search", {"query": "AI"}, "Found 5 results")

    events = sv.list_audit_events()
    assert len(events) == 2
    assert "xoxb-secret-leak" not in events[1]["args_redacted"]
    assert "[REDACTED]" in events[1]["args_redacted"]

    chain = sv.verify_audit_chain()
    assert chain["valid"] is True
    assert chain["checked"] == 2

    # Directly mutate SQLite row behind the vault's back -> chain verification catches it!
    with sqlite3.connect(str(sv.AUDIT_DB_PATH)) as conn:
        conn.execute("UPDATE audit_logs SET action = 'forged_action' WHERE id = 1")
        conn.commit()

    broken = sv.verify_audit_chain()
    assert broken["valid"] is False
    assert broken["broken_at_id"] == 1


def test_revocable_guest_portals_and_1click_shutoff(isolated_sec):
    from fastapi.testclient import TestClient

    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        created = client.post(
            "/api/hud/action",
            json={
                "action": "portal_create",
                "title": "Q4 Architecture Brief",
                "content_body": "Confidential summary for external reviewer.",
                "expires_hours": 12,
                "max_views": 2,
            },
        ).json()
        assert created["ok"] is True
        portal_path = created["portal"]["path"]
        portal_id = created["portal"]["id"]

        # 1st visit succeeds (HTTP 200)
        r1 = client.get(portal_path, headers={"user-agent": "ReviewerBrowser/1.0"})
        assert r1.status_code == 200
        assert "Q4 Architecture Brief" in r1.text

        # 1-click revoke shuts off access immediately (HTTP 403)
        client.post(
            "/api/hud/action",
            json={"action": "portal_revoke", "portal_id": portal_id},
        )
        r2 = client.get(portal_path)
        assert r2.status_code == 403
        assert "PORTAL CLOSED" in r2.text

        sec = client.get("/api/hud/security").json()["security"]
        p_info = next(p for p in sec["portals"] if p["id"] == portal_id)
        assert p_info["revoked"] is True
        assert len(p_info["visits"]) == 2


def test_one_click_installer_environment_and_launchers(tmp_path):
    st = install_jarvis.check_environment()
    assert st["python_ok"] is True
    assert st["requirements_present"] is True

    created = install_jarvis.write_native_launchers(tmp_path)
    assert len(created) == 2
    assert (tmp_path / "Start_JARVIS.bat").is_file()
    assert (tmp_path / "Start_JARVIS.command").is_file()
