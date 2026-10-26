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


def _profile_verified(page, username: str) -> bool:
    """Canonical metadata OR an exact profile-header username, never a display name."""
    metadata = page.locator('link[rel="canonical"], meta[property="og:url"]')
    for i in range(metadata.count()):
        node = metadata.nth(i)
        identity = urlsplit(node.get_attribute("href") or node.get_attribute("content") or "")
        if identity.hostname in ("www.instagram.com", "instagram.com") and identity.path.rstrip("/").lower() == "/" + username:
            return True
    return page.evaluate("""username => Array.from(document.querySelectorAll(
      'main header h1, main header h2, main header [role="heading"], main > div header a'
    )).some(el => (el.innerText || '').trim().replace(/^@/, '').toLowerCase() === username)""", username) is True


_CHAT_READY_JS = r"""username => {
  if (/\/(accounts\/login|challenge|checkpoint)(\/|$)/.test(location.pathname)) return 'blocked';
  // A profile may open a chat dialog without navigating to /direct/t/.
  for (const dialog of document.querySelectorAll('[role="dialog"]')) {
    if (!dialog.getBoundingClientRect().width) continue;
    const identity = Array.from(dialog.querySelectorAll('a[href]')).some(a => {
      const u = new URL(a.href);
      return ['www.instagram.com', 'instagram.com'].includes(u.hostname) &&
             u.pathname.replace(/\/$/, '').toLowerCase() === '/' + username;
    });
    if (identity && dialog.querySelector('textarea, [role="textbox"][contenteditable="true"]')) {
      dialog.setAttribute('data-jarvis-verified-chat', 'true');
      return 'dialog';
    }
  }
  return /^\/direct\/(?:e2ee\/)?t\/[^/]+/.test(location.pathname) ? 'thread' : false;
}"""


def _wait_chat(page, username: str, *, timeout: int = 12000):
    state = page.wait_for_function(_CHAT_READY_JS, arg=username, timeout=timeout).json_value()
    if state == "blocked":
        raise RecipientError("Complete Instagram's login/security check in the HUD; nothing was sent.")
    return page.locator('[data-jarvis-verified-chat="true"]') if state == "dialog" else page


def _open_from_compose(page, username: str):
    """Recover only pre-submission navigation, never retry a message write.

    Instagram's profile Message button may be missing, blocked by an overlay,
    or leave the profile unchanged. Its dedicated new-message page is a separate
    first-party route. Resolve one exact username there before opening the chat.
    """
    page.goto("https://www.instagram.com/direct/new/", wait_until="domcontentloaded")
    searches = page.locator('input[name="queryBox"]:visible, input[placeholder*="Search" i]:visible, '
                            'input[placeholder*="بحث"]:visible, input[aria-label*="Search" i]:visible')
    searches.first.wait_for(state="visible")
    if searches.count() != 1:
        raise RecipientError("Instagram did not expose a unique recipient search. Nothing was sent.")
    searches.fill(username)
    # Inspect only selectable search rows, not arbitrary text elsewhere in the
    # inbox. The username must be the row's primary label, not a full-name
    # substring, and there must be exactly one matching row.
    page.wait_for_function(r"""username => {
      for (const old of document.querySelectorAll('[data-jarvis-recipient]')) old.removeAttribute('data-jarvis-recipient');
      const rows = Array.from(document.querySelectorAll('[role="button"], label'))
        .filter(row => row.getBoundingClientRect().width && row.querySelector('input[type="checkbox"], [role="checkbox"], [role="radio"], input[type="radio"]'));
      const matches = rows.filter(row => {
        const lines = (row.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
        return lines[0] && lines[0].replace(/^@/, '').toLowerCase() === username;
      }).filter(row => !rows.some(other => other !== row && row.contains(other)));
      if (matches.length !== 1) return false;
      matches[0].setAttribute('data-jarvis-recipient', 'exact');
      return true;
    }""", arg=username, timeout=15000)
    row = page.locator('[data-jarvis-recipient="exact"]')
    selected = r"""() => Array.from(document.querySelectorAll(
      'input[type="checkbox"]:checked, input[type="radio"]:checked, [role="checkbox"][aria-checked="true"], [role="radio"][aria-checked="true"]'
    )).filter(el => el.closest('[data-jarvis-recipient="exact"]') === null).length"""
    if page.evaluate(selected):
        raise RecipientError("Instagram already has another recipient selected. No group was created and nothing was sent.")
    row.click()
    page.wait_for_function(r"""() => {
      const row = document.querySelector('[data-jarvis-recipient="exact"]');
      return row && row.querySelector('input:checked, [aria-checked="true"]');
    }""", timeout=5000)
    if page.evaluate(selected):
        raise RecipientError("Instagram selected more than the approved recipient. Nothing was sent.")
    # This selects a recipient, NOT a Send operation. Never click a generic
    # "Send" control here or infer success from selecting a search result.
    next_control = page.get_by_role("button", name=re.compile(r"^(Chat|Next|دردشة|التالي)$", re.I))
    next_control.first.wait_for(state="visible")
    if next_control.count() != 1 or not next_control.is_enabled():
        raise RecipientError("Instagram did not expose a unique Chat/Next control. Nothing was sent.")
    next_control.click()
    return _wait_chat(page, username)


