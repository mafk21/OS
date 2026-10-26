"""
core/social_hub.py — Silent Background Socials Engine + Live Interactive HUD Social Viewport
(Instagram, Snapchat, TikTok, X, WhatsApp, Reddit).

Architecture:
  * Instagram: reuse the current browser session with same-origin fetch, or use
    encrypted-cookie HTTP without starting a browser. Safe read failures may
    recover through headless CDP. A native web-composer fallback runs only if
    lookup failed BEFORE a send attempt; it verifies the exact profile, preserves
    existing drafts, and requires a provider-issued send acknowledgment.
  * Background tasks and HUD interactions use separate tabs in the persistent
    headless profile. Routine social operations never open a desktop window.
  * Saved credentials are not proof of live login. API/DOM observations update
    shared session health; login and security challenges are shown in the HUD.
  * Outbound actions obey Ask/Full/ReadOnly/Paused policies. Ask approval executes
    once, rechecks policy/account identity, and reports the actual result.
    Unknown write outcomes are never retried or presented as successful.
  * Instagram's web APIs/markup may change. Unsupported operations fail honestly;
    this is not an official general-purpose personal Instagram messaging API.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import base64
import hashlib
from io import BytesIO
import json
import os
import platform as _py_platform
from pathlib import Path
import random
import re
import shutil
import socket
import stat
import sys
import subprocess
import threading
import time
from typing import Any, Callable
from urllib.parse import quote, urlsplit

import httpx
import websockets

from core import confirm as confirm_gate
from core import security_vault
from memory import accounts
from core.instagram_direct import InstagramSession, RecipientError, SendRejected, DeliveryUnknown, exact_thread, receipt_id

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

_IG_WEB_APP_ID = "936619743392459"
_DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)
_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
)


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


# ── Tier 1: Zero-Window Direct Authenticated HTTP API (Instagram & Reddit) ───


def _usable_platform_cookies(platform: str, cookies: list) -> list[dict[str, Any]]:
    domains = SOCIAL_PLATFORMS[platform]["domains"]
    now = time.time()
    usable = []
    for c in cookies:
        if not isinstance(c, dict):
            continue
        domain = str(c.get("domain") or "").lower().lstrip(".")
        if not any(domain == d or domain.endswith("." + d) for d in domains):
            continue
        try:
            expiry = float(c.get("expires") or 0)
        except (ValueError, TypeError):
            continue
        if expiry <= 0 or expiry > now:
            usable.append(c)
    return usable


def _cookie_dict(platform: str) -> dict[str, str]:
    cookies = _usable_platform_cookies(platform, load_encrypted_cookies(platform))
    if _CDP._endpoint_alive():
        live = _usable_platform_cookies(platform, _CDP.get_all_cookies())
        auth = set(SOCIAL_PLATFORMS[platform]["auth_cookies"])
        # A refreshed browser session wins, but don't overwrite a saved login
        # with anonymous cookies from an unrelated/just-created tab.
        if any(c.get("name") in auth and c.get("value") for c in live):
            if live != cookies:
                save_encrypted_cookies(platform, live)
            cookies = live
    return {str(c["name"]): str(c["value"]) for c in cookies if c.get("name") and c.get("value")}


def _set_session_health(platform: str, health: str) -> None:
    previous = (accounts.get_account(platform) or {}).get("session_health")
    accounts.update_session_health(platform, health)
    if previous != health:
        try:
            from core.apex_bridge import get_active_bridge
            bridge = get_active_bridge()
            if bridge is not None:
                bridge.push_integrations()
        except Exception:
            pass


def _ig_client(cookies: dict[str, str]) -> InstagramSession:
    return InstagramSession(sys.modules[__name__], cookies)


def _ig_headers(cdict: dict[str, str]) -> dict[str, str]:
    csrf = cdict.get("csrftoken", "")
    return {
        "User-Agent": _DESKTOP_UA,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": _IG_WEB_APP_ID,
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrf,
        "Referer": "https://www.instagram.com/direct/inbox/",
        "Origin": "https://www.instagram.com",
    }


def _ig_format_item(item: dict[str, Any], my_pk: str, user_map: dict[str, str]) -> str:
    uid = str(item.get("user_id") or "")
    sender = "You" if (my_pk and uid == my_pk) else user_map.get(uid, "Them")
    itype = str(item.get("item_type") or "")
    if itype == "text":
        body = str(item.get("text") or "").strip()
    elif itype in ("clip", "reel_share"):
        clip_txt = (
            ((item.get("clip") or {}).get("clip") or {}).get("caption", {}) or {}
        ).get("text") or (item.get("reel_share") or {}).get("text") or ""
        body = f"[Shared Reel]{': ' + str(clip_txt)[:90] if clip_txt else ''}"
    elif itype == "media_share":
        body = "[Shared Post]"
    elif itype == "voice_media":
        body = "[Voice Note]"
    elif itype == "raven_media":
        body = "[Photo/Video Snap]"
    elif itype == "media":
        body = "[Photo/Video]"
    elif itype == "link":
        link_txt = ((item.get("link") or {}).get("text")) or "[Shared Link]"
        body = str(link_txt)
    elif itype == "like":
        body = "❤️"
    else:
        body = str(item.get("text") or f"[{itype or 'message'}]").strip()
    return f"{sender}: {body}"


def _ig_api_fetch_inbox(
    *,
    include_notifications: bool = True,
    limit: int = 15,
) -> dict[str, Any] | None:
    """Fetch Instagram Direct inbox & notifications silently via HTTP API (0 windows, ~250ms)."""
    cdict = _cookie_dict("instagram")
    if "sessionid" not in cdict:
        return None
    my_pk = str(cdict.get("ds_user_id") or "")

    try:
        with _ig_client(cdict) as client:
            r = client.get(
                "https://www.instagram.com/api/v1/direct_v2/inbox/",
                params={
                    "persistentBadging": "true",
                    "folder": "",
                    "limit": str(limit),
                    "thread_message_limit": "8",
                },
            )
            if r.status_code != 200:
                return None
            data = r.json()
            inbox = data.get("inbox") or {}
            threads = inbox.get("threads")
            if not isinstance(threads, list):
                return None

            unseen_count = int(inbox.get("unseen_count") or 0)
            unread_lines: list[str] = []
            recent_lines: list[str] = []

            for th in threads[:limit]:
                users = th.get("users") or []
                user_map: dict[str, str] = {}
                handles: list[str] = []
                for u in users:
                    pk = str(u.get("pk") or u.get("pk_id") or "")
                    uname = str(u.get("username") or "").strip()
                    fname = str(u.get("full_name") or "").strip()
                    label = f"@{uname}" + (f" ({fname})" if fname and fname != uname else "") if uname else (fname or "User")
                    if pk:
                        user_map[pk] = f"@{uname}" if uname else label
                    handles.append(label)

                title = str(th.get("thread_title") or "").strip() or ", ".join(handles) or "Conversation"
                items = th.get("items") or []
                preview = _ig_format_item(items[0], my_pk, user_map) if items else "(no messages)"

                is_unread = bool(int(th.get("read_state") or 0) > 0)
                if not is_unread and my_pk and items:
                    last_item_ts = int(items[0].get("timestamp") or 0)
                    seen_info = (th.get("last_seen_at") or {}).get(my_pk) or {}
                    seen_ts = int(seen_info.get("timestamp") or 0)
                    last_uid = str(items[0].get("user_id") or "")
                    if last_uid != my_pk and last_item_ts > seen_ts > 0:
                        is_unread = True

                row_txt = f"• {title} — {preview}"
                if is_unread:
                    unread_lines.append(f"• [UNREAD] {title} — {preview}")
                else:
                    recent_lines.append(row_txt)

            parts = [f"=== Instagram Inbox ({max(unseen_count, len(unread_lines))} unread) ==="]
            if unread_lines:
                parts.append("Unread Messages:\n" + "\n".join(unread_lines[:10]))
            else:
                parts.append("Unread Messages: None — you're all caught up!")
            if recent_lines:
                parts.append("Recent Conversations:\n" + "\n".join(recent_lines[:6]))

            if include_notifications:
                try:
                    nr = client.get("https://www.instagram.com/api/v1/news/inbox/")
                    if nr.status_code == 200:
                        ndata = nr.json()
                        stories = (ndata.get("new_stories") or []) + (ndata.get("old_stories") or [])[:5]
                        notif_rows: list[str] = []
                        for st in stories[:6]:
                            args = st.get("args") or {}
                            txt = re.sub(r"\s+", " ", str(args.get("text") or "").strip())
                            if txt:
                                notif_rows.append(f"• {txt}")
                        if notif_rows:
                            parts.append("--- Instagram Notifications ---\n" + "\n".join(notif_rows))
                except Exception:
                    pass

            return {"ok": True, "summary": "\n\n".join(parts), "threads": threads}
    except Exception:
        return None


def _ig_api_read_thread(contact: str) -> dict[str, Any] | None:
    """Read a specific Instagram Direct thread silently via HTTP API (0 windows)."""
    cdict = _cookie_dict("instagram")
    if "sessionid" not in cdict:
        return None
    my_pk = str(cdict.get("ds_user_id") or "")
    try:
        with _ig_client(cdict) as client:
            r = client.get(
                "https://www.instagram.com/api/v1/direct_v2/inbox/",
                params={"persistentBadging": "true", "limit": "25", "thread_message_limit": "20"},
            )
            if r.status_code != 200:
                return None
            inbox = r.json().get("inbox") or {}
            threads = inbox.get("threads") or []
            chosen = exact_thread(threads, contact)
            cursors = set()
            for _ in range(5):
                cursor = inbox.get("oldest_cursor")
                if chosen or not contact or not inbox.get("has_older") or not cursor or cursor in cursors:
                    break
                cursors.add(cursor)
                page = client.get("https://www.instagram.com/api/v1/direct_v2/inbox/",
                                  params={"limit": "50", "cursor": cursor, "thread_message_limit": "20"})
                if page.status_code != 200:
                    return None
                inbox = page.json().get("inbox") or {}
                chosen = exact_thread(inbox.get("threads") or [], contact)
            if chosen is None:
                raise RecipientError("Conversation not found. Use the person's exact @username, not a display-name fragment.")

            tid = str(chosen.get("thread_id") or "")
            if tid:
                tr = client.get(
                    f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/",
                    params={"limit": "20"},
                )
                if tr.status_code == 200 and isinstance(tr.json().get("thread"), dict):
                    detail = tr.json()["thread"]
                    if contact and not exact_thread([detail], contact):
                        raise RecipientError("Instagram returned a different conversation. No messages were read.")
                    chosen = detail

            user_map: dict[str, str] = {}
            for u in chosen.get("users") or []:
                pk = str(u.get("pk") or u.get("pk_id") or "")
                uname = str(u.get("username") or "").strip()
                if pk:
                    user_map[pk] = f"@{uname}" if uname else str(u.get("full_name") or "Them")

            items = list(reversed((chosen.get("items") or [])[:18]))
            lines = [_ig_format_item(it, my_pk, user_map) for it in items]
            title = str(chosen.get("thread_title") or contact or "Thread")
            return {
                "ok": True,
                "platform": "instagram",
                "label": "Instagram",
                "contact": title,
                "messages": f"=== Instagram Chat with {title} ===\n" + ("\n".join(lines) or "(no messages yet)"),
            }
    except RecipientError:
        raise
    except Exception:
        return None


def _ig_api_send_dm(recipient: str, message: str) -> str | None:
    """Send an Instagram Direct text message silently via HTTP API (0 windows, ~250ms)."""
    cdict = _cookie_dict("instagram")
    if "sessionid" not in cdict:
        return None
    clean_rec = recipient.strip().lstrip("@")
    needle = clean_rec.lower()
    attempted = False

    try:
        with _ig_client(cdict) as client:
            # Exact handles only. Group membership/display-name substrings are
            # not proof of identity. Resolve before issuing any write.
            r_in = client.get("https://www.instagram.com/api/v1/direct_v2/inbox/",
                              params={"limit": "50", "thread_message_limit": "1"})
            if r_in.status_code != 200:
                return None
            inbox = r_in.json().get("inbox")
            if not isinstance(inbox, dict):
                return None
            chosen = exact_thread(inbox.get("threads") or [], clean_rec)
            thread_id = str((chosen or {}).get("thread_id") or "")
            user_pk = ""
            if not chosen:
                r_prof = client.get("https://www.instagram.com/api/v1/users/web_profile_info/",
                                    params={"username": clean_rec})
                if r_prof.status_code != 200:
                    raise RecipientError("Could not resolve that recipient. Use their exact @username and check the Instagram HUD.")
                user = ((r_prof.json().get("data") or {}).get("user")) or {}
                if str(user.get("username") or "").casefold() != needle:
                    raise RecipientError("Recipient identity could not be verified. Nothing was sent; provide the exact @username.")
                user_pk = str(user.get("id") or user.get("pk") or "")
            if not thread_id and not user_pk:
                raise RecipientError("No verified recipient found. Nothing was sent.")

            client_ctx = str((int(time.time() * 1000) << 22) | random.randint(10000, 3999999))
            form_data: dict[str, str] = {
                "action": "send_item",
                "text": message,
                "client_context": client_ctx,
                "mutation_token": client_ctx,
            }
            if thread_id:
                form_data["thread_ids"] = json.dumps([thread_id])
            else:
                form_data["recipient_users"] = json.dumps([[str(user_pk)]])

            client.prepare_write()
            current_sender = _cookie_dict("instagram")
            identity_key = "ds_user_id" if cdict.get("ds_user_id") else "sessionid"
            if current_sender.get(identity_key) != cdict.get(identity_key):
                raise RecipientError("The signed-in account changed during lookup. Nothing was sent; request a new confirmation.")
            attempted = True
            r_send = client.post(
                "https://www.instagram.com/api/v1/direct_v2/threads/broadcast/text/", data=form_data)
            data = r_send.json()
            ack = receipt_id(data) if r_send.status_code == 200 else ""
            if ack:
                return (f"Sent Instagram message to @{clean_rec} (silently in the background). "
                        f"Instagram acknowledgment: {ack}. This does not mean the recipient has read it.")
            if isinstance(data, dict) and data.get("status") == "fail":
                raise SendRejected("Instagram rejected the send. Open its HUD to check login, challenges or messaging restrictions; no automatic retry was made.")
            raise DeliveryUnknown("Instagram did not acknowledge the message. Delivery is unknown; check the chat in the HUD before retrying. No automatic retry was made.")
    except (RecipientError, SendRejected, DeliveryUnknown):
        raise
    except Exception as exc:
        if attempted:
            raise DeliveryUnknown("The send was attempted but no reliable receipt was received. Delivery is unknown; check the HUD before retrying. No automatic retry was made.") from exc
        return None
    return None


def _reddit_api_fetch_inbox() -> dict[str, Any] | None:
    cdict = _cookie_dict("reddit")
    if not ("reddit_session" in cdict or "token_v2" in cdict):
        return None
    try:
        r = httpx.get(
            "https://www.reddit.com/message/inbox.json?limit=12",
            headers={"User-Agent": _DESKTOP_UA},
            cookies=cdict,
            follow_redirects=True,
            timeout=8.0,
        )
        if r.status_code != 200:
            return None
        children = ((r.json().get("data") or {}).get("children")) or []
        unread: list[str] = []
        recent: list[str] = []
        for ch in children[:12]:
            d = ch.get("data") or {}
            author = str(d.get("author") or "reddit")
            subj = str(d.get("subject") or "")
            body = re.sub(r"\s+", " ", str(d.get("body") or ""))[:140]
            line = f"• u/{author} ({subj}): {body}"
            if d.get("new"):
                unread.append(f"• [UNREAD] u/{author} ({subj}): {body}")
            else:
                recent.append(line)
        parts = [f"=== Reddit Inbox ({len(unread)} unread) ==="]
        parts.append("Unread:\n" + ("\n".join(unread) if unread else "None"))
        if recent:
            parts.append("Recent:\n" + "\n".join(recent[:5]))
        return {"ok": True, "summary": "\n\n".join(parts)}
    except Exception:
        return None


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
    """Import active session cookies from installed browsers (with automatic fallback on Windows v20 lock)."""
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
                if not any(dom.lstrip(".") == d or dom.endswith("." + d) for d in domains):
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
                    "window on your screen right now! Sign in once there and all future checks stay 100% in the background."
                ),
            }

    return {
        "ok": False,
        "platform": plat,
        "error": (
            f"Could not read live {spec['label']} cookies from {browser or 'local browsers'}"
            + (f" ({last_err[:120]})" if last_err else "")
            + f". Click 'OPEN IN HUD' or 'SIGN IN WINDOW' to sign into {spec['label']} once."
        ),
    }


# ── Native Chrome DevTools Protocol (CDP) Client & Browser Manager ───────────


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _spawn_visible_or_hidden(args: list[str], *, visible: bool) -> subprocess.Popen:
    """Spawn browser bypassing `main.py`'s Windows `CREATE_NO_WINDOW` patch ONLY when `visible=True`."""
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
        self._ws_io_lock = threading.RLock()
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

    def shutdown(self) -> None:
        with self._lock:
            self._shutdown_locked()

    def _shutdown_locked(self) -> None:
        if self._port and not os.environ.get("JARVIS_SOCIALS_CDP_PORT", "").strip():
            try:
                v = httpx.get(f"http://127.0.0.1:{self._port}/json/version", timeout=1.0).json()
                b_ws = v.get("webSocketDebuggerUrl")
                if b_ws:
                    self.run_on_tab(
                        b_ws,
                        lambda c, ws: c.send_cmd(ws, "Browser.close", timeout=2.0),
                        timeout=3.0,
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
        if not os.environ.get("JARVIS_SOCIALS_CDP_PORT", "").strip():
            self._port = 0
        self._headless = None
        self._tab_ids.clear()
        time.sleep(0.3)

    def ensure_browser(self, *, headless: bool = True, start_url: str = "about:blank") -> int:
        env_port = os.environ.get("JARVIS_SOCIALS_CDP_PORT", "").strip()
        if env_port.isdigit():
            self._port = int(env_port)
            self._headless = bool(headless)
            return self._port

        with self._lock:
            if self._endpoint_alive():
                # Switch mode cleanly if caller needs visible window vs silent headless background!
                if self._headless is not None and self._headless != bool(headless):
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
                # 100% invisible background browser — NEVER opens a desktop window!
                args.extend(["--headless=new", "--mute-audio", "--disable-gpu"])
            else:
                args.append("--new-window")
            args.append("about:blank")  # hydrate cookies before navigating to authenticated pages

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

            all_saved: list[dict[str, Any]] = []
            live_cookies = self.get_all_cookies()
            for pk, spec in SOCIAL_PLATFORMS.items():
                live = _usable_platform_cookies(pk, live_cookies)
                if any(c.get("name") in spec["auth_cookies"] and c.get("value") for c in live):
                    save_encrypted_cookies(pk, live)
                else:
                    all_saved.extend(_usable_platform_cookies(pk, load_encrypted_cookies(pk)))
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
        headless: bool = True,
        force_navigate: bool = True,
        purpose: str = "interactive",
    ) -> dict[str, Any]:
        self.ensure_browser(headless=headless, start_url=url)
        spec = SOCIAL_PLATFORMS[platform]
        domains = spec["domains"]

        pages = self._list_page_targets()
        chosen: dict[str, Any] | None = None

        tab_key = platform if purpose == "interactive" else f"{platform}:{purpose}"
        tid = self._tab_ids.get(tab_key)
        if tid:
            chosen = next((p for p in pages if p.get("id") == tid), None)

        if chosen is None and purpose == "interactive":
            for p in pages:
                u_low = str(p.get("url") or "").lower()
                if (p.get("id") not in [v for k, v in self._tab_ids.items() if k != tab_key]
                        and any((urlsplit(u_low).hostname or "") == d or
                                (urlsplit(u_low).hostname or "").endswith("." + d) for d in domains)):
                    chosen = p
                    break

        if chosen is None:
            for p in pages:
                u_low = str(p.get("url") or "").lower()
                if p.get("id") not in self._tab_ids.values() and (u_low in ("about:blank", "") or "newtab" in u_low):
                    chosen = p
                    break

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
        self._tab_ids[tab_key] = str(chosen.get("id") or "")
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

        self.run_on_tab(ws_url, _prep, timeout=25.0)
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
            return self.run_on_tab(ws_url, _fetch, timeout=10.0)
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

        self.run_on_tab(ws_url, _push, timeout=10.0)

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
                if any(dom.lstrip(".") == d or dom.endswith("." + d) for d in domains):
                    await conn.send_cmd(
                        ws,
                        "Network.deleteCookies",
                        {"name": c.get("name"), "domain": c.get("domain"), "path": c.get("path", "/")},
                    )

        try:
            self.run_on_tab(ws_url, _wipe, timeout=10.0)
        except Exception:
            pass
        keys = [k for k in self._tab_ids if k == platform or k.startswith(platform + ":")]
        for key in keys:
            tid = self._tab_ids.pop(key, None)
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
        # Sync Playwright keeps an asyncio loop running on its calling thread
        # (including the confirmation worker). CDP must not nest asyncio.run()
        # on that thread. Build/await the coroutine on a separate thread only
        # when necessary; keep Playwright objects on their owning thread.
        def execute() -> Any:
            # Acquire this INSIDE the executing thread. A worker cannot acquire
            # an RLock held by the caller that is waiting for that worker.
            with self._ws_io_lock:
                return asyncio.run(_CdpConnection(ws_url).call_many(fn, timeout=timeout))

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return execute()

        # No retry: the original result/exception, including an ambiguous
        # write timeout, crosses this boundary exactly once.
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="social-cdp") as worker:
            return worker.submit(execute).result()


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


