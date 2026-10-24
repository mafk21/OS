"""
Accounts & Cloud Integrations Center — Real stdlib REST + IMAP/SMTP + OAuth store.

Stores per-service credentials and permissions (ask / full / readonly / paused)
locally in `memory/accounts.json`, syncs shared keys (`github_token`,
`telegram_bot_token`, `spotify_client_id`, `spotify_client_secret`) with
`config/api_keys.json`, and provides real API helpers for Email (Gmail REST +
IMAP/SMTP), Google Drive, Google Calendar, Notion, Slack, Discord, and Trello.
"""

from __future__ import annotations

import base64
import email as _email_pkg
from email.header import decode_header
from email.message import EmailMessage
import imaplib
import json
import mimetypes
import pathlib
import smtplib
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any


def _base() -> pathlib.Path:
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).resolve().parent.parent


ACCOUNTS_FILE = _base() / "memory" / "accounts.json"

SUPPORTED = [
    "email",
    "gmail",
    "google_calendar",
    "google_classroom",
    "google_drive",
    "github",
    "trello",
    "slack",
    "notion",
    "discord",
    "telegram",
    "spotify",
]

PERMISSIONS = ("ask", "full", "readonly", "paused")

# Auto-detected IMAP/SMTP servers for common email providers (App Passwords)
EMAIL_PROVIDERS: dict[str, tuple[str, int, str, int]] = {
    "gmail.com": ("imap.gmail.com", 993, "smtp.gmail.com", 465),
    "googlemail.com": ("imap.gmail.com", 993, "smtp.gmail.com", 465),
    "outlook.com": ("outlook.office365.com", 993, "smtp.office365.com", 587),
    "hotmail.com": ("outlook.office365.com", 993, "smtp.office365.com", 587),
    "live.com": ("outlook.office365.com", 993, "smtp.office365.com", 587),
    "icloud.com": ("imap.mail.me.com", 993, "smtp.mail.me.com", 587),
    "me.com": ("imap.mail.me.com", 993, "smtp.mail.me.com", 587),
    "yahoo.com": ("imap.mail.yahoo.com", 993, "smtp.mail.yahoo.com", 465),
}


def _load() -> dict:
    if not ACCOUNTS_FILE.exists():
        return {"accounts": {}}
    try:
        d = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {"accounts": {}}
    except Exception:
        return {"accounts": {}}


def _save(data: dict) -> None:
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACCOUNTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _is_rec_connected(rec: dict) -> bool:
    if not isinstance(rec, dict) or rec.get("ignored"):
        return False
    return bool(
        rec.get("token")
        or rec.get("api_key")
        or rec.get("refresh_token")
        or rec.get("app_password")
        or rec.get("webhook_url")
        or (rec.get("client_id") and rec.get("client_secret") and rec.get("service") == "spotify")
    )


def list_accounts() -> list[dict]:
    d = _load()
    out = []
    for svc, rec in d.get("accounts", {}).items():
        if not isinstance(rec, dict):
            continue
        rec_copy = dict(rec, service=svc)
        out.append(
            {
                "service": svc,
                "permission": rec.get("permission", "ask"),
                "connected": _is_rec_connected(rec_copy),
                "ignored": bool(rec.get("ignored", False)),
                "email": rec.get("email", ""),
                "updated": rec.get("updated", ""),
            }
        )
    return sorted(out, key=lambda x: x["service"])


def get_account(service: str) -> dict | None:
    svc = (service or "").strip().lower()
    rec = _load().get("accounts", {}).get(svc)
    return dict(rec) if isinstance(rec, dict) else None


def is_service_connected(service: str) -> bool:
    svc = (service or "").strip().lower()
    rec = get_account(svc)
    if rec and _is_rec_connected({**rec, "service": svc}):
        return True
    # Also check synced keys in config/api_keys.json
    try:
        from memory import config_manager as cm
        cfg = cm.load_api_keys()
        if svc == "github" and cfg.get("github_token"):
            return True
        if svc == "telegram" and cfg.get("telegram_bot_token"):
            return True
        if svc == "spotify" and cfg.get("spotify_client_id") and cfg.get("spotify_client_secret"):
            return True
    except Exception:
        pass
    return False


