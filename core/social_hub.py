"""
core/social_hub.py — Personal Social Accounts Hub (Instagram, Snapchat, TikTok, X, WhatsApp, Reddit).

Provides:
  1. Persistent Isolated Social Browser Profile (`~/.jarvis_socials/browser_profile`)
     that never collides with the user's open Chrome/Edge windows and stays signed in
     across restarts.
  2. 1-Click Browser Cookie Import (`yt-dlp` browser cookie extractor -> encrypted
     Playwright cookie vault `~/.jarvis_socials/cookies_<platform>.enc` protected by
     `core.security_vault` AES-256-GCM) OR Interactive Sign-In / QR Window with
     automatic login-completion detection.
  3. Hybrid ARIA/DOM + Multimodal Vision (`GPT-4o` / `Gemini Vision`) Social Inbox
     inspector (`check_social_inbox`, `read_social_messages`).
  4. Unforgeable HUD Confirmation Gate (`core.confirm.request`) + SHA-256 Audit Log
     (`core.security_vault.log_audit_event`) before sending any DM, Snap chat reply,
     or social post when permission is `ask` (default).
  5. Hands-Free Voice Feed & Reel Control (`open_reels`, `next`, `previous`, `like`,
     `save`, `open_profile`, `look`).
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from io import BytesIO
import json
import os
from pathlib import Path
import re
import stat
import threading
import time
from typing import Any, Callable
import webbrowser

from core import confirm as confirm_gate
from core import security_vault
from memory import accounts

SOCIAL_PLATFORMS: dict[str, dict[str, Any]] = {
    "instagram": {
        "label": "Instagram",
        "home_url": "https://www.instagram.com/",
        "login_url": "https://www.instagram.com/accounts/login/",
        "inbox_url": "https://www.instagram.com/direct/inbox/",
        "notifications_url": "https://www.instagram.com/notifications/",
        "reels_url": "https://www.instagram.com/reels/",
        "compose_post_url": "https://www.instagram.com/",
        "profile_url_tpl": "https://www.instagram.com/{handle}/",
        "domains": ("instagram.com",),
        "auth_cookies": ("sessionid", "ds_user_id"),
        "logged_in_selectors": (
            'a[href*="/direct/inbox"]',
            'svg[aria-label="Direct"]',
            'svg[aria-label="Home"]',
            'a[href*="/reels/"]',
        ),
    },
    "snapchat": {
        "label": "Snapchat",
        "home_url": "https://web.snapchat.com/",
        "login_url": "https://web.snapchat.com/",
        "inbox_url": "https://web.snapchat.com/",
        "notifications_url": "https://web.snapchat.com/",
        "reels_url": "https://www.snapchat.com/spotlight",
        "compose_post_url": "https://web.snapchat.com/",
        "profile_url_tpl": "https://www.snapchat.com/add/{handle}",
        "domains": ("snapchat.com",),
        "auth_cookies": ("sc-a-session", "__Host-sc-a-session", "sc-a-nonce"),
        "logged_in_selectors": (
            '[ role="list" ]',
            'button[aria-label*="Chat" i]',
            'input[placeholder*="Search" i]',
        ),
    },
    "tiktok": {
        "label": "TikTok",
        "home_url": "https://www.tiktok.com/foryou",
        "login_url": "https://www.tiktok.com/login",
        "inbox_url": "https://www.tiktok.com/messages",
        "notifications_url": "https://www.tiktok.com/foryou",
        "reels_url": "https://www.tiktok.com/foryou",
        "compose_post_url": "https://www.tiktok.com/tiktokstudio/upload",
        "profile_url_tpl": "https://www.tiktok.com/@{handle}",
        "domains": ("tiktok.com",),
        "auth_cookies": ("sessionid", "sessionid_ss", "sid_tt", "uid_tt"),
        "logged_in_selectors": (
            '[data-e2e="profile-icon"]',
            'a[href*="/messages"]',
            '[data-e2e="inbox-icon"]',
        ),
    },
    "x": {
        "label": "X",
        "home_url": "https://x.com/home",
        "login_url": "https://x.com/i/flow/login",
        "inbox_url": "https://x.com/messages",
        "notifications_url": "https://x.com/notifications",
        "reels_url": "https://x.com/explore",
        "compose_post_url": "https://x.com/compose/post",
        "profile_url_tpl": "https://x.com/{handle}",
        "domains": ("x.com", "twitter.com"),
        "auth_cookies": ("auth_token", "twid"),
        "logged_in_selectors": (
            '[data-testid="AppTabBar_DirectMessage_Link"]',
            '[data-testid="SideNav_AccountSwitcher_Button"]',
            '[data-testid="tweetTextarea_0"]',
        ),
    },
    "whatsapp": {
        "label": "WhatsApp",
        "home_url": "https://web.whatsapp.com/",
        "login_url": "https://web.whatsapp.com/",
        "inbox_url": "https://web.whatsapp.com/",
        "notifications_url": "https://web.whatsapp.com/",
        "reels_url": "https://web.whatsapp.com/",
        "compose_post_url": "https://web.whatsapp.com/",
        "profile_url_tpl": "https://web.whatsapp.com/",
        "domains": ("whatsapp.com",),
        "auth_cookies": (),
        "logged_in_selectors": (
            "#pane-side",
            '[aria-label*="Chat list" i]',
            '[data-testid="chat-list"]',
        ),
    },
    "reddit": {
        "label": "Reddit",
        "home_url": "https://www.reddit.com/",
        "login_url": "https://www.reddit.com/login/",
        "inbox_url": "https://www.reddit.com/message/inbox/",
        "notifications_url": "https://www.reddit.com/notifications",
        "reels_url": "https://www.reddit.com/r/popular/",
        "compose_post_url": "https://www.reddit.com/submit",
        "profile_url_tpl": "https://www.reddit.com/user/{handle}/",
        "domains": ("reddit.com",),
        "auth_cookies": ("reddit_session", "token_v2"),
        "logged_in_selectors": (
            'a[href*="/message/inbox"]',
            'button[id*="USER_DROPDOWN" i]',
            'faceplate-tracker[noun="user_menu"]',
        ),
    },
}

_PLATFORM_ALIASES: dict[str, str] = {
    "ig": "instagram",
    "insta": "instagram",
    "instagram": "instagram",
    "snap": "snapchat",
    "snapchat": "snapchat",
    "sc": "snapchat",
    "tt": "tiktok",
    "tik_tok": "tiktok",
    "tiktok": "tiktok",
    "x": "x",
    "twitter": "x",
    "tweet": "x",
    "wa": "whatsapp",
    "whats_app": "whatsapp",
    "whatsapp": "whatsapp",
    "reddit": "reddit",
}


def normalize_social_platform(raw: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", (raw or "").strip().lower()).strip("_")
    return _PLATFORM_ALIASES.get(key, "")


def socials_root_dir() -> Path:
    env_dir = os.environ.get("JARVIS_SOCIALS_DIR", "").strip()
    root = Path(env_dir).expanduser() if env_dir else (Path.home() / ".jarvis_socials")
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, stat.S_IRWXU)
    except Exception:
        pass
    return root


def _cookie_vault_file(platform: str) -> Path:
    return socials_root_dir() / f"cookies_{platform}.enc"


def save_encrypted_cookies(platform: str, cookies: list[dict[str, Any]]) -> None:
    if not cookies:
        return
    raw_json = json.dumps(cookies, ensure_ascii=False)
    enc = security_vault.encrypt_secret(raw_json)
    fp = _cookie_vault_file(platform)
    fp.write_text(enc, encoding="utf-8")
    try:
        os.chmod(fp, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass


def load_encrypted_cookies(platform: str) -> list[dict[str, Any]]:
    fp = _cookie_vault_file(platform)
    if not fp.is_file():
        return []
    try:
        enc = fp.read_text(encoding="utf-8").strip()
        dec = security_vault.decrypt_secret(enc)
        parsed = json.loads(dec)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def clear_encrypted_cookies(platform: str) -> None:
    fp = _cookie_vault_file(platform)
    try:
        if fp.exists():
            fp.unlink()
    except Exception:
        pass


def _candidate_browsers(preferred: str = "") -> list[str]:
    p = (preferred or "").strip().lower()
    if p and p != "auto":
        return [p]
    if os.name == "nt":
        return ["chrome", "edge", "brave", "firefox"]
    return ["chrome", "brave", "firefox", "safari", "chromium", "edge"]


def import_cookies_from_browser(
    platform: str,
    browser: str = "auto",
    *,
    handle: str = "",
    permission: str = "ask",
) -> dict[str, Any]:
    """Import active session cookies for `platform` from an installed browser into the AES-256-GCM vault."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform: {platform}"}

    spec = SOCIAL_PLATFORMS[plat]
    domains: tuple[str, ...] = spec["domains"]
    auth_names: set[str] = set(spec["auth_cookies"])

    try:
        from yt_dlp.cookies import extract_cookies_from_browser
    except Exception as exc:
        return {"ok": False, "error": f"Cookie extractor unavailable: {exc}"}

    last_err = ""
    for cand in _candidate_browsers(browser):
        try:
            jar = extract_cookies_from_browser(cand)
        except Exception as exc:
            last_err = str(exc)
            continue

        matched: list[dict[str, Any]] = []
        found_names: set[str] = set()
        for c in jar:
            dom = str(getattr(c, "domain", "") or "").lower()
            if not any(dom == d or dom.endswith("." + d) or dom.endswith(d) for d in domains):
                continue
            name = str(getattr(c, "name", "") or "")
            val = str(getattr(c, "value", "") or "")
            if not name or not val:
                continue
            found_names.add(name)
            item: dict[str, Any] = {
                "name": name,
                "value": val,
                "domain": getattr(c, "domain", "") or f".{domains[0]}",
                "path": getattr(c, "path", "/") or "/",
                "secure": bool(getattr(c, "secure", True)),
            }
            exp = getattr(c, "expires", None)
            if isinstance(exp, (int, float)) and exp > 0:
                item["expires"] = float(exp)
            matched.append(item)

        has_auth = bool(found_names & auth_names) if auth_names else (len(matched) >= 2)
        if matched and has_auth:
            save_encrypted_cookies(plat, matched)
            accounts.connect_account(
                plat,
                handle=handle.lstrip("@"),
                cookies_browser=cand,
                session_connected=True,
                auth_mode="browser_cookies",
                permission=permission if permission in accounts.PERMISSIONS else "ask",
            )
            security_vault.log_audit_event(
                "user",
                f"social_connect_cookies:{plat}",
                {"platform": plat, "browser": cand, "cookie_count": len(matched)},
                result_summary=f"Imported {len(matched)} {spec['label']} session cookies from {cand}.",
                status="ok",
            )
            return {
                "ok": True,
                "platform": plat,
                "label": spec["label"],
                "browser": cand,
                "cookie_count": len(matched),
                "auth_mode": "browser_cookies",
            }

    return {
        "ok": False,
        "platform": plat,
        "error": (
            f"No signed-in {spec['label']} cookies found in {browser or 'local browsers'}"
            + (f" ({last_err})" if last_err else "")
            + f". Click 'Sign In Window' to log into {spec['label']} directly."
        ),
    }