async def _cdp_wait_settled(conn: _CdpConnection, ws: Any, wait_s: float = 1.6) -> None:
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
            await asyncio.sleep(0.3)
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
        await asyncio.sleep(0.03)


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
        await asyncio.sleep(0.03)


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

    plat_cookies = _usable_platform_cookies(platform, _CDP.get_all_cookies())
    found_names = {str(c.get("name") or "") for c in plat_cookies if c.get("value")}
    has_cookie = bool(found_names & auth_names)
    if has_cookie:
        save_encrypted_cookies(platform, plat_cookies)
        if platform != "instagram":
            return True, ""
    if auth_names and platform in ("instagram", "x", "tiktok", "reddit") and not has_cookie:
        return False, "No usable authentication cookie"
    if platform == "instagram" and not ws_url:
        for page in _CDP._list_page_targets():
            if urlsplit(str(page.get("url") or "")).hostname in ("instagram.com", "www.instagram.com"):
                ws_url = page.get("webSocketDebuggerUrl")
                break

    if ws_url:
        sels_json = json.dumps(list(spec["logged_in_selectors"]))
        probe_js = f"""
        (() => {{
          const u = (location.href || '').toLowerCase();
          if (u.includes('/accounts/login') || u.includes('/i/flow/login') || u.includes('/login') || u.includes('/challenge') || u.includes('/checkpoint')) return false;
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
                _set_session_health(platform, "authenticated")
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


# ── Live Interactive HUD Social Viewport Engine ──────────────────────────────


_HUD_SOCIAL_LOCK = threading.RLock()
_HUD_SOCIAL_SESSIONS: dict[str, dict[str, Any]] = {}


def _resolve_view_url(plat: str, view: str = "feed", target: str = "") -> str:
    spec = SOCIAL_PLATFORMS[plat]
    v = (view or "feed").strip().lower()
    if v in ("reels", "foryou", "spotlight", "open_reels"):
        return spec["reels_url"]
    if v in ("inbox", "dms", "chats", "messages", "open_inbox"):
        return spec["inbox_url"]
    if v in ("notifications", "alerts"):
        return spec["notifications_url"]
    if v in ("login", "signin"):
        return spec["login_url"]
    if v in ("profile", "open_profile") and target:
        return spec["profile_url_tpl"].format(handle=target.strip().lstrip("@"))
    return spec["home_url"]


async def _cdp_apply_hud_viewport(conn: _CdpConnection, ws: Any, layout: str) -> tuple[int, int]:
    is_wide = layout == "wide"
    width, height = (1024, 680) if is_wide else (430, 760)
    try:
        await conn.send_cmd(
            ws,
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1.5 if not is_wide else 1.25,
                "mobile": False,
            },
        )
    except Exception:
        pass
    return width, height


def open_social_in_hud(
    platform: str,
    *,
    view: str = "feed",
    target: str = "",
    layout: str = "mobile",
) -> dict[str, Any]:
    """Open `platform` directly inside JARVIS's own HUD (100% headless CDP — zero external desktop window)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    mode = "wide" if str(layout or "").lower() == "wide" else (
        "wide" if plat == "whatsapp" else "mobile"
    )

    rec = accounts.get_account(plat) or {}
    if not rec.get("ignored") and not accounts.is_service_connected(plat) and not _cookie_dict(plat):
        import_cookies_from_browser(plat, "auto", permission=str(rec.get("permission") or "ask"))
    # Navigate to what the user asked for. Instagram itself may redirect to
    # login; never redirect away from DMs based only on stale local metadata.
    initial_view = view
    url = _resolve_view_url(plat, initial_view, target=target)

    width, height = (1024, 680) if mode == "wide" else (430, 760)
    try:
        tab = _CDP.get_or_open_tab(plat, url, headless=True, force_navigate=True)
        ws_url = str(tab["webSocketDebuggerUrl"])

        async def _init_hud_tab(conn: _CdpConnection, ws: Any) -> str:
            await _cdp_apply_hud_viewport(conn, ws, mode)
            await _cdp_wait_settled(conn, ws, 0.8)
            await _cdp_dismiss_popups(conn, ws)
            return str(await _cdp_eval_json(conn, ws, "location.href") or url)

        live_url = _CDP.run_on_tab(ws_url, _init_hud_tab, timeout=18.0)
    except Exception as exc:
        return {"ok": False, "error": f"Could not initialize HUD viewport for {spec['label']}: {exc}"}

    authenticated, _ = _probe_platform_authenticated(plat, ws_url)
    health = "authenticated" if authenticated else str((accounts.get_account(plat) or {}).get("session_health") or "unverified")
    if any(part in live_url.lower() for part in ("/accounts/login", "/i/flow/login")):
        health = "login_required"
    elif any(part in live_url.lower() for part in ("/challenge", "/checkpoint")):
        health = "challenge_required"
    if authenticated and not rec:
        accounts.connect_account(plat, session_connected=True, auth_mode="web_session", permission="ask")
    _set_session_health(plat, health)
    if not authenticated:
        _start_login_watcher(plat, perm=str(rec.get("permission") or "ask"), close_visible_on_success=False)

    hud_payload = {
        "active": True,
        "platform": plat,
        "label": spec["label"],
        "view": initial_view,
        "layout": mode,
        "width": width,
        "height": height,
        "url": live_url,
        "connected": authenticated,
        "session_health": health,
        "opened_at": int(time.time() * 1000),
    }
    with _HUD_SOCIAL_LOCK:
        _HUD_SOCIAL_SESSIONS["current"] = dict(hud_payload)

    try:
        from core.apex_bridge import get_active_bridge

        br = get_active_bridge()
        if br is not None:
            br.set_social_hud(hud_payload)
    except Exception:
        pass

    return {
        "ok": True,
        "in_hud": True,
        "social_hud": hud_payload,
        "message": f"Opened {spec['label']} ({initial_view}) right inside JARVIS's HUD.",
    }


