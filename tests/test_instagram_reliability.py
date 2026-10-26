"""No live Instagram credentials or messages: failure/safety/confirmation regressions."""
from __future__ import annotations

import asyncio
import json
import subprocess
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from actions.social_hub import TOOL, social_hub
from core import confirm, security_vault, social_hub as hub
from core import instagram_web as web
from core.instagram_direct import DeliveryUnknown, InstagramSession, RecipientError, exact_thread, receipt_id
from memory import accounts


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "accounts.json")
    monkeypatch.setenv("JARVIS_SOCIALS_DIR", str(tmp_path / "socials"))
    monkeypatch.setattr(security_vault, "AUDIT_DB_PATH", tmp_path / "audit.db")
    monkeypatch.setattr(security_vault, "VAULT_KEY_FILE", tmp_path / "key")
    monkeypatch.setattr(hub, "_CDP", hub._NativeCdpSocialBrowser())
    monkeypatch.setattr(hub._CDP, "_endpoint_alive", lambda: False)
    monkeypatch.setattr(hub, "_HUD_SOCIAL_SESSIONS", {})
    monkeypatch.setattr(confirm, "_pending", None)
    monkeypatch.setattr(confirm, "_show_cb", Mock())
    monkeypatch.setattr(confirm, "_hide_cb", Mock())
    monkeypatch.setattr(confirm, "_log_cb", Mock())
    # Tests must not start a real browser or use the network by accident.
    monkeypatch.setattr(hub._CDP, "ensure_browser", Mock(side_effect=AssertionError("Unexpected real browser")))
    monkeypatch.setattr(hub, "_start_login_watcher", Mock())
    yield
    confirm.resolve(False)


def connected(permission="full"):
    accounts.connect_account("instagram", session_connected=True, permission=permission)
    hub.save_encrypted_cookies("instagram", [
        {"name": "sessionid", "value": "fake-session", "domain": ".instagram.com"},
        {"name": "ds_user_id", "value": "1", "domain": ".instagram.com"},
        {"name": "csrftoken", "value": "csrf", "domain": ".instagram.com"},
    ])


def thread(username="sarah", **extra):
    return {"thread_id": "exact-thread", "users": [{"username": username, "pk": "2"}], **extra}


def api_mock(monkeypatch, post_result, threads=None):
    requests = []
    original = httpx.Client

    def handle(request):
        requests.append(request)
        if request.method == "POST":
            if isinstance(post_result, Exception):
                raise post_result
            return post_result
        if "/threads/exact-thread/" in str(request.url):
            return httpx.Response(200, json={"thread": thread(items=[])})
        if "/web_profile_info/" in str(request.url):
            return httpx.Response(200, json={"data": {"user": {"id": "2", "username": "sarah"}}})
        return httpx.Response(200, json={"inbox": {"threads": threads if threads is not None else [thread()]}})

    monkeypatch.setattr(httpx, "Client", lambda *a, **kw: original(*a, **kw, transport=httpx.MockTransport(handle)))
    return requests


@pytest.mark.parametrize("candidate", ["sar", "sarah k", "Sarah K", "arah", "sarah_other"])
def test_no_partial_or_display_name_match(candidate):
    assert exact_thread([thread(full_name="Sarah K")], candidate) is None


def test_exact_handles_not_groups_and_ambiguous_threads_fail():
    group = thread(users=[{"username": "sarah"}, {"username": "omar"}])
    assert exact_thread([group], "@sarah") is None
    assert exact_thread([thread(is_group=True)], "sarah") is None
    assert exact_thread([group, thread()], "@SARAH")["thread_id"] == "exact-thread"
    with pytest.raises(RecipientError):
        exact_thread([thread(), thread()], "sarah")


@pytest.mark.parametrize("payload,expected", [
    ({"status": "ok"}, ""), ({"status": "fail", "item_id": "bad"}, ""),
    ({"status": "ok", "payload": {"item_id": "server-id"}}, "server-id"),
    ({"status": "ok", "message_metadata": {"message_id": "message-id"}}, "message-id"),
    ({"status": "ok", "client_context": "optimistic-id"}, ""),
])
def test_receipt_requires_provider_id(payload, expected):
    assert receipt_id(payload) == expected


