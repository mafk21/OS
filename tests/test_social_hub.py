"""
Tests for `core/social_hub.py`, `actions/social_hub.py`, `memory/accounts.py`,
and HUD `LINKS` Personal Socials endpoints (`Instagram`, `Snapchat`, `TikTok`, `X`, `WhatsApp`, `Reddit`).
"""

from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from actions.social_hub import social_hub
from core import confirm as confirm_gate
from core import security_vault
from core import social_hub as sh
from core.apex_bridge import ApexHudBridge
from memory import accounts


@pytest.fixture()
def isolated_socials_env(tmp_path, monkeypatch):
    acc_file = tmp_path / "accounts.json"
    soc_dir = tmp_path / "jarvis_socials"
    audit_db = tmp_path / "security_audit.db"
    vault_key = tmp_path / ".vault.key"

    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", acc_file)
    monkeypatch.setenv("JARVIS_SOCIALS_DIR", str(soc_dir))
    monkeypatch.setattr(security_vault, "AUDIT_DB_PATH", audit_db)
    monkeypatch.setattr(security_vault, "VAULT_KEY_FILE", vault_key)
    return tmp_path


def test_social_accounts_onboarding_ignore_and_prompt_injection(isolated_socials_env):
    res = accounts.save_onboarding_integrations(
        {
            "instagram": {"ignore": False, "session_connected": True, "handle": "@mafk", "permission": "ask"},
            "snapchat": {"ignore": True},
            "tiktok": {"ignore": False},  # left blank -> stays optional without error
        }
    )
    assert res["ok"] is True
    assert "instagram" in res["saved"]
    assert "snapchat" in res["ignored"]

    summary = accounts.get_integrations_status_summary()
    assert summary["services"]["instagram"]["connected"] is True
    assert summary["services"]["instagram"]["handle"] == "mafk"
    assert summary["services"]["instagram"]["permission"] == "ask"
    assert summary["services"]["snapchat"]["ignored"] is True
    assert summary["services"]["tiktok"]["connected"] is False

    prompt_ctx = accounts.format_connected_for_prompt()
    assert "instagram (@mafk) [ask]" in prompt_ctx
    assert "social_hub" in prompt_ctx


def test_encrypted_cookie_vault_and_browser_cookie_import(isolated_socials_env):
    fake_cookies = [
        SimpleNamespace(
            domain=".instagram.com",
            name="sessionid",
            value="ig_secret_session_999",
            path="/",
            secure=True,
            expires=1999999999,
        ),
        SimpleNamespace(
            domain=".instagram.com",
            name="ds_user_id",
            value="424242",
            path="/",
            secure=True,
            expires=1999999999,
        ),
    ]

    with patch("yt_dlp.cookies.extract_cookies_from_browser", return_value=fake_cookies):
        out = social_hub(
            {
                "action": "connect",
                "platform": "instagram",
                "cookies_browser": "chrome",
                "handle": "@mafk",
                "permission": "ask",
            }
        )

    assert "Connected Instagram" in out
    assert "2 session cookies" in out

    # Verify cookies are encrypted on disk (`enc:v1:...`), NEVER plaintext!
    vault_fp = sh._cookie_vault_file("instagram")
    raw_disk = vault_fp.read_text(encoding="utf-8")
    assert raw_disk.startswith("enc:v1:")
    assert "ig_secret_session_999" not in raw_disk

    loaded = sh.load_encrypted_cookies("instagram")
    assert len(loaded) == 2
    assert {c["name"] for c in loaded} == {"sessionid", "ds_user_id"}
    assert security_vault.verify_audit_chain()["valid"] is True


def test_check_inbox_and_read_messages_with_multimodal_vision_and_dom(isolated_socials_env):
    accounts.connect_account("instagram", session_connected=True, handle="mafk", permission="ask")
    accounts.connect_account("snapchat", session_connected=True, handle="mafk_snap", permission="ask")

    # Build a valid JPEG screenshot buffer
    buf = BytesIO()
    Image.new("RGB", (320, 200), (24, 32, 48)).save(buf, format="JPEG")
    fake_jpg = buf.getvalue()

    def _fake_inspect(platform: str, url: str, *, headless: bool = True):
        return (
            fake_jpg,
            {
                "title": f"{platform.capitalize()} Inbox",
                "url": url,
                "unread_badges": ["2 unread messages"],
                "items": ["Sarah · Hey are we still meeting at 7? · 2m", "Omar · New Snap · 5m"],
            },
            True,
        )

    seen_vision_inputs: list[object] = []

    def _fake_llm(contents, **_kw):
        seen_vision_inputs.extend(contents if isinstance(contents, list) else [contents])
        return SimpleNamespace(text="• Sarah (2m ago): 'Hey are we still meeting at 7?'\n• Omar (5m ago): Unopened Snap.")

    with patch("core.social_hub._inspect_url_in_session", side_effect=_fake_inspect), patch(
        "core.gemini.call", side_effect=_fake_llm
    ):
        digest = social_hub({"action": "check_inbox", "platform": "all", "include_notifications": False})

    assert "=== Instagram Inbox ===" in digest
    assert "=== Snapchat Inbox ===" in digest
    assert "Sarah" in digest and "Omar" in digest
    # Confirm real PIL.Image screenshots were passed to multimodal vision!
    assert sum(1 for x in seen_vision_inputs if isinstance(x, Image.Image)) >= 2


