"""
core/social_hub.py — Personal Social Accounts Hub (Instagram, Snapchat, TikTok, X, WhatsApp, Reddit).

Architecture (v2 — Zero-Playwright-Driver Native Chrome/Edge CDP Engine):
  • Launches the user's genuine installed browser (`chrome.exe`, `msedge.exe`,
    `brave.exe`, `opera.exe`, or Chromium) via `unpatched_popen` (`subprocess._OrigPopen`
    — never swallowed by `main.py`'s Windows `CREATE_NO_WINDOW` patch!) on a dedicated
    persistent profile (`~/.jarvis_socials/browser_profile`) with
    `--remote-debugging-port=<port> --remote-allow-origins=*`.
  • Speaks native Chrome DevTools Protocol (CDP) directly over `httpx` + `websockets`
    (zero `--enable-automation` flag, `navigator.webdriver === false`, zero
    `playwright install` requirement — so Instagram, Snapchat Web, WhatsApp Web,
    TikTok, X, and Reddit never block login with automation errors!).
  • Dispatches genuine OS-trusted events (`event.isTrusted === true`) via CDP
    `Input.dispatchMouseEvent`, `Input.insertText`, and `Input.dispatchKeyEvent`,
    working 100% natively with Meta's Lexical editor on Instagram Direct, Snapchat
    Web's chat input, WhatsApp Web, TikTok, and X.
  • Multi-profile browser cookie importer (`Default`, `Profile 1..3`, Chrome, Edge,
    Brave, Opera, Opera GX, Vivaldi, Firefox, Safari) with AES-256-GCM at-rest vault
    encryption AND automatic visible Sign-In Window fallback whenever Windows Chrome
    v127+ App-Bound Encryption (`v20`) locks live cookies.
  • Unforgeable HUD `CONFIRM / CANCEL` gate (`core.confirm.request`) + SHA-256
    Hash-Chained Audit Log (`core.security_vault.log_audit_event`) before sending any
    DM, Snap chat reply, or social post when permission is `ask` (default).
"""

from __future__ import annotations

import asyncio
import base64
from io import BytesIO
import json
import os
import platform as _py_platform
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import threading
import time
from typing import Any, Callable
from urllib.parse import quote
import webbrowser

