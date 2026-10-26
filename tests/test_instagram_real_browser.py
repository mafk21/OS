"""Actual Chromium, DOM, React-style input and CDP; ALL Instagram requests intercepted.

Run with JARVIS_TEST_CHROMIUM=/path/to/chromium. No live Instagram account,
credentials, requests or DMs. The browser binary is external, never checked in.
"""
import json
import os
import socket
import threading
from pathlib import Path
from urllib.parse import urlsplit
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from core import confirm, instagram_web, security_vault, social_hub as hub
from memory import accounts


@pytest.fixture
def browser_env(tmp_path, monkeypatch):
    binary = os.environ.get("JARVIS_TEST_CHROMIUM", "")
    if not binary or not Path(binary).is_file():
        pytest.skip("Set JARVIS_TEST_CHROMIUM for isolated actual-browser DOM tests")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    ready, stop = threading.Event(), threading.Event()
    state = {"mode": "button", "posts": [], "errors": []}

    def route(request_route):
        request = request_route.request
        path = urlsplit(request.url).path
        # There is deliberately NO route.continue_ anywhere in this fixture.
        if request.method == "POST":
            state["posts"].append(request.post_data)
            return request_route.fulfill(json={"status": "ok", "payload": {"item_id": "real-browser-simulated-id"}})
        if path == "/api/v1/direct_v2/inbox/" and state["mode"] == "direct_lookup":
            return request_route.fulfill(json={"status":"ok", "inbox":{"threads":[
                {"thread_id":"test-thread", "users":[{"username":"sarah"}], "items":[{"text":"never returned to Python"}]}
            ]}})
        if path == "/sarah/":
            if state["mode"] == "login":
                return request_route.fulfill(status=302, headers={"Location": "https://www.instagram.com/accounts/login/"})
            meta = '<link rel="canonical" href="https://www.instagram.com/sarah/">' if state["mode"] != "header" else ''
            control = '<a href="/direct/t/test-thread/">Message</a>' if state["mode"] == "link" else '<button onclick="location.href=\'/direct/t/test-thread/\'">Message</button>'
            if state["mode"] == "encrypted":
                control = '<button onclick="location.href=\'/direct/e2ee/t/test-thread/\'">Message</button>'
            if state["mode"] in ("stuck", "wrong_recipient", "ambiguous_recipient", "preselected_recipient", "aria_option", "inbox_launcher", "direct_lookup", "nested_action", "profile_anchor", "contradictory_anchor"):
                control = '<button>Message</button>'
            if state["mode"] == "hidden_copy":
                control = '<button style="display:none">Message</button>' + control
            if state["mode"] == "modal":
                chat = '<div role="dialog"><a href="/sarah/">sarah</a>' + composer() + '</div>'
                control = '<button id="open">Message</button><script>document.querySelector("#open").onclick=()=>{document.querySelector("main").insertAdjacentHTML("beforeend", '+json.dumps(chat)+'); setup();}</script>'
            return request_route.fulfill(content_type="text/html", body='<html><head>'+meta+'</head><body><main><header><h2>sarah</h2></header>'+control+'</main>'+script()+'</body></html>')
        if path.startswith(("/direct/t/", "/direct/e2ee/t/")):
            return request_route.fulfill(content_type="text/html", body='<html><body><main>'+composer()+'</main>'+script()+'<script>setup()</script></body></html>')
        if path == "/direct/new/":
            username = 'someoneelse' if state['mode'] == 'wrong_recipient' else 'sarah'
            row = '<label><span>'+username+'</span><br><span>Display name</span><input type="checkbox"></label>'
            if state['mode'] == 'ambiguous_recipient':
                row += row
            if state['mode'] == 'preselected_recipient':
                row += '<label>someoneelse<input type="checkbox" checked></label>'
            if state['mode'] == 'aria_option':
                row = '<div role="option" onclick="this.setAttribute(\'aria-selected\', \'true\')">sarah<br>Display name</div>'
            if state['mode'] == 'nested_action':
                row = '<label>sarah<br>Display name<input type="checkbox"><button type="button">More info</button></label>'
            if state['mode'] == 'profile_anchor':
                row = '<label>Display Name<br><a href="/sarah/" onclick="event.preventDefault()">sarah</a><input type="checkbox"></label>'
            if state['mode'] == 'contradictory_anchor':
                row = '<label>sarah<br><a href="/someoneelse/">Different account</a><input type="checkbox"></label>'
            search = '<input name="queryBox" placeholder="Search">'
            if state['mode'] == 'inbox_launcher':
                search = '<button onclick="this.outerHTML=\'<input name=&quot;queryBox&quot; placeholder=&quot;Search&quot;>\'"><svg aria-label="New message"></svg></button>'
            return request_route.fulfill(content_type="text/html", body='<html><body>'+search+row+'<button onclick="location.href=\'/direct/e2ee/t/test-thread/\'">Chat</button></body></html>')
        if path == "/accounts/login/":
            return request_route.fulfill(content_type="text/html", body='<input type="password">Sign in')
        return request_route.fulfill(status=404, body="simulated only")

    def composer():
        mode = state["mode"]
        editable = '<div role="textbox" aria-label="Message" contenteditable="true"></div>' if mode == "editable" else '<textarea placeholder="Message...">'+('my existing draft' if mode == 'draft' else '')+'</textarea>'
        send = '' if mode == "enter" else '<div role="button" aria-label="'+('Send message' if mode == 'send_label' else 'Send')+'" onclick="submitOnce()">Send</div>'
        return editable + send + '<textarea placeholder="Search unrelated"></textarea>'

    def script():
        return '''<script>
          function box(){return document.querySelector('textarea[placeholder="Message..."], [contenteditable=true]')}
          function submitOnce(){let b=box(); fetch('/api/v1/direct_v2/threads/broadcast/text/', {method:'POST', body:new URLSearchParams({text: b.value || b.innerText})});}
          function setup(){box().addEventListener('keydown', e=>{if(e.key==='Enter'){e.preventDefault();submitOnce();}});}
        </script>'''

    def controller():
        try:
            with sync_playwright() as pw:
                context = pw.chromium.launch_persistent_context(str(tmp_path / "browser"), executable_path=binary, headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", f"--remote-debugging-port={port}"])
                context.route("**/*", route)
                context.add_cookies([{"name": "sessionid", "value": "simulation-only", "domain": ".instagram.com", "path": "/", "secure": True},
                                     {"name": "ds_user_id", "value": "123", "domain": ".instagram.com", "path": "/", "secure": True}])
                ready.set()
                while not stop.is_set():
                    context.pages[0].wait_for_timeout(30)
                context.close()
        except Exception as exc:
            state["errors"].append(exc)
            ready.set()
    thread = threading.Thread(target=controller, daemon=True)
    thread.start()
    assert ready.wait(15), "Browser did not start"
    if state["errors"]:
        pytest.fail(str(state["errors"][0]))
    monkeypatch.setenv("JARVIS_SOCIALS_CDP_PORT", str(port))
    monkeypatch.setenv("JARVIS_SOCIALS_DIR", str(tmp_path / "socials"))
    monkeypatch.setattr(hub, "_CDP", hub._NativeCdpSocialBrowser())
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "accounts.json")
    monkeypatch.setattr(security_vault, "VAULT_KEY_FILE", tmp_path / "vault.key")
    monkeypatch.setattr(security_vault, "AUDIT_DB_PATH", tmp_path / "audit.db")
    monkeypatch.setattr(confirm, "_pending", None)
    monkeypatch.setattr(confirm, "_show_cb", lambda *_: None)
    monkeypatch.setattr(confirm, "_hide_cb", lambda: None)
    monkeypatch.setattr(confirm, "_log_cb", lambda *_: None)
    accounts.connect_account("instagram", session_connected=True, permission="ask")
    # Bind the external browser before staging captures the sending identity.
    hub._CDP.ensure_browser(headless=True)
    try:
        yield state
    finally:
        stop.set()
        thread.join(10)
        assert not thread.is_alive(), "Browser controller leaked"