# ── Persistent Playwright Social Session Runtime ──────────────────────────────


class _SocialSessionRuntime:
    """Thread-safe dedicated asyncio loop managing `~/.jarvis_socials/browser_profile`."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._pw: Any = None
        self._ctx: Any = None
        self._headless: bool | None = None
        self._pages: dict[str, Any] = {}

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        with self._lock:
            if self._loop is not None and self._loop.is_running():
                return self._loop
            ready = threading.Event()

            def _runner() -> None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self._loop = loop
                ready.set()
                loop.run_forever()

            t = threading.Thread(target=_runner, daemon=True, name="jarvis-socials-loop")
            t.start()
            ready.wait(timeout=5.0)
            self._thread = t
            assert self._loop is not None
            return self._loop

    def run(self, coro: Any, timeout: float = 45.0) -> Any:
        loop = self._ensure_loop()
        fut = asyncio.run_coroutine_threadsafe(coro, loop)
        return fut.result(timeout=timeout)

    async def _ensure_context(self, *, headless: bool = False) -> Any:
        from playwright.async_api import async_playwright

        # If currently running headless and caller needs a visible window (e.g. Sign-In / Feed), reopen headed!
        if self._ctx is not None and self._headless is True and headless is False:
            try:
                await self._ctx.close()
            except Exception:
                pass
            self._ctx = None
            self._pages.clear()

        if self._ctx is not None:
            return self._ctx

        if self._pw is None:
            self._pw = await async_playwright().start()

        profile_dir = socials_root_dir() / "browser_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        # Clean stale Chromium singleton lock if left behind by a crashed process
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lp = profile_dir / lock_name
            if lp.is_symlink() or lp.exists():
                try:
                    lp.unlink()
                except Exception:
                    pass

        launch_kwargs: dict[str, Any] = {
            "user_data_dir": str(profile_dir),
            "headless": bool(headless),
            "viewport": {"width": 1280, "height": 840},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--no-first-run",
            ],
            "permissions": ["notifications"],
        }

        ctx = None
        for channel in ("chrome", "msedge", None):
            try:
                kw = dict(launch_kwargs)
                if channel:
                    kw["channel"] = channel
                ctx = await self._pw.chromium.launch_persistent_context(**kw)
                break
            except Exception:
                continue

        if ctx is None:
            raise RuntimeError(
                "Could not launch Chrome/Edge/Chromium via Playwright. "
                "Install Chrome/Edge or run: python -m playwright install chromium"
            )

        self._ctx = ctx
        self._headless = bool(headless)

        # Hydrate any encrypted vault cookies across all social platforms
        for plat_key in SOCIAL_PLATFORMS:
            vault_cookies = load_encrypted_cookies(plat_key)
            if vault_cookies:
                try:
                    await ctx.add_cookies(vault_cookies)
                except Exception:
                    pass

        return ctx

    async def get_page(self, platform: str, *, headless: bool = True) -> Any:
        ctx = await self._ensure_context(headless=headless)
        existing = self._pages.get(platform)
        if existing is not None:
            try:
                if not existing.is_closed():
                    return existing
            except Exception:
                pass
        # Reuse blank initial page if available
        for pg in ctx.pages:
            try:
                if pg.url in ("about:blank", "") and pg not in self._pages.values():
                    self._pages[platform] = pg
                    return pg
            except Exception:
                continue
        pg = await ctx.new_page()
        self._pages[platform] = pg
        return pg

    async def check_logged_in(self, platform: str, page: Any | None = None) -> tuple[bool, str]:
        spec = SOCIAL_PLATFORMS[platform]
        ctx = self._ctx
        if ctx is None:
            return False, ""

        try:
            cookies = await ctx.cookies()
        except Exception:
            cookies = []

        domains = spec["domains"]
        auth_names = set(spec["auth_cookies"])
        plat_cookies = [
            c
            for c in cookies
            if any(
                str(c.get("domain", "")).lower().endswith(d)
                for d in domains
            )
        ]
        found_names = {str(c.get("name", "")) for c in plat_cookies}
        if auth_names and (found_names & auth_names):
            save_encrypted_cookies(platform, plat_cookies)
            return True, ""

        if page is not None:
            url_low = (page.url or "").lower()
            if not any(k in url_low for k in ("/login", "/flow/login", "accounts.snapchat.com/accounts/v2/login")):
                for sel in spec["logged_in_selectors"]:
                    try:
                        loc = page.locator(sel)
                        if await loc.count() > 0:
                            if plat_cookies:
                                save_encrypted_cookies(platform, plat_cookies)
                            return True, ""
                    except Exception:
                        continue
        return False, ""

    async def clear_platform(self, platform: str) -> None:
        pg = self._pages.pop(platform, None)
        if pg is not None:
            try:
                if not pg.is_closed():
                    await pg.close()
            except Exception:
                pass


_RUNTIME = _SocialSessionRuntime()


def _dismiss_common_popups_js() -> str:
    return """
    () => {
      const labels = ['not now', 'maybe later', 'decline optional cookies', 'allow all cookies', 'dismiss'];
      const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
      for (const b of buttons) {
        const txt = (b.innerText || b.getAttribute('aria-label') || '').trim().toLowerCase();
        if (labels.includes(txt)) {
          try { b.click(); } catch (_) {}
        }
      }
    }
    """


def _extract_dom_snapshot_js() -> str:
    return """
    () => {
      const clean = (s) => (s || '').replace(/\\s+/g, ' ').trim();
      const out = {
        title: document.title || '',
        url: location.href || '',
        unread_badges: [],
        items: [],
      };
      const badgeEls = document.querySelectorAll('[aria-label*="unread" i], [aria-label*="new" i], [data-testid*="unread" i]');
      for (const el of Array.from(badgeEls).slice(0, 20)) {
        const t = clean(el.getAttribute('aria-label') || el.innerText);
        if (t && t.length < 180) out.unread_badges.push(t);
      }
      const rowSelectors = [
        '[role="listitem"]',
        '[role="row"]',
        '[data-testid="conversation"]',
        '[data-testid="cellInnerDiv"]',
        '[data-testid="messageEntry"]',
        'article',
      ];
      const seen = new Set();
      for (const sel of rowSelectors) {
        for (const el of Array.from(document.querySelectorAll(sel))) {
          const txt = clean(el.innerText || el.getAttribute('aria-label'));
          if (!txt || txt.length < 3 || seen.has(txt)) continue;
          seen.add(txt);
          out.items.push(txt.slice(0, 320));
          if (out.items.length >= 28) break;
        }
        if (out.items.length >= 28) break;
      }
      if (out.items.length === 0 && document.body) {
        out.items.push(clean(document.body.innerText).slice(0, 2500));
      }
      return out;
    }
    """


def _analyze_with_vision_and_dom(
    png_bytes: bytes | None,
    dom_data: dict[str, Any],
    instruction: str,
) -> str:
    from core import gemini

    dom_summary = (
        f"Page Title: {dom_data.get('title', '')}\n"
        f"URL: {dom_data.get('url', '')}\n"
        f"Unread Badges: {', '.join(dom_data.get('unread_badges') or []) or '(none detected in DOM)'}\n"
        "Visible Items / Rows:\n"
        + "\n".join(f"- {row}" for row in (dom_data.get("items") or [])[:25])
    )
    prompt = f"{instruction}\n\nStructured Page Snapshot:\n{dom_summary}"

    contents: Any = prompt
    if png_bytes:
        try:
            from PIL import Image

            img = Image.open(BytesIO(png_bytes)).convert("RGB")
            img.thumbnail((1120, 1120))
            contents = [img, prompt]
        except Exception:
            contents = prompt

    resp = gemini.call(contents, tier=gemini.SMART, timeout_ms=50_000)
    txt = (getattr(resp, "text", "") or "").strip() if resp else ""
    return txt or dom_summary


# ── Public API: Connect, Verify, Disconnect, Status ──────────────────────────


def start_social_login(
    platform: str,
    *,
    handle: str = "",
    permission: str = "ask",
    on_connected: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Open a persistent login/QR window for `platform` and auto-detect sign-in completion."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    perm = permission if permission in accounts.PERMISSIONS else "ask"
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    async def _open_login() -> tuple[bool, bool]:
        pg = await _RUNTIME.get_page(plat, headless=headless_env)
        await pg.goto(spec["login_url"], wait_until="domcontentloaded", timeout=30_000)
        try:
            await pg.wait_for_timeout(1200)
        except Exception:
            pass
        already, _ = await _RUNTIME.check_logged_in(plat, pg)
        return True, already

    try:
        _opened, already_in = _RUNTIME.run(_open_login(), timeout=40.0)
    except Exception as exc:
        # Fallback: open in user's default system browser so they can sign in & use cookie import
        try:
            webbrowser.open(spec["login_url"])
        except Exception:
            pass
        return {
            "ok": True,
            "platform": plat,
            "label": spec["label"],
            "already_connected": False,
            "fallback_browser": True,
            "message": (
                f"Opened {spec['label']} in your default browser ({exc}). "
                f"Once signed in, click 'Import Browser Cookies' in LINKS to link {spec['label']} immediately."
            ),
        }

    if already_in:
        accounts.connect_account(
            plat,
            handle=handle.lstrip("@"),
            session_connected=True,
            auth_mode="web_session",
            permission=perm,
        )
        if callable(on_connected):
            try:
                on_connected()
            except Exception:
                pass
        return {
            "ok": True,
            "platform": plat,
            "label": spec["label"],
            "already_connected": True,
            "message": f"{spec['label']} is already signed in and connected ({perm} mode)!",
        }

    # Background watcher polls for up to 3 minutes so the HUD updates live when login/QR completes!
    def _watch_login() -> None:
        deadline = time.time() + 180.0
        while time.time() < deadline:
            time.sleep(2.5)
            try:
                async def _probe() -> bool:
                    pg = _RUNTIME._pages.get(plat)
                    if pg is None or pg.is_closed():
                        return False
                    ok_in, _ = await _RUNTIME.check_logged_in(plat, pg)
                    return ok_in

                if _RUNTIME.run(_probe(), timeout=10.0):
                    accounts.connect_account(
                        plat,
                        handle=handle.lstrip("@"),
                        session_connected=True,
                        auth_mode="web_session",
                        permission=perm,
                    )
                    security_vault.log_audit_event(
                        "user",
                        f"social_connect_web:{plat}",
                        {"platform": plat, "permission": perm},
                        result_summary=f"{spec['label']} web session authenticated.",
                        status="ok",
                    )
                    if callable(on_connected):
                        on_connected()
                    return
            except Exception:
                continue

    threading.Thread(target=_watch_login, daemon=True, name=f"social-watch-{plat}").start()
    return {
        "ok": True,
        "platform": plat,
        "label": spec["label"],
        "already_connected": False,
        "message": (
            f"Opened {spec['label']} sign-in window ({spec['login_url']}). "
            "Sign in or scan the QR code — JARVIS will automatically mark it CONNECTED the moment you're in."
        ),
    }


def disconnect_social_account(platform: str) -> dict[str, Any]:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}
    clear_encrypted_cookies(plat)
    try:
        _RUNTIME.run(_RUNTIME.clear_platform(plat), timeout=8.0)
    except Exception:
        pass
    accounts.disconnect_account(plat)
    security_vault.log_audit_event(
        "user",
        f"social_disconnect:{plat}",
        {"platform": plat},
        result_summary=f"Disconnected {SOCIAL_PLATFORMS[plat]['label']} session.",
        status="ok",
    )
    return {"ok": True, "platform": plat, "label": SOCIAL_PLATFORMS[plat]["label"]}


def get_social_hub_status() -> dict[str, Any]:
    summary = accounts.get_integrations_status_summary()
    svcs = summary.get("services", {})
    items: list[dict[str, Any]] = []
    for plat, spec in SOCIAL_PLATFORMS.items():
        st = svcs.get(plat, {})
        items.append(
            {
                "platform": plat,
                "label": spec["label"],
                "connected": bool(st.get("connected")),
                "ignored": bool(st.get("ignored")),
                "handle": str(st.get("handle") or ""),
                "permission": str(st.get("permission") or "ask"),
                "auth_mode": str(st.get("auth_mode") or ""),
                "cookies_browser": str(st.get("cookies_browser") or ""),
            }
        )
    return {
        "ok": True,
        "platforms": items,
        "connected_platforms": [x["platform"] for x in items if x["connected"]],
    }


def _ensure_platform_ready(platform: str) -> tuple[bool, str]:
    rec = accounts.get_account(platform)
    if rec:
        allowed, reason = accounts.check_permission(platform, "read")
        if not allowed:
            return False, reason
        # Refresh browser cookies seamlessly if configured with `cookies_browser`
        cb = str(rec.get("cookies_browser") or "").strip()
        if cb and not load_encrypted_cookies(platform):
            import_cookies_from_browser(
                platform,
                cb,
                handle=str(rec.get("handle") or ""),
                permission=str(rec.get("permission") or "ask"),
            )
        return True, "ok"

    # Auto-try opportunistic browser cookie import if user hasn't explicitly ignored this platform
    imp = import_cookies_from_browser(platform, "auto")
    if imp.get("ok"):
        return True, "ok"
    lbl = SOCIAL_PLATFORMS[platform]["label"]
    return (
        False,
        f"{lbl} is not connected yet. Open HUD -> LINKS (or ask 'connect my {lbl}') to sign in first.",
    )


# ── 1. Check Unread DMs, Snaps & Notifications ───────────────────────────────


def _inspect_url_in_session(platform: str, url: str, *, headless: bool = True) -> tuple[bytes | None, dict[str, Any], bool]:
    async def _task() -> tuple[bytes | None, dict[str, Any], bool]:
        pg = await _RUNTIME.get_page(platform, headless=headless)
        await pg.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await pg.wait_for_timeout(2200)
        try:
            await pg.evaluate(_dismiss_common_popups_js())
            await pg.wait_for_timeout(400)
        except Exception:
            pass
        logged_in, _ = await _RUNTIME.check_logged_in(platform, pg)
        dom_data = await pg.evaluate(_extract_dom_snapshot_js())
        try:
            shot = await pg.screenshot(type="jpeg", quality=72, full_page=False)
        except Exception:
            shot = None
        return shot, dom_data if isinstance(dom_data, dict) else {}, logged_in

    return _RUNTIME.run(_task(), timeout=45.0)


def check_social_inbox(
    platform: str = "all",
    *,
    include_notifications: bool = True,
) -> dict[str, Any]:
    """Check unread DMs, Snaps, & notifications across one or all connected social platforms."""
    if platform and platform.strip().lower() not in ("all", "*", "any"):
        plat = normalize_social_platform(platform)
        if not plat:
            return {"ok": False, "error": f"Unknown social platform '{platform}'."}
        targets = [plat]
    else:
        st = get_social_hub_status()
        targets = st["connected_platforms"]
        if not targets:
            return {
                "ok": False,
                "error": (
                    "No personal social accounts are connected yet. "
                    "Open HUD -> LINKS (or say 'connect my Instagram / Snapchat / X / TikTok / WhatsApp') to sign in."
                ),
            }

    reports: list[str] = []
    checked: list[str] = []
    for plat in targets:
        spec = SOCIAL_PLATFORMS[plat]
        ready, reason = _ensure_platform_ready(plat)
        if not ready:
            reports.append(f"• {spec['label']}: {reason}")
            continue
        try:
            shot, dom_data, logged_in = _inspect_url_in_session(
                plat, spec["inbox_url"], headless=True
            )
            if not logged_in and any(
                k in str(dom_data.get("url", "")).lower() for k in ("/login", "/flow/login")
            ):
                reports.append(
                    f"• {spec['label']}: Session expired or awaiting login — run action='connect' for {spec['label']}."
                )
                continue
            digest = _analyze_with_vision_and_dom(
                shot,
                dom_data,
                instruction=(
                    f"You are inspecting the user's {spec['label']} inbox / chats screen. "
                    "List any unread messages/Snaps first (sender name + preview/status + time), "
                    "followed by the 3–5 most recent conversations or notifications. Be concise and accurate."
                ),
            )
            checked.append(plat)
            reports.append(f"=== {spec['label']} Inbox ===\n{digest}")

            if include_notifications and spec["notifications_url"] != spec["inbox_url"]:
                try:
                    n_shot, n_dom, _ = _inspect_url_in_session(
                        plat, spec["notifications_url"], headless=True
                    )
                    n_digest = _analyze_with_vision_and_dom(
                        n_shot,
                        n_dom,
                        instruction=f"Summarize the latest 3–5 {spec['label']} notifications concisely.",
                    )
                    reports.append(f"--- {spec['label']} Notifications ---\n{n_digest}")
                except Exception:
                    pass
        except Exception as exc:
            reports.append(f"• {spec['label']}: Could not inspect inbox ({exc})")

    return {
        "ok": bool(checked) or bool(reports),
        "checked_platforms": checked,
        "summary": "\n\n".join(reports),
    }


# ── 2. Read Specific DM / Snap Conversation ──────────────────────────────────


def read_social_messages(platform: str, contact: str = "") -> dict[str, Any]:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat)
    if not ready:
        return {"ok": False, "error": reason}

    clean_contact = (contact or "").strip().lstrip("@")

    async def _open_and_read() -> tuple[bytes | None, dict[str, Any]]:
        pg = await _RUNTIME.get_page(plat, headless=True)
        await pg.goto(spec["inbox_url"], wait_until="domcontentloaded", timeout=30_000)
        await pg.wait_for_timeout(2200)
        try:
            await pg.evaluate(_dismiss_common_popups_js())
        except Exception:
            pass

        if clean_contact:
            clicked = False
            try:
                loc = pg.get_by_text(clean_contact, exact=False).first
                if await loc.count() > 0:
                    await loc.click(timeout=5_000)
                    clicked = True
            except Exception:
                clicked = False
            if not clicked:
                # Try inbox search input if contact isn't immediately in top visible rows
                for s_sel in ('input[placeholder*="Search" i]', '[role="searchbox"]'):
                    try:
                        sb = pg.locator(s_sel).first
                        if await sb.count() > 0:
                            await sb.click(timeout=3_000)
                            await sb.fill(clean_contact)
                            await pg.wait_for_timeout(1200)
                            cand = pg.get_by_text(clean_contact, exact=False).first
                            if await cand.count() > 0:
                                await cand.click(timeout=4_000)
                                break
                    except Exception:
                        continue
            await pg.wait_for_timeout(1600)

        dom_data = await pg.evaluate(_extract_dom_snapshot_js())
        try:
            shot = await pg.screenshot(type="jpeg", quality=75, full_page=False)
        except Exception:
            shot = None
        return shot, dom_data if isinstance(dom_data, dict) else {}

    try:
        shot, dom_data = _RUNTIME.run(_open_and_read(), timeout=48.0)
    except Exception as exc:
        return {"ok": False, "error": f"Could not read {spec['label']} conversation: {exc}"}

    who = f"with '{clean_contact}'" if clean_contact else "(latest visible thread)"
    transcript = _analyze_with_vision_and_dom(
        shot,
        dom_data,
        instruction=(
            f"Read the open {spec['label']} chat thread {who}. "
            "Quote or summarize the most recent messages in chronological order, clearly distinguishing who said what."
        ),
    )
    return {
        "ok": True,
        "platform": plat,
        "label": spec["label"],
        "contact": clean_contact,
        "messages": transcript,
    }


# ── 3. Send DM / Snap Reply & Publish Post (Unforgeable Confirmation Gate!) ──


def _execute_send_message_now(platform: str, recipient: str, message: str, actor: str) -> str:
    spec = SOCIAL_PLATFORMS[platform]
    clean_rec = recipient.strip().lstrip("@")

    async def _send_coro() -> str:
        pg = await _RUNTIME.get_page(platform, headless=False)
        if spec["inbox_url"].rstrip("/") not in (pg.url or ""):
            await pg.goto(spec["inbox_url"], wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(2200)
        try:
            await pg.evaluate(_dismiss_common_popups_js())
        except Exception:
            pass

        if clean_rec:
            loc = pg.get_by_text(clean_rec, exact=False).first
            if await loc.count() > 0:
                await loc.click(timeout=5_000)
                await pg.wait_for_timeout(1300)

        composer_selectors = (
            '[role="textbox"][contenteditable="true"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="message" i]',
            'input[placeholder*="Send a chat" i]',
            'textarea',
        )
        box = None
        for sel in composer_selectors:
            cand = pg.locator(sel).last
            if await cand.count() > 0:
                box = cand
                break
        if box is None:
            raise RuntimeError(f"Could not locate message input box on {spec['label']}.")

        await box.click(timeout=4_000)
        await box.fill(message)
        await pg.wait_for_timeout(250)
        await pg.keyboard.press("Enter")
        await pg.wait_for_timeout(1200)
        return f"Sent {spec['label']} message to {clean_rec}."

    res_msg = _RUNTIME.run(_send_coro(), timeout=50.0)
    security_vault.log_audit_event(
        actor,
        f"social_send_message:{platform}",
        {"platform": platform, "recipient": clean_rec, "length": len(message)},
        result_summary=res_msg,
        status="ok",
    )
    return res_msg


def stage_or_send_social_message(
    platform: str,
    recipient: str,
    message: str,
) -> str:
    """Enforce `memory/accounts.py` permissions and `core.confirm` HUD gate before sending any DM/Snap."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return f"Unsupported social platform '{platform}'."
    if not (recipient or "").strip():
        return "Please specify who to message."
    if not (message or "").strip():
        return "Please specify the message text."

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat)
    if not ready:
        return reason

    allowed, perm_reason = accounts.check_permission(plat, "send")
    if not allowed:
        return f"Blocked by {spec['label']} permission policy: {perm_reason}."

    rec = accounts.get_account(plat) or {}
    perm = str(rec.get("permission") or "ask").lower()

    if perm == "full":
        try:
            return _execute_send_message_now(plat, recipient, message, actor="jarvis_full_perm")
        except Exception as exc:
            return f"Failed to send {spec['label']} message: {exc}"

    # Default `ask` mode -> Unforgeable on-screen HUD confirmation gate (`core.confirm.request`)!
    title = f"Send {spec['label']} message to {recipient.strip()}"
    detail = f"Message: \"{message.strip()[:220]}\""
    return confirm_gate.request(
        key=f"social-msg-{plat}",
        title=title,
        detail=detail,
        run=lambda: _execute_send_message_now(plat, recipient, message, actor="user_confirmed"),
    )