def close_social_hud() -> dict[str, Any]:
    with _HUD_SOCIAL_LOCK:
        _HUD_SOCIAL_SESSIONS.pop("current", None)
    try:
        from core.apex_bridge import get_active_bridge

        br = get_active_bridge()
        if br is not None:
            br.set_social_hud(None)
    except Exception:
        pass
    return {"ok": True}


def get_hud_social_frame(platform: str = "") -> dict[str, Any]:
    """Capture a fast live JPEG frame + metadata from the headless HUD social tab."""
    with _HUD_SOCIAL_LOCK:
        cur = dict(_HUD_SOCIAL_SESSIONS.get("current") or {})
    plat = normalize_social_platform(platform or str(cur.get("platform") or "instagram"))
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": "Unknown platform"}

    layout = str(cur.get("layout") or ("wide" if plat == "whatsapp" else "mobile"))
    width, height = (1024, 680) if layout == "wide" else (430, 760)
    spec = SOCIAL_PLATFORMS[plat]

    try:
        tab = _CDP.get_or_open_tab(plat, spec["home_url"], headless=True, force_navigate=False)
        ws_url = str(tab["webSocketDebuggerUrl"])

        async def _grab(conn: _CdpConnection, ws: Any) -> tuple[str, str, str, bool]:
            await _cdp_apply_hud_viewport(conn, ws, layout)
            meta = await _cdp_eval_json(
                conn,
                ws,
                "({ url: location.href || '', title: document.title || '', authenticated: "
                + "Boolean(" + json.dumps(list(spec["logged_in_selectors"]))
                + ".some(s => document.querySelector(s))) })",
            )
            shot = await conn.send_cmd(
                ws,
                "Page.captureScreenshot",
                {"format": "jpeg", "quality": 70},
            )
            m = meta if isinstance(meta, dict) else {}
            return str(shot.get("data") or ""), str(m.get("url") or ""), str(m.get("title") or ""), m.get("authenticated") is True

        b64, cur_url, cur_title, live_auth = _CDP.run_on_tab(ws_url, _grab, timeout=10.0)
        health = str((accounts.get_account(plat) or {}).get("session_health") or "unverified")
        if any(v in cur_url.lower() for v in ("/accounts/login", "/i/flow/login")):
            health, live_auth = "login_required", False
        elif any(v in cur_url.lower() for v in ("/challenge", "/checkpoint")):
            health, live_auth = "challenge_required", False
        elif live_auth:
            health = "authenticated"
        _set_session_health(plat, health)
        return {
            "ok": bool(b64),
            "platform": plat,
            "label": spec["label"],
            "image_b64": b64,
            "url": cur_url,
            "title": cur_title,
            "width": width,
            "height": height,
            "layout": layout,
            "connected": live_auth,
            "session_health": health,
        }
    except Exception as exc:
        return {"ok": False, "platform": plat, "error": str(exc)}


