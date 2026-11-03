"""
End-to-end tests for First-Run Optional Integrations Onboarding + Direct Cloud & Email APIs
across both Male and Female interface editions.
"""

from __future__ import annotations

import base64
import json
from unittest.mock import MagicMock, patch

import pytest

from actions.cloud_integrations import TOOL as CLOUD_TOOL, cloud_integrations
from core.action_loader import discover_actions
from core.apex_bridge import ApexHudBridge, map_tool_to_nodes
from core.gws_pack import gws_pack
from memory import accounts
from memory import config_manager as cfg


@pytest.fixture()
def isolated_env(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_file = cfg_dir / "api_keys.json"
    acc_file = tmp_path / "memory" / "accounts.json"
    monkeypatch.setattr(cfg, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cfg, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", acc_file)
    monkeypatch.delenv("JARVIS_SKIP_INTEGRATIONS_PROMPT", raising=False)
    monkeypatch.delenv("JARVIS_SKIP_PERSONA_PROMPT", raising=False)
    monkeypatch.delenv("JARVIS_HUD_PREVIEW_READY", raising=False)
    return {"cfg_file": cfg_file, "acc_file": acc_file, "tmp_path": tmp_path}


class _DummyWin:
    def __init__(self):
        self._ready = False

    def _on_setup_done(self, *_a):
        self._ready = True

    def mark_integrations_done(self):
        pass


class _OnboardingUI:
    def __init__(self):
        self._win = _DummyWin()
        self._integrations_ready = False
        self._persona_selected = False
        self.muted = False
        self.persona = "male"
        self.ui_color = "#00d4ff"
        self.voice_changes: list[str] = []
        self.integrations_refreshes = 0

    def apply_persona_visuals(self, persona: str, ui_color: str):
        self._persona_selected = True
        self.persona = persona
        self.ui_color = ui_color

    def on_voice_change(self, v: str):
        self.voice_changes.append(v)

    def on_integrations_change(self):
        self.integrations_refreshes += 1


def test_first_run_three_step_flow_female_with_partial_ignore(isolated_env):
    """First run: Step 1 API key -> Step 2 connect Email/GitHub/Notion & ignore Slack/Discord -> Step 3 Female edition."""
    ui = _OnboardingUI()
    bridge = ApexHudBridge(ui, host="127.0.0.1", port=0)

    # Initial state: nothing configured yet
    s0 = bridge.snapshot()
    assert s0["ready"] is False
    assert s0["integrations_ready"] is False
    assert s0["persona_chosen"] is False

    # Step 1: Save Gemini API key
    r1 = bridge.handle_action({"action": "save_api_key", "key": ("AI" + "zaSyTestFirstRunKey123456")})
    assert r1["ok"] is True
    ui._win._ready = True
    s1 = bridge.snapshot()
    assert s1["ready"] is True
    assert s1["integrations_ready"] is False
    assert s1["persona_chosen"] is False

    # Step 2: Connect Email + GitHub + Notion, explicitly ignore Slack & Discord, leave others blank
    r2 = bridge.handle_action(
        {
            "action": "save_integrations",
            "integrations": {
                "email": {"email": "jane@gmail.com", "app_password": "abcd efgh ijkl mnop"},
                "github": {"token": "ghp_test token123".replace(" ", "")},
                "notion": {"token": "ntn_secret_123"},
                "slack": {"ignore": True},
                "discord": {"ignore": True},
                "spotify": {"client_id": "", "client_secret": ""},
            },
        }
    )
    assert r2["ok"] is True
    assert set(r2["saved"]) == {"email", "github", "notion"}
    assert "slack" in r2["ignored"] and "discord" in r2["ignored"]

    # Verify GitHub token synced to config/api_keys.json AND onboarding flag persisted
    saved_cfg = cfg.load_api_keys()
    assert saved_cfg["github_token"] == "ghp_testtoken123"
    assert saved_cfg["integrations_onboarding_done"] is True

    s2 = bridge.snapshot()
    assert s2["integrations_ready"] is True
    assert s2["integrations"]["connected_count"] == 3
    assert s2["integrations"]["services"]["slack"]["ignored"] is True
    assert s2["persona_chosen"] is False  # Step 3 still awaits edition choice!

    # Step 3: Choose Female Edition
    r3 = bridge.handle_action({"action": "set_persona", "persona": "female"})
    assert r3["ok"] is True
    assert r3["persona"] == "female"
    assert r3["voice"] == "Aoede"
    s3 = bridge.snapshot()
    assert s3["persona_chosen"] is True
    assert s3["persona"] == "female"
    assert ui.ui_color == "#ff4db8"

    # Prompt context lists connected services cleanly for Female edition
    prompt_blk = accounts.format_connected_for_prompt()
    assert "email" in prompt_blk
    assert "github" in prompt_blk
    assert "notion" in prompt_blk


def test_first_run_skip_all_integrations_male_edition(isolated_env):
    """First run: user enters Gemini API key, skips ALL integrations, and launches Male edition."""
    ui = _OnboardingUI()
    bridge = ApexHudBridge(ui, host="127.0.0.1", port=0)

    bridge.handle_action({"action": "save_api_key", "key": ("AI" + "zaSySkipAllKey123456789")})
    ui._win._ready = True
    skip_res = bridge.handle_action({"action": "skip_integrations"})
    assert skip_res["ok"] is True
    assert cfg.is_integrations_onboarding_done() is True

    snap_mid = bridge.snapshot()
    assert snap_mid["integrations_ready"] is True
    assert snap_mid["integrations"]["connected_count"] == 0
    assert snap_mid["persona_chosen"] is False

    p_res = bridge.handle_action({"action": "set_persona", "persona": "male"})
    assert p_res["ok"] is True
    assert p_res["persona"] == "male"
    assert p_res["voice"] == "Charon"
    assert bridge.snapshot()["persona_chosen"] is True


def test_email_gmail_api_and_imap_smtp_execution(isolated_env):
    """Verify both Gmail REST API and Direct IMAP/SMTP App Password send & search."""
    test_file = isolated_env["tmp_path"] / "note.txt"
    test_file.write_text("Quarterly summary", encoding="utf-8")

    # 1. Gmail REST API mode
    accounts.connect_account("gmail", token="ya29.mock_gmail_token", email="operator@gmail.com")
    sent_payloads = []

    def fake_http(url, *, method="GET", headers=None, payload=None, raw_body=None, timeout=15.0):
        assert headers and headers.get("Authorization") == "Bearer ya29.mock_gmail_token"
        if url.endswith("/messages/send"):
            sent_payloads.append(payload)
            return {"id": "msg_sent_1"}
        if "/messages?" in url:
            return {"messages": [{"id": "m101"}]}
        if "/messages/m101" in url:
            return {
                "id": "m101",
                "snippet": "Deployment succeeded",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "CI Bot <ci@example.com>"},
                        {"name": "Subject", "value": "Build #42 Green"},
                        {"name": "Date", "value": "Sat, 24 Oct 2026 10:00:00 +0300"},
                    ]
                },
            }
        return {}

    with patch.object(accounts, "_http_json", side_effect=fake_http):
        unread_out = cloud_integrations({"action": "email_unread"})
        assert "Build #42 Green" in unread_out
        assert "Deployment succeeded" in unread_out

        send_out = cloud_integrations(
            {
                "action": "email_send",
                "to": "team@example.com",
                "subject": "Report",
                "body": "Attached.",
                "file_path": str(test_file),
            }
        )
        assert "Gmail API" in send_out
        assert len(sent_payloads) == 1
        raw_decoded = base64.urlsafe_b64decode(sent_payloads[0]["raw"]).decode("utf-8", errors="ignore")
        assert "team@example.com" in raw_decoded
        assert "note.txt" in raw_decoded

        # gws_pack also routes through direct Gmail API when connected!
        gws_out = gws_pack({"action": "gmail_search", "query": "Build"})
        assert "Build #42 Green" in gws_out

    # 2. Direct IMAP/SMTP App Password mode (after disconnecting Gmail OAuth)
    accounts.disconnect_account("gmail")
    accounts.connect_account("email", email="user@outlook.com", app_password="app_pw_secret")
    imap_h, imap_p, smtp_h, smtp_p = accounts._resolve_imap_smtp(accounts.get_account("email"))
    assert imap_h == "outlook.office365.com" and smtp_h == "smtp.office365.com" and smtp_p == 587

    mock_smtp = MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp
    with patch("smtplib.SMTP", return_value=mock_smtp):
        res_smtp = cloud_integrations(
            {"action": "email_send", "to": "boss@example.com", "subject": "Ping", "body": "Ready"}
        )
        assert "user@outlook.com" in res_smtp
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@outlook.com", "app_pw_secret")
        mock_smtp.send_message.assert_called_once()


