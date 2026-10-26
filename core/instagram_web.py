"""Conservative native-web fallback for Instagram Direct, including encrypted chats.

This drives Instagram's own composer using the existing headless profile. It is
only called when API lookup failed BEFORE any send attempt. No speculative
clicks, display-name matching, draft overwrites, or click-as-success reporting.
"""
from __future__ import annotations

import re
import threading
import time
from urllib.parse import urlsplit

from core.instagram_direct import DeliveryUnknown, RecipientError, receipt_id

_LOCK = threading.Lock()


def _playwright():
    from playwright.sync_api import sync_playwright
    return sync_playwright()


def _send_ack(response) -> str:
    """Only observe known send operations, never an arbitrary GraphQL response."""
    request = response.request
    if request.method != "POST" or response.status != 200:
        return ""
    url = urlsplit(response.url)
    if url.hostname not in ("www.instagram.com", "instagram.com"):
        return ""
    body = request.post_data or ""
    direct = "/direct_v2/threads/broadcast/text/" in url.path
    graphql_send = "graphql" in url.path and bool(re.search(r"send_?message", body, re.I))
    if not (direct or graphql_send):
        return ""
    try:
        payload = response.json()
    except Exception:
        return ""
    if not isinstance(payload, dict) or payload.get("errors") or payload.get("error"):
        return ""
    if direct:
        return receipt_id(payload)

    def find(node):
        if isinstance(node, dict):
            # A provider message ID, not an optimistic client/offline ID.
            if node.get("errors") or node.get("error") or node.get("success") is False:
                return ""
            for key in ("message_id", "item_id"):
                if isinstance(node.get(key), (str, int)) and str(node[key]):
                    return str(node[key])
            for value in node.values():
                result = find(value)
                if result:
                    return result
        elif isinstance(node, list):
            for value in node:
                result = find(value)
                if result:
                    return result
        return ""

    return find(payload.get("data"))


def send_instagram_message(hub, recipient: str, message: str, *, expected_sender: dict | None = None) -> str:
    """Use the exact profile's Message button, then wait for a server send receipt."""
    username = recipient.strip().lstrip("@").lower()
    if not re.fullmatch(r"[a-z0-9_.]{1,30}", username):
        raise RecipientError("Use an exact Instagram @username. Nothing was sent.")
    attempted = False
    with _LOCK:
        manager = _playwright()
        playwright = manager.start()
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            tab = hub._CDP.get_or_open_tab("instagram", profile_url, headless=True,
                                          force_navigate=True, purpose="send")
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{hub._CDP._port}", timeout=15000)
            page = None
            # Select the exact CDP target, not another tab with the same URL.
            for context in browser.contexts:
                for candidate in context.pages:
                    session = context.new_cdp_session(candidate)
                    try:
                        info = session.send("Target.getTargetInfo")["targetInfo"]
                        if info.get("targetId") == tab.get("id"):
                            page = candidate
                    finally:
                        session.detach()
            if page is None:
                raise RuntimeError("Could not attach to Instagram's background tab. Open Instagram in the HUD.")
            page.set_default_timeout(12000)
            page.wait_for_url(profile_url)
            page.wait_for_load_state("domcontentloaded")
            parsed = urlsplit(page.url)
            if parsed.hostname != "www.instagram.com" or parsed.path.rstrip("/").lower() != "/" + username:
                raise RecipientError("Instagram redirected away from the exact profile. Complete login/security verification in the HUD; nothing was sent.")
            # The canonical profile metadata must independently confirm identity.
            canonical = page.locator('link[rel="canonical"], meta[property="og:url"]').first
            canonical.wait_for(state="attached")
            canonical_url = canonical.get_attribute("href") or canonical.get_attribute("content") or ""
            identity = urlsplit(canonical_url)
            if identity.hostname not in ("www.instagram.com", "instagram.com") or identity.path.rstrip("/").lower() != "/" + username:
                raise RecipientError("Instagram did not confirm the exact profile identity. Nothing was sent.")
            buttons = page.get_by_role("button", name=re.compile(r"^(Message|Send message|إرسال رسالة|رسالة)$", re.I))
            buttons.first.wait_for(state="visible")
            if buttons.count() != 1:
                raise RecipientError("The exact profile has no unique Message button. Check messaging restrictions in the HUD; nothing was sent.")
            buttons.click()
            page.wait_for_url(re.compile(r"https://www\.instagram\.com/direct/t/[^/]+/?"))
            composers = page.locator('textarea[placeholder]:visible, [role="textbox"][contenteditable="true"]:visible')
            composers.first.wait_for(state="visible")
            if composers.count() != 1:
                raise RuntimeError("No unique Instagram message composer. Open the chat in the HUD; nothing was sent.")
            composer = composers.first
            draft = composer.input_value() if composer.evaluate("el => el.tagName === 'TEXTAREA'") else composer.inner_text()
            if draft.strip():
                raise RuntimeError("This Instagram chat already has an unsent draft. It was not changed or sent; review it in the HUD.")
            def check_sender():
                if expected_sender is None:
                    return
                current = hub._cookie_dict("instagram")
                key = "ds_user_id" if expected_sender.get("ds_user_id") else "sessionid"
                if not expected_sender.get(key) or expected_sender.get(key) != current.get(key):
                    raise RecipientError("The signed-in account changed. The draft was not submitted; request a new confirmation.")

            check_sender()
            composer.fill(message)
            send = page.get_by_role("button", name=re.compile(r"^(Send|إرسال)$", re.I))
            send.first.wait_for(state="visible")
            if send.count() != 1 or not send.is_enabled():
                raise RuntimeError("No unique enabled Send button. The draft was not submitted; review it in the HUD.")
            check_sender()
            allowed, reason = hub.accounts.check_permission("instagram", "send")
            if not allowed:
                raise RuntimeError(f"Send blocked by current permission: {reason}. The draft was not submitted.")
            acknowledgments = []

            def observe(response):
                ack = _send_ack(response)
                if ack:
                    acknowledgments.append(ack)

            page.on("response", observe)
            attempted = True  # a click timeout can still mean the message was submitted
            send.click()
            deadline = time.monotonic() + 15.0
            while not acknowledgments and time.monotonic() < deadline:
                page.wait_for_timeout(250)
            if not acknowledgments:
                raise DeliveryUnknown("Instagram's native Send control was activated, but no server acknowledgment was received. Check the chat in the HUD before retrying. No automatic retry was made.")
            return (f"Sent Instagram message to @{username} through Instagram's own web composer. "
                    f"Instagram acknowledgment: {acknowledgments[0]}. This does not mean the recipient has read it.")
        except DeliveryUnknown:
            raise
        except Exception as exc:
            if attempted:
                raise DeliveryUnknown("The Instagram native send was attempted, but its result is unknown. Check the chat in the HUD before retrying; no automatic retry was made.") from exc
            raise
        finally:
            # Stop this CDP client, NOT the user's persistent browser/profile.
            playwright.stop()