@pytest.mark.parametrize("result", [
    httpx.ReadTimeout("connection lost after POST"),
    httpx.Response(200, json={"status": "ok"}),
    httpx.Response(200, text="<html>login</html>"),
    httpx.Response(500, json={}), httpx.Response(302, headers={"location": "/accounts/login/"}),
    httpx.Response(403, json={"status": "fail", "message": "challenge_required"}),
])
def test_uncertain_or_rejected_post_never_retried(monkeypatch, result):
    connected()
    requests = api_mock(monkeypatch, result)
    fallback = Mock(side_effect=AssertionError("Duplicate-send fallback must never run"))
    monkeypatch.setattr(web, "send_instagram_message", fallback)
    output = hub.stage_or_send_social_message("instagram", "@sarah", "same text")
    assert "send not confirmed" in output
    assert sum(r.method == "POST" for r in requests) == 1
    fallback.assert_not_called()
    hub._CDP.ensure_browser.assert_not_called()
    assert security_vault.verify_audit_chain()["valid"]


def test_group_membership_cannot_select_group_as_dm(monkeypatch):
    connected()
    requests = api_mock(monkeypatch, httpx.Response(200, json={"status": "ok", "item_id": "ack"}),
                        threads=[thread(users=[{"username": "sarah"}, {"username": "omar"}])])
    output = hub.stage_or_send_social_message("instagram", "@sarah", "private text")
    posts = [r for r in requests if r.method == "POST"]
    assert len(posts) == 1 and "recipient_users=" in posts[0].content.decode()
    assert "thread_ids" not in posts[0].content.decode()
    assert "Instagram acknowledgment: ack" in output


def test_api_failure_before_post_can_use_native_composer(monkeypatch):
    connected()
    monkeypatch.setattr(hub, "_ig_api_send_dm", lambda *_: None)
    fallback = Mock(return_value="Instagram acknowledgment: native-id")
    monkeypatch.setattr(web, "send_instagram_message", fallback)
    output = hub.stage_or_send_social_message("instagram", "sarah", "hello")
    assert "native-id" in output
    fallback.assert_called_once_with(hub, "sarah", "hello", expected_sender=hub._cookie_dict("instagram"))


def test_confirm_then_result_visible_and_spoken_once(monkeypatch):
    connected("ask")
    sent = Mock(return_value="Instagram acknowledgment: id-1")
    monkeypatch.setattr(hub, "_ig_api_send_dm", sent)
    completed = threading.Event()
    cards = []
    spoken = []
    player = SimpleNamespace(show_content=lambda title, body: cards.append((title, body)))

    def speak(text):
        spoken.append(text)
        completed.set()

    result = social_hub({"action": "send_message", "platform": "instagram", "recipient": "@sarah", "message": "مرحبا"}, player=player, speak=speak)
    assert "CONFIRMATION_PENDING" in result
    sent.assert_not_called()
    assert not cards
    confirm.resolve(True)
    confirm.resolve(True)
    assert completed.wait(2)
    sent.assert_called_once_with("sarah", "مرحبا")
    assert "id-1" in cards[0][1] and "id-1" in spoken[0]


@pytest.mark.parametrize("change", ["readonly", "paused", "disconnect", "account"])
def test_confirmation_rechecks_permission_and_sending_account(monkeypatch, change):
    connected("ask")
    sent = Mock(side_effect=AssertionError("Must not send after policy/account change"))
    monkeypatch.setattr(hub, "_ig_api_send_dm", sent)
    done = threading.Event()
    results = []
    hub.stage_or_send_social_message("instagram", "sarah", "hello", on_result=lambda r: (results.append(r), done.set()))
    if change == "disconnect":
        hub.disconnect_social_account("instagram")
    elif change == "account":
        hub.save_encrypted_cookies("instagram", [{"domain": ".instagram.com", "name": "sessionid", "value": "other-account"}])
    else:
        accounts.set_permission("instagram", change)
    confirm.resolve(True)
    assert done.wait(2)
    assert "send not confirmed" in results[0]
    sent.assert_not_called()