def _execute_publish_post_now(platform: str, text: str, actor: str) -> str:
    spec = SOCIAL_PLATFORMS[platform]

    async def _post_coro() -> str:
        pg = await _RUNTIME.get_page(platform, headless=False)
        await pg.goto(spec["compose_post_url"], wait_until="domcontentloaded", timeout=30_000)
        await pg.wait_for_timeout(2000)
        box = pg.locator('[data-testid="tweetTextarea_0"], [role="textbox"][contenteditable="true"], textarea').first
        if await box.count() == 0:
            raise RuntimeError(f"Could not find post composer on {spec['label']}.")
        await box.click(timeout=4_000)
        await box.fill(text)
        await pg.wait_for_timeout(400)
        btn = pg.locator('[data-testid="tweetButton"], [data-testid="tweetButtonInline"], button:has-text("Post")').first
        if await btn.count() > 0:
            await btn.click(timeout=4_000)
            await pg.wait_for_timeout(1500)
            return f"Published post on {spec['label']}."
        raise RuntimeError(f"Draft typed into {spec['label']}, please click Post in the window to finish.")

    res_msg = _RUNTIME.run(_post_coro(), timeout=50.0)
    security_vault.log_audit_event(
        actor,
        f"social_publish_post:{platform}",
        {"platform": platform, "length": len(text)},
        result_summary=res_msg,
        status="ok",
    )
    return res_msg