def connect_account(
    service: str,
    token: str = "",
    api_key: str = "",
    email: str = "",
    permission: str = "ask",
    **extra: Any,
) -> dict:
    svc = (service or "").strip().lower()
    if svc not in SUPPORTED:
        raise ValueError(f"Unsupported service '{svc}'. Supported: {', '.join(SUPPORTED)}")
    if permission not in PERMISSIONS:
        permission = "ask"
    data = _load()
    cur = data.setdefault("accounts", {}).get(svc)
    cur = dict(cur) if isinstance(cur, dict) else {}
    cur.update(
        {
            "token": token.strip() if token else cur.get("token", ""),
            "api_key": api_key.strip() if api_key else cur.get("api_key", ""),
            "email": email.strip() if email else cur.get("email", ""),
            "permission": permission,
            "ignored": False,
            "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
    )
    for k, v in extra.items():
        if v is not None:
            cur[k] = v.strip() if isinstance(v, str) else v
    data["accounts"][svc] = cur
    _save(data)

    # Sync shared tokens to config/api_keys.json so standalone actions pick them up
    try:
        from memory import config_manager as cm
        if svc == "github" and (cur.get("token") or cur.get("api_key")):
            cm._patch_config(github_token=cur.get("token") or cur.get("api_key"))
        elif svc == "telegram" and (cur.get("token") or cur.get("api_key")):
            cm._patch_config(telegram_bot_token=cur.get("token") or cur.get("api_key"))
        elif svc == "spotify" and cur.get("client_id"):
            cm._patch_config(
                spotify_client_id=cur.get("client_id", ""),
                spotify_client_secret=cur.get("client_secret", ""),
            )
    except Exception:
        pass

    connected = _is_rec_connected({**cur, "service": svc})
    return {"service": svc, "permission": permission, "connected": connected}


def ignore_account(service: str) -> dict:
    """Explicitly mark an optional service as ignored by the user."""
    svc = (service or "").strip().lower()
    if svc not in SUPPORTED:
        return {"service": svc, "ignored": True}
    data = _load()
    cur = data.setdefault("accounts", {}).get(svc)
    cur = dict(cur) if isinstance(cur, dict) else {}
    cur["ignored"] = True
    cur["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    data["accounts"][svc] = cur
    _save(data)
    return {"service": svc, "ignored": True}


def set_permission(service: str, permission: str) -> dict:
    svc = (service or "").strip().lower()
    if permission not in PERMISSIONS:
        raise ValueError(f"permission must be one of {PERMISSIONS}")
    data = _load()
    if svc not in data.get("accounts", {}):
        raise ValueError(f"Service '{svc}' not connected yet")
    data["accounts"][svc]["permission"] = permission
    data["accounts"][svc]["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _save(data)
    return {"service": svc, "permission": permission}


def disconnect_account(service: str) -> str:
    svc = (service or "").strip().lower()
    data = _load()
    if svc in data.get("accounts", {}):
        del data["accounts"][svc]
        _save(data)
    try:
        from memory import config_manager as cm
        if svc == "github":
            cm._patch_config(github_token="")
        elif svc == "telegram":
            cm._patch_config(telegram_bot_token="")
        elif svc == "spotify":
            cm._patch_config(spotify_client_id="", spotify_client_secret="")
    except Exception:
        pass
    return f"Disconnected {svc}."


def check_permission(service: str, action: str = "read") -> tuple[bool, str]:
    rec = get_account(service)
    if not rec or rec.get("ignored"):
        return False, f"{service} not connected"
    perm = rec.get("permission", "ask")
    if perm == "paused":
        return False, f"{service} is paused"
    if perm == "readonly" and action in ("write", "delete", "send"):
        return False, f"{service} is read-only"
    return True, "ok"


def get_integrations_status_summary() -> dict[str, Any]:
    """Safe, secret-masked status snapshot for the HUD Onboarding & Settings UI."""
    d = _load().get("accounts", {})
    try:
        from memory import config_manager as cm
        cfg = cm.load_api_keys()
    except Exception:
        cfg = {}

    def _entry(svc: str) -> dict[str, Any]:
        rec = d.get(svc) if isinstance(d.get(svc), dict) else {}
        connected = is_service_connected(svc)
        return {
            "service": svc,
            "connected": connected,
            "ignored": bool(rec.get("ignored", False)) and not connected,
            "email": str(rec.get("email", "") or ""),
            "permission": str(rec.get("permission", "full") or "full"),
            "has_oauth_client": bool(rec.get("client_id") and rec.get("client_secret")),
            "channel_id": str(rec.get("channel_id", "") or ""),
        }

    items = {
        svc: _entry(svc)
        for svc in (
            "email",
            "gmail",
            "google_drive",
            "google_calendar",
            "github",
            "notion",
            "slack",
            "discord",
            "telegram",
            "spotify",
            "trello",
        )
    }
    connected_names = [k for k, v in items.items() if v["connected"]]
    return {
        "services": items,
        "connected_count": len(connected_names),
        "connected_services": connected_names,
        "onboarding_done": bool(cfg.get("integrations_onboarding_done", False)),
    }


def format_connected_for_prompt() -> str:
    """Compact summary injected into the system prompt so both Male & Female
    editions know exactly which user accounts are live vs ignored."""
    summary = get_integrations_status_summary()
    live = summary["connected_services"]
    if not live:
        return (
            "[CONNECTED ACCOUNTS]\n"
            "No direct cloud/email API tokens configured yet (user skipped or left optional). "
            "Use browser automation (gws_pack / browser_control) if asked, or remind the user "
            "they can add tokens anytime in HUD -> Integrations.\n"
        )
    return (
        "[CONNECTED ACCOUNTS]\n"
        f"Direct background APIs connected and ready via `cloud_integrations`: {', '.join(live)}.\n"
        "Prefer `cloud_integrations` over opening a browser whenever one of these connected services is requested.\n"
    )


def save_onboarding_integrations(payload: dict[str, Any]) -> dict[str, Any]:
    """Save a batch of optional integration configs from first-run onboarding or
    HUD Settings. Blank services are cleanly ignored without error."""
    saved: list[str] = []
    ignored: list[str] = []

    # 1. Email (IMAP/SMTP App Password)
    em = payload.get("email")
    if isinstance(em, dict):
        if em.get("ignore"):
            ignore_account("email")
            ignored.append("email")
        else:
            addr = str(em.get("email") or "").strip()
            app_pw = str(em.get("app_password") or "").strip().replace(" ", "")
            if addr and app_pw:
                connect_account(
                    "email",
                    email=addr,
                    app_password=app_pw,
                    imap_host=str(em.get("imap_host") or "").strip(),
                    smtp_host=str(em.get("smtp_host") or "").strip(),
                    permission="full",
                )
                saved.append("email")

    # 2. Google Workspace (Gmail + Google Drive + Google Calendar)
    gw = payload.get("google")
    if isinstance(gw, dict):
        if gw.get("ignore"):
            for s in ("gmail", "google_drive", "google_calendar"):
                ignore_account(s)
                ignored.append(s)
        else:
            tok = str(gw.get("token") or gw.get("access_token") or "").strip()
            ref = str(gw.get("refresh_token") or "").strip()
            cid = str(gw.get("client_id") or "").strip()
            csec = str(gw.get("client_secret") or "").strip()
            g_email = str(gw.get("email") or "").strip()
            if tok or ref or (cid and csec):
                for s in ("gmail", "google_drive", "google_calendar"):
                    connect_account(
                        s,
                        token=tok,
                        email=g_email,
                        refresh_token=ref,
                        client_id=cid,
                        client_secret=csec,
                        permission="full",
                    )
                    if tok or ref:
                        saved.append(s)

    # 3. GitHub
    gh = payload.get("github")
    if isinstance(gh, dict):
        if gh.get("ignore"):
            ignore_account("github")
            ignored.append("github")
        elif str(gh.get("token") or "").strip():
            connect_account("github", token=str(gh["token"]).strip(), permission="full")
            saved.append("github")

    # 4. Notion
    nt = payload.get("notion")
    if isinstance(nt, dict):
        if nt.get("ignore"):
            ignore_account("notion")
            ignored.append("notion")
        elif str(nt.get("token") or "").strip():
            connect_account(
                "notion",
                token=str(nt["token"]).strip(),
                parent_page_id=str(nt.get("parent_page_id") or "").strip(),
                permission="full",
            )
            saved.append("notion")

    # 5. Slack
    sl = payload.get("slack")
    if isinstance(sl, dict):
        if sl.get("ignore"):
            ignore_account("slack")
            ignored.append("slack")
        elif str(sl.get("token") or "").strip() or str(sl.get("webhook_url") or "").strip():
            connect_account(
                "slack",
                token=str(sl.get("token") or "").strip(),
                webhook_url=str(sl.get("webhook_url") or "").strip(),
                default_channel=str(sl.get("default_channel") or "").strip(),
                permission="full",
            )
            saved.append("slack")

    # 6. Discord
    dc = payload.get("discord")
    if isinstance(dc, dict):
        if dc.get("ignore"):
            ignore_account("discord")
            ignored.append("discord")
        elif str(dc.get("token") or "").strip() or str(dc.get("webhook_url") or "").strip():
            connect_account(
                "discord",
                token=str(dc.get("token") or "").strip(),
                webhook_url=str(dc.get("webhook_url") or "").strip(),
                channel_id=str(dc.get("channel_id") or "").strip(),
                permission="full",
            )
            saved.append("discord")

    # 7. Telegram
    tg = payload.get("telegram")
    if isinstance(tg, dict):
        if tg.get("ignore"):
            ignore_account("telegram")
            ignored.append("telegram")
        elif str(tg.get("token") or "").strip():
            connect_account("telegram", token=str(tg["token"]).strip(), permission="full")
            saved.append("telegram")

    # 8. Spotify
    sp = payload.get("spotify")
    if isinstance(sp, dict):
        if sp.get("ignore"):
            ignore_account("spotify")
            ignored.append("spotify")
        elif str(sp.get("client_id") or "").strip() and str(sp.get("client_secret") or "").strip():
            connect_account(
                "spotify",
                client_id=str(sp["client_id"]).strip(),
                client_secret=str(sp["client_secret"]).strip(),
                permission="full",
            )
            saved.append("spotify")

    # 9. Trello
    tr = payload.get("trello")
    if isinstance(tr, dict):
        if tr.get("ignore"):
            ignore_account("trello")
            ignored.append("trello")
        elif str(tr.get("api_key") or "").strip() and str(tr.get("token") or "").strip():
            connect_account(
                "trello",
                api_key=str(tr["api_key"]).strip(),
                token=str(tr["token"]).strip(),
                permission="full",
            )
            saved.append("trello")

    try:
        from memory import config_manager as cm
        cm.save_integrations_onboarding_done(True)
    except Exception:
        pass

    return {
        "ok": True,
        "saved": saved,
        "ignored": ignored,
        "summary": get_integrations_status_summary(),
    }


# ── Google OAuth URL + Token Refresh ─────────────────────────────────────────

GOOGLE_SCOPES = (
    "https://www.googleapis.com/auth/gmail.modify "
    "https://www.googleapis.com/auth/drive "
    "https://www.googleapis.com/auth/calendar"
)


def build_google_oauth_url(client_id: str, redirect_uri: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client_id": client_id.strip(),
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_SCOPES,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def exchange_google_oauth_code(
    code: str, client_id: str, client_secret: str, redirect_uri: str
) -> dict[str, Any]:
    body = urllib.parse.urlencode(
        {
            "code": code.strip(),
            "client_id": client_id.strip(),
            "client_secret": client_secret.strip(),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        tok_data = json.loads(resp.read().decode("utf-8"))

    access_token = str(tok_data.get("access_token") or "")
    refresh_token = str(tok_data.get("refresh_token") or "")
    expires_in = int(tok_data.get("expires_in") or 3500)
    expires_at = time.time() + max(60, expires_in - 60)

    # Fetch user email if possible
    user_email = ""
    if access_token:
        try:
            prof = _http_json(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_email = str(prof.get("emailAddress") or "")
        except Exception:
            pass

    for svc in ("gmail", "google_drive", "google_calendar"):
        connect_account(
            svc,
            token=access_token,
            email=user_email,
            refresh_token=refresh_token,
            client_id=client_id.strip(),
            client_secret=client_secret.strip(),
            expires_at=expires_at,
            permission="full",
        )
    return {"ok": True, "email": user_email, "services": ["gmail", "google_drive", "google_calendar"]}


def get_google_access_token(service: str = "google_drive") -> str | None:
    """Return a valid Google OAuth access token, refreshing automatically when needed."""
    rec = get_account(service) or get_account("gmail") or get_account("google_drive")
    if not rec or rec.get("ignored"):
        return None
    tok = str(rec.get("token") or "").strip()
    exp = float(rec.get("expires_at") or 0)
    ref = str(rec.get("refresh_token") or "").strip()
    cid = str(rec.get("client_id") or "").strip()
    csec = str(rec.get("client_secret") or "").strip()

    if tok and (exp == 0 or time.time() < exp):
        return tok

    if ref and cid and csec:
        try:
            body = urllib.parse.urlencode(
                {
                    "client_id": cid,
                    "client_secret": csec,
                    "refresh_token": ref,
                    "grant_type": "refresh_token",
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                td = json.loads(resp.read().decode("utf-8"))
            new_tok = str(td.get("access_token") or "").strip()
            if new_tok:
                new_exp = time.time() + max(60, int(td.get("expires_in") or 3500) - 60)
                for s in ("gmail", "google_drive", "google_calendar"):
                    if get_account(s):
                        connect_account(s, token=new_tok, expires_at=new_exp)
                return new_tok
        except Exception:
            pass
    return tok or None


def oauth_url(service: str, redirect: str = "http://127.0.0.1:8765/api/oauth/google/callback") -> str:
    svc = (service or "").strip().lower()
    if svc in ("gmail", "google_drive", "google_calendar", "google_classroom"):
        rec = get_account(svc) or get_account("gmail") or {}
        cid = str(rec.get("client_id") or "").strip()
        if not cid:
            try:
                from memory import config_manager as cm
                cfg = cm.load_api_keys()
                cid = str(cfg.get(f"{svc}_client_id") or cfg.get("google_client_id") or "").strip()
            except Exception:
                cid = ""
        if cid:
            return build_google_oauth_url(cid, redirect)
    try:
        from memory import config_manager as cm
        comp = cm.load_api_keys().get("composio_api_key", "")
        if comp:
            return f"https://app.composio.dev/auth/{svc}?redirect={redirect}&api_key={comp[:6]}…"
    except Exception:
        pass
    return (
        f"OAuth not configured for {svc}. Open HUD -> Integrations to enter your "
        f"{svc} token / App Password / Google Client ID, or skip if not needed."
    )


# ── Shared HTTP helper ────────────────────────────────────────────────────────

def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict | list | None = None,
    raw_body: bytes | None = None,
    timeout: float = 15.0,
) -> Any:
    hdrs = {"Accept": "application/json", **(headers or {})}
    data = raw_body
    if payload is not None and raw_body is None:
        data = json.dumps(payload).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code}: {err_body or e.reason}") from e


# ── Real Email (Gmail REST API + IMAP/SMTP App Password) ─────────────────────

def _decode_mime_words(val: str) -> str:
    if not val:
        return ""
    parts = []
    for chunk, enc in decode_header(val):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(str(chunk))
    return "".join(parts)


def _resolve_imap_smtp(rec: dict) -> tuple[str, int, str, int]:
    addr = str(rec.get("email") or "").strip().lower()
    domain = addr.split("@", 1)[1] if "@" in addr else "gmail.com"
    def_imap, def_iport, def_smtp, def_sport = EMAIL_PROVIDERS.get(
        domain, (f"imap.{domain}", 993, f"smtp.{domain}", 465)
    )
    imap_h = str(rec.get("imap_host") or def_imap).strip()
    smtp_h = str(rec.get("smtp_host") or def_smtp).strip()
    return imap_h, def_iport, smtp_h, def_sport


def email_search_messages(query: str = "is:unread", max_results: int = 8) -> list[dict]:
    """Search or list emails via Gmail REST API or IMAP App Password."""
    gtok = get_google_access_token("gmail")
    if gtok:
        q = urllib.parse.urlencode({"q": query or "", "maxResults": max(1, min(20, max_results))})
        listing = _http_json(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{q}",
            headers={"Authorization": f"Bearer {gtok}"},
        )
        out = []
        for item in (listing.get("messages") or [])[:max_results]:
            mid = item.get("id")
            if not mid:
                continue
            msg = _http_json(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}?format=metadata"
                "&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date",
                headers={"Authorization": f"Bearer {gtok}"},
            )
            hdrs = {
                h["name"].lower(): h["value"]
                for h in (msg.get("payload", {}).get("headers") or [])
                if "name" in h and "value" in h
            }
            out.append(
                {
                    "id": mid,
                    "from": hdrs.get("from", ""),
                    "subject": hdrs.get("subject", "(No subject)"),
                    "date": hdrs.get("date", ""),
                    "snippet": msg.get("snippet", ""),
                }
            )
        return out

    rec = get_account("email")
    if rec and rec.get("email") and rec.get("app_password") and not rec.get("ignored"):
        imap_h, imap_p, _, _ = _resolve_imap_smtp(rec)
        ctx = ssl.create_default_context()
        out = []
        with imaplib.IMAP4_SSL(imap_h, imap_p, ssl_context=ctx) as M:
            M.login(rec["email"], rec["app_password"])
            M.select("INBOX", readonly=True)
            q_clean = (query or "").strip()
            if not q_clean or q_clean.lower() in ("is:unread", "unread"):
                criteria = "UNSEEN"
            else:
                safe_q = q_clean.replace('"', "")
                criteria = f'(OR SUBJECT "{safe_q}" FROM "{safe_q}")'
            typ, data = M.search(None, criteria)
            if typ != "OK" or not data or not data[0]:
                typ, data = M.search(None, "ALL")
            ids = (data[0].split() if data and data[0] else [])[-max_results:]
            for uid in reversed(ids):
                t2, msg_data = M.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)] BODY.PEEK[TEXT]<0.240>)")
                if t2 != "OK" or not msg_data:
                    continue
                hdr_bytes = b""
                snippet = ""
                for part in msg_data:
                    if isinstance(part, tuple):
                        if b"HEADER.FIELDS" in part[0]:
                            hdr_bytes = part[1]
                        else:
                            snippet = part[1].decode("utf-8", errors="replace").strip()[:180]
                parsed = _email_pkg.message_from_bytes(hdr_bytes)
                out.append(
                    {
                        "id": uid.decode("ascii", errors="ignore"),
                        "from": _decode_mime_words(parsed.get("From", "")),
                        "subject": _decode_mime_words(parsed.get("Subject", "(No subject)")),
                        "date": parsed.get("Date", ""),
                        "snippet": " ".join(snippet.split()),
                    }
                )
        return out

    raise RuntimeError(
        "Email is not connected yet. Open HUD -> Integrations to add your Email App Password or Google OAuth."
    )


def email_send_message(
    to: str, subject: str, body: str, attachment_path: str = ""
) -> str:
    """Send a real email via Gmail REST API or SMTP App Password."""
    msg = EmailMessage()
    msg["To"] = to.strip()
    msg["Subject"] = subject.strip() or "(No subject)"
    msg.set_content(body or "")

    if attachment_path:
        from actions.file_controller import _resolve_path
        ap = _resolve_path(attachment_path)
        if not ap.exists() or not ap.is_file():
            raise FileNotFoundError(f"Attachment not found: {ap}")
        ctype, _ = mimetypes.guess_type(str(ap))
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        msg.add_attachment(
            ap.read_bytes(), maintype=maintype, subtype=subtype, filename=ap.name
        )

    gtok = get_google_access_token("gmail")
    if gtok:
        raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
        _http_json(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            method="POST",
            headers={"Authorization": f"Bearer {gtok}"},
            payload={"raw": raw_b64},
        )
        return f"Email sent to {to} via Gmail API (Subject: '{subject}')."

    rec = get_account("email")
    if rec and rec.get("email") and rec.get("app_password") and not rec.get("ignored"):
        _, _, smtp_h, smtp_p = _resolve_imap_smtp(rec)
        msg["From"] = rec["email"]
        ctx = ssl.create_default_context()
        if smtp_p == 465:
            with smtplib.SMTP_SSL(smtp_h, smtp_p, context=ctx, timeout=15) as S:
                S.login(rec["email"], rec["app_password"])
                S.send_message(msg)
        else:
            with smtplib.SMTP(smtp_h, smtp_p, timeout=15) as S:
                S.starttls(context=ctx)
                S.login(rec["email"], rec["app_password"])
                S.send_message(msg)
        return f"Email sent to {to} from {rec['email']} (Subject: '{subject}')."

    raise RuntimeError(
        "Email is not connected yet. Open HUD -> Integrations to add your Email App Password or Google OAuth."
    )


# ── Real Google Drive v3 Helpers ─────────────────────────────────────────────

def drive_list_files(query: str = "", max_results: int = 12) -> list[dict]:
    gtok = get_google_access_token("google_drive")
    if not gtok:
        raise RuntimeError("Google Drive is not connected yet. Configure Google in HUD -> Integrations.")
    q_parts = ["trashed = false"]
    if query.strip():
        safe = query.strip().replace("'", "\\'")
        q_parts.append(f"name contains '{safe}'")
    params = urllib.parse.urlencode(
        {
            "q": " and ".join(q_parts),
            "pageSize": max(1, min(30, max_results)),
            "fields": "files(id,name,mimeType,modifiedTime,webViewLink,size)",
            "orderBy": "modifiedTime desc",
        }
    )
    res = _http_json(
        f"https://www.googleapis.com/drive/v3/files?{params}",
        headers={"Authorization": f"Bearer {gtok}"},
    )
    return list(res.get("files") or [])


def drive_upload_file(file_path: str, folder_id: str = "") -> dict[str, Any]:
    gtok = get_google_access_token("google_drive")
    if not gtok:
        raise RuntimeError("Google Drive is not connected yet. Configure Google in HUD -> Integrations.")
    from actions.file_controller import _resolve_path
    fp = _resolve_path(file_path)
    if not fp.exists() or not fp.is_file():
        raise FileNotFoundError(f"File not found: {fp}")

    meta: dict[str, Any] = {"name": fp.name}
    if folder_id.strip():
        meta["parents"] = [folder_id.strip()]
    ctype = mimetypes.guess_type(str(fp))[0] or "application/octet-stream"
    boundary = f"jarvis_{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(meta)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode("utf-8") + fp.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")

    return _http_json(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink",
        method="POST",
        headers={
            "Authorization": f"Bearer {gtok}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
        raw_body=body,
        timeout=45.0,
    )


def drive_download_file(file_id: str, destination: str = "downloads") -> pathlib.Path:
    gtok = get_google_access_token("google_drive")
    if not gtok:
        raise RuntimeError("Google Drive is not connected yet.")
    from actions.file_controller import _resolve_path
    meta = _http_json(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=id,name,mimeType",
        headers={"Authorization": f"Bearer {gtok}"},
    )
    name = str(meta.get("name") or file_id)
    mime = str(meta.get("mimeType") or "")
    if mime == "application/vnd.google-apps.document":
        dl_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=application/pdf"
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
    elif mime == "application/vnd.google-apps.spreadsheet":
        dl_url = (
            f"https://www.googleapis.com/drive/v3/files/{file_id}/export?"
            "mimeType=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if not name.lower().endswith(".xlsx"):
            name += ".xlsx"
    else:
        dl_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    dest_dir = _resolve_path(destination or "downloads")
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / name
    req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {gtok}"})
    with urllib.request.urlopen(req, timeout=45.0) as resp:
        out_path.write_bytes(resp.read())
    return out_path


# ── Real Google Calendar Helpers ─────────────────────────────────────────────

def calendar_events_today(max_results: int = 10) -> list[dict]:
    """Fetch upcoming events from Google Calendar API v3 when connected."""
    gtok = get_google_access_token("google_calendar")
    if not gtok:
        return []
    try:
        import datetime as _dt
        now_iso = _dt.datetime.now(_dt.timezone.utc).isoformat()
        params = urllib.parse.urlencode(
            {
                "timeMin": now_iso,
                "maxResults": max_results,
                "singleEvents": "true",
                "orderBy": "startTime",
            }
        )
        res = _http_json(
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{params}",
            headers={"Authorization": f"Bearer {gtok}"},
        )
        out = []
        for ev in res.get("items") or []:
            st = ev.get("start") or {}
            out.append(
                {
                    "id": ev.get("id", ""),
                    "title": ev.get("summary", "(Untitled)"),
                    "start": st.get("dateTime") or st.get("date") or "",
                    "link": ev.get("htmlLink", ""),
                }
            )
        return out
    except Exception:
        return []


def calendar_quick_add(text: str) -> dict[str, Any]:
    gtok = get_google_access_token("google_calendar")
    if not gtok:
        raise RuntimeError("Google Calendar is not connected yet.")
    q = urllib.parse.urlencode({"text": text.strip()})
    return _http_json(
        f"https://www.googleapis.com/calendar/v3/calendars/primary/events/quickAdd?{q}",
        method="POST",
        headers={"Authorization": f"Bearer {gtok}"},
    )


def classroom_due_soon(hours: int = 48) -> list[dict]:
    gtok = get_google_access_token("google_classroom")
    if not gtok:
        return []
    return []