@pytest.mark.parametrize("mode", ["button", "link", "header", "editable", "enter", "send_label", "modal", "encrypted", "hidden_copy", "stuck", "aria_option", "inbox_launcher", "direct_lookup", "nested_action", "profile_anchor"])
def test_actual_confirmed_native_send_variants(browser_env, mode):
    browser_env["mode"] = mode
    completed = threading.Event()
    results = []
    def report(result):
        results.append(result)
        completed.set()
    pending = hub.stage_or_send_social_message("instagram", "sarah", "simulated approved text", on_result=report)
    assert "CONFIRMATION_PENDING" in pending
    assert not browser_env["posts"]
    confirm.resolve(True)
    assert completed.wait(35), "No execution result after confirmation"
    assert "Instagram acknowledgment: real-browser-simulated-id" in results[0], results[0]
    assert len(browser_env["posts"]) == 1
    assert 'simulated+approved+text' in browser_env["posts"][0]


@pytest.mark.parametrize("mode", ["draft", "login"])
def test_actual_browser_blocks_draft_or_login_without_sending(browser_env, mode):
    browser_env["mode"] = mode
    with pytest.raises(RuntimeError, match=r"\[IG:"):
        instagram_web.send_instagram_message(hub, "sarah", "must not send", expected_sender={"ds_user_id": "123"})
    assert not browser_env["posts"]


@pytest.mark.parametrize("mode", ["wrong_recipient", "ambiguous_recipient", "preselected_recipient", "contradictory_anchor"])
def test_compose_recovery_never_selects_wrong_or_ambiguous_recipient(browser_env, mode):
    browser_env["mode"] = mode
    with pytest.raises(RuntimeError, match=r"IG:compose_(exact_recipient|selection)"):
        instagram_web.send_instagram_message(hub, "sarah", "must not send", expected_sender={"ds_user_id": "123"})
    assert not browser_env["posts"]



def test_actual_send_without_extra_confirmation(browser_env, monkeypatch):
    monkeypatch.delenv("JARVIS_INSTAGRAM_CONFIRM_SEND", raising=False)
    browser_env["mode"] = "aria_option"
    result = hub.stage_or_send_social_message("instagram", "sarah", "explicit no-prompt test")
    assert "Instagram acknowledgment: real-browser-simulated-id" in result, result
    assert "CONFIRMATION_PENDING" not in result
    assert confirm._pending is None
    assert len(browser_env["posts"]) == 1
