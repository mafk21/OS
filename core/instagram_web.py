"""Stateful native Instagram messaging: GET-only resolution, one native submission.

No undocumented API write, speculative resend, draft overwrite or click-as-success.
Failures leave a privacy-filtered local diagnostic without requiring hidden logs.
"""
from __future__ import annotations

import json
import os
import re
import uuid
import threading
import time
from urllib.parse import urlsplit

from core.instagram_direct import DeliveryUnknown, RecipientError, receipt_id, exact_thread

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


def _open_from_compose(page, username: str, progress=lambda _: None):
    """Recover only pre-submission navigation, never retry a message write.

    Instagram's profile Message button may be missing, blocked by an overlay,
    or leave the profile unchanged. Its dedicated new-message page is a separate
    first-party route. Resolve one exact username there before opening the chat.
    """
    progress("compose_search")
    page.goto("https://www.instagram.com/direct/new/", wait_until="domcontentloaded")
    searches = page.locator('input[name="queryBox"]:visible, input[placeholder*="Search" i]:visible, '
                            'input[placeholder*="بحث"]:visible, input[aria-label*="Search" i]:visible')
    try:
        searches.first.wait_for(state="visible", timeout=5000)
    except Exception as exc:
        if not (type(exc).__name__ == "TimeoutError" and type(exc).__module__.startswith("playwright")):
            raise
        # Some versions redirect /direct/new/ to the inbox; open its composer
        # rather than waiting indefinitely for a search input that isn't there.
        progress("compose_launcher")
        names = re.compile(r"^(New message|Compose|رسالة جديدة|إنشاء رسالة)$", re.I)
        launcher = page.get_by_role("button", name=names).or_(page.get_by_role("link", name=names))
        icons = page.locator('svg[aria-label="New message"], svg[aria-label="رسالة جديدة"]')
        launcher = launcher.or_(icons.locator('xpath=ancestor::*[self::button or @role="button" or self::a][1]')).and_(page.locator(":visible"))
        launcher.first.wait_for(state="visible")
        if launcher.count() != 1:
            raise RecipientError("No unique New message control in the Instagram inbox. Nothing was sent.")
        launcher.click()
        progress("compose_search")
        searches.first.wait_for(state="visible")
    # Prefer the dedicated recipient input over the inbox's unrelated search.
    query_box = page.locator('input[name="queryBox"]:visible')
    dialog_search = page.locator('[role="dialog"] input:not([type="checkbox"]):not([type="radio"]):visible')
    if query_box.count() == 1:
        searches = query_box
    elif dialog_search.count() == 1:
        searches = dialog_search
    if searches.count() != 1:
        raise RecipientError("Instagram did not expose a unique recipient search. Nothing was sent.")
    searches.fill(username)
    progress("compose_exact_recipient")
    # Inspect only selectable search rows, not arbitrary text elsewhere in the
    # inbox. The username must be the row's primary label, not a full-name
    # substring, and there must be exactly one matching row.
    page.wait_for_function(r"""username => {
      for (const old of document.querySelectorAll('[data-jarvis-recipient]')) old.removeAttribute('data-jarvis-recipient');
      const search = document.querySelector('input[name="queryBox"], input[placeholder*="Search" i], input[placeholder*="بحث"], input[aria-label*="Search" i]');
      const scope = search?.closest('[role="dialog"]') || document.querySelector('main') || document.body;
      const normalize = s => (s || '').trim().replace(/^@/, '').toLowerCase();
      const visible = el => el.getBoundingClientRect().width > 0 && getComputedStyle(el).visibility !== 'hidden';
      const rows = Array.from(scope.querySelectorAll('button, [role="button"], [role="option"], label, [tabindex="0"]')).filter(visible);
      const matches = rows.filter(row => {
        // An exact first-party profile link is independent username evidence,
        // including rows that render a display name before the actual handle.
        const handles = Array.from(row.querySelectorAll('a[href]')).map(a => {
          try {const u = new URL(a.href); return ['www.instagram.com', 'instagram.com'].includes(u.hostname) && /^\/[a-z0-9_.]{1,30}\/?$/i.test(u.pathname) ? u.pathname.replace(/^\/|\/$/g, '').toLowerCase() : '';} catch {return '';}
        }).filter(Boolean);
        if (handles.length) return handles.every(handle => handle === username);
        const lines = (row.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
        return lines.length > 0 && normalize(lines[0]) === username;
      });
      // Only collapse nested MATCHES. An unrelated child button must not
      // discard an otherwise valid row (the previous picker did exactly that).
      const unique = matches.filter(row => !matches.some(other => other !== row && row.contains(other)));
      if (unique.length !== 1) return false;
      unique[0].setAttribute('data-jarvis-recipient', 'exact');
      return true;
    }""", arg=username, timeout=15000)
    row = page.locator('[data-jarvis-recipient="exact"]')
    selected = r"""() => Array.from(document.querySelectorAll(
      'input[type="checkbox"]:checked, input[type="radio"]:checked, [role="option"][aria-selected="true"], [role="checkbox"][aria-checked="true"], [role="radio"][aria-checked="true"]'
    )).filter(el => el.closest('[data-jarvis-recipient="exact"]') === null).length"""
    if page.evaluate(selected):
        raise RecipientError("Instagram already has another recipient selected. No group was created and nothing was sent.")
    progress("compose_selection")
    row.click()
    page.wait_for_function(r"""username => {
      const row = document.querySelector('[data-jarvis-recipient="exact"]');
      if (!row) return false;
      if (row.matches('[aria-selected="true"], [aria-checked="true"]') || row.querySelector('input:checked, [aria-checked="true"]')) return true;
      // Some layouts use an SVG selection indicator instead of a checkbox.
      // Require an exact selected-recipient chip with a removal control.
      return Array.from(document.querySelectorAll('[role="button"], button')).some(chip => {
        const label = (chip.innerText || '').trim().replace(/^@/, '').toLowerCase();
        return label === username &&
          !!chip.querySelector('[aria-label*="Remove" i], [aria-label*="إزالة"]');
      });
    }""", arg=username, timeout=5000)
    if page.evaluate(selected):
        raise RecipientError("Instagram selected more than the approved recipient. Nothing was sent.")
    # This selects a recipient, NOT a Send operation. Never click a generic
    # "Send" control here or infer success from selecting a search result.
    progress("compose_open_chat")
    next_control = page.get_by_role("button", name=re.compile(r"^(Chat|Next|دردشة|التالي)$", re.I))
    next_control.first.wait_for(state="visible")
    if next_control.count() != 1 or not next_control.is_enabled():
        raise RecipientError("Instagram did not expose a unique Chat/Next control. Nothing was sent.")
    next_control.click()
    progress("compose_chat_transition")
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
        return _open_from_compose(page, username, progress)


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