def stage_or_publish_social_post(platform: str, text: str) -> str:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return f"Unsupported social platform '{platform}'."
    if not (text or "").strip():
        return "Please provide the text to post."

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat)
    if not ready:
        return reason

    allowed, perm_reason = accounts.check_permission(plat, "write")
    if not allowed:
        return f"Blocked by {spec['label']} permission policy: {perm_reason}."

    rec = accounts.get_account(plat) or {}
    perm = str(rec.get("permission") or "ask").lower()
    if perm == "full":
        try:
            return _execute_publish_post_now(plat, text, actor="jarvis_full_perm")
        except Exception as exc:
            return f"Could not publish on {spec['label']}: {exc}"

    return confirm_gate.request(
        key=f"social-post-{plat}",
        title=f"Publish {spec['label']} post",
        detail=f"Post: \"{text.strip()[:220]}\"",
        run=lambda: _execute_publish_post_now(plat, text, actor="user_confirmed"),
    )


# ── 4. Hands-Free Voice Feed, Reels & Story Control ──────────────────────────


def control_social_feed(
    platform: str,
    command: str = "open_feed",
    *,
    target: str = "",
) -> dict[str, Any]:
    """Hands-free navigation & interaction (`open_reels`, `next`, `previous`, `like`, `save`, `open_profile`, `look`)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    cmd = (command or "open_feed").strip().lower()
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    # Best-effort hydrate cookies so user lands straight into their signed-in feed
    _ensure_platform_ready(plat)

    async def _feed_coro() -> dict[str, Any]:
        pg = await _RUNTIME.get_page(plat, headless=headless_env)

        if cmd in ("open_feed", "home", "feed"):
            await pg.goto(spec["home_url"], wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(1500)
            return {"ok": True, "message": f"Opened your {spec['label']} feed."}

        if cmd in ("open_reels", "reels", "foryou", "spotlight"):
            await pg.goto(spec["reels_url"], wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(1800)
            return {"ok": True, "message": f"Opened {spec['label']} Reels / Spotlight."}

        if cmd in ("open_inbox", "inbox", "dms", "chats"):
            await pg.goto(spec["inbox_url"], wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(1800)
            return {"ok": True, "message": f"Opened your {spec['label']} inbox."}

        if cmd in ("open_profile", "profile"):
            handle = (target or (accounts.get_account(plat) or {}).get("handle") or "").strip().lstrip("@")
            if not handle:
                return {"ok": False, "error": f"Pass a @username (`target`) to open on {spec['label']}."}
            url = spec["profile_url_tpl"].format(handle=handle)
            await pg.goto(url, wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(1500)
            return {"ok": True, "message": f"Opened @{handle} on {spec['label']} ({url})."}

        # Ensure page isn't blank before running in-page actions
        if (pg.url or "") in ("", "about:blank"):
            await pg.goto(spec["reels_url"], wait_until="domcontentloaded", timeout=30_000)
            await pg.wait_for_timeout(1600)

        if cmd in ("next", "scroll_down", "down", "skip"):
            await pg.keyboard.press("ArrowDown")
            await pg.mouse.wheel(0, 650)
            await pg.wait_for_timeout(500)
            return {"ok": True, "message": f"Moved to the next post/reel on {spec['label']}."}

        if cmd in ("previous", "prev", "scroll_up", "up", "back"):
            await pg.keyboard.press("ArrowUp")
            await pg.mouse.wheel(0, -650)
            await pg.wait_for_timeout(500)
            return {"ok": True, "message": f"Moved back to the previous post/reel on {spec['label']}."}

        if cmd == "like":
            allowed, rsn = accounts.check_permission(plat, "write")
            if accounts.get_account(plat) and not allowed:
                return {"ok": False, "error": rsn}
            for sel in (
                'svg[aria-label="Like"]',
                '[data-testid="like"]',
                '[data-e2e="like-icon"]',
                'button[aria-label*="Like" i]',
            ):
                loc = pg.locator(sel).first
                if await loc.count() > 0:
                    await loc.click(timeout=3_000)
                    return {"ok": True, "message": f"Liked the active post/reel on {spec['label']}."}
            return {"ok": False, "error": f"Could not find an unliked Like button on {spec['label']}."}

        if cmd in ("save", "bookmark"):
            for sel in (
                'svg[aria-label="Save"]',
                '[data-testid="bookmark"]',
                '[data-e2e="undefined-icon"]',
                'button[aria-label*="Save" i]',
                'button[aria-label*="Bookmark" i]',
            ):
                loc = pg.locator(sel).first
                if await loc.count() > 0:
                    await loc.click(timeout=3_000)
                    return {"ok": True, "message": f"Saved/bookmarked the active item on {spec['label']}."}
            return {"ok": False, "error": f"Could not find Save/Bookmark button on {spec['label']}."}

        if cmd in ("look", "describe", "see", "what_is_this"):
            dom_data = await pg.evaluate(_extract_dom_snapshot_js())
            shot = await pg.screenshot(type="jpeg", quality=75, full_page=False)
            desc = _analyze_with_vision_and_dom(
                shot,
                dom_data if isinstance(dom_data, dict) else {},
                instruction=f"Describe what is currently visible on the user's {spec['label']} screen (post, reel, creator, caption, and visuals).",
            )
            return {"ok": True, "message": desc}

        return {"ok": False, "error": f"Unknown feed command '{command}'."}

    try:
        return _RUNTIME.run(_feed_coro(), timeout=45.0)
    except Exception as exc:
        # Graceful fallback for open_* commands if Playwright isn't installed yet
        if cmd in ("open_feed", "open_reels", "open_inbox", "open_profile"):
            url = (
                spec["reels_url"]
                if "reel" in cmd
                else spec["inbox_url"]
                if "inbox" in cmd
                else spec["profile_url_tpl"].format(handle=target.lstrip("@"))
                if "profile" in cmd and target
                else spec["home_url"]
            )
            try:
                webbrowser.open(url)
                return {"ok": True, "message": f"Opened {spec['label']} ({url}) in your browser."}
            except Exception:
                pass
        return {"ok": False, "error": f"{spec['label']} feed control failed: {exc}"}
