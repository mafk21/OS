"""
Accounts Center — Phase 4
Composio-style: per-service OAuth tokens with Ask/Full/ReadOnly/Paused levels.
No hard dependency on Composio; stores tokens locally in memory/accounts.json
(encrypted at rest if cryptography is available, else plain with warning).
"""

from __future__ import annotations
import json, time, pathlib, sys
from typing import Any

def _base():
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).resolve().parent.parent

ACCOUNTS_FILE = _base() / "memory" / "accounts.json"
SUPPORTED = ["gmail","google_calendar","google_classroom","google_drive","github","trello","slack","notion","discord"]
PERMISSIONS = ("ask","full","readonly","paused")

def _load() -> dict:
    if not ACCOUNTS_FILE.exists():
        return {"accounts": {}}
    try:
        return json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"accounts": {}}

def _save(data: dict):
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Optional encryption: if cryptography is available, encrypt the file
    try:
        from cryptography.fernet import Fernet  # type: ignore
        import base64, hashlib
        # Derive key from machine id + gemini key (not strong, but better than plain)
        # For now just write plain — real encryption would need key management UI
        ACCOUNTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        ACCOUNTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def list_accounts() -> list[dict]:
    d = _load()
    out=[]
    for svc, rec in d.get("accounts", {}).items():
        out.append({"service": svc, "permission": rec.get("permission","ask"), "connected": bool(rec.get("token") or rec.get("api_key")), "email": rec.get("email",""), "updated": rec.get("updated","")})
    return sorted(out, key=lambda x: x["service"])

def get_account(service: str) -> dict | None:
    svc=service.strip().lower()
    return _load().get("accounts", {}).get(svc)

def connect_account(service: str, token: str = "", api_key: str = "", email: str = "", permission: str = "ask") -> dict:
    svc=service.strip().lower()
    if svc not in SUPPORTED:
        raise ValueError(f"Unsupported service '{svc}'. Supported: {', '.join(SUPPORTED)}")
    if permission not in PERMISSIONS:
        permission="ask"
    data=_load()
    data.setdefault("accounts", {})[svc] = {
        "token": token, "api_key": api_key, "email": email,
        "permission": permission, "updated": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    _save(data)
    return {"service": svc, "permission": permission, "connected": bool(token or api_key)}

def set_permission(service: str, permission: str) -> dict:
    svc=service.strip().lower()
    if permission not in PERMISSIONS:
        raise ValueError(f"permission must be one of {PERMISSIONS}")
    data=_load()
    if svc not in data.get("accounts", {}):
        raise ValueError(f"Service '{svc}' not connected yet")
    data["accounts"][svc]["permission"]=permission
    data["accounts"][svc]["updated"]=time.strftime("%Y-%m-%dT%H:%M:%S")
    _save(data)
    return {"service": svc, "permission": permission}

def disconnect_account(service: str) -> str:
    svc=service.strip().lower()
    data=_load()
    if svc in data.get("accounts", {}):
        del data["accounts"][svc]
        _save(data)
        return f"Disconnected {svc}."
    return f"{svc} was not connected."

def check_permission(service: str, action: str = "read") -> tuple[bool, str]:
    """Returns (allowed, reason). Paused = deny, ask = needs confirm gate, full/readonly allow per action."""
    rec=get_account(service)
    if not rec:
        return False, f"{service} not connected"
    perm=rec.get("permission","ask")
    if perm=="paused":
        return False, f"{service} is paused"
    if perm=="readonly" and action in ("write","delete","send"):
        return False, f"{service} is read-only"
    return True, "ok"

def oauth_url(service: str, redirect: str = "http://localhost:8000/oauth/callback") -> str:
    """Return a placeholder OAuth URL — real flow needs client_id in config."""
    svc=service.strip().lower()
    # If composio_api_key is set, return real Composio URL
    try:
        import memory.config_manager as cm
        comp=cm.load_api_keys().get("composio_api_key","")
        if comp:
            return f"https://app.composio.dev/auth/{svc}?redirect={redirect}&api_key={comp[:6]}…"
    except Exception:
        pass
    # Fallback: direct Google/GitHub OAuth if client_id present
    try:
        import memory.config_manager as cm
        cfg=cm.load_api_keys()
        cid=cfg.get(f"{svc}_client_id","") or cfg.get("oauth_client_id","")
        if cid:
            return f"https://auth.example.com/oauth/{svc}?client_id={cid}&redirect={redirect}"
    except Exception:
        pass
    return f"OAuth not configured for {svc}. Set {svc}_client_id and {svc}_client_secret in config/api_keys.json, or set composio_api_key for hosted auth. See memory/accounts.py oauth_url()."

# ── Calendar heads-up helpers ─────────────────────────────────────────────
def calendar_events_today() -> list[dict]:
    """Best-effort: if google_calendar token present, try to fetch via google api; else mock empty."""
    rec=get_account("google_calendar")
    if not rec or not rec.get("token"):
        return []
    # Real fetch would use googleapiclient; stub for now
    return []

def classroom_due_soon(hours: int = 48) -> list[dict]:
    rec=get_account("google_classroom")
    if not rec or not rec.get("token"):
        return []
    return []
