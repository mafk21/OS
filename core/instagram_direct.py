"""Instagram Direct session transport and conservative recipient/receipt checks.

The web API is undocumented and may change. Never interpret a click, HTTP 200,
optimistic UI text, or a timeout as a delivery receipt. Never retry a POST.
"""
from __future__ import annotations

import json
from urllib.parse import urlencode, urlsplit

import httpx


class RecipientError(RuntimeError):
    pass


class SendRejected(RuntimeError):
    pass


class DeliveryUnknown(RuntimeError):
    pass


def exact_thread(threads: list, contact: str) -> dict | None:
    """Resolve only an exact username in a one-to-one thread, never a group/name fragment."""
    needle = contact.strip().lstrip("@").casefold()
    if not needle:
        return threads[0] if threads else None
    matches = []
    for thread in threads:
        users = thread.get("users") or []
        if len(users) == 1 and not thread.get("is_group"):
            if str(users[0].get("username") or "").casefold() == needle:
                matches.append(thread)
    if len(matches) > 1:
        raise RecipientError("Multiple matching conversations. Open the intended chat in the HUD; nothing was sent.")
    return matches[0] if matches else None


def receipt_id(payload: dict) -> str:
    """An API success must include a provider-issued message identifier."""
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        return ""
    for node in (payload.get("payload"), payload.get("message_metadata"), payload):
        if isinstance(node, dict):
            value = node.get("item_id") or node.get("message_id")
            if isinstance(value, (str, int)) and str(value):
                return str(value)
    return ""


class InstagramSession:
    """Use the authenticated browser when available; otherwise encrypted-cookie HTTP.

    A rejected/failed GET may safely switch to same-origin browser fetch (the
    browser supplies current session cookies and CSRF). Writes are issued once
    through the transport selected during recipient lookup, with no fallback.
    """
    def __init__(self, hub, cookies: dict):
        self.hub = hub
        self.http = httpx.Client(headers=hub._ig_headers(cookies), cookies=cookies,
                                 follow_redirects=False, timeout=12.0)
        self.browser = hub._CDP._endpoint_alive()
        self.ws_url = ""
        self.cookies = self.http.cookies
        self.headers = self.http.headers

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.http.close()

    def _fetch(self, url: str, method: str, data=None):
        # Only fixed, same-origin Instagram endpoints may receive credentials.
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "www.instagram.com":
            raise ValueError("Invalid Instagram endpoint")
        hub = self.hub
        if not self.ws_url:
            tab = hub._CDP.get_or_open_tab(
                "instagram", hub.SOCIAL_PLATFORMS["instagram"]["inbox_url"],
                headless=True, force_navigate=False, purpose="automation")
            self.ws_url = str(tab["webSocketDebuggerUrl"])
            hub._CDP.run_on_tab(self.ws_url,
                               lambda c, w: hub._cdp_wait_settled(c, w, 0.5), timeout=15.0)
        expression = """(async () => {
          const request = __REQUEST__;
          if (location.origin !== 'https://www.instagram.com') throw new Error('Instagram login required');
          const csrf = document.cookie.split('; ').find(c => c.startsWith('csrftoken='));
          const headers = {'X-IG-App-ID': '936619743392459', 'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf ? decodeURIComponent(csrf.slice(10)) : ''};
          const opts = {method: request.method, credentials: 'same-origin', headers,
                        signal: AbortSignal.timeout(12000), redirect: 'error'};
          if (request.body !== null) {headers['Content-Type'] = 'application/x-www-form-urlencoded'; opts.body = request.body;}
          const response = await fetch(request.url, opts);
          return {status: response.status, body: await response.text()};
        })()""".replace("__REQUEST__", json.dumps({"method": method, "url": url,
                  "body": urlencode(data) if data is not None else None}))
        result = hub._CDP.run_on_tab(self.ws_url,
                                    lambda c, w: hub._cdp_eval_json(c, w, expression), timeout=20.0)
        if not isinstance(result, dict) or not isinstance(result.get("status"), int):
            raise RuntimeError("Instagram did not return a response. Open its HUD to check login/challenges.")
        return httpx.Response(result["status"], text=str(result.get("body") or ""))

    def _observe(self, result):
        try:
            payload = result.json()
        except ValueError:
            payload = {}
        health = None
        if isinstance(payload, dict):
            marker = str(payload.get("message") or "").lower()
            if "login_required" in marker or result.status_code == 401:
                health = "login_required"
            elif payload.get("challenge") or "challenge_required" in marker or "checkpoint_required" in marker:
                health = "challenge_required"
            elif isinstance(payload.get("inbox"), dict) or isinstance(payload.get("thread"), dict):
                health = "authenticated"
        if health:
            self.hub._set_session_health("instagram", health)
        return result

    def get(self, url: str, params=None):
        if params:
            url += "?" + urlencode(params)
        if self.browser:
            return self._observe(self._fetch(url, "GET"))
        try:
            result = self.http.get(url)
            # Login redirects, anti-bot responses and non-JSON pages are not an inbox.
            payload = result.json()
            if result.status_code == 200 and isinstance(payload, dict) and payload.get("status") != "fail":
                return self._observe(result)
            self._observe(result)
        except (httpx.HTTPError, ValueError):
            pass
        self.browser = True
        return self._observe(self._fetch(url, "GET"))

    def prepare_write(self):
        """Refresh HTTP CSRF from the server before crossing the write boundary."""
        if self.browser:
            return
        def csrf_cookie():
            candidates = [c for c in self.http.cookies.jar if c.name == "csrftoken" and c.value
                          and (not c.domain or c.domain.lstrip(".") in ("instagram.com", "www.instagram.com"))]
            candidates.sort(key=lambda c: bool(c.domain))
            return candidates[-1].value if candidates else ""
        csrf = csrf_cookie()
        if not csrf:
            # This is a safe read, not a speculative first send.
            self.http.get("https://www.instagram.com/")
            csrf = csrf_cookie()
        if not csrf:
            raise RuntimeError("Instagram did not provide a current CSRF token. Use its native web composer.")
        self.http.headers["X-CSRFToken"] = csrf

    def post(self, url: str, data):
        # In particular, do NOT catch a timeout here and submit via another path.
        result = self._fetch(url, "POST", data) if self.browser else self.http.post(url, data=data)
        return self._observe(result)