def test_google_drive_calendar_notion_slack_discord_trello(isolated_env):
    """Verify real REST payloads for Drive, Calendar, Notion, Slack, Discord, and Trello."""
    sample_doc = isolated_env["tmp_path"] / "plan.md"
    sample_doc.write_text("# Launch Plan", encoding="utf-8")

    accounts.save_onboarding_integrations(
        {
            "google": {"token": "ya29.drive_cal_tok"},
            "notion": {"token": "ntn_live_tok", "parent_page_id": "page_parent_1"},
            "slack": {"token": "xoxb-slack-tok", "default_channel": "#general"},
            "discord": {"webhook_url": "https://discord.com/api/webhooks/123/abc"},
            "trello": {"api_key": "tkey", "token": "ttok"},
            "telegram": {"token": "999:TG_BOT"},
            "spotify": {"client_id": "sp_id", "client_secret": "sp_sec"},
        }
    )

    # Check config/api_keys.json sync for Telegram & Spotify
    k = cfg.load_api_keys()
    assert k["telegram_bot_token"] == "999:TG_BOT"
    assert k["spotify_client_id"] == "sp_id"

    def fake_router(url, *, method="GET", headers=None, payload=None, raw_body=None, timeout=15.0):
        if "googleapis.com/drive/v3/files" in url and method == "GET":
            return {"files": [{"id": "drv1", "name": "Roadmap.pdf", "mimeType": "application/pdf", "webViewLink": "https://drive.google.com/d/drv1"}]}
        if "googleapis.com/upload/drive/v3/files" in url:
            assert raw_body and b"plan.md" in raw_body
            return {"id": "drv2", "name": "plan.md", "webViewLink": "https://drive.google.com/d/drv2"}
        if "calendar/v3/calendars/primary/events/quickAdd" in url:
            return {"summary": "Design Review", "htmlLink": "https://calendar.google.com/ev1"}
        if "calendar/v3/calendars/primary/events?" in url:
            return {"items": [{"id": "e1", "summary": "Standup", "start": {"dateTime": "2026-10-24T09:00:00Z"}}]}
        if "api.notion.com/v1/pages" in url:
            return {"id": "np1", "url": "https://notion.so/np1"}
        if "slack.com/api/conversations.list" in url:
            return {"ok": True, "channels": [{"id": "C01", "name": "general"}]}
        if "slack.com/api/chat.postMessage" in url:
            assert payload["channel"] == "C01"
            return {"ok": True}
        if "discord.com/api/webhooks" in url:
            assert payload["content"] == "Hello Discord"
            return {}
        if "api.trello.com/1/cards" in url:
            return {"id": "tc1", "shortUrl": "https://trello.com/c/tc1"}
        return {}

    with patch.object(accounts, "_http_json", side_effect=fake_router):
        assert "Roadmap.pdf" in cloud_integrations({"action": "drive_search", "query": "Roadmap"})
        assert "plan.md" in cloud_integrations({"action": "drive_upload", "file_path": str(sample_doc)})
        assert "Standup" in cloud_integrations({"action": "calendar_list"})
        assert "Design Review" in cloud_integrations({"action": "calendar_add", "title": "Design Review", "when": "tomorrow 2pm"})
        assert "notion.so/np1" in cloud_integrations({"action": "notion_create_page", "title": "Sprint Notes", "body": "Shipped PR 25"})
        assert "Posted to Slack" in cloud_integrations({"action": "slack_send", "body": "Shipped!"})
        assert "Discord" in cloud_integrations({"action": "discord_send", "body": "Hello Discord"})
        assert "trello.com/c/tc1" in cloud_integrations({"action": "trello_create_card", "list_id": "L1", "title": "QA Pass"})