def interact_hud_social(payload: dict[str, Any]) -> dict[str, Any]:
    """Forward HUD user clicks, wheel scrolls, typing, keys, view switches, or pop-out into the headless tab."""
    with _HUD_SOCIAL_LOCK:
        cur = dict(_HUD_SOCIAL_SESSIONS.get("current") or {})
    plat = normalize_social_platform(str(payload.get("platform") or cur.get("platform") or "instagram"))
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": "Unsupported platform"}

    if not cur or cur.get("platform") != plat:
        return {"ok": False, "error": "This social HUD is no longer active. Open it again before interacting."}
    if payload.get("opened_at") is not None and payload["opened_at"] != cur.get("opened_at"):
        return {"ok": False, "error": "This interaction belongs to an older HUD session; it was not applied."}
    kind = str(payload.get("kind") or "").strip().lower()
    if kind not in {"close", "popout", "layout", "navigate", "click", "wheel", "type", "key"}:
        return {"ok": False, "error": f"Unknown HUD interaction: {kind}"}
    layout = str(payload.get("layout") or cur.get("layout") or ("wide" if plat == "whatsapp" else "mobile"))
    width, height = (1024, 680) if layout == "wide" else (430, 760)
    spec = SOCIAL_PLATFORMS[plat]

    if kind == "close":
        return close_social_hud()

    if kind == "popout":
        close_social_hud()
        return start_social_login(plat)

    if kind == "layout":
        new_mode = "wide" if str(payload.get("mode") or "").lower() == "wide" else "mobile"
        return open_social_in_hud(plat, view=str(cur.get("view") or "feed"), layout=new_mode)

    if kind == "navigate":
        nav_view = str(payload.get("view") or "feed").strip().lower()
        if nav_view in ("next", "previous", "like", "save"):
            return control_social_feed(plat, nav_view, in_hud=True)
        return open_social_in_hud(plat, view=nav_view, layout=layout)

    try:
        tab = _CDP.get_or_open_tab(plat, spec["home_url"], headless=True, force_navigate=False)
        ws_url = str(tab["webSocketDebuggerUrl"])

        async def _act(conn: _CdpConnection, ws: Any) -> None:
            await _cdp_apply_hud_viewport(conn, ws, layout)
            if kind == "click":
                nx = max(0.0, min(1.0, float(payload.get("nx", 0.5))))
                ny = max(0.0, min(1.0, float(payload.get("ny", 0.5))))
                await _cdp_trusted_click(conn, ws, nx * width, ny * height)
            elif kind == "wheel":
                dx = float(payload.get("deltaX") or 0.0)
                dy = float(payload.get("deltaY", 360.0))
                await conn.send_cmd(
                    ws,
                    "Input.dispatchMouseEvent",
                    {"type": "mouseWheel", "x": width / 2, "y": height / 2, "deltaX": dx, "deltaY": dy},
                )
            elif kind == "type":
                txt = str(payload.get("text") or "")
                if txt:
                    await conn.send_cmd(ws, "Input.insertText", {"text": txt})
                if payload.get("submit"):
                    await asyncio.sleep(0.08)
                    await _cdp_press_key(conn, ws, "Enter", 13)
            elif kind == "key":
                key_name = str(payload.get("key") or "Enter")
                vk_map = {
                    "Enter": 13,
                    "Backspace": 8,
                    "Tab": 9,
                    "Escape": 27,
                    "ArrowDown": 40,
                    "ArrowUp": 38,
                    "ArrowLeft": 37,
                    "ArrowRight": 39,
                }
                if key_name not in vk_map:
                    raise ValueError("Unsupported key")
                await _cdp_press_key(conn, ws, key_name, vk_map[key_name])

        _CDP.run_on_tab(ws_url, _act, timeout=12.0)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ── Public API: Connect, Auto-Watch Login, Disconnect, Status ────────────────


