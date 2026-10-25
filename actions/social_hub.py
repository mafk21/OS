"""
actions/social_hub.py — Personal Social Accounts Action for Instagram, Snapchat,
TikTok, X / Twitter, WhatsApp Web, and Reddit.

Capabilities:
  • status        — View connected personal social accounts, @handles & permissions
  • connect       — Open persistent Sign-In / QR window OR 1-click import cookies
                    from Chrome / Edge / Brave / Firefox / Safari
  • disconnect    — Sign out & purge encrypted session vault for a platform
  • check_inbox   — Check unread DMs, Snaps, & notifications across connected socials
  • read_messages — Open & read a specific DM / Snap chat thread (`contact`)
  • send_message  — Draft & send a DM / Snap chat reply (protected by JARVIS's
                    unforgeable HUD CONFIRM/CANCEL gate when permission is `ask`)
  • post          — Draft & publish a social post/tweet (protected by HUD CONFIRM gate)
  • feed          — Hands-free voice feed & Reel control (`open_feed`, `open_reels`,
                    `open_inbox`, `open_profile`, `next`, `previous`, `like`, `save`, `look`)
"""

from __future__ import annotations

from core.social_hub import (
    check_social_inbox,
    control_social_feed,
    disconnect_social_account,
    get_social_hub_status,
    import_cookies_from_browser,
    normalize_social_platform,
    read_social_messages,
    stage_or_publish_social_post,
    stage_or_send_social_message,
    start_social_login,
)
from memory import accounts


def social_hub(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    params = parameters or {}
    action = str(params.get("action") or "check_inbox").strip().lower()
    raw_platform = str(params.get("platform") or "").strip()

    # ── 1. STATUS ─────────────────────────────────────────────────────────────
    if action in ("status", "list", "accounts"):
        st = get_social_hub_status()
        lines = ["Personal Social Accounts:"]
        for item in st["platforms"]:
            badge = "✓ CONNECTED" if item["connected"] else ("⊘ IGNORED" if item["ignored"] else "○ NOT CONNECTED")
            handle_s = f" (@{item['handle'].lstrip('@')})" if item["handle"] else ""
            mode_s = f" · {item['auth_mode']}" if item["connected"] and item["auth_mode"] else ""
            lines.append(
                f"  • {item['label']:10s} : {badge}{handle_s} [policy: {item['permission']}]{mode_s}"
            )
        out = "\n".join(lines)
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content("Socials Hub Status", out)
            except Exception:
                pass
        return out

    # ── 2. CONNECT (PERSISTENT WEB SIGN-IN OR BROWSER COOKIE IMPORT) ──────────
    if action in ("connect", "login", "signin", "sign_in"):
        plat = normalize_social_platform(raw_platform)
        if not plat:
            return (
                "Specify which social platform to connect: "
                "'instagram', 'snapchat', 'tiktok', 'x', 'whatsapp', or 'reddit'."
            )
        handle = str(params.get("handle") or "").strip()
        permission = str(params.get("permission") or "ask").strip().lower()
        cookies_browser = str(params.get("cookies_browser") or "").strip().lower()

        if cookies_browser:
            res = import_cookies_from_browser(
                plat,
                cookies_browser,
                handle=handle,
                permission=permission,
            )
            if res.get("ok"):
                msg = (
                    f"Connected {res['label']} by importing {res['cookie_count']} session cookies "
                    f"from {res['browser']} (policy: {permission})."
                )
                if player is not None and hasattr(player, "show_content"):
                    try:
                        player.show_content(f"{res['label']} Connected", msg)
                    except Exception:
                        pass
                return msg
            # Fall through to interactive login window if cookie import found nothing
        res_login = start_social_login(plat, handle=handle, permission=permission)
        return str(res_login.get("message") or res_login.get("error") or "Done.")

    # ── 3. SET PERMISSION OR DISCONNECT ───────────────────────────────────────
    if action in ("permission", "set_permission"):
        plat = normalize_social_platform(raw_platform)
        perm = str(params.get("permission") or "ask").strip().lower()
        if not plat:
            return "Specify platform ('instagram', 'snapchat', 'tiktok', 'x', 'whatsapp', 'reddit')."
        res_p = accounts.set_permission(plat, perm)
        return f"Updated {plat} permission policy to '{res_p['permission']}'."

    if action in ("disconnect", "logout", "signout"):
        plat = normalize_social_platform(raw_platform)
        if not plat:
            return "Specify which social platform to disconnect."
        res_d = disconnect_social_account(plat)
        if not res_d.get("ok"):
            return str(res_d.get("error"))
        return f"Disconnected {res_d['label']} and cleared its saved session."

    # ── 4. CHECK UNREAD DMS, SNAPS & NOTIFICATIONS ────────────────────────────
    if action in ("check_inbox", "inbox", "unread", "notifications", "check"):
        target_plat = raw_platform or "all"
        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Socials] Checking {target_plat} inbox & notifications…")
        include_notif = bool(params.get("include_notifications", True))
        res_in = check_social_inbox(target_plat, include_notifications=include_notif)
        if not res_in.get("ok"):
            return str(res_in.get("error"))
        body = str(res_in.get("summary") or "").strip()
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content("Socials Inbox Digest", body)
            except Exception:
                pass
        return body

    # ── 5. READ CONVERSATION / THREAD ─────────────────────────────────────────
    if action in ("read_messages", "read_chat", "read_dm", "read"):
        if not raw_platform:
            return "Specify platform ('instagram', 'snapchat', 'tiktok', 'x', 'whatsapp', or 'reddit')."
        contact = str(params.get("contact") or params.get("recipient") or "").strip()
        if player is not None and hasattr(player, "write_log"):
            player.write_log(f"[Socials] Reading {raw_platform} thread {contact or '(top)'}…")
        res_rd = read_social_messages(raw_platform, contact=contact)
        if not res_rd.get("ok"):
            return str(res_rd.get("error"))
        title = f"{res_rd['label']} Chat" + (f" · {contact}" if contact else "")
        body = str(res_rd.get("messages") or "").strip()
        if player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(title, body)
            except Exception:
                pass
        return f"{title}:\n{body}"

    # ── 6. SEND DM / SNAP CHAT REPLY (HUD CONFIRMATION GATED!) ────────────────
    if action in ("send_message", "reply", "dm", "send"):
        if not raw_platform:
            return "Specify platform ('instagram', 'snapchat', 'tiktok', 'x', 'whatsapp', or 'reddit')."
        recipient = str(params.get("recipient") or params.get("contact") or "").strip()
        message = str(params.get("message") or params.get("text") or "").strip()
        return stage_or_send_social_message(raw_platform, recipient, message)

    # ── 7. PUBLISH POST / TWEET (HUD CONFIRMATION GATED!) ─────────────────────
    if action in ("post", "tweet", "publish"):
        if not raw_platform:
            return "Specify platform (e.g. 'x', 'reddit', 'instagram')."
        text = str(params.get("text") or params.get("message") or "").strip()
        return stage_or_publish_social_post(raw_platform, text)

    # ── 8. HANDS-FREE FEED, REELS & STORY CONTROL ─────────────────────────────
    if action in (
        "feed",
        "open_feed",
        "open_reels",
        "open_inbox",
        "open_profile",
        "next",
        "previous",
        "like",
        "save",
        "look",
    ):
        plat = raw_platform or "instagram"
        cmd = str(params.get("command") or (action if action != "feed" else "open_feed")).strip()
        target = str(params.get("target") or params.get("handle") or params.get("contact") or "").strip()
        res_fd = control_social_feed(plat, cmd, target=target)
        if not res_fd.get("ok"):
            return str(res_fd.get("error"))
        msg = str(res_fd.get("message") or "Done.")
        if cmd in ("look", "describe", "see") and player is not None and hasattr(player, "show_content"):
            try:
                player.show_content(f"{plat.capitalize()} Screen View", msg)
            except Exception:
                pass
        return msg

    return (
        f"Unknown social_hub action '{action}'. Supported actions: "
        "status, connect, disconnect, permission, check_inbox, read_messages, send_message, post, feed."
    )