def test_action_discovery_and_hud_spoke_mapping():
    from pathlib import Path

    reg = discover_actions(Path(__file__).resolve().parent.parent / "actions")
    names = {d["name"] for d in reg.get_tool_declarations()}
    assert "cloud_integrations" in names
    assert CLOUD_TOOL["name"] == "cloud_integrations"
    nodes = map_tool_to_nodes("cloud_integrations")
    assert "email" in nodes and "drive" in nodes


def test_google_oauth_start_and_disconnect_via_http(isolated_env):
    from fastapi.testclient import TestClient

    ui = _OnboardingUI()
    ui._win._ready = True
    ui._integrations_ready = True
    ui._persona_selected = True
    bridge = ApexHudBridge(ui, host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        r = client.post(
            "/api/hud/action",
            json={
                "action": "start_google_oauth",
                "client_id": "12345.apps.googleusercontent.com",
                "client_secret": "GOCSPX-secret",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert "accounts.google.com/o/oauth2/v2/auth" in body["auth_url"]
        assert "gmail.modify" in body["auth_url"]

        accounts.connect_account("gmail", token="ya29.temp")
        assert accounts.is_service_connected("gmail") is True

        disc = client.post(
            "/api/hud/action",
            json={"action": "disconnect_integration", "service": "google"},
        )
        assert disc.status_code == 200
        assert accounts.is_service_connected("gmail") is False