import httpx
import websockets

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
        "auth_cookies": ("sessionid",),
        "logged_in_selectors": (
            'a[href*="/direct/inbox"]',
            'svg[aria-label="Direct"]',
            'svg[aria-label="Messenger"]',
            'svg[aria-label="New message"]',
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
            'button[aria-label*="Chat" i]',
            'input[placeholder*="Search" i]',
            '[role="list"]',
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
        "auth_cookies": ("sessionid", "sessionid_ss", "sid_tt"),
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
    "instagram_com": "instagram",
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
    "whatsapp_web": "whatsapp",
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


# ── Browser Discovery & Multi-Profile Cookie Importer ────────────────────────


def find_chromium_binary() -> str | None:
    """Locate genuine installed Chrome, Edge, Brave, Opera, or Chromium across Windows/macOS/Linux."""
    env_bin = os.environ.get("JARVIS_SOCIALS_BROWSER_BIN", "").strip()
    if env_bin and os.path.isfile(env_bin):
        return env_bin

    sys_name = _py_platform.system()
    candidates: list[str] = []

    if sys_name == "Windows":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")
        candidates.extend(
            [
                os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(pf86, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(pf86, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(pf, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(pf, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(local, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                os.path.join(local, "Programs", "Opera GX", "opera.exe"),
                os.path.join(local, "Programs", "Opera", "opera.exe"),
                os.path.join(local, "Vivaldi", "Application", "vivaldi.exe"),
            ]
        )
        for cmd in ("chrome", "msedge", "brave", "vivaldi", "opera"):
            found = shutil.which(cmd)
            if found:
                candidates.append(found)
    elif sys_name == "Darwin":
        candidates.extend(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
                "/Applications/Opera.app/Contents/MacOS/Opera",
            ]
        )
    else:
        for cmd in (
            "google-chrome",
            "google-chrome-stable",
            "brave-browser",
            "microsoft-edge",
            "microsoft-edge-stable",
            "chromium",
            "chromium-browser",
            "vivaldi",
        ):
            found = shutil.which(cmd)
            if found:
                candidates.append(found)

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _candidate_cookie_specs(preferred: str = "") -> list[tuple[str, str | None]]:
    """Return `(browser, profile)` pairs across Default and numbered profiles."""
    p = (preferred or "").strip().lower()
    if p and p != "auto":
        return [(p, None), (p, "Default"), (p, "Profile 1"), (p, "Profile 2")]
    if os.name == "nt":
        browsers = ["firefox", "chrome", "edge", "brave", "opera", "vivaldi"]
    else:
        browsers = ["chrome", "brave", "firefox", "safari", "chromium", "edge", "opera"]
    specs: list[tuple[str, str | None]] = []
    for b in browsers:
        specs.append((b, None))
        if b in ("chrome", "edge", "brave", "vivaldi"):
            specs.append((b, "Profile 1"))
            specs.append((b, "Profile 2"))
    return specs


def import_cookies_from_browser(
    platform: str,
    browser: str = "auto",
    *,
    handle: str = "",
    permission: str = "ask",
    auto_open_window_on_lock: bool = False,
    on_connected: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Import active session cookies from installed browsers (with automatic Sign-In Window fallback on Windows v20 lock)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform: {platform}"}

    spec = SOCIAL_PLATFORMS[plat]
    domains: tuple[str, ...] = spec["domains"]
    auth_names: set[str] = set(spec["auth_cookies"])

    try:
        from yt_dlp.cookies import extract_cookies_from_browser
    except Exception as exc:
        extract_cookies_from_browser = None  # type: ignore[assignment]
        last_err = str(exc)
    else:
        last_err = ""

    if extract_cookies_from_browser is not None:
        for cand_browser, cand_profile in _candidate_cookie_specs(browser):
            try:
                jar = (
                    extract_cookies_from_browser(cand_browser, profile=cand_profile)
                    if cand_profile
                    else extract_cookies_from_browser(cand_browser)
                )
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
                # Also push into live CDP browser immediately if running
                try:
                    _CDP.inject_cookies(matched)
                except Exception:
                    pass
                src_label = f"{cand_browser}:{cand_profile}" if cand_profile else cand_browser
                accounts.connect_account(
                    plat,
                    handle=handle.lstrip("@"),
                    cookies_browser=cand_browser,
                    session_connected=True,
                    auth_mode="browser_cookies",
                    permission=permission if permission in accounts.PERMISSIONS else "ask",
                )
                security_vault.log_audit_event(
                    "user",
                    f"social_connect_cookies:{plat}",
                    {"platform": plat, "browser": src_label, "cookie_count": len(matched)},
                    result_summary=f"Imported {len(matched)} {spec['label']} session cookies from {src_label}.",
                    status="ok",
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
                    "browser": src_label,
                    "cookie_count": len(matched),
                    "auth_mode": "browser_cookies",
                }

    # On Windows Chrome 127+ / Edge 127+, App-Bound Encryption (`v20`) locks live cookies while the browser is open.
    # Automatically launch the dedicated Sign-In Window right away so the user is NEVER stuck!
    if auto_open_window_on_lock:
        win_res = start_social_login(
            plat,
            handle=handle,
            permission=permission,
            on_connected=on_connected,
        )
        if win_res.get("ok"):
            if win_res.get("already_connected"):
                return {
                    "ok": True,
                    "platform": plat,
                    "label": spec["label"],
                    "browser": "persistent_session",
                    "cookie_count": len(load_encrypted_cookies(plat)) or 1,
                    "auth_mode": "web_session",
                    "message": win_res.get("message"),
                }
            return {
                "ok": False,
                "auto_opened_window": True,
                "platform": plat,
                "label": spec["label"],
                "error": (
                    f"Your browser encrypts live cookies while open — so I opened a dedicated {spec['label']} "
                    "window on your screen right now! Sign in once there and it will turn CONNECTED automatically."
                ),
            }

    return {
        "ok": False,
        "platform": plat,
        "error": (
            f"Could not read live {spec['label']} cookies from {browser or 'local browsers'}"
            + (f" ({last_err[:120]})" if last_err else "")
            + f". Click 'SIGN IN WINDOW' to sign into {spec['label']} directly."
        ),
    }


# ── Native Chrome DevTools Protocol (CDP) Client & Browser Manager ───────────


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _spawn_visible_or_hidden(args: list[str], *, visible: bool) -> subprocess.Popen:
    """Spawn browser bypassing `main.py`'s Windows `CREATE_NO_WINDOW` patch when `visible=True`."""
    if visible:
        popen_cls = getattr(subprocess, "_OrigPopen", subprocess.Popen)
        return popen_cls(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    kw: dict[str, Any] = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return subprocess.Popen(args, **kw)


class _CdpConnection:
    """Async JSON-RPC session over a single Chrome DevTools WebSocket target."""

    def __init__(self, ws_url: str) -> None:
        self.ws_url = ws_url
        self._id = 0

    async def call_many(
        self,
        steps: Callable[["_CdpConnection", Any], Any],
        *,
        timeout: float = 40.0,
    ) -> Any:
        async with websockets.connect(
            self.ws_url,
            origin=None,
            max_size=32 * 1024 * 1024,
            open_timeout=10.0,
            close_timeout=2.0,
        ) as ws:
            return await asyncio.wait_for(steps(self, ws), timeout=timeout)

    async def send_cmd(
        self,
        ws: Any,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float = 20.0,
    ) -> dict[str, Any]:
        self._id += 1
        req_id = self._id
        payload: dict[str, Any] = {"id": req_id, "method": method}
        if params:
            payload["params"] = params
        await ws.send(json.dumps(payload))

        deadline = time.monotonic() + timeout
        while True:
            rem = max(0.2, deadline - time.monotonic())
            raw = await asyncio.wait_for(ws.recv(), timeout=rem)
            msg = json.loads(raw)
            if msg.get("id") == req_id:
                if "error" in msg:
                    err_obj = msg["error"]
                    err_txt = err_obj.get("message") if isinstance(err_obj, dict) else str(err_obj)
                    raise RuntimeError(f"CDP {method} error: {err_txt}")
                res = msg.get("result")
                return res if isinstance(res, dict) else {}


class _NativeCdpSocialBrowser:
    """Manages `~/.jarvis_socials/browser_profile` via real Chrome/Edge + CDP."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._port: int = 0
        self._proc: subprocess.Popen | None = None
        self._headless: bool | None = None
        self._tab_ids: dict[str, str] = {}

    def _endpoint_alive(self) -> bool:
        if not self._port:
            return False
        try:
            r = httpx.get(f"http://127.0.0.1:{self._port}/json/version", timeout=1.2)
            return r.status_code == 200
        except Exception:
            return False

    def _shutdown_locked(self) -> None:
        if self._port:
            try:
                v = httpx.get(f"http://127.0.0.1:{self._port}/json/version", timeout=1.0).json()
                b_ws = v.get("webSocketDebuggerUrl")
                if b_ws:
                    asyncio.run(
                        _CdpConnection(b_ws).call_many(
                            lambda c, ws: c.send_cmd(ws, "Browser.close", timeout=2.0),
                            timeout=3.0,
                        )
                    )
            except Exception:
                pass
        if self._proc is not None:
            try:
                if self._proc.poll() is None:
                    self._proc.terminate()
                    self._proc.wait(timeout=2.5)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None
        self._port = 0
        self._headless = None
        self._tab_ids.clear()
        time.sleep(0.35)

    def ensure_browser(self, *, headless: bool = False, start_url: str = "about:blank") -> int:
        env_port = os.environ.get("JARVIS_SOCIALS_CDP_PORT", "").strip()
        if env_port.isdigit():
            self._port = int(env_port)
            self._headless = bool(headless)
            return self._port

        with self._lock:
            # If currently running headless and user now needs a visible window, restart visibly on the same profile!
            if self._endpoint_alive():
                if self._headless is True and headless is False:
                    self._shutdown_locked()
                else:
                    return self._port

            exe = find_chromium_binary()
            if not exe:
                raise RuntimeError(
                    "No Chromium browser (Chrome, Edge, Brave, Opera) found on this machine."
                )

            profile_dir = socials_root_dir() / "browser_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)
            for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                lp = profile_dir / lock_name
                if lp.is_symlink() or lp.exists():
                    try:
                        lp.unlink()
                    except Exception:
                        pass

            port = _pick_free_port()
            args = [
                exe,
                f"--user-data-dir={profile_dir}",
                f"--remote-debugging-port={port}",
                "--remote-allow-origins=*",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--window-size=1220,860",
            ]
            if headless:
                args.extend(["--headless=new", "--mute-audio", "--disable-gpu"])
            else:
                args.append("--new-window")
            args.append(start_url or "about:blank")

            self._proc = _spawn_visible_or_hidden(args, visible=not headless)
            self._port = port
            self._headless = bool(headless)

            deadline = time.monotonic() + 14.0
            while time.monotonic() < deadline:
                if self._endpoint_alive():
                    break
                time.sleep(0.2)
            else:
                self._shutdown_locked()
                raise RuntimeError("Timed out waiting for Chrome/Edge social session port.")

            # Hydrate all encrypted vault cookies into the browser profile
            all_saved: list[dict[str, Any]] = []
            for pk in SOCIAL_PLATFORMS:
                all_saved.extend(load_encrypted_cookies(pk))
            if all_saved:
                try:
                    self.inject_cookies(all_saved)
                except Exception:
                    pass

            return self._port

    def _list_page_targets(self) -> list[dict[str, Any]]:
        if not self._endpoint_alive():
            return []
        try:
            items = httpx.get(f"http://127.0.0.1:{self._port}/json/list", timeout=3.0).json()
            return [
                t
                for t in items
                if isinstance(t, dict)
                and t.get("type") == "page"
                and t.get("webSocketDebuggerUrl")
            ]
        except Exception:
            return []

    def get_or_open_tab(
        self,
        platform: str,
        url: str,
        *,
        headless: bool = False,
        force_navigate: bool = True,
    ) -> dict[str, Any]:
        self.ensure_browser(headless=headless, start_url=url)
        spec = SOCIAL_PLATFORMS[platform]
        domains = spec["domains"]

        pages = self._list_page_targets()
        chosen: dict[str, Any] | None = None

        # 1. Exact tracked tab ID for this platform
        tid = self._tab_ids.get(platform)
        if tid:
            chosen = next((p for p in pages if p.get("id") == tid), None)

        # 2. Existing tab already on this social domain
        if chosen is None:
            for p in pages:
                u_low = str(p.get("url") or "").lower()
                if any(d in u_low for d in domains):
                    chosen = p
                    break

        # 3. Blank / newtab page we can adopt cleanly
        if chosen is None:
            for p in pages:
                u_low = str(p.get("url") or "").lower()
                if u_low in ("about:blank", "") or "newtab" in u_low:
                    chosen = p
                    break

        # 4. Open a fresh tab via PUT /json/new (Chrome 115+) with GET fallback
        if chosen is None:
            enc_u = quote(url, safe=":/?&=%#+-_~.")
            new_url = f"http://127.0.0.1:{self._port}/json/new?{enc_u}"
            resp = httpx.put(new_url, timeout=5.0)
            if resp.status_code == 405:
                resp = httpx.get(new_url, timeout=5.0)
            resp.raise_for_status()
            chosen = resp.json()
            force_navigate = False

        assert chosen is not None
        self._tab_ids[platform] = str(chosen.get("id") or "")
        ws_url = str(chosen["webSocketDebuggerUrl"])
        cur_url = str(chosen.get("url") or "")

        async def _prep(conn: _CdpConnection, ws: Any) -> None:
            await conn.send_cmd(ws, "Page.enable")
            await conn.send_cmd(ws, "Network.enable")
            if not headless:
                try:
                    await conn.send_cmd(ws, "Page.bringToFront")
                except Exception:
                    pass
            if force_navigate and url and cur_url.rstrip("/") != url.rstrip("/"):
                await conn.send_cmd(ws, "Page.navigate", {"url": url})

        asyncio.run(_CdpConnection(ws_url).call_many(_prep, timeout=25.0))
        return chosen

    def get_all_cookies(self) -> list[dict[str, Any]]:
        pages = self._list_page_targets()
        if not pages:
            try:
                v = httpx.get(f"http://127.0.0.1:{self._port}/json/version", timeout=2.0).json()
                ws_url = v.get("webSocketDebuggerUrl")
            except Exception:
                ws_url = None
        else:
            ws_url = pages[0]["webSocketDebuggerUrl"]
        if not ws_url:
            return []

        async def _fetch(conn: _CdpConnection, ws: Any) -> list[dict[str, Any]]:
            res = await conn.send_cmd(ws, "Network.getAllCookies")
            c_list = res.get("cookies")
            return c_list if isinstance(c_list, list) else []

        try:
            return asyncio.run(_CdpConnection(ws_url).call_many(_fetch, timeout=10.0))
        except Exception:
            return []

    def inject_cookies(self, cookies: list[dict[str, Any]]) -> None:
        if not cookies or not self._endpoint_alive():
            return
        pages = self._list_page_targets()
        ws_url = pages[0]["webSocketDebuggerUrl"] if pages else None
        if not ws_url:
            return

        async def _push(conn: _CdpConnection, ws: Any) -> None:
            await conn.send_cmd(ws, "Network.setCookies", {"cookies": cookies})

        asyncio.run(_CdpConnection(ws_url).call_many(_push, timeout=10.0))

    def clear_platform_cookies(self, platform: str) -> None:
        if not self._endpoint_alive():
            return
        domains = SOCIAL_PLATFORMS[platform]["domains"]
        pages = self._list_page_targets()
        ws_url = pages[0]["webSocketDebuggerUrl"] if pages else None
        if not ws_url:
            return

        async def _wipe(conn: _CdpConnection, ws: Any) -> None:
            res = await conn.send_cmd(ws, "Network.getAllCookies")
            for c in res.get("cookies") or []:
                dom = str(c.get("domain") or "").lower()
                if any(dom == d or dom.endswith("." + d) or dom.endswith(d) for d in domains):
                    await conn.send_cmd(
                        ws,
                        "Network.deleteCookies",
                        {"name": c.get("name"), "domain": c.get("domain"), "path": c.get("path", "/")},
                    )

        try:
            asyncio.run(_CdpConnection(ws_url).call_many(_wipe, timeout=10.0))
        except Exception:
            pass
        tid = self._tab_ids.pop(platform, None)
        if tid:
            try:
                httpx.get(f"http://127.0.0.1:{self._port}/json/close/{tid}", timeout=2.0)
            except Exception:
                pass

    def run_on_tab(
        self,
        ws_url: str,
        fn: Callable[[_CdpConnection, Any], Any],
        *,
        timeout: float = 40.0,
    ) -> Any:
        return asyncio.run(_CdpConnection(ws_url).call_many(fn, timeout=timeout))


_CDP = _NativeCdpSocialBrowser()


# ── CDP Page Helpers: Wait, Dismiss Modals, DOM Snapshot, Trusted Input ──────


async def _cdp_eval_json(conn: _CdpConnection, ws: Any, js_expr: str) -> Any:
    res = await conn.send_cmd(
        ws,
        "Runtime.evaluate",
        {
            "expression": js_expr,
            "returnByValue": True,
            "awaitPromise": True,
        },
    )
    return (res.get("result") or {}).get("value")


async def _cdp_wait_settled(conn: _CdpConnection, ws: Any, wait_s: float = 2.0) -> None:
    deadline = time.monotonic() + 8.0
    while time.monotonic() < deadline:
        state = await _cdp_eval_json(conn, ws, "document.readyState")
        if state in ("interactive", "complete"):
            break
        await asyncio.sleep(0.2)
    await asyncio.sleep(wait_s)


async def _cdp_dismiss_popups(conn: _CdpConnection, ws: Any) -> None:
    js = """
    (() => {
      const exactLabels = new Set([
        'not now', 'maybe later', 'decline optional cookies',
        'allow all cookies', 'dismiss', 'cancel'
      ]);
      const els = document.querySelectorAll('button, [role="button"]');
      let clicked = 0;
      for (const el of els) {
        const t = (el.innerText || el.getAttribute('aria-label') || '').trim().toLowerCase();
        if (exactLabels.has(t)) {
          try { el.click(); clicked++; } catch (_) {}
        }
      }
      return clicked;
    })()
    """
    try:
        n = await _cdp_eval_json(conn, ws, js)
        if n:
            await asyncio.sleep(0.35)
    except Exception:
        pass


async def _cdp_trusted_click(conn: _CdpConnection, ws: Any, x: float, y: float) -> None:
    for ev_type in ("mouseMoved", "mousePressed", "mouseReleased"):
        await conn.send_cmd(
            ws,
            "Input.dispatchMouseEvent",
            {
                "type": ev_type,
                "x": float(x),
                "y": float(y),
                "button": "left",
                "clickCount": 1,
            },
        )
        await asyncio.sleep(0.04)


async def _cdp_press_key(conn: _CdpConnection, ws: Any, key: str, vk: int) -> None:
    for ev_type in ("keyDown", "keyUp"):
        await conn.send_cmd(
            ws,
            "Input.dispatchKeyEvent",
            {
                "type": ev_type,
                "key": key,
                "code": key,
                "windowsVirtualKeyCode": vk,
                "nativeVirtualKeyCode": vk,
            },
        )
        await asyncio.sleep(0.04)


async def _cdp_capture_snapshot(conn: _CdpConnection, ws: Any) -> tuple[bytes | None, dict[str, Any]]:
    dom_js = """
    (() => {
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
        'div[role="button"]',
        'article',
      ];
      const seen = new Set();
      for (const sel of rowSelectors) {
        for (const el of Array.from(document.querySelectorAll(sel))) {
          const txt = clean(el.innerText || el.getAttribute('aria-label'));
          if (!txt || txt.length < 3 || seen.has(txt)) continue;
          seen.add(txt);
          out.items.push(txt.slice(0, 340));
          if (out.items.length >= 30) break;
        }
        if (out.items.length >= 30) break;
      }
      if (out.items.length === 0 && document.body) {
        out.items.push(clean(document.body.innerText).slice(0, 2600));
      }
      return out;
    })()
    """
    dom_data = await _cdp_eval_json(conn, ws, dom_js)
    shot_bytes: bytes | None = None
    try:
        shot_res = await conn.send_cmd(
            ws,
            "Page.captureScreenshot",
            {"format": "jpeg", "quality": 74},
        )
        b64 = shot_res.get("data")
        if isinstance(b64, str) and b64:
            shot_bytes = base64.b64decode(b64)
    except Exception:
        shot_bytes = None
    return shot_bytes, (dom_data if isinstance(dom_data, dict) else {})


def _probe_platform_authenticated(platform: str, ws_url: str | None = None) -> tuple[bool, str]:
    """Check CDP cookies AND DOM login markers to detect whether `platform` is authenticated."""
    spec = SOCIAL_PLATFORMS[platform]
    domains = spec["domains"]
    auth_names = set(spec["auth_cookies"])

    cookies = _CDP.get_all_cookies()
    plat_cookies = [
        c
        for c in cookies
        if any(
            str(c.get("domain") or "").lower().endswith(d)
            or str(c.get("domain") or "").lower() == d
            for d in domains
        )
    ]
    found_names = {str(c.get("name") or "") for c in plat_cookies if c.get("value")}
    if auth_names and (found_names & auth_names):
        save_encrypted_cookies(platform, plat_cookies)
        return True, ""

    # Platforms with strict server auth cookies (Instagram `sessionid`, X `auth_token`, TikTok `sid_tt`, Reddit `token_v2`)
    # MUST have their auth cookie present in `Network.getAllCookies()` (which includes HttpOnly cookies).
    # Public logged-out Instagram pages still render `a[href*="/reels/"]` in the DOM, so never false-positive on DOM there!
    if auth_names and platform in ("instagram", "x", "tiktok", "reddit"):
        return False, ""

    if ws_url:
        sels_json = json.dumps(list(spec["logged_in_selectors"]))
        probe_js = f"""
        (() => {{
          const u = (location.href || '').toLowerCase();
          if (u.includes('/accounts/login') || u.includes('/i/flow/login') || u.includes('/login')) return false;
          const sels = {sels_json};
          return Boolean(sels.some((s) => document.querySelector(s) !== null));
        }})()
        """
        try:
            res_dom = _CDP.run_on_tab(
                ws_url,
                lambda conn, ws: _cdp_eval_json(conn, ws, probe_js),
                timeout=8.0,
            )
            if res_dom is True:
                if plat_cookies:
                    save_encrypted_cookies(platform, plat_cookies)
                return True, ""
        except Exception:
            pass

    return False, ""


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
        + "\n".join(f"- {row}" for row in (dom_data.get("items") or [])[:28])
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


# ── Public API: Connect, Auto-Watch Login, Disconnect, Status ────────────────


_WATCHERS_ACTIVE: set[str] = set()
_WATCHERS_LOCK = threading.Lock()


def _start_login_watcher(
    plat: str,
    *,
    handle: str = "",
    perm: str = "ask",
    on_connected: Callable[[], None] | None = None,
) -> None:
    with _WATCHERS_LOCK:
        if plat in _WATCHERS_ACTIVE:
            return
        _WATCHERS_ACTIVE.add(plat)

    spec = SOCIAL_PLATFORMS[plat]

    def _watch() -> None:
        try:
            deadline = time.monotonic() + 240.0
            while time.monotonic() < deadline:
                time.sleep(1.2)
                if not _CDP._endpoint_alive():
                    return
                pages = _CDP._list_page_targets()
                tab_ws = None
                for p in pages:
                    if any(d in str(p.get("url") or "").lower() for d in spec["domains"]):
                        tab_ws = p.get("webSocketDebuggerUrl")
                        break
                ok_in, _ = _probe_platform_authenticated(plat, tab_ws)
                if ok_in:
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
                        result_summary=f"{spec['label']} persistent session authenticated.",
                        status="ok",
                    )
                    # Show non-intrusive toast inside the browser window so user knows JARVIS linked it!
                    if tab_ws:
                        toast_js = f"""
                        (() => {{
                          const d = document.createElement('div');
                          d.textContent = '✓ {spec["label"]} Connected to JARVIS — session saved!';
                          Object.assign(d.style, {{
                            position: 'fixed', bottom: '22px', right: '22px', zIndex: '2147483647',
                            padding: '12px 18px', borderRadius: '999px',
                            background: 'rgba(6, 22, 34, 0.95)', color: '#34d399',
                            border: '1px solid #34d399', fontFamily: 'system-ui, sans-serif',
                            fontSize: '13px', fontWeight: '600', boxShadow: '0 12px 32px rgba(0,0,0,0.45)'
                          }});
                          document.body.appendChild(d);
                          setTimeout(() => d.remove(), 5000);
                        }})()
                        """
                        try:
                            _CDP.run_on_tab(tab_ws, lambda c, w: _cdp_eval_json(c, w, toast_js), timeout=4.0)
                        except Exception:
                            pass
                    if callable(on_connected):
                        try:
                            on_connected()
                        except Exception:
                            pass
                    return
        finally:
            with _WATCHERS_LOCK:
                _WATCHERS_ACTIVE.discard(plat)

    threading.Thread(target=_watch, daemon=True, name=f"social-watch-{plat}").start()


def start_social_login(
    platform: str,
    *,
    handle: str = "",
    permission: str = "ask",
    on_connected: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Open a genuine visible Chrome/Edge window on `~/.jarvis_socials/browser_profile` and watch for sign-in."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    perm = permission if permission in accounts.PERMISSIONS else "ask"
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    try:
        # Navigate directly to home/inbox first — if already signed in, user skips login completely!
        tab = _CDP.get_or_open_tab(
            plat,
            spec["inbox_url"] if plat in ("instagram", "snapchat", "whatsapp") else spec["login_url"],
            headless=headless_env,
            force_navigate=True,
        )
        ws_url = str(tab["webSocketDebuggerUrl"])
        _CDP.run_on_tab(ws_url, lambda c, w: _cdp_wait_settled(c, w, 1.4), timeout=15.0)
        already_in, _ = _probe_platform_authenticated(plat, ws_url)
        if not already_in and spec["login_url"] != spec["inbox_url"]:
            # Ensure login form is shown cleanly if not yet signed in
            cur_u = str(_CDP.run_on_tab(ws_url, lambda c, w: _cdp_eval_json(c, w, "location.href"), timeout=5.0) or "")
            if "/login" not in cur_u.lower():
                _CDP.run_on_tab(
                    ws_url,
                    lambda c, w: c.send_cmd(w, "Page.navigate", {"url": spec["login_url"]}),
                    timeout=12.0,
                )
    except Exception as exc:
        return {
            "ok": False,
            "platform": plat,
            "label": spec["label"],
            "error": f"Could not launch {spec['label']} sign-in window: {exc}",
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

    _start_login_watcher(plat, handle=handle, perm=perm, on_connected=on_connected)
    return {
        "ok": True,
        "platform": plat,
        "label": spec["label"],
        "already_connected": False,
        "message": (
            f"Opened {spec['label']} in a dedicated window on your screen. "
            "Log in once (or scan the QR code) — JARVIS will automatically switch to CONNECTED the second you're in!"
        ),
    }


def disconnect_social_account(platform: str) -> dict[str, Any]:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}
    clear_encrypted_cookies(plat)
    _CDP.clear_platform_cookies(plat)
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


def _ensure_platform_ready(
    platform: str,
    *,
    auto_open_login_if_needed: bool = True,
) -> tuple[bool, str]:
    """Ensure `platform` is authenticated — auto-importing cookies or popping open the sign-in window if needed."""
    rec = accounts.get_account(platform)
    if rec and not rec.get("ignored"):
        allowed, reason = accounts.check_permission(platform, "read")
        if not allowed:
            return False, reason
        if bool(rec.get("session_connected") or rec.get("cookies_browser")):
            cb = str(rec.get("cookies_browser") or "").strip()
            if cb and not load_encrypted_cookies(platform):
                import_cookies_from_browser(
                    platform,
                    cb,
                    handle=str(rec.get("handle") or ""),
                    permission=str(rec.get("permission") or "ask"),
                )
            return True, "ok"

    # 1. Try silent browser cookie import across Firefox/Chrome/Edge/Brave/Opera profiles
    imp = import_cookies_from_browser(platform, "auto")
    if imp.get("ok"):
        return True, "ok"

    # 2. Check if `~/.jarvis_socials/browser_profile` ALREADY has an active login from an earlier window!
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")
    try:
        if (socials_root_dir() / "browser_profile").exists():
            _CDP.ensure_browser(headless=True)
            already, _ = _probe_platform_authenticated(platform)
            if already:
                accounts.connect_account(
                    platform,
                    session_connected=True,
                    auth_mode="web_session",
                    permission="ask",
                )
                return True, "ok"
    except Exception:
        pass

    # 3. Zero-dead-end UX: automatically pop open the visible login window right on screen!
    lbl = SOCIAL_PLATFORMS[platform]["label"]
    if auto_open_login_if_needed and not headless_env:
        login_res = start_social_login(platform, permission="ask")
        if login_res.get("already_connected"):
            return True, "ok"
        if login_res.get("ok"):
            # Wait briefly (up to 15s) in case user clicks 1-tap saved account immediately
            wait_end = time.monotonic() + 15.0
            while time.monotonic() < wait_end:
                time.sleep(1.2)
                if accounts.is_service_connected(platform):
                    return True, "ok"
            return (
                False,
                f"I just opened {lbl} right on your screen! Sign in once in that window "
                f"(your session is saved permanently), then ask me again.",
            )

    return (
        False,
        f"{lbl} is not signed in yet. Click 'SIGN IN WINDOW' on {lbl} in HUD -> LINKS (or say 'connect my {lbl}').",
    )


# ── 1. Check Unread DMs, Snaps & Notifications ───────────────────────────────


def _inspect_url_in_session(
    platform: str,
    url: str,
    *,
    headless: bool = True,
) -> tuple[bytes | None, dict[str, Any], bool]:
    tab = _CDP.get_or_open_tab(platform, url, headless=headless, force_navigate=True)
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _inspect(conn: _CdpConnection, ws: Any) -> tuple[bytes | None, dict[str, Any]]:
        await _cdp_wait_settled(conn, ws, 2.2)
        await _cdp_dismiss_popups(conn, ws)
        return await _cdp_capture_snapshot(conn, ws)

    shot, dom_data = _CDP.run_on_tab(ws_url, _inspect, timeout=35.0)
    logged_in, _ = _probe_platform_authenticated(platform, ws_url)
    return shot, dom_data, logged_in


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
                    "Say 'connect my Instagram' (or open HUD -> LINKS) to sign in once."
                ),
            }

    reports: list[str] = []
    checked: list[str] = []
    headless_pref = not bool(_CDP._endpoint_alive() and _CDP._headless is False)

    for plat in targets:
        spec = SOCIAL_PLATFORMS[plat]
        ready, reason = _ensure_platform_ready(plat, auto_open_login_if_needed=(len(targets) == 1))
        if not ready:
            reports.append(f"• {spec['label']}: {reason}")
            continue
        try:
            shot, dom_data, logged_in = _inspect_url_in_session(
                plat, spec["inbox_url"], headless=headless_pref
            )
            cur_u = str(dom_data.get("url") or "").lower()
            if not logged_in and any(k in cur_u for k in ("/accounts/login", "/i/flow/login", "/login")):
                # Session expired -> open visible login window automatically!
                start_social_login(plat)
                reports.append(
                    f"• {spec['label']}: Session needed sign-in — I opened the {spec['label']} login window on your screen."
                )
                continue

            digest = _analyze_with_vision_and_dom(
                shot,
                dom_data,
                instruction=(
                    f"You are inspecting the user's {spec['label']} inbox / chats screen. "
                    "List any unread messages/Snaps first (sender name + preview/status + time), "
                    "followed by the 3–5 most recent conversations. Be concise and accurate."
                ),
            )
            checked.append(plat)
            reports.append(f"=== {spec['label']} Inbox ===\n{digest}")

            if include_notifications and spec["notifications_url"] != spec["inbox_url"]:
                try:
                    n_shot, n_dom, _ = _inspect_url_in_session(
                        plat, spec["notifications_url"], headless=headless_pref
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


# ── 2. Open & Read Specific DM / Snap Conversation ───────────────────────────


async def _cdp_open_contact_thread(
    conn: _CdpConnection,
    ws: Any,
    platform: str,
    clean_contact: str,
) -> bool:
    """Find and click `clean_contact` in the inbox list, falling back to Instagram/social search/compose."""
    if not clean_contact:
        return True

    target_json = json.dumps(clean_contact.lower())

    # Step A: Look for a visible conversation row matching `clean_contact`
    find_row_js = f"""
    (() => {{
      const needle = {target_json};
      const candidates = document.querySelectorAll(
        '[role="listitem"], [role="row"], [data-testid="conversation"], div[role="button"], a[href*="/direct/t/"]'
      );
      for (const el of candidates) {{
        const txt = (el.innerText || el.getAttribute('aria-label') || '').toLowerCase();
        if (!txt || !txt.includes(needle)) continue;
        const r = el.getBoundingClientRect();
        if (r.width > 30 && r.height > 20 && r.top >= 0 && r.bottom <= window.innerHeight) {{
          return {{ x: r.left + Math.min(120, r.width / 2), y: r.top + r.height / 2 }};
        }}
      }}
      return null;
    }})()
    """
    pt = await _cdp_eval_json(conn, ws, find_row_js)
    if isinstance(pt, dict) and "x" in pt and "y" in pt:
        await _cdp_trusted_click(conn, ws, pt["x"], pt["y"])
        await asyncio.sleep(1.5)
        return True

    # Step B: Instagram Direct `New message` (`svg[aria-label="New message"]`) modal search for any @handle!
    if platform == "instagram":
        new_msg_pt = await _cdp_eval_json(
            conn,
            ws,
            """
            (() => {
              const svg = document.querySelector('svg[aria-label="New message"]');
              const btn = svg ? (svg.closest('[role="button"], button') || svg) : null;
              if (!btn) return null;
              const r = btn.getBoundingClientRect();
              return r.width > 0 ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
            })()
            """,
        )
        if isinstance(new_msg_pt, dict):
            await _cdp_trusted_click(conn, ws, new_msg_pt["x"], new_msg_pt["y"])
            await asyncio.sleep(1.0)
            inp_pt = await _cdp_eval_json(
                conn,
                ws,
                """
                (() => {
                  const inp = document.querySelector('input[name="queryBox"], input[placeholder*="Search" i]');
                  if (!inp) return null;
                  const r = inp.getBoundingClientRect();
                  return r.width > 0 ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
                })()
                """,
            )
            if isinstance(inp_pt, dict):
                await _cdp_trusted_click(conn, ws, inp_pt["x"], inp_pt["y"])
                await conn.send_cmd(ws, "Input.insertText", {"text": clean_contact})
                await asyncio.sleep(1.5)
                pick_pt = await _cdp_eval_json(
                    conn,
                    ws,
                    f"""
                    (() => {{
                      const needle = {target_json};
                      const rows = document.querySelectorAll('div[role="dialog"] div[role="button"], div[role="dialog"] label');
                      for (const el of rows) {{
                        const t = (el.innerText || '').toLowerCase();
                        if (t.includes(needle)) {{
                          const r = el.getBoundingClientRect();
                          if (r.width > 20 && r.height > 20) return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
                        }}
                      }}
                      return null;
                    }})()
                    """,
                )
                if isinstance(pick_pt, dict):
                    await _cdp_trusted_click(conn, ws, pick_pt["x"], pick_pt["y"])
                    await asyncio.sleep(0.5)
                    chat_btn = await _cdp_eval_json(
                        conn,
                        ws,
                        """
                        (() => {
                          const btns = document.querySelectorAll('div[role="dialog"] div[role="button"], div[role="dialog"] button');
                          for (const b of btns) {
                            const t = (b.innerText || '').trim().toLowerCase();
                            if (t === 'chat' || t === 'next') {
                              const r = b.getBoundingClientRect();
                              return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                            }
                          }
                          return null;
                        })()
                        """,
                    )
                    if isinstance(chat_btn, dict):
                        await _cdp_trusted_click(conn, ws, chat_btn["x"], chat_btn["y"])
                        await asyncio.sleep(1.5)
                        return True

    # Step C: Generic inbox search input (WhatsApp Web, Snapchat Web, X, TikTok)
    sb_pt = await _cdp_eval_json(
        conn,
        ws,
        """
        (() => {
          const inp = document.querySelector('input[placeholder*="Search" i], [role="searchbox"], [data-testid="SearchBox_Search_Input"]');
          if (!inp) return null;
          const r = inp.getBoundingClientRect();
          return r.width > 0 ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
        })()
        """,
    )
    if isinstance(sb_pt, dict):
        await _cdp_trusted_click(conn, ws, sb_pt["x"], sb_pt["y"])
        await conn.send_cmd(ws, "Input.insertText", {"text": clean_contact})
        await asyncio.sleep(1.3)
        pt2 = await _cdp_eval_json(conn, ws, find_row_js)
        if isinstance(pt2, dict):
            await _cdp_trusted_click(conn, ws, pt2["x"], pt2["y"])
            await asyncio.sleep(1.4)
            return True

    return False


def read_social_messages(platform: str, contact: str = "") -> dict[str, Any]:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat, auto_open_login_if_needed=True)
    if not ready:
        return {"ok": False, "error": reason}

    clean_contact = (contact or "").strip().lstrip("@")
    headless_pref = not bool(_CDP._endpoint_alive() and _CDP._headless is False)

    try:
        tab = _CDP.get_or_open_tab(plat, spec["inbox_url"], headless=headless_pref, force_navigate=True)
        ws_url = str(tab["webSocketDebuggerUrl"])

        async def _open_and_read(conn: _CdpConnection, ws: Any) -> tuple[bytes | None, dict[str, Any]]:
            await _cdp_wait_settled(conn, ws, 2.2)
            await _cdp_dismiss_popups(conn, ws)
            if clean_contact:
                await _cdp_open_contact_thread(conn, ws, plat, clean_contact)
            return await _cdp_capture_snapshot(conn, ws)

        shot, dom_data = _CDP.run_on_tab(ws_url, _open_and_read, timeout=45.0)
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


# ── 3. Send DM / Snap Reply & Publish Post (Trusted Lexical Input + Confirm!) ─


def _execute_send_message_now(platform: str, recipient: str, message: str, actor: str) -> str:
    spec = SOCIAL_PLATFORMS[platform]
    clean_rec = recipient.strip().lstrip("@")
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    tab = _CDP.get_or_open_tab(platform, spec["inbox_url"], headless=headless_env, force_navigate=True)
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _send_coro(conn: _CdpConnection, ws: Any) -> str:
        await _cdp_wait_settled(conn, ws, 2.2)
        await _cdp_dismiss_popups(conn, ws)
        if clean_rec:
            opened = await _cdp_open_contact_thread(conn, ws, platform, clean_rec)
            if not opened:
                raise RuntimeError(f"Could not find conversation or user '{clean_rec}' on {spec['label']}.")

        # Locate the DM message composer (supports Meta Lexical `[aria-label="Message"][role="textbox"]`, Snapchat, WhatsApp, X, TikTok)
        box_pt = await _cdp_eval_json(
            conn,
            ws,
            """
            (() => {
              const sels = [
                'div[aria-label*="Message" i][role="textbox"]',
                '[data-testid="dmComposerTextInput"]',
                'div[contenteditable="true"][role="textbox"]',
                'textarea[placeholder*="message" i]',
                'input[placeholder*="Send a chat" i]',
                'div[contenteditable="true"]',
                'textarea'
              ];
              for (const s of sels) {
                const els = Array.from(document.querySelectorAll(s));
                for (let i = els.length - 1; i >= 0; i--) {
                  const r = els[i].getBoundingClientRect();
                  if (r.width > 40 && r.height > 14 && r.bottom <= window.innerHeight + 20) {
                    return { x: r.left + Math.min(80, r.width / 2), y: r.top + r.height / 2 };
                  }
                }
              }
              return null;
            })()
            """,
        )
        if not isinstance(box_pt, dict):
            raise RuntimeError(f"Could not locate message input box on {spec['label']}.")

        await _cdp_trusted_click(conn, ws, box_pt["x"], box_pt["y"])
        await asyncio.sleep(0.2)
        await conn.send_cmd(ws, "Input.insertText", {"text": message})
        await asyncio.sleep(0.35)

        # Click explicit Send button if visible (Instagram Direct shows `Send` button), else press Enter
        send_pt = await _cdp_eval_json(
            conn,
            ws,
            """
            (() => {
              const btns = document.querySelectorAll('div[role="button"], button, [data-testid="dmComposerSendButton"]');
              for (const b of btns) {
                const t = (b.innerText || b.getAttribute('aria-label') || '').trim().toLowerCase();
                if (t === 'send' || t === 'send message') {
                  const r = b.getBoundingClientRect();
                  if (r.width > 10 && r.height > 10) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                }
              }
              return null;
            })()
            """,
        )
        if isinstance(send_pt, dict):
            await _cdp_trusted_click(conn, ws, send_pt["x"], send_pt["y"])
        else:
            await _cdp_press_key(conn, ws, "Enter", 13)

        await asyncio.sleep(1.2)
        return f"Sent {spec['label']} message to {clean_rec}."

    res_msg = _CDP.run_on_tab(ws_url, _send_coro, timeout=50.0)
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
    ready, reason = _ensure_platform_ready(plat, auto_open_login_if_needed=True)
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
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    tab = _CDP.get_or_open_tab(platform, spec["compose_post_url"], headless=headless_env, force_navigate=True)
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _post_coro(conn: _CdpConnection, ws: Any) -> str:
        await _cdp_wait_settled(conn, ws, 2.0)
        box_pt = await _cdp_eval_json(
            conn,
            ws,
            """
            (() => {
              const el = document.querySelector('[data-testid="tweetTextarea_0"], [role="textbox"][contenteditable="true"], textarea');
              if (!el) return null;
              const r = el.getBoundingClientRect();
              return r.width > 20 ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null;
            })()
            """,
        )
        if not isinstance(box_pt, dict):
            raise RuntimeError(f"Could not find post composer on {spec['label']}.")
        await _cdp_trusted_click(conn, ws, box_pt["x"], box_pt["y"])
        await asyncio.sleep(0.2)
        await conn.send_cmd(ws, "Input.insertText", {"text": text})
        await asyncio.sleep(0.4)
        btn_pt = await _cdp_eval_json(
            conn,
            ws,
            """
            (() => {
              const el = document.querySelector('[data-testid="tweetButton"], [data-testid="tweetButtonInline"]');
              if (el) {
                const r = el.getBoundingClientRect();
                if (r.width > 10) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
              }
              for (const b of document.querySelectorAll('button, [role="button"]')) {
                if ((b.innerText || '').trim().toLowerCase() === 'post') {
                  const r = b.getBoundingClientRect();
                  if (r.width > 10) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                }
              }
              return null;
            })()
            """,
        )
        if isinstance(btn_pt, dict):
            await _cdp_trusted_click(conn, ws, btn_pt["x"], btn_pt["y"])
            await asyncio.sleep(1.4)
            return f"Published post on {spec['label']}."
        raise RuntimeError(f"Draft typed into {spec['label']} — click Post in the window to finish.")

    res_msg = _CDP.run_on_tab(ws_url, _post_coro, timeout=50.0)
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
    ready, reason = _ensure_platform_ready(plat, auto_open_login_if_needed=True)
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
    """Hands-free navigation & interaction (`open_feed`, `open_reels`, `open_inbox`, `open_profile`, `next`, `previous`, `like`, `save`, `look`)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    cmd = (command or "open_feed").strip().lower()
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    # Opportunistic cookie sync without blocking visible window launch
    if not accounts.is_service_connected(plat):
        import_cookies_from_browser(plat, "auto")

    try:
        if cmd in ("open_feed", "home", "feed", "open"):
            tab = _CDP.get_or_open_tab(plat, spec["home_url"], headless=headless_env, force_navigate=True)
            _start_login_watcher(plat)
            return {"ok": True, "message": f"Opened your {spec['label']} feed."}

        if cmd in ("open_reels", "reels", "foryou", "spotlight"):
            tab = _CDP.get_or_open_tab(plat, spec["reels_url"], headless=headless_env, force_navigate=True)
            _start_login_watcher(plat)
            return {"ok": True, "message": f"Opened {spec['label']} Reels / Spotlight."}

        if cmd in ("open_inbox", "inbox", "dms", "chats"):
            tab = _CDP.get_or_open_tab(plat, spec["inbox_url"], headless=headless_env, force_navigate=True)
            _start_login_watcher(plat)
            return {"ok": True, "message": f"Opened your {spec['label']} inbox."}

        if cmd in ("open_profile", "profile"):
            handle = (target or (accounts.get_account(plat) or {}).get("handle") or "").strip().lstrip("@")
            if not handle:
                return {"ok": False, "error": f"Pass a @username (`target`) to open on {spec['label']}."}
            url = spec["profile_url_tpl"].format(handle=handle)
            _CDP.get_or_open_tab(plat, url, headless=headless_env, force_navigate=True)
            _start_login_watcher(plat)
            return {"ok": True, "message": f"Opened @{handle} on {spec['label']} ({url})."}

        # For in-page commands (`next`, `previous`, `like`, `save`, `look`), adopt open tab without forcing reload!
        tab = _CDP.get_or_open_tab(plat, spec["reels_url"], headless=headless_env, force_navigate=False)
        ws_url = str(tab["webSocketDebuggerUrl"])

        if cmd in ("next", "scroll_down", "down", "skip"):
            async def _next(conn: _CdpConnection, ws: Any) -> None:
                await _cdp_press_key(conn, ws, "ArrowDown", 40)
                await conn.send_cmd(
                    ws,
                    "Input.dispatchMouseEvent",
                    {"type": "mouseWheel", "x": 600, "y": 440, "deltaX": 0, "deltaY": 720},
                )
            _CDP.run_on_tab(ws_url, _next, timeout=12.0)
            return {"ok": True, "message": f"Moved to the next post/reel on {spec['label']}."}

        if cmd in ("previous", "prev", "scroll_up", "up", "back"):
            async def _prev(conn: _CdpConnection, ws: Any) -> None:
                await _cdp_press_key(conn, ws, "ArrowUp", 38)
                await conn.send_cmd(
                    ws,
                    "Input.dispatchMouseEvent",
                    {"type": "mouseWheel", "x": 600, "y": 440, "deltaX": 0, "deltaY": -720},
                )
            _CDP.run_on_tab(ws_url, _prev, timeout=12.0)
            return {"ok": True, "message": f"Moved back to the previous post/reel on {spec['label']}."}

        if cmd == "like":
            if accounts.get_account(plat):
                allowed, rsn = accounts.check_permission(plat, "write")
                if not allowed:
                    return {"ok": False, "error": rsn}

            async def _like(conn: _CdpConnection, ws: Any) -> bool:
                pt = await _cdp_eval_json(
                    conn,
                    ws,
                    """
                    (() => {
                      const sels = [
                        'svg[aria-label="Like"]',
                        '[data-testid="like"]',
                        '[data-e2e="like-icon"]',
                        'button[aria-label="Like"]'
                      ];
                      let best = null;
                      let bestDist = 1e9;
                      const cy = window.innerHeight / 2;
                      for (const s of sels) {
                        for (const el of document.querySelectorAll(s)) {
                          const target = el.closest('button, [role="button"]') || el;
                          const r = target.getBoundingClientRect();
                          if (r.width < 10 || r.height < 10 || r.bottom < 0 || r.top > window.innerHeight) continue;
                          const d = Math.abs((r.top + r.height / 2) - cy);
                          if (d < bestDist) {
                            bestDist = d;
                            best = { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                          }
                        }
                      }
                      return best;
                    })()
                    """,
                )
                if isinstance(pt, dict):
                    await _cdp_trusted_click(conn, ws, pt["x"], pt["y"])
                    return True
                return False

            if _CDP.run_on_tab(ws_url, _like, timeout=12.0):
                return {"ok": True, "message": f"Liked the active post/reel on {spec['label']}."}
            return {"ok": False, "error": f"Could not find an unliked Like button on {spec['label']}."}

        if cmd in ("save", "bookmark"):
            async def _save(conn: _CdpConnection, ws: Any) -> bool:
                pt = await _cdp_eval_json(
                    conn,
                    ws,
                    """
                    (() => {
                      const sels = [
                        'svg[aria-label="Save"]',
                        '[data-testid="bookmark"]',
                        'button[aria-label*="Save" i]',
                        'button[aria-label*="Bookmark" i]'
                      ];
                      for (const s of sels) {
                        for (const el of document.querySelectorAll(s)) {
                          const target = el.closest('button, [role="button"]') || el;
                          const r = target.getBoundingClientRect();
                          if (r.width >= 10 && r.top >= 0 && r.bottom <= window.innerHeight) {
                            return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                          }
                        }
                      }
                      return null;
                    })()
                    """,
                )
                if isinstance(pt, dict):
                    await _cdp_trusted_click(conn, ws, pt["x"], pt["y"])
                    return True
                return False

            if _CDP.run_on_tab(ws_url, _save, timeout=12.0):
                return {"ok": True, "message": f"Saved/bookmarked the active item on {spec['label']}."}
            return {"ok": False, "error": f"Could not find Save/Bookmark button on {spec['label']}."}

        if cmd in ("look", "describe", "see", "what_is_this"):
            shot, dom_data = _CDP.run_on_tab(ws_url, _cdp_capture_snapshot, timeout=20.0)
            desc = _analyze_with_vision_and_dom(
                shot,
                dom_data,
                instruction=f"Describe what is currently visible on the user's {spec['label']} screen (post, reel, creator, caption, and visuals).",
            )
            return {"ok": True, "message": desc}

        return {"ok": False, "error": f"Unknown feed command '{command}'."}
    except Exception as exc:
        return {"ok": False, "error": f"{spec['label']} feed control failed: {exc}"}