def _open_conversation(page, username: str, progress):
    names = re.compile(r"^(Message|Send message|إرسال رسالة|ارسال رسالة|رسالة)$", re.I)
    try:
        progress("profile_message_control")
        # Hidden responsive copies should not make a unique visible control
        # appear ambiguous or cause us to wait forever on the first hidden one.
        buttons = page.get_by_role("button", name=names).or_(page.get_by_role("link", name=names)).and_(page.locator(":visible"))
        buttons.first.wait_for(state="visible", timeout=8000)
        if buttons.count() != 1:
            raise RecipientError("No unique visible profile Message control.")
        buttons.click(timeout=8000)
        progress("conversation_transition")
        return _wait_chat(page, username)
    except Exception as exc:
        # Only a Playwright timeout justifies navigation recovery; identity,
        # security-check and other explicit failures must not be bypassed.
        if not (type(exc).__name__ == "TimeoutError" and type(exc).__module__.startswith("playwright")):
            raise
        # A click can finish navigating just as its wait expires. Inspect state
        # again before abandoning it, without filling or submitting anything.
        state = page.evaluate(_CHAT_READY_JS, username)
        if state == "blocked":
            raise RecipientError("Complete Instagram's login/security check in the HUD; nothing was sent.") from exc
        if state in ("thread", "dialog"):
            return page.locator('[data-jarvis-verified-chat="true"]') if state == "dialog" else page
        progress("compose_recipient_lookup")
        return _open_from_compose(page, username)


def _composer(root):
    # Prefer a message-labelled composer to an unrelated visible search box.
    preferred = root.locator('textarea[placeholder*="message" i]:visible, '
        '[role="textbox"][contenteditable="true"][aria-label*="message" i]:visible, '
        'textarea[placeholder*="رسالة"]:visible, '
        '[role="textbox"][contenteditable="true"][aria-label*="رسالة"]:visible')
    preferred.first.wait_for(state="visible") if preferred.count() else None
    if preferred.count() == 1:
        return preferred.first
    candidates = root.locator('textarea[placeholder]:visible, [role="textbox"][contenteditable="true"]:visible')
    candidates.first.wait_for(state="visible")
    if candidates.count() != 1:
        raise RecipientError("No unique Instagram message composer. Open the intended chat in the HUD; nothing was sent.")
    return candidates.first