TOOL = {
    "name": "social_hub",
    "description": (
        "Accesses and controls the user's personal social accounts across Instagram, Snapchat Web "
        "(web.snapchat.com), TikTok, X / Twitter, WhatsApp Web, and Reddit using a persistent "
        "encrypted local session. Use to: "
        "• Check unread DMs, Snaps, & notifications ('check_inbox') across one or all socials. "
        "• Read a specific DM or Snapchat chat thread ('read_messages' with `contact`). "
        "• Reply to a DM / Snap chat ('send_message') or publish a post ('post') — automatically "
        "guarded by JARVIS's on-screen HUD CONFIRM/CANCEL banner when permission is 'ask'. "
        "• Control feeds & Reels hands-free ('feed' with command='open_reels'|'next'|'previous'|'like'|'save'|'open_profile'|'look'). "
        "• Connect ('connect') or check status ('status') of personal social accounts."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'check_inbox', 'read_messages', 'send_message', 'post', 'feed', 'connect', 'disconnect', 'permission', or 'status'.",
                "enum": [
                    "check_inbox",
                    "read_messages",
                    "send_message",
                    "post",
                    "feed",
                    "connect",
                    "disconnect",
                    "permission",
                    "status",
                ],
            },
            "platform": {
                "type": "STRING",
                "description": "Social platform: 'instagram', 'snapchat', 'tiktok', 'x', 'whatsapp', 'reddit', or 'all' (for check_inbox).",
            },
            "contact": {
                "type": "STRING",
                "description": "Contact name or @handle when reading ('read_messages') or replying ('send_message').",
            },
            "recipient": {
                "type": "STRING",
                "description": "Recipient name or @handle for 'send_message'.",
            },
            "message": {
                "type": "STRING",
                "description": "Exact message text (in the user's requested language) for 'send_message' or 'post'.",
            },
            "command": {
                "type": "STRING",
                "description": "For action='feed': 'open_feed', 'open_reels', 'open_inbox', 'open_profile', 'next', 'previous', 'like', 'save', or 'look'.",
            },
            "target": {
                "type": "STRING",
                "description": "Optional @username for command='open_profile'.",
            },
            "cookies_browser": {
                "type": "STRING",
                "description": "For action='connect': optional browser ('chrome', 'edge', 'brave', 'firefox', 'safari', 'auto') to import an active session in 1 click.",
            },
            "handle": {
                "type": "STRING",
                "description": "Optional @handle label when connecting an account.",
            },
            "permission": {
                "type": "STRING",
                "description": "Permission policy: 'ask' (default — HUD confirm before sending/posting), 'full', 'readonly', or 'paused'.",
            },
            "include_notifications": {
                "type": "BOOLEAN",
                "description": "For action='check_inbox': include recent notifications alongside unread DMs/Snaps (default true).",
            },
        },
        "required": ["action"],
    },
    "handler": social_hub,
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}