def test_unforgeable_hud_confirmation_gate_on_dm_reply_and_posts(isolated_socials_env):
    sent_calls: list[tuple[str, str, str, str]] = []

    def _fake_exec_send(plat: str, rec: str, msg: str, actor: str) -> str:
        sent_calls.append((plat, rec, msg, actor))
        security_vault.log_audit_event(
            actor,
            f"social_send_message:{plat}",
            {"platform": plat, "recipient": rec},
            result_summary="Sent.",
            status="ok",
        )
        return f"Sent {plat} message to {rec}."

    # 1. Read-Only policy blocks sending completely
    accounts.connect_account("snapchat", session_connected=True, permission="readonly")
    blocked = social_hub(
        {"action": "send_message", "platform": "snapchat", "recipient": "Ahmed", "message": "Yo!"}
    )
    assert "read-only" in blocked.lower()
    assert len(sent_calls) == 0

    # 2. Default `ask` policy stages on HUD Confirmation Banner WITHOUT sending until human approves!
    accounts.set_permission("snapchat", "ask")
    banners: list[tuple[str, str]] = []
    confirm_gate.bind(
        show=lambda t, d: banners.append((t, d)),
        hide=lambda: None,
        log=lambda _m: None,
    )

    with patch("core.social_hub._execute_send_message_now", side_effect=_fake_exec_send):
        pending_msg = social_hub(
            {
                "action": "send_message",
                "platform": "snapchat",
                "recipient": "Ahmed",
                "message": "On my way in 10 mins!",
            }
        )
        assert "[CONFIRMATION_PENDING]" in pending_msg
        assert len(banners) == 1
        assert "Snapchat" in banners[0][0] and "Ahmed" in banners[0][0]
        # Crucial: message has NOT been sent yet!
        assert len(sent_calls) == 0

        # Human clicks CANCEL -> still NOT sent!
        confirm_gate.resolve(False)
        assert len(sent_calls) == 0

        # Stage again & human clicks CONFIRM -> sends on worker thread!
        social_hub(
            {
                "action": "send_message",
                "platform": "snapchat",
                "recipient": "Ahmed",
                "message": "On my way in 10 mins!",
            }
        )
        confirm_gate.resolve(True)
        import time

        deadline = time.time() + 2.0
        while not sent_calls and time.time() < deadline:
            time.sleep(0.02)

        assert len(sent_calls) == 1
        assert sent_calls[0] == ("snapchat", "Ahmed", "On my way in 10 mins!", "user_confirmed")
        assert security_vault.verify_audit_chain()["valid"] is True


def test_hands_free_feed_and_apex_bridge_social_endpoints(isolated_socials_env):
    fake_cookies = [
        SimpleNamespace(
            domain=".x.com",
            name="auth_token",
            value="x_tok_777",
            path="/",
            secure=True,
            expires=1999999999,
        )
    ]

    bridge = ApexHudBridge(None)
    app = bridge._build_app()

    with TestClient(app) as client, patch(
        "yt_dlp.cookies.extract_cookies_from_browser", return_value=fake_cookies
    ):
        r = client.post(
            "/api/hud/action",
            json={
                "action": "social_import_cookies",
                "platform": "x",
                "browser": "chrome",
                "handle": "@mafk_x",
                "permission": "ask",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["summary"]["services"]["x"]["connected"] is True

        # Disconnect wipes both account state and encrypted cookie vault
        r_disc = client.post(
            "/api/hud/action",
            json={"action": "disconnect_integration", "service": "x"},
        )
        assert r_disc.status_code == 200
        assert r_disc.json()["summary"]["services"]["x"]["connected"] is False
        assert sh.load_encrypted_cookies("x") == []

    with patch(
        "actions.social_hub.control_social_feed",
        return_value={"ok": True, "message": "Moved to the next post/reel on Instagram."},
    ):
        fd_out = social_hub({"action": "feed", "platform": "instagram", "command": "next"})
        assert "next post/reel on Instagram" in fd_out