def test_pending_confirmation_cannot_be_silently_replaced(monkeypatch):
    connected("ask")
    first = "exact message " + "x" * 300
    hub.stage_or_send_social_message("instagram", "sarah", first)
    assert first in confirm._show_cb.call_args.args[1]
    pending = confirm._pending
    result = hub.stage_or_send_social_message("instagram", "omar", "different message")
    assert "already pending" in result
    assert confirm._pending is pending
    confirm.resolve(False)
    assert confirm.pending_title() == ""


def test_expired_or_cancelled_confirmation_cannot_send(monkeypatch):
    connected("ask")
    sent = Mock()
    monkeypatch.setattr(hub, "_ig_api_send_dm", sent)
    hub.stage_or_send_social_message("instagram", "sarah", "hello")
    confirm._pending.at -= confirm.TIMEOUT_SECONDS + 1
    confirm.resolve(True)
    assert confirm.pending_title() == ""
    sent.assert_not_called()


@pytest.mark.parametrize("policy", ["readonly", "paused", "ignored"])
def test_silent_recovery_never_upgrades_or_unignores_policy(monkeypatch, policy):
    connected(policy if policy != "ignored" else "ask")
    if policy == "ignored":
        accounts.ignore_account("instagram")
    importer = Mock(side_effect=AssertionError("Must not bypass saved policy"))
    monkeypatch.setattr(hub, "import_cookies_from_browser", importer)
    output = hub.stage_or_send_social_message("instagram", "sarah", "hello")
    assert "read-only" in output or "paused" in output or "not connected" in output
    importer.assert_not_called()


def test_saved_cookie_session_recovers_missing_record_with_ask_policy():
    connected()
    accounts.ACCOUNTS_FILE.unlink()
    ready, _ = hub._ensure_platform_ready("instagram")
    assert ready
    assert accounts.get_account("instagram")["permission"] == "ask"


def test_live_session_wins_over_vault_and_ignores_expired_or_suffix_domains(monkeypatch):
    connected()
    monkeypatch.setattr(hub._CDP, "_endpoint_alive", lambda: True)
    monkeypatch.setattr(hub._CDP, "get_all_cookies", lambda: [
        {"domain": ".instagram.com", "name": "sessionid", "value": "fresh"},
        {"domain": "evilinstagram.com", "name": "sessionid", "value": "attacker"},
        {"domain": ".instagram.com", "name": "expired", "value": "bad", "expires": 1},
        {"domain": ".instagram.com", "name": "malformed", "value": "bad", "expires": "not-a-number"},
    ])
    assert hub._cookie_dict("instagram") == {"sessionid": "fresh"}
    assert "fake-session" not in json.dumps(hub.load_encrypted_cookies("instagram"))


def test_anonymous_live_cookies_do_not_erase_saved_authentication(monkeypatch):
    connected()
    monkeypatch.setattr(hub._CDP, "_endpoint_alive", lambda: True)
    monkeypatch.setattr(hub._CDP, "get_all_cookies", lambda: [{"domain": ".instagram.com", "name": "csrftoken", "value": "anonymous"}])
    assert hub._cookie_dict("instagram")["sessionid"] == "fake-session"


def test_cookie_alone_does_not_prove_instagram_is_authenticated(monkeypatch):
    connected()
    monkeypatch.setattr(hub._CDP, "get_all_cookies", lambda: hub.load_encrypted_cookies("instagram"))
    monkeypatch.setattr(hub._CDP, "run_on_tab", lambda *_a, **_k: False)
    assert hub._probe_platform_authenticated("instagram", "ws://fake") == (False, "")