class InstagramMessageRun:
    """One operation, one owner, one write boundary, explicit terminal states.

    Browser/session recovery and recipient lookup are read-only. Once submit()
    begins, no navigation or retry branch is reachable. Playwright objects stay
    on this thread; the shared CDP runner handles its own event-loop boundary.
    """
    def __init__(self, hub, username, message, expected_sender):
        self.hub, self.username, self.message = hub, username, message
        self.expected_sender = expected_sender
        self.stage = "browser_start"
        self.history = []
        self.page = None
        self.playwright = None
        self.attempted = False
        self.acknowledgments = []

    def progress(self, stage):
        self.stage = stage
        self.history.append(stage)

    def attach(self):
        self.progress("browser_start")
        self.hub._CDP.ensure_browser(headless=True)
        self.progress("background_tab_prepare")
        url = f"https://www.instagram.com/{self.username}/"
        tab = self.hub._CDP.get_or_open_tab("instagram", url, headless=True,
                    force_navigate=True, purpose="send")
        self.progress("playwright_driver_start")
        self.playwright = _playwright().start()
        self.progress("browser_attach")
        browser = self.playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{self.hub._CDP._port}", timeout=15000)
        for context in browser.contexts:
            for candidate in context.pages:
                session = context.new_cdp_session(candidate)
                try:
                    if session.send("Target.getTargetInfo")["targetInfo"].get("targetId") == tab.get("id"):
                        self.page = candidate
                finally:
                    session.detach()
        if self.page is None:
            raise RuntimeError("Could not attach to the dedicated Instagram target.")
        self.page.set_default_timeout(12000)
        self.progress("profile_identity")
        self.page.wait_for_url(lambda url: urlsplit(str(url)).path.rstrip("/").lower() == "/" + self.username
                  or any(part in str(url) for part in ("/accounts/login", "/challenge", "/checkpoint")))
        self.page.wait_for_load_state("domcontentloaded")
        current = urlsplit(self.page.url)
        if current.hostname not in ("www.instagram.com", "instagram.com") or current.path.rstrip("/").lower() != "/" + self.username:
            raise RecipientError("Instagram redirected to login or a security check; complete that specific screen in the HUD.")

    def existing_thread(self):
        """Resolve existing exact 1:1 chats with GETs, never a speculative API POST.

        A changed/unsupported read API simply leaves the UI resolver available.
        A verified different/group identity is never accepted. Bound the work
        to three pages instead of scraping the inbox or reading message bodies.
        """
        self.progress("session_thread_lookup")
        cursor = ""
        matches = []
        for _ in range(3):
            try:
                result = self.page.evaluate(r"""async cursor => {
                  const query = new URLSearchParams({limit:'50', thread_message_limit:'0'});
                  if (cursor) query.set('cursor', cursor);
                  const response = await fetch('/api/v1/direct_v2/inbox/?' + query, {
                    method:'GET', credentials:'same-origin', redirect:'error',
                    headers:{'X-IG-App-ID':'936619743392459', 'X-Requested-With':'XMLHttpRequest'},
                    signal:AbortSignal.timeout(5000)
                  });
                  if (!response.ok) return null;
                  const payload = await response.json();
                  // Do not return message contents to Python or diagnostics.
                  if (!payload.inbox) return null;
                  return {threads:(payload.inbox.threads || []).map(t => ({
                    thread_id:t.thread_id, is_group:t.is_group,
                    users:(t.users || []).map(u => ({username:u.username}))
                  })), cursor:payload.inbox.has_older ? payload.inbox.oldest_cursor : ''};
                }""", cursor)
            except Exception:
                return None
            if not isinstance(result, dict) or not isinstance(result.get("threads"), list):
                return None
            match = exact_thread(result["threads"], self.username)
            if match:
                matches.append(match)
            cursor = result.get("cursor")
            if not isinstance(cursor, str) or not cursor:
                break
        # Repeated pagination results cannot silently resolve to another chat.
        ids = {str(t.get("thread_id") or "") for t in matches}
        ids.discard("")
        if len(ids) > 1:
            raise RecipientError("More than one exact one-to-one conversation was returned; no chat was selected.")
        if not ids:
            return None
        thread_id = ids.pop()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", thread_id):
            return None
        return thread_id

    def open_chat(self):
        thread_id = self.existing_thread()
        if thread_id:
            self.progress("resolved_thread_navigation")
            self.page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="domcontentloaded")
            root = _wait_chat(self.page, self.username)
            # A server-verified thread ID must survive native navigation; do
            # not accept a redirect to some other conversation.
            path = urlsplit(self.page.url).path.rstrip("/")
            if path.split("/")[-1] != thread_id:
                raise RecipientError("Instagram redirected to a different conversation; nothing was filled.")
            return root
        self.progress("profile_identity")
        if not _profile_verified(self.page, self.username):
            raise RecipientError("Instagram did not expose independent exact-profile identity.")
        return _open_conversation(self.page, self.username, self.progress)

    def check_sender(self):
        if self.expected_sender is None:
            return
        current = self.hub._cookie_dict("instagram")
        key = "ds_user_id" if self.expected_sender.get("ds_user_id") else "sessionid"
        if not self.expected_sender.get(key) or self.expected_sender[key] != current.get(key):
            raise RecipientError("The signed-in account changed. Request a new operation; nothing was submitted.")

    def prepare(self, root):
        self.progress("message_composer")
        composer = _composer(root)
        text = lambda: composer.input_value() if composer.evaluate("el => el.tagName === 'TEXTAREA'") else composer.inner_text()
        if text().strip():
            raise RuntimeError("This chat already has an unsent draft. It was not changed or sent.")
        self.check_sender()
        composer.fill(self.message)
        if text() != self.message:
            raise RuntimeError("The composer did not retain the exact approved message. The draft was not submitted.")
        self.progress("send_control")
        send = root.get_by_role("button", name=re.compile(r"^(Send|Send message|إرسال|ارسال|إرسال رسالة|ارسال رسالة)$", re.I))
        count = send.count()
        if count > 1 or (count == 1 and not send.is_enabled()):
            raise RuntimeError("No unique enabled Send control. The draft was not submitted.")
        self.check_sender()
        allowed, reason = self.hub.accounts.check_permission("instagram", "send")
        if not allowed:
            raise RuntimeError(f"Send blocked by current permission: {reason}. The draft was not submitted.")
        return composer, send, count

    def submit(self, composer, send, count):
        def observe(response):
            ack = _send_ack(response)
            if ack:
                self.acknowledgments.append(ack)
        self.page.on("response", observe)
        self.progress("submit_once")
        self.attempted = True  # even a click timeout may have submitted
        if count:
            send.click()
        else:
            composer.press("Enter")
        self.progress("server_receipt")
        deadline = time.monotonic() + 15
        while not self.acknowledgments and time.monotonic() < deadline:
            self.page.wait_for_timeout(250)
        if not self.acknowledgments:
            raise DeliveryUnknown("Submission was attempted but no server receipt arrived. Check the chat before retrying. No automatic retry was made.")
        self.progress("acknowledged")
        return (f"Sent Instagram message to @{self.username} through Instagram's own web composer. "
                f"Instagram acknowledgment: {self.acknowledgments[0]}. This does not mean the recipient has read it.")

    def failure_diagnostic(self):
        """Strict allowlist: never serialize DOM text, cookies, URLs or messages."""
        report = {"version": 2, "stage": self.stage, "history": self.history[-20:], "attempted": self.attempted}
        if self.page is not None:
            try:
                observed = self.page.evaluate("""() => ({
                  visible_dialogs: [...document.querySelectorAll('[role="dialog"]')].filter(e=>e.getBoundingClientRect().width).length,
                  visible_inputs: [...document.querySelectorAll('input')].filter(e=>e.getBoundingClientRect().width).length,
                  selectable_rows: document.querySelectorAll('[role="option"], [role="button"], label').length,
                  exact_rows: document.querySelectorAll('[data-jarvis-recipient="exact"]').length,
                  login_form: !!document.querySelector('input[type="password"]')
                })""")
                if isinstance(observed, dict):
                    for key in ("visible_dialogs", "visible_inputs", "selectable_rows", "exact_rows", "login_form"):
                        if type(observed.get(key)) in (int, bool):
                            report[key] = observed[key]
            except Exception:
                pass
        try:
            directory = self.hub.socials_root_dir()
            target = directory / "instagram_last_failure.json"
            temporary = directory / (".instagram-diagnostic-" + uuid.uuid4().hex)
            try:
                with temporary.open("x", encoding="utf-8") as stream:
                    os.chmod(temporary, 0o600)
                    json.dump(report, stream)
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        except Exception:
            pass
        return report

    def fail(self, exc):
        diagnostic = self.failure_diagnostic()
        if self.attempted:
            raise DeliveryUnknown(f"[IG:{self.stage}] The send was attempted but its result is unknown. Check the chat before retrying. No automatic retry was made.") from exc
        if isinstance(exc, (RecipientError, RuntimeError)) and not type(exc).__module__.startswith("playwright"):
            raise type(exc)(f"[IG:{self.stage}] {exc}") from exc
        explanations = {
            "compose_search": "Instagram's recipient search input did not appear.",
            "compose_launcher": "The inbox did not expose an accessible New Message control.",
            "compose_exact_recipient": "The search did not produce one verifiable exact username row.",
            "compose_selection": "The exact recipient row did not expose a verifiable selected state.",
            "compose_open_chat": "The selected recipient did not produce an enabled Chat/Next control.",
            "compose_chat_transition": "Instagram did not open the selected recipient's conversation.",
            "session_thread_lookup": "The read-only session lookup could not resolve the recipient.",
        }
        reason = explanations.get(self.stage, "Instagram did not complete this operation state.")
        if self.stage in ("browser_start", "background_tab_prepare", "playwright_driver_start", "browser_attach"):
            reason = "The dedicated browser control could not start or attach; this is not an Instagram login error."
        if diagnostic.get("login_form"):
            reason += " A login form is actually visible in the browser."
        counts = ", ".join(f"{k}={diagnostic[k]}" for k in ("visible_inputs", "selectable_rows", "exact_rows") if k in diagnostic)
        raise RuntimeError(f"[IG:{self.stage}] {reason} Nothing was submitted. "
                           f"Diagnostic v2: {counts or 'page unavailable'}. Details: ~/.jarvis_socials/instagram_last_failure.json (or JARVIS_SOCIALS_DIR).") from exc

    def run(self):
        try:
            self.attach()
            root = self.open_chat()
            return self.submit(*self.prepare(root))
        except Exception as exc:
            self.fail(exc)
        finally:
            if self.playwright is not None:
                try:
                    self.playwright.stop()
                except Exception:
                    pass


def send_instagram_message(hub, recipient: str, message: str, *, expected_sender: dict | None = None) -> str:
    """Native Instagram send engine; this entry point never retries a write."""
    username = recipient.strip().lstrip("@").lower()
    if not re.fullmatch(r"[a-z0-9_.]{1,30}", username):
        raise RecipientError("Use an exact Instagram @username. Nothing was sent.")
    with _LOCK:
        return InstagramMessageRun(hub, username, message, expected_sender).run()