_WATCHERS_ACTIVE: set[str] = set()
_WATCHERS_LOCK = threading.Lock()
_WATCHERS_CANCEL: dict[str, threading.Event] = {}


def _start_login_watcher(
    plat: str,
    *,
    handle: str = "",
    perm: str = "ask",
    on_connected: Callable[[], None] | None = None,
    close_visible_on_success: bool = True,
) -> None:
    with _WATCHERS_LOCK:
        if plat in _WATCHERS_ACTIVE:
            return
        _WATCHERS_ACTIVE.add(plat)
        cancelled = threading.Event()
        _WATCHERS_CANCEL[plat] = cancelled

    spec = SOCIAL_PLATFORMS[plat]

    def _watch() -> None:
        try:
            deadline = time.monotonic() + 240.0
            while time.monotonic() < deadline:
                if cancelled.wait(1.2):
                    return
                if not _CDP._endpoint_alive():
                    return
                pages = _CDP._list_page_targets()
                tab_ws = None
                for p in pages:
                    if any((urlsplit(str(p.get("url") or "")).hostname or "") == d or
                           (urlsplit(str(p.get("url") or "")).hostname or "").endswith("." + d)
                           for d in spec["domains"]):
                        tab_ws = p.get("webSocketDebuggerUrl")
                        break
                ok_in, _ = _probe_platform_authenticated(plat, tab_ws)
                if ok_in:
                    if cancelled.is_set():
                        return
                    current_rec = accounts.get_account(plat) or {}
                    if current_rec.get("ignored"):
                        return
                    accounts.connect_account(
                        plat,
                        handle=handle.lstrip("@"),
                        session_connected=True,
                        auth_mode="web_session",
                        permission=str(current_rec.get("permission") or perm),
                        session_health="authenticated",
                    )
                    security_vault.log_audit_event(
                        "user",
                        f"social_connect_web:{plat}",
                        {"platform": plat, "permission": perm},
                        result_summary=f"{spec['label']} persistent session authenticated.",
                        status="ok",
                    )
                    if tab_ws:
                        toast_js = f"""
                        (() => {{
                          const d = document.createElement('div');
                          d.textContent = '✓ {spec["label"]} Connected to JARVIS — background sync active!';
                          Object.assign(d.style, {{
                            position: 'fixed', bottom: '22px', right: '22px', zIndex: '2147483647',
                            padding: '12px 18px', borderRadius: '999px',
                            background: 'rgba(6, 22, 34, 0.95)', color: '#34d399',
                            border: '1px solid #34d399', fontFamily: 'system-ui, sans-serif',
                            fontSize: '13px', fontWeight: '600', boxShadow: '0 12px 32px rgba(0,0,0,0.45)'
                          }});
                          document.body.appendChild(d);
                          setTimeout(() => d.remove(), 4000);
                        }})()
                        """
                        try:
                            _CDP.run_on_tab(tab_ws, lambda c, w: _cdp_eval_json(c, w, toast_js), timeout=4.0)
                        except Exception:
                            pass

                    # Update HUD viewport state if open
                    with _HUD_SOCIAL_LOCK:
                        if "current" in _HUD_SOCIAL_SESSIONS and _HUD_SOCIAL_SESSIONS["current"].get("platform") == plat:
                            _HUD_SOCIAL_SESSIONS["current"]["connected"] = True
                            _HUD_SOCIAL_SESSIONS["current"]["session_health"] = "authenticated"
                            try:
                                from core.apex_bridge import get_active_bridge

                                br = get_active_bridge()
                                if br is not None:
                                    br.set_social_hud(dict(_HUD_SOCIAL_SESSIONS["current"]))
                            except Exception:
                                pass

                    if callable(on_connected):
                        try:
                            on_connected()
                        except Exception:
                            pass

                    # Crucial: if login happened in a visible sign-in popup window, close that popup
                    # automatically after saving cookies so all future checks stay 100% invisible!
                    if close_visible_on_success and _CDP._headless is False:
                        time.sleep(1.2)
                        _CDP.shutdown()
                    return
        finally:
            with _WATCHERS_LOCK:
                if _WATCHERS_CANCEL.get(plat) is cancelled:
                    _WATCHERS_ACTIVE.discard(plat)
                    _WATCHERS_CANCEL.pop(plat, None)

    threading.Thread(target=_watch, daemon=True, name=f"social-watch-{plat}").start()


def start_social_login(
    platform: str,
    *,
    handle: str = "",
    permission: str = "ask",
    in_hud: bool = False,
    on_connected: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Open sign-in session (either embedded inside JARVIS's HUD when `in_hud=True` or in a one-time popup window)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    if in_hud:
        res_hud = open_social_in_hud(plat, view="login")
        if res_hud.get("ok"):
            _start_login_watcher(plat, handle=handle, perm=permission, on_connected=on_connected, close_visible_on_success=False)
            return {
                "ok": True,
                "platform": plat,
                "label": SOCIAL_PLATFORMS[plat]["label"],
                "in_hud": True,
                "already_connected": bool(accounts.is_service_connected(plat)),
                "message": f"Opened {SOCIAL_PLATFORMS[plat]['label']} right inside JARVIS's HUD!",
            }

    spec = SOCIAL_PLATFORMS[plat]
    perm = permission if permission in accounts.PERMISSIONS else "ask"
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")

    try:
        tab = _CDP.get_or_open_tab(
            plat,
            spec["inbox_url"] if plat in ("instagram", "snapchat", "whatsapp") else spec["login_url"],
            headless=headless_env,
            force_navigate=True,
        )
        ws_url = str(tab["webSocketDebuggerUrl"])
        _CDP.run_on_tab(ws_url, lambda c, w: _cdp_wait_settled(c, w, 1.3), timeout=15.0)
        already_in, _ = _probe_platform_authenticated(plat, ws_url)
        if not already_in and spec["login_url"] != spec["inbox_url"]:
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
            session_health="authenticated",
        )
        if _CDP._headless is False:
            _CDP.shutdown()
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
            "message": f"{spec['label']} is signed in! JARVIS will check & send messages silently in the background.",
        }

    _start_login_watcher(plat, handle=handle, perm=perm, on_connected=on_connected, close_visible_on_success=True)
    return {
        "ok": True,
        "platform": plat,
        "label": spec["label"],
        "already_connected": False,
        "message": (
            f"Opened {spec['label']} for one-time sign-in. Once you log in, the window closes automatically "
            "and JARVIS will read & send messages silently in the background without opening the app!"
        ),
    }