def test_session_health_is_shared_without_changing_permissions():
    connected("readonly")
    accounts.update_session_health("instagram", "login_required")
    assert not accounts.get_integrations_status_summary()["services"]["instagram"]["connected"]
    assert hub.get_social_hub_status()["platforms"][0]["session_health"] == "login_required"
    accounts.update_session_health("instagram", "authenticated")
    assert accounts.is_service_connected("instagram")
    assert accounts.get_account("instagram")["permission"] == "readonly"


def test_failed_thread_open_does_not_summarize_other_conversation(monkeypatch):
    connected()
    monkeypatch.setattr(hub, "_ig_api_read_thread", lambda *_: None)
    monkeypatch.setattr(hub._CDP, "get_or_open_tab", lambda *_a, **_k: {"webSocketDebuggerUrl": "ws://fake"})
    monkeypatch.setattr(hub._CDP, "run_on_tab", lambda _url, fn, **_kw: asyncio.run(fn(None, None)))
    async def noop(*_):
        pass
    async def not_found(*_):
        return False
    monkeypatch.setattr(hub, "_cdp_wait_settled", noop)
    monkeypatch.setattr(hub, "_cdp_dismiss_popups", noop)
    monkeypatch.setattr(hub, "_cdp_open_contact_thread", not_found)
    capture = Mock(side_effect=AssertionError("Must not capture the wrong chat"))
    monkeypatch.setattr(hub, "_cdp_capture_snapshot", capture)
    result = hub.read_social_messages("instagram", "sarah")
    assert not result["ok"] and "no other chat was read" in result["error"]
    capture.assert_not_called()


def test_hud_opens_requested_inbox_even_when_local_metadata_says_disconnected(monkeypatch):
    monkeypatch.setattr(hub, "import_cookies_from_browser", lambda *_a, **_kw: {"ok": False})
    opened = Mock(return_value={"webSocketDebuggerUrl": "ws://fake"})
    monkeypatch.setattr(hub._CDP, "get_or_open_tab", opened)
    monkeypatch.setattr(hub._CDP, "run_on_tab", lambda *_a, **_kw: "https://www.instagram.com/direct/inbox/")
    monkeypatch.setattr(hub, "_probe_platform_authenticated", lambda *_a: (True, ""))
    result = hub.open_social_in_hud("instagram", view="inbox")
    assert result["ok"] and result["social_hud"]["view"] == "inbox"
    assert opened.call_args.args[1].endswith("/direct/inbox/")
    assert accounts.is_service_connected("instagram")


@pytest.mark.parametrize("action", ["open_inbox", "open_feed", "open_reels", "open_profile", "close_hud"])
def test_hud_actions_are_exposed_to_model(action):
    assert action in TOOL["parameters"]["properties"]["action"]["enum"]


def test_unknown_and_stale_hud_interactions_fail_without_touching_browser():
    hub._HUD_SOCIAL_SESSIONS["current"] = {"platform": "instagram", "opened_at": 2}
    assert not hub.interact_hud_social({"kind": "bogus"})["ok"]
    assert not hub.interact_hud_social({"kind": "type", "text": "send", "opened_at": 1})["ok"]
    assert not hub.interact_hud_social({"kind": "type", "platform": "x", "text": "send"})["ok"]
    hub._CDP.ensure_browser.assert_not_called()


def test_zero_hud_coordinates_stay_zero(monkeypatch):
    hub._HUD_SOCIAL_SESSIONS["current"] = {"platform": "instagram", "opened_at": 2}
    monkeypatch.setattr(hub._CDP, "get_or_open_tab", lambda *_a, **_kw: {"webSocketDebuggerUrl": "ws://fake"})
    monkeypatch.setattr(hub._CDP, "run_on_tab", lambda _url, fn, **_kw: asyncio.run(fn(None, None)))
    async def noop(*_):
        pass
    points = []
    async def click(_c, _w, x, y):
        points.append((x, y))
    monkeypatch.setattr(hub, "_cdp_apply_hud_viewport", noop)
    monkeypatch.setattr(hub, "_cdp_trusted_click", click)
    assert hub.interact_hud_social({"kind": "click", "nx": 0, "ny": 0})["ok"]
    assert points == [(0, 0)]