def send_instagram_message(hub, recipient: str, message: str, *, expected_sender: dict | None = None) -> str:
    """Use the exact profile's Message button, then wait for a server send receipt."""
    username = recipient.strip().lstrip("@").lower()
    if not re.fullmatch(r"[a-z0-9_.]{1,30}", username):
        raise RecipientError("Use an exact Instagram @username. Nothing was sent.")
    attempted = False
    step = "browser_start"
    playwright = None
    with _LOCK:
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            tab = hub._CDP.get_or_open_tab("instagram", profile_url, headless=True,
                                          force_navigate=True, purpose="send")
            playwright = _playwright().start()
            step = "browser_attach"
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
            step = "profile_identity"
            page.wait_for_url(lambda url: urlsplit(str(url)).path.rstrip("/").lower() == "/" + username
                              or any(part in str(url) for part in ("/accounts/login", "/challenge", "/checkpoint")))
            page.wait_for_load_state("domcontentloaded")
            parsed = urlsplit(page.url)
            if parsed.hostname not in ("www.instagram.com", "instagram.com") or parsed.path.rstrip("/").lower() != "/" + username:
                raise RecipientError("Instagram requires login or a security check. Complete it in the HUD; nothing was sent.")
            # SPA pages can omit/stale their canonical metadata. A rendered,
            # exact username in the profile header is independent identity proof.
            if not _profile_verified(page, username):
                raise RecipientError("Instagram did not confirm the exact profile identity. Nothing was sent.")
            def progress(value):
                nonlocal step
                step = value
            root = _open_conversation(page, username, progress)
            step = "message_composer"
            composer = _composer(root)
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
            actual = composer.input_value() if composer.evaluate("el => el.tagName === 'TEXTAREA'") else composer.inner_text()
            if actual != message:
                raise RuntimeError("The composer did not retain the exact approved text. The draft was not submitted.")
            step = "send_control"
            send = root.get_by_role("button", name=re.compile(r"^(Send|Send message|إرسال|ارسال|إرسال رسالة|ارسال رسالة)$", re.I))
            count = send.count()
            if count > 1 or (count == 1 and not send.is_enabled()):
                raise RuntimeError("No unique enabled Send control. The draft was not submitted; review it in the HUD.")
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
            step = "submit_once"
            attempted = True  # a click timeout can still mean the message was submitted
            if count == 1:
                send.click()
            else:
                # Instagram also exposes Enter-to-send composers with no
                # labelled Send button. Submit only this verified composer.
                composer.press("Enter")
            step = "server_receipt"
            deadline = time.monotonic() + 15.0
            while not acknowledgments and time.monotonic() < deadline:
                page.wait_for_timeout(250)
            if not acknowledgments:
                raise DeliveryUnknown("Instagram's native Send control was activated, but no server acknowledgment was received. Check the chat in the HUD before retrying. No automatic retry was made.")
            return (f"Sent Instagram message to @{username} through Instagram's own web composer. "
                    f"Instagram acknowledgment: {acknowledgments[0]}. This does not mean the recipient has read it.")
        except DeliveryUnknown as exc:
            raise DeliveryUnknown(f"[IG:{step}] {exc}") from exc
        except Exception as exc:
            if attempted:
                raise DeliveryUnknown(f"[IG:{step}] The Instagram native send was attempted, but its result is unknown. Check the chat in the HUD before retrying; no automatic retry was made.") from exc
            if isinstance(exc, RecipientError):
                raise RecipientError(f"[IG:{step}] {exc}") from exc
            if isinstance(exc, RuntimeError) and not type(exc).__module__.startswith("playwright"):
                raise RuntimeError(f"[IG:{step}] {exc}") from exc
            # Playwright call logs may contain approved message text; do not
            # expose those logs or hide the failing step behind a generic error.
            raise RuntimeError(f"[IG:{step}] {type(exc).__name__}. Open Instagram DMs in the HUD and check login, security prompts, or an unsent draft. Nothing was submitted.") from exc
        finally:
            # Cleanup cannot turn an acknowledged send into a failure/retry.
            if playwright is not None:
                try:
                    playwright.stop()
                except Exception:
                    pass