def disconnect_social_account(platform: str) -> dict[str, Any]:
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}
    with _WATCHERS_LOCK:
        cancellation = _WATCHERS_CANCEL.pop(plat, None)
        if cancellation:
            cancellation.set()
        _WATCHERS_ACTIVE.discard(plat)
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
                "session_health": str(st.get("session_health") or "unverified"),
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
    auto_open_hud_login_if_needed: bool = True,
) -> tuple[bool, str]:
    """Ensure `platform` is authenticated — NEVER popping open an external desktop window during background checks!"""
    rec = accounts.get_account(platform)
    if rec:
        allowed, reason = accounts.check_permission(platform, "read")
        if not allowed:
            return False, reason
    # A saved or live session can exist without an accounts.json entry. Restore
    # the record, but never silently upgrade an existing permission policy.
    cookies = _cookie_dict(platform)
    if any(cookies.get(n) for n in SOCIAL_PLATFORMS[platform]["auth_cookies"]):
        if not rec:
            accounts.connect_account(platform, session_connected=True, auth_mode="web_session", permission="ask")
        return True, "session available; authentication will be checked by the operation"
    if rec and rec.get("session_connected"):
        # Older connections can have a persistent Chromium profile but no vault
        # export. Hydrate that session BEFORE approval captures sending identity.
        if (socials_root_dir() / "browser_profile").exists() or os.environ.get("JARVIS_SOCIALS_CDP_PORT"):
            try:
                _CDP.ensure_browser(headless=True)
                _cookie_dict(platform)
            except Exception:
                pass
        return True, "saved browser session; authentication will be checked by the operation"

    # 1. Silent browser cookie import (0 windows)
    imp = import_cookies_from_browser(platform, str((rec or {}).get("cookies_browser") or "auto"),
                                      handle=str((rec or {}).get("handle") or ""),
                                      permission=str((rec or {}).get("permission") or "ask"))
    if imp.get("ok"):
        return True, "ok"

    # 2. Silent headless check of `~/.jarvis_socials/browser_profile` (0 windows)
    try:
        if (socials_root_dir() / "browser_profile").exists() or os.environ.get("JARVIS_SOCIALS_CDP_PORT"):
            _CDP.ensure_browser(headless=True)
            already, _ = _probe_platform_authenticated(platform)
            if already:
                accounts.connect_account(
                    platform,
                    session_connected=True,
                    auth_mode="web_session",
                    permission=str((rec or {}).get("permission") or "ask"),
                )
                return True, "ok"
    except Exception:
        pass

    # 3. Not signed in yet -> open sign-in right inside JARVIS's own HUD (NOT an external desktop window!)
    lbl = SOCIAL_PLATFORMS[platform]["label"]
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")
    if auto_open_hud_login_if_needed and not headless_env:
        hud_res = open_social_in_hud(platform, view="login")
        if hud_res.get("ok"):
            return (
                False,
                f"{lbl} isn't signed in yet — I opened {lbl} right inside my HUD for a one-time login. "
                "Once you sign in there, I'll check and send messages silently in the background without opening anything!",
            )

    return (
        False,
        f"{lbl} is not signed in yet. Open HUD -> LINKS (or say 'open {lbl} in your HUD') to sign in once.",
    )


# ── 1. Check Unread DMs, Snaps & Notifications (100% Silent Background!) ─────


def _inspect_url_in_session(
    platform: str,
    url: str,
    *,
    headless: bool = True,
) -> tuple[bytes | None, dict[str, Any], bool]:
    # ALWAYS `headless=True` for background inspection — never open an external window!
    tab = _CDP.get_or_open_tab(platform, url, headless=True, force_navigate=True, purpose="automation")
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _inspect(conn: _CdpConnection, ws: Any) -> tuple[bytes | None, dict[str, Any]]:
        await _cdp_wait_settled(conn, ws, 1.8)
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
    """Check unread DMs, Snaps, & notifications 100% silently in the background (0 windows opened)."""
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
                    "Say 'open Instagram in your HUD' (or open HUD -> LINKS) to sign in once."
                ),
            }

    reports: list[str] = []
    checked: list[str] = []

    for plat in targets:
        spec = SOCIAL_PLATFORMS[plat]
        ready, reason = _ensure_platform_ready(plat, auto_open_hud_login_if_needed=(len(targets) == 1))
        if not ready:
            reports.append(f"• {spec['label']}: {reason}")
            continue

        # Tier 1: Instant zero-window HTTP API (Instagram & Reddit — ~250ms, 0 browser processes!)
        if plat == "instagram":
            api_in = _ig_api_fetch_inbox(include_notifications=include_notifications)
            if api_in and api_in.get("ok"):
                checked.append(plat)
                reports.append(str(api_in["summary"]))
                continue
        elif plat == "reddit":
            r_in = _reddit_api_fetch_inbox()
            if r_in and r_in.get("ok"):
                checked.append(plat)
                reports.append(str(r_in["summary"]))
                continue

        # Tier 2: 100% invisible `--headless=new` background CDP (zero desktop window!)
        try:
            shot, dom_data, logged_in = _inspect_url_in_session(
                plat, spec["inbox_url"], headless=True
            )
            cur_u = str(dom_data.get("url") or "").lower()
            if not logged_in and any(k in cur_u for k in ("/accounts/login", "/i/flow/login", "/login")):
                open_social_in_hud(plat, view="login")
                reports.append(
                    f"• {spec['label']}: Session expired — I opened {spec['label']} inside my HUD so you can re-authenticate."
                )
                continue

            if not logged_in:
                reports.append(f"• {spec['label']}: Could not verify a signed-in inbox. Check the HUD for login or a security challenge.")
                continue

            # If Instagram headless CDP just refreshed cookies, try fast API again or summarize via Vision+DOM
            if plat == "instagram":
                api_retry = _ig_api_fetch_inbox(include_notifications=include_notifications)
                if api_retry and api_retry.get("ok"):
                    checked.append(plat)
                    reports.append(str(api_retry["summary"]))
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


# ── 2. Read Specific DM / Snap Conversation (100% Silent Background!) ────────