def test_instagram_text_only_post_honestly_unsupported():
    assert "does not support text-only" in hub.stage_or_publish_social_post("instagram", "caption")
    assert confirm.pending_title() == ""


def test_same_origin_fetch_javascript_uses_browser_credentials_and_csrf(monkeypatch):
    connected()
    monkeypatch.setattr(hub._CDP, "get_or_open_tab", lambda *_a, **_kw: {"webSocketDebuggerUrl": "ws://fake"})
    class Connection:
        async def send_cmd(self, _ws, method, params):
            assert method == "Runtime.evaluate" and params["awaitPromise"]
            runner = """
              global.location = {origin: 'https://www.instagram.com'};
              global.document = {cookie: 'other=foo; csrftoken=fresh%2Bcsrf'};
              global.fetch = async (url, options) => ({status: 200,
                text: async () => JSON.stringify({url, method: options.method, body: options.body,
                  credentials: options.credentials, headers: options.headers, redirect: options.redirect})});
              eval(process.argv[1]).then(result => {console.log(JSON.stringify(result)); process.exit(0);});
            """
            result = subprocess.run(["node", "-e", runner, params["expression"]], capture_output=True, text=True, check=True, timeout=5)
            return {"result": {"value": json.loads(result.stdout)}}
    async def noop(*_):
        pass
    monkeypatch.setattr(hub, "_cdp_wait_settled", noop)
    monkeypatch.setattr(hub._CDP, "run_on_tab", lambda _url, fn, **_kw: asyncio.run(fn(Connection(), None)))
    with InstagramSession(hub, hub._cookie_dict("instagram")) as client:
        result = client._fetch("https://www.instagram.com/api/v1/direct_v2/threads/broadcast/text/", "POST", {"text": "مرحبا & hello URL BODY METHOD __REQUEST__"}).json()
        from urllib.parse import parse_qs
        assert parse_qs(result["body"])["text"] == ["مرحبا & hello URL BODY METHOD __REQUEST__"]
        assert result["credentials"] == "same-origin"
        assert result["headers"]["X-CSRFToken"] == "fresh+csrf"
        assert result["redirect"] == "error" and result["method"] == "POST"
        with pytest.raises(ValueError):
            client._fetch("https://evilinstagram.com/steal", "POST", {})


def test_read_get_can_recover_through_browser_but_write_is_never_retried(monkeypatch):
    connected()
    api_mock(monkeypatch, httpx.ReadTimeout("POST result lost"))
    with InstagramSession(hub, hub._cookie_dict("instagram")) as client:
        client.http.get = Mock(return_value=httpx.Response(401, json={"message": "login_required"}))
        fetch = Mock(return_value=httpx.Response(200, json={"inbox": {"threads": []}}))
        client._fetch = fetch
        assert client.get("https://www.instagram.com/api/v1/direct_v2/inbox/").status_code == 200
        assert accounts.get_account("instagram")["session_health"] == "authenticated"
        client.browser = False
        with pytest.raises(httpx.ReadTimeout):
            client.post("https://www.instagram.com/api/v1/direct_v2/threads/broadcast/text/", {"text": "hello"})
        assert fetch.call_count == 1


def test_http_csrf_is_refreshed_before_write(monkeypatch):
    connected()
    with InstagramSession(hub, {"sessionid": "fake-session"}) as client:
        def home(_url):
            client.http.cookies.set("csrftoken", "fresh-from-server", domain="www.instagram.com")
            return httpx.Response(200)
        client.http.get = Mock(side_effect=home)
        client.prepare_write()
        assert client.headers["X-CSRFToken"] == "fresh-from-server"
        client.http.get.assert_called_once_with("https://www.instagram.com/")


def test_http_server_csrf_rotation_beats_old_hostless_cookie():
    connected()
    with InstagramSession(hub, {"sessionid": "fake-session", "csrftoken": "stale"}) as client:
        client.http.cookies.set("csrftoken", "rotated", domain="www.instagram.com")
        client.prepare_write()
        assert client.headers["X-CSRFToken"] == "rotated"


