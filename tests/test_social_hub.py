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


def test_windows_unpatched_popen_bypasses_create_no_window_for_visible_social_window(monkeypatch):
    import subprocess as sp

    orig_calls: list[tuple[list[str], dict]] = []
    patched_calls: list[tuple[list[str], dict]] = []

    class _FakeOrigPopen:
        def __init__(self, args, **kw):
            orig_calls.append((list(args), dict(kw)))

    class _FakePatchedPopen(_FakeOrigPopen):
        def __init__(self, args, **kw):
            kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
            patched_calls.append((list(args), dict(kw)))

    monkeypatch.setattr(sp, "_OrigPopen", _FakeOrigPopen, raising=False)
    monkeypatch.setattr(sp, "Popen", _FakePatchedPopen)

    sh._spawn_visible_or_hidden(["chrome.exe", "https://www.instagram.com/"], visible=True)
    assert len(orig_calls) == 1
    assert len(patched_calls) == 0
    assert "creationflags" not in orig_calls[0][1]


def test_chrome_v20_cookie_lock_auto_opens_instagram_signin_window(isolated_socials_env):
    bridge = ApexHudBridge(None)
    app = bridge._build_app()

    with TestClient(app) as client, patch(
        "yt_dlp.cookies.extract_cookies_from_browser",
        side_effect=RuntimeError("Could not copy Chrome cookie database (App-Bound Encryption v20)"),
    ), patch(
        "core.social_hub.start_social_login",
        return_value={
            "ok": True,
            "platform": "instagram",
            "label": "Instagram",
            "already_connected": False,
            "message": "Opened Instagram in a dedicated window on your screen.",
        },
    ) as mock_login:
        r = client.post(
            "/api/hud/action",
            json={
                "action": "social_import_cookies",
                "platform": "instagram",
                "browser": "auto",
                "handle": "@mafk",
                "permission": "ask",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["auto_opened_window"] is True
        assert "opened a dedicated Instagram window" in data["error"]
        mock_login.assert_called_once()


def test_open_app_and_send_message_route_insta_through_social_hub(isolated_socials_env):
    from actions.open_app import open_app
    from actions.send_message import send_message

    with patch(
        "core.social_hub.control_social_feed",
        return_value={"ok": True, "message": "Opened your Instagram feed."},
    ) as mock_feed:
        res_open = open_app({"app_name": "insta"})
        assert res_open == "Opened your Instagram feed."
        mock_feed.assert_called_once_with("instagram", "open_feed")

    with patch(
        "core.social_hub.control_social_feed",
        return_value={"ok": True, "message": "Opened Instagram Reels / Spotlight."},
    ) as mock_reels:
        res_reels = open_app({"app_name": "insta reels"})
        assert "Reels" in res_reels
        mock_reels.assert_called_once_with("instagram", "open_reels")

    with patch(
        "core.social_hub.stage_or_send_social_message",
        return_value="[CONFIRMATION_PENDING] Send Instagram message to @sarah",
    ) as mock_send:
        res_msg = send_message(
            {"platform": "insta", "receiver": "@sarah", "message_text": "Hey from JARVIS!"}
        )
        assert "[CONFIRMATION_PENDING]" in res_msg
        mock_send.assert_called_once_with("instagram", "@sarah", "Hey from JARVIS!")


def test_media_engine_uses_encrypted_instagram_vault_cookiefile_for_ytdlp(isolated_socials_env):
    from pathlib import Path

    from core.media_engine import _build_social_vault_cookiefile

    sh.save_encrypted_cookies(
        "instagram",
        [
            {
                "name": "sessionid",
                "value": "ig_reel_vault_token_123",
                "domain": ".instagram.com",
                "path": "/",
                "secure": True,
                "expires": 1999999999,
            }
        ],
    )
    cf = _build_social_vault_cookiefile("https://www.instagram.com/reel/C9xyz123/")
    assert cf is not None
    try:
        txt = Path(cf).read_text(encoding="utf-8")
        assert "# Netscape HTTP Cookie File" in txt
        assert ".instagram.com\tTRUE\t/\tTRUE\t1999999999\tsessionid\tig_reel_vault_token_123" in txt
    finally:
        Path(cf).unlink(missing_ok=True)


def test_real_cdp_websocket_instagram_login_inbox_lexical_dm_and_reels(
    isolated_socials_env, monkeypatch
):
    """End-to-end test over a REAL local HTTP + WebSocket CDP server."""
    import asyncio
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import json
    import socket
    import threading
    import time

    import websockets

    buf = BytesIO()
    Image.new("RGB", (240, 160), (15, 25, 45)).save(buf, format="JPEG")
    import base64

    jpg_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    cdp_events: list[tuple[str, dict]] = []
    state = {
        "url": "https://www.instagram.com/accounts/login/",
        "cookies": [],
    }

    # 1. Start real WebSocket CDP target server
    ws_port_holder: dict[str, int] = {}
    ws_ready = threading.Event()
    ws_stop: dict[str, Any] = {}

    def _run_ws_server() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _handler(websocket):
            async for raw in websocket:
                req = json.loads(raw)
                req_id = req["id"]
                method = req["method"]
                params = req.get("params") or {}
                cdp_events.append((method, params))

                result: dict = {}
                if method == "Page.navigate":
                    state["url"] = params.get("url", state["url"])
                    result = {"frameId": "main"}
                elif method == "Network.getAllCookies":
                    result = {"cookies": list(state["cookies"])}
                elif method == "Page.captureScreenshot":
                    result = {"data": jpg_b64}
                elif method == "Runtime.evaluate":
                    expr = str(params.get("expression") or "")
                    if "document.readyState" in expr:
                        result = {"result": {"type": "string", "value": "complete"}}
                    elif "location.href" in expr and "unread_badges" in expr:
                        result = {
                            "result": {
                                "type": "object",
                                "value": {
                                    "title": "Instagram · Inbox",
                                    "url": state["url"],
                                    "unread_badges": ["1 unread message"],
                                    "items": ["Sarah · Are you free tonight? · 1m"],
                                },
                            }
                        }
                    elif "dmComposerTextInput" in expr or 'aria-label*="Message"' in expr:
                        result = {"result": {"type": "object", "value": {"x": 520, "y": 760}}}
                    elif "dmComposerSendButton" in expr or "=== 'send'" in expr:
                        result = {"result": {"type": "object", "value": {"x": 880, "y": 760}}}
                    elif "needle" in expr or 'aria-label="Like"' in expr:
                        result = {"result": {"type": "object", "value": {"x": 220, "y": 310}}}
                    elif "location.href" in expr:
                        result = {"result": {"type": "string", "value": state["url"]}}
                    else:
                        result = {"result": {"type": "number", "value": 0}}

                await websocket.send(json.dumps({"id": req_id, "result": result}))

        async def _serve():
            stop_fut = loop.create_future()
            ws_stop["loop"] = loop
            ws_stop["fut"] = stop_fut
            async with websockets.serve(_handler, "127.0.0.1", 0) as srv:
                ws_port_holder["port"] = srv.sockets[0].getsockname()[1]
                ws_ready.set()
                await stop_fut

        loop.run_until_complete(_serve())

    ws_thread = threading.Thread(target=_run_ws_server, daemon=True)
    ws_thread.start()
    assert ws_ready.wait(timeout=5.0)
    ws_url = f"ws://127.0.0.1:{ws_port_holder['port']}/devtools/page/tab1"

    # 2. Start real HTTP `/json/version` & `/json/list` CDP discovery server
    class _CdpHttpHandler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_GET(self):
            if self.path.startswith("/json/version"):
                payload = {"Browser": "Chrome/134.0", "webSocketDebuggerUrl": ws_url}
            else:
                payload = [
                    {
                        "id": "tab1",
                        "type": "page",
                        "title": "Instagram",
                        "url": state["url"],
                        "webSocketDebuggerUrl": ws_url,
                    }
                ]
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    http_srv = HTTPServer(("127.0.0.1", 0), _CdpHttpHandler)
    http_port = http_srv.server_address[1]
    threading.Thread(target=http_srv.serve_forever, daemon=True).start()
    monkeypatch.setenv("JARVIS_SOCIALS_CDP_PORT", str(http_port))

    try:
        # Step A: Start Instagram login -> not logged in yet -> watcher starts
        connected_flag = threading.Event()
        res_login = sh.start_social_login(
            "instagram",
            handle="@mafk",
            permission="full",
            on_connected=connected_flag.set,
        )
        assert res_login["ok"] is True
        assert res_login["already_connected"] is False

        # Simulate user finishing login in the Chrome window -> `sessionid` cookie appears!
        state["url"] = "https://www.instagram.com/direct/inbox/"
        state["cookies"] = [
            {
                "name": "sessionid",
                "value": "live_cdp_ig_session_777",
                "domain": ".instagram.com",
                "path": "/",
                "secure": True,
            }
        ]
        assert connected_flag.wait(timeout=5.0), "Watcher did not detect live Instagram sessionid!"
        assert accounts.is_service_connected("instagram") is True
        assert sh.load_encrypted_cookies("instagram")[0]["value"] == "live_cdp_ig_session_777"

        # Step B: Check Instagram inbox over real CDP + Vision
        with patch(
            "core.gemini.call",
            return_value=SimpleNamespace(text="1 unread DM from Sarah: 'Are you free tonight?'"),
        ):
            inbox = sh.check_social_inbox("insta", include_notifications=False)
        assert inbox["ok"] is True
        assert "Sarah" in inbox["summary"]

        # Step C: Send Instagram DM via trusted CDP mouse click + `Input.insertText` (Meta Lexical!)
        sent = sh.stage_or_send_social_message("insta", "@sarah", "Yes see you at 8!")
        assert "Sent Instagram message to sarah" in sent
        typed_texts = [p.get("text") for m, p in cdp_events if m == "Input.insertText"]
        assert "Yes see you at 8!" in typed_texts

        # Step D: Hands-free Instagram Reels scroll & Like over real CDP
        assert sh.control_social_feed("insta", "open_reels")["ok"] is True
        assert sh.control_social_feed("insta", "next")["ok"] is True
        assert sh.control_social_feed("insta", "like")["ok"] is True
        methods_called = {m for m, _ in cdp_events}
        assert {"Input.dispatchKeyEvent", "Input.dispatchMouseEvent", "Input.insertText"} <= methods_called
    finally:
        http_srv.shutdown()
        if "loop" in ws_stop and "fut" in ws_stop:
            ws_stop["loop"].call_soon_threadsafe(ws_stop["fut"].set_result, True)