async def _cdp_open_contact_thread(
    conn: _CdpConnection,
    ws: Any,
    platform: str,
    clean_contact: str,
) -> bool:
    if not clean_contact:
        if platform != "instagram":
            return False
        point = await _cdp_eval_json(conn, ws, """
        (() => {
          for (const a of document.querySelectorAll('a[href^="/direct/t/"]')) {
            const r = a.getBoundingClientRect();
            if (r.width > 30 && r.height > 20 && r.top >= 0 && r.bottom <= innerHeight)
              return {x: r.left + r.width / 2, y: r.top + r.height / 2};
          }
          return null;
        })()
        """)
        if not isinstance(point, dict):
            return False
        await _cdp_trusted_click(conn, ws, point["x"], point["y"])
        await asyncio.sleep(1.3)
        return await _cdp_eval_json(conn, ws, "location.pathname.startsWith('/direct/t/')") is True

    target_json = json.dumps(clean_contact.lower())

    find_row_js = f"""
    (() => {{
      const needle = {target_json};
      const candidates = document.querySelectorAll(
        '[role="listitem"], [role="row"], [data-testid="conversation"], div[role="button"], a[href*="/direct/t/"]'
      );
      for (const el of candidates) {{
        const txt = (el.innerText || el.getAttribute('aria-label') || '').toLowerCase();
        if (!txt || !txt.split('\\n').some(line => line.trim().replace(/^@/, '') === needle)) continue;
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
        await asyncio.sleep(1.3)
        return True

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
            await asyncio.sleep(0.9)
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
                await asyncio.sleep(1.3)
                pick_pt = await _cdp_eval_json(
                    conn,
                    ws,
                    f"""
                    (() => {{
                      const needle = {target_json};
                      const rows = document.querySelectorAll('div[role="dialog"] div[role="button"], div[role="dialog"] label');
                      for (const el of rows) {{
                        const t = (el.innerText || '').toLowerCase();
                        if (t.split('\\n').some(line => line.trim().replace(/^@/, '') === needle)) {{
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
                    await asyncio.sleep(0.45)
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
                        await asyncio.sleep(1.3)
                        return True

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
        await asyncio.sleep(1.2)
        pt2 = await _cdp_eval_json(conn, ws, find_row_js)
        if isinstance(pt2, dict):
            await _cdp_trusted_click(conn, ws, pt2["x"], pt2["y"])
            await asyncio.sleep(1.2)
            return True

    return False


def read_social_messages(platform: str, contact: str = "") -> dict[str, Any]:
    """Read a specific DM/Snap conversation 100% silently in the background (0 windows opened)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unknown social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat, auto_open_hud_login_if_needed=True)
    if not ready:
        return {"ok": False, "error": reason}

    clean_contact = (contact or "").strip().lstrip("@")

    # Tier 1: Instant zero-window Instagram Direct HTTP API
    if plat == "instagram":
        try:
            api_th = _ig_api_read_thread(clean_contact)
        except RecipientError as exc:
            return {"ok": False, "error": str(exc)}
        if api_th and api_th.get("ok"):
            return api_th

    # Tier 2: 100% invisible `--headless=new` background CDP (NEVER opens a desktop window!)
    try:
        tab = _CDP.get_or_open_tab(plat, spec["inbox_url"], headless=True, force_navigate=True, purpose="automation")
        ws_url = str(tab["webSocketDebuggerUrl"])

        async def _open_and_read(conn: _CdpConnection, ws: Any) -> tuple[bytes | None, dict[str, Any]]:
            await _cdp_wait_settled(conn, ws, 1.8)
            await _cdp_dismiss_popups(conn, ws)
            if not await _cdp_open_contact_thread(conn, ws, plat, clean_contact):
                raise RecipientError(f"Could not open the exact conversation with {clean_contact or 'the latest contact'}; no other chat was read.")
            if clean_contact:
                if plat == "instagram":
                    expected_path = json.dumps("/" + clean_contact.lower() + "/")
                    verified = await _cdp_eval_json(conn, ws, r"""
                    (() => {
                      if (!/^\/direct\/t\/[^/]+\//.test(location.pathname)) return false;
                      const links = document.querySelectorAll('main header a[href], [role="main"] header a[href]');
                      return Array.from(links).some(a => new URL(a.href).pathname.toLowerCase() === EXPECTED);
                    })()
                    """.replace("EXPECTED", expected_path))
                    if verified is not True:
                        raise RecipientError("Instagram did not expose a verifiable exact recipient. Open the intended chat in the HUD; no conversation was summarized.")
            return await _cdp_capture_snapshot(conn, ws)

        shot, dom_data = _CDP.run_on_tab(ws_url, _open_and_read, timeout=45.0)
    except Exception as exc:
        return {"ok": False, "error": f"Could not read {spec['label']} conversation: {exc}"}

    if not _probe_platform_authenticated(plat, ws_url)[0]:
        return {"ok": False, "error": f"Could not verify a signed-in {spec['label']} conversation. Check the HUD for login or a challenge."}

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


# ── 3. Send DM / Snap Reply & Publish Post (100% Silent Background + Confirm!) ─


def _execute_send_message_now(platform: str, recipient: str, message: str, actor: str) -> str:
    spec = SOCIAL_PLATFORMS[platform]
    allowed, reason = accounts.check_permission(platform, "send")
    if not allowed:
        raise RuntimeError(f"Send blocked by current permission policy: {reason}")
    clean_rec = recipient.strip().lstrip("@")

    original_sender = _cookie_dict(platform)

    # Tier 1: Session-backed Instagram Direct API (same-origin browser or cookie HTTP).
    if platform == "instagram":
        api_sent = _ig_api_send_dm(clean_rec, message)
        if api_sent:
            security_vault.log_audit_event(
                actor,
                f"social_send_message:{platform}",
                {"platform": platform, "recipient": clean_rec, "length": len(message), "transport": "http_api"},
                result_summary=api_sent,
                status="ok",
            )
            return api_sent

        # API lookup failed before a POST. Instagram's own composer also
        # supports chat variants the undocumented API may not expose.
        from core.instagram_web import send_instagram_message
        result = send_instagram_message(sys.modules[__name__], clean_rec, message, expected_sender=original_sender)
        security_vault.log_audit_event(actor, f"social_send_message:{platform}",
            {"platform": platform, "recipient": clean_rec, "length": len(message), "transport": "instagram_web_ui"},
            result_summary=result, status="ok")
        return result

    # Tier 2: 100% invisible `--headless=new` background CDP (`headless=True` ALWAYS — NEVER opens a visible window!)
    tab = _CDP.get_or_open_tab(platform, spec["inbox_url"], headless=True, force_navigate=True, purpose="automation")
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _send_coro(conn: _CdpConnection, ws: Any) -> str:
        await _cdp_wait_settled(conn, ws, 1.8)
        await _cdp_dismiss_popups(conn, ws)
        if clean_rec:
            opened = await _cdp_open_contact_thread(conn, ws, platform, clean_rec)
            if not opened:
                raise RuntimeError(f"Could not find conversation or user '{clean_rec}' on {spec['label']}.")

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
        await asyncio.sleep(0.18)
        await conn.send_cmd(ws, "Input.insertText", {"text": message})
        await asyncio.sleep(0.3)

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

        await asyncio.sleep(1.0)
        raise DeliveryUnknown(f"The send control was activated on {spec['label']}, but delivery could not be verified. Check the HUD before retrying; no automatic retry was made.")

    res_msg = _CDP.run_on_tab(ws_url, _send_coro, timeout=50.0)
    security_vault.log_audit_event(
        actor,
        f"social_send_message:{platform}",
        {"platform": platform, "recipient": clean_rec, "length": len(message), "transport": "headless_cdp"},
        result_summary=res_msg,
        status="ok",
    )
    return res_msg


def stage_or_send_social_message(
    platform: str,
    recipient: str,
    message: str,
    on_result: Callable[[str], None] | None = None,
) -> str:
    """Enforce `memory/accounts.py` permissions and `core.confirm` HUD gate before sending any DM/Snap."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return f"Unsupported social platform '{platform}'."
    if not (recipient or "").strip():
        return "Please specify who to message."
    if not (message or "").strip():
        return "Please specify the message text."

    if len(message) > 3800:
        return "The message is too long to fully preview in the confirmation panel. Please shorten it or send smaller parts; nothing was sent."
    if plat == "instagram" and not re.fullmatch(r"@?[A-Za-z0-9_.]{1,30}", recipient.strip()):
        return "Please provide the recipient's exact Instagram @username, not a display name. Nothing was sent."
    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat, auto_open_hud_login_if_needed=True)
    if not ready:
        return reason

    allowed, perm_reason = accounts.check_permission(plat, "send")
    if not allowed:
        return f"Blocked by {spec['label']} permission policy: {perm_reason}."

    rec = accounts.get_account(plat) or {}
    perm = str(rec.get("permission") or "ask").lower()

    staged_cookies = _cookie_dict(plat)
    staged_identity = staged_cookies.get("ds_user_id") or hashlib.sha256(staged_cookies.get("sessionid", "").encode()).hexdigest()

    def execute(actor: str) -> str:
        try:
            current_cookies = _cookie_dict(plat)
            current_identity = current_cookies.get("ds_user_id") or hashlib.sha256(current_cookies.get("sessionid", "").encode()).hexdigest()
            if current_identity != staged_identity:
                raise RuntimeError("The signed-in account changed after confirmation was requested. Nothing was sent; request a new confirmation.")
            result = _execute_send_message_now(plat, recipient, message, actor=actor)
        except Exception as exc:
            result = f"{spec['label']} send not confirmed: {exc}"
            security_vault.log_audit_event(actor, f"social_send_message:{plat}",
                {"platform": plat, "recipient": recipient, "length": len(message)},
                result_summary=result, status="unknown" if isinstance(exc, DeliveryUnknown) else "error")
        if on_result:
            try:
                on_result(result)
            except Exception:
                pass
        return result

    if perm == "full":
        return execute("jarvis_full_perm")

    title = f"Send {spec['label']} message to {recipient.strip()}"
    detail = f"Message: \"{message}\""
    return confirm_gate.request(
        key=f"social-msg-{plat}",
        title=title,
        detail=detail,
        run=lambda: execute("user_confirmed"),
    )


def _execute_publish_post_now(platform: str, text: str, actor: str) -> str:
    allowed, reason = accounts.check_permission(platform, "write")
    if not allowed:
        raise RuntimeError(reason)
    if platform == "instagram":
        raise RuntimeError("Instagram posts require photo/video media. Text-only publishing is not supported; use Create in the HUD. Nothing was published.")
    spec = SOCIAL_PLATFORMS[platform]
    tab = _CDP.get_or_open_tab(platform, spec["compose_post_url"], headless=True, force_navigate=True)
    ws_url = str(tab["webSocketDebuggerUrl"])

    async def _post_coro(conn: _CdpConnection, ws: Any) -> str:
        await _cdp_wait_settled(conn, ws, 1.8)
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
        await asyncio.sleep(0.18)
        await conn.send_cmd(ws, "Input.insertText", {"text": text})
        await asyncio.sleep(0.35)
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
            await asyncio.sleep(1.2)
            raise DeliveryUnknown(f"The publish control was activated on {spec['label']}, but publication was not verified. Check the HUD before retrying.")
        raise RuntimeError(f"Could not submit post automatically on {spec['label']}.")

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
    if plat == "instagram":
        return "Instagram posts require photo/video media; this tool does not support text-only Instagram publishing. Use Create in the HUD. Nothing was published."

    spec = SOCIAL_PLATFORMS[plat]
    ready, reason = _ensure_platform_ready(plat, auto_open_hud_login_if_needed=True)
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


# ── 4. HUD-First Feed, Reels & Story Control ─────────────────────────────────


def control_social_feed(
    platform: str,
    command: str = "open_feed",
    *,
    target: str = "",
    in_hud: bool = True,
) -> dict[str, Any]:
    """Open and control Instagram / Social feeds, Reels, DMs & profiles — directly inside JARVIS's HUD by default (`in_hud=True`)."""
    plat = normalize_social_platform(platform)
    if not plat or plat not in SOCIAL_PLATFORMS:
        return {"ok": False, "error": f"Unsupported social platform '{platform}'."}

    spec = SOCIAL_PLATFORMS[plat]
    cmd = (command or "open_feed").strip().lower()
    headless_env = os.environ.get("QT_QPA_PLATFORM", "").strip().lower() in ("offscreen", "minimal")
    use_headless = True if (in_hud or headless_env) else False

    record = accounts.get_account(plat) or {}
    if not record.get("ignored") and not accounts.is_service_connected(plat):
        import_cookies_from_browser(plat, "auto", permission=str(record.get("permission") or "ask"))

    try:
        if cmd in ("open_feed", "home", "feed", "open", "open_hud"):
            if in_hud:
                return open_social_in_hud(plat, view="feed")
            _CDP.get_or_open_tab(plat, spec["home_url"], headless=use_headless, force_navigate=True)
            _start_login_watcher(plat, close_visible_on_success=False)
            return {"ok": True, "message": f"Opened your {spec['label']} feed."}

        if cmd in ("open_reels", "reels", "foryou", "spotlight"):
            if in_hud:
                return open_social_in_hud(plat, view="reels")
            _CDP.get_or_open_tab(plat, spec["reels_url"], headless=use_headless, force_navigate=True)
            _start_login_watcher(plat, close_visible_on_success=False)
            return {"ok": True, "message": f"Opened {spec['label']} Reels / Spotlight."}

        if cmd in ("open_inbox", "inbox", "dms", "chats"):
            if in_hud:
                return open_social_in_hud(plat, view="inbox")
            _CDP.get_or_open_tab(plat, spec["inbox_url"], headless=use_headless, force_navigate=True)
            _start_login_watcher(plat, close_visible_on_success=False)
            return {"ok": True, "message": f"Opened your {spec['label']} inbox."}

        if cmd in ("open_profile", "profile"):
            handle = (target or (accounts.get_account(plat) or {}).get("handle") or "").strip().lstrip("@")
            if not handle:
                return {"ok": False, "error": f"Pass a @username (`target`) to open on {spec['label']}."}
            if in_hud:
                return open_social_in_hud(plat, view="profile", target=handle)
            url = spec["profile_url_tpl"].format(handle=handle)
            _CDP.get_or_open_tab(plat, url, headless=use_headless, force_navigate=True)
            return {"ok": True, "message": f"Opened @{handle} on {spec['label']} ({url})."}

        tab = _CDP.get_or_open_tab(plat, spec["reels_url"], headless=True, force_navigate=False)
        ws_url = str(tab["webSocketDebuggerUrl"])

        if cmd in ("next", "scroll_down", "down", "skip"):
            async def _next(conn: _CdpConnection, ws: Any) -> None:
                await _cdp_press_key(conn, ws, "ArrowDown", 40)
                await conn.send_cmd(
                    ws,
                    "Input.dispatchMouseEvent",
                    {"type": "mouseWheel", "x": 215, "y": 380, "deltaX": 0, "deltaY": 620},
                )
            _CDP.run_on_tab(ws_url, _next, timeout=12.0)
            return {"ok": True, "message": f"Moved to the next post/reel on {spec['label']}."}

        if cmd in ("previous", "prev", "scroll_up", "up", "back"):
            async def _prev(conn: _CdpConnection, ws: Any) -> None:
                await _cdp_press_key(conn, ws, "ArrowUp", 38)
                await conn.send_cmd(
                    ws,
                    "Input.dispatchMouseEvent",
                    {"type": "mouseWheel", "x": 215, "y": 380, "deltaX": 0, "deltaY": -620},
                )
            _CDP.run_on_tab(ws_url, _prev, timeout=12.0)
            return {"ok": True, "message": f"Moved back to the previous post/reel on {spec['label']}."}

        if cmd == "like":
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
                            window.__jarvisSocialActionTarget = target;
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
                    await asyncio.sleep(0.35)
                    verified = await _cdp_eval_json(conn, ws, """
                    (() => { // jarvisVerifyLike
                      const el = window.__jarvisSocialActionTarget;
                      return Boolean(el && el.isConnected && (el.getAttribute('aria-pressed') === 'true' ||
                        el.getAttribute('aria-label') === 'Unlike' || el.querySelector('[aria-label="Unlike"], [data-testid="unlike"]')));
                    })()
                    """)
                    if verified is not True:
                        raise RuntimeError("Like was clicked but its state change was not verified. Check the HUD before retrying; it was not clicked again.")
                    return True
                return False

            if _CDP.run_on_tab(ws_url, _like, timeout=12.0):
                return {"ok": True, "message": f"Liked the active post/reel on {spec['label']}."}
            return {"ok": False, "error": f"Could not find an unliked Like button on {spec['label']}."}

        if cmd in ("save", "bookmark"):
            allowed, reason = accounts.check_permission(plat, "write")
            if not allowed:
                return {"ok": False, "error": reason}
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
                            window.__jarvisSocialActionTarget = target;
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
                    await asyncio.sleep(0.35)
                    verified = await _cdp_eval_json(conn, ws, """
                    (() => { // jarvisVerifySave
                      const el = window.__jarvisSocialActionTarget;
                      return Boolean(el && el.isConnected && (el.getAttribute('aria-pressed') === 'true' ||
                        /^(Unsave|Remove|Remove bookmark)$/i.test(el.getAttribute('aria-label') || '') ||
                        el.querySelector('[aria-label="Remove"], [aria-label="Unsave"], [data-testid="removeBookmark"]')));
                    })()
                    """)
                    if verified is not True:
                        raise RuntimeError("Save was clicked but its state change was not verified. Check the HUD before retrying; it was not clicked again.")
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