def test_background_tab_cannot_reuse_hud_target(monkeypatch):
    browser = hub._CDP
    browser._port = 1234
    browser._tab_ids = {"instagram": "hud-tab"}
    hud = {"id": "hud-tab", "url": "https://www.instagram.com/direct/inbox/", "webSocketDebuggerUrl": "ws://fake/hud"}
    background = {"id": "background-tab", "url": "https://www.instagram.com/", "webSocketDebuggerUrl": "ws://fake/background"}
    monkeypatch.setattr(browser, "ensure_browser", lambda **_: 1234)
    monkeypatch.setattr(browser, "_list_page_targets", lambda: [hud])
    monkeypatch.setattr(browser, "run_on_tab", lambda *_a, **_kw: None)
    create = Mock(return_value=httpx.Response(200, json=background, request=httpx.Request("PUT", "http://127.0.0.1/json/new")))
    monkeypatch.setattr(httpx, "put", create)
    result = browser.get_or_open_tab("instagram", "https://www.instagram.com/", purpose="automation")
    assert result["id"] == "background-tab"
    assert browser._tab_ids["instagram"] == "hud-tab"
    assert browser._tab_ids["instagram:automation"] == "background-tab"
    assert browser.get_or_open_tab("instagram", hud["url"])["id"] == "hud-tab"
    create.assert_called_once()


def test_disconnect_cancels_login_watcher():
    connected()
    event = threading.Event()
    hub._WATCHERS_CANCEL["instagram"] = event
    hub._WATCHERS_ACTIVE.add("instagram")
    hub.disconnect_social_account("instagram")
    assert event.is_set() and "instagram" not in hub._WATCHERS_ACTIVE
    assert not accounts.is_service_connected("instagram")


def test_string_false_cannot_approve_confirmation(monkeypatch):
    from core.apex_bridge import ApexHudBridge
    resolve = Mock()
    monkeypatch.setattr(confirm, "resolve", resolve)
    assert not ApexHudBridge(None).handle_action({"action": "confirm_decision", "approved": "false"})["ok"]
    resolve.assert_not_called()


def test_full_preview_reaches_apex_confirmation_panel():
    from core.apex_bridge import ApexHudBridge
    detail = "Message: " + "x" * 1000
    bridge = ApexHudBridge(None)
    bridge.push_confirm("Send Instagram message to @sarah", detail)
    assert bridge.snapshot()["confirm"]["detail"] == detail


def test_oversized_message_is_not_staged_or_silently_truncated():
    connected("ask")
    assert "too long to fully preview" in hub.stage_or_send_social_message("instagram", "sarah", "x" * 4000)
    assert confirm.pending_title() == ""


def test_read_paginates_to_exact_older_thread(monkeypatch):
    connected()
    original = httpx.Client
    def handle(request):
        if "/threads/" in str(request.url):
            return httpx.Response(200, json={"thread": thread(items=[{"item_type": "text", "text": "older chat", "user_id": "2"}])})
        if request.url.params.get("cursor") == "older":
            return httpx.Response(200, json={"inbox": {"threads": [thread()]}})
        return httpx.Response(200, json={"inbox": {"threads": [thread("omar")], "has_older": True, "oldest_cursor": "older"}})
    monkeypatch.setattr(httpx, "Client", lambda *a, **kw: original(*a, **kw, transport=httpx.MockTransport(handle)))
    result = hub.read_social_messages("instagram", "sarah")
    assert result["ok"] and "older chat" in result["messages"]


@pytest.mark.parametrize("command", ["like", "save"])
def test_feed_writes_honor_readonly_policy_before_any_click(monkeypatch, command):
    connected("readonly")
    monkeypatch.setattr(hub._CDP, "get_or_open_tab", lambda *_a, **_kw: {"webSocketDebuggerUrl": "ws://fake"})
    run = Mock(side_effect=AssertionError("No interaction may be dispatched"))
    monkeypatch.setattr(hub._CDP, "run_on_tab", run)
    result = hub.control_social_feed("instagram", command)
    assert not result["ok"] and "read-only" in result["error"]
    run.assert_not_called()


def test_legacy_persistent_profile_is_hydrated_before_confirmation(monkeypatch):
    connected("ask")
    hub.clear_encrypted_cookies("instagram")
    (hub.socials_root_dir() / "browser_profile").mkdir()
    browser_state = {"alive": False}
    monkeypatch.setattr(hub._CDP, "_endpoint_alive", lambda: browser_state["alive"])
    ensure = Mock(side_effect=lambda **_: browser_state.update(alive=True))
    monkeypatch.setattr(hub._CDP, "ensure_browser", ensure)
    monkeypatch.setattr(hub._CDP, "get_all_cookies", lambda: [
        {"domain": ".instagram.com", "name": "sessionid", "value": "persistent-session"},
        {"domain": ".instagram.com", "name": "ds_user_id", "value": "123"},
    ])
    output = hub.stage_or_send_social_message("instagram", "sarah", "hello")
    assert "CONFIRMATION_PENDING" in output
    assert hub._cookie_dict("instagram")["ds_user_id"] == "123"
    ensure.assert_called_once_with(headless=True)


def test_send_result_survives_broken_hud_display(monkeypatch):
    connected("ask")
    monkeypatch.setattr(hub, "_ig_api_send_dm", Mock(return_value="Instagram acknowledgment: safe-id"))
    completed = threading.Event()
    spoken = []
    def speak(text):
        spoken.append(text)
        completed.set()
    player = SimpleNamespace(show_content=Mock(side_effect=RuntimeError("display unavailable")))
    pending = social_hub({"action": "send_message", "platform": "instagram", "recipient": "sarah", "message": "hello"}, player=player, speak=speak)
    assert "CONFIRMATION_PENDING" in pending
    confirm.resolve(True)
    assert completed.wait(3)
    assert len(spoken) == 1 and "safe-id" in spoken[0]


def test_native_session_does_not_issue_speculative_api_write(monkeypatch):
    from core import instagram_web
    connected("full")
    monkeypatch.setattr(hub._CDP, "_endpoint_alive", lambda: True)
    api = Mock(side_effect=AssertionError("Must not write to private API first"))
    native = Mock(return_value="Instagram acknowledgment: native-id")
    monkeypatch.setattr(hub, "_ig_api_send_dm", api)
    monkeypatch.setattr(instagram_web, "send_instagram_message", native)
    result = hub.stage_or_send_social_message("instagram", "sarah", "hello")
    assert "native-id" in result
    api.assert_not_called()
    native.assert_called_once()


def test_instagram_no_confirmation_preference_executes_once(monkeypatch):
    connected("ask")
    monkeypatch.delenv("JARVIS_INSTAGRAM_CONFIRM_SEND", raising=False)
    sent = Mock(return_value="Instagram acknowledgment: direct-no-prompt")
    monkeypatch.setattr(hub, "_ig_api_send_dm", sent)
    results = []
    assert hub._instagram_send_confirmation_required() is False
    result = hub.stage_or_send_social_message("instagram", "sarah", "hello", on_result=results.append)
    assert "direct-no-prompt" in result
    assert "CONFIRMATION_PENDING" not in result
    assert results == [result]
    assert confirm._pending is None
    sent.assert_called_once_with("sarah", "hello")


@pytest.mark.parametrize("permission", ["readonly", "paused"])
def test_no_confirmation_preference_does_not_override_send_restrictions(monkeypatch, permission):
    connected(permission)
    monkeypatch.delenv("JARVIS_INSTAGRAM_CONFIRM_SEND", raising=False)
    sent = Mock(side_effect=AssertionError("Policy must block before execution"))
    monkeypatch.setattr(hub, "_ig_api_send_dm", sent)
    result = hub.stage_or_send_social_message("instagram", "sarah", "hello")
    assert "blocked" in result.lower() or "paused" in result.lower()
    sent.assert_not_called()
