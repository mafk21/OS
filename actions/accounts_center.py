def manage_accounts(parameters: dict, player=None, **_):
    import memory.accounts as ac
    action=str(parameters.get("action","list")).strip().lower()
    try:
        if action=="list":
            rows=ac.list_accounts()
            if not rows:
                return (
                    f"No accounts connected. Supported: {', '.join(ac.SUPPORTED)}. "
                    "Use action=connect with service and token."
                )
            lines=["Accounts:"]
            for r in rows:
                lines.append(f"  {r['service']} — {r['permission']} — {'✓' if r['connected'] else '✗'} {r['email']}")
            if player:
                from pathlib import Path
                p=Path("memory/accounts.json")
                extra=f"\nStored in {p} ({p.stat().st_size} bytes)" if p.exists() else ""
                player.show_content("ACCOUNTS", "\n".join(lines)+extra)
            return "\n".join(lines)
        elif action=="connect":
            svc=str(parameters.get("service") or parameters.get("provider") or "").strip()
            token=str(parameters.get("token") or "")
            api_key=str(parameters.get("api_key") or parameters.get("apiKey") or "")
            email=str(parameters.get("email") or "")
            perm=str(parameters.get("permission") or "ask").strip().lower()
            if not svc: return "Missing service. Example: connect service=gmail token=ya29..."
            res=ac.connect_account(svc, token=token, api_key=api_key, email=email, permission=perm)
            if player: player.write_log(f"[Accounts] Connected {svc} ({perm})")
            return f"Connected {res['service']} as {perm} — {'✓ token' if (token or api_key) else 'no token yet, use oauth_url'}"
        elif action=="permission":
            svc=str(parameters.get("service") or "").strip()
            perm=str(parameters.get("permission") or "").strip().lower()
            res=ac.set_permission(svc, perm)
            return f"{res['service']} permission set to {res['permission']}"
        elif action in ("disconnect","remove","revoke"):
            svc=str(parameters.get("service") or "").strip()
            return ac.disconnect_account(svc)
        elif action=="oauth_url":
            svc=str(parameters.get("service") or "").strip()
            return ac.oauth_url(svc)
        elif action=="status":
            svc=str(parameters.get("service") or "").strip()
            rec=ac.get_account(svc)
            if not rec: return f"{svc} not connected"
            return f"{svc}: permission={rec.get('permission')} email={rec.get('email','—')} updated={rec.get('updated','')}"
        else: return "Actions: list/connect/permission/disconnect/oauth_url/status"
    except Exception as e: return f"Accounts error: {e}"

TOOL={
    "name":"manage_accounts",
    "description":"Account Center: list/connect/disconnect accounts (email, gmail, google_calendar, google_classroom, google_drive, github, trello, slack, notion, discord, telegram, spotify, linear, outlook, dropbox, hubspot, calendly). Each has permission ask/full/readonly/paused.",
    "parameters":{
        "type":"OBJECT",
        "properties":{
            "action":{"type":"STRING","description":"list|connect|disconnect|permission|oauth_url|status"},
            "service":{"type":"STRING","description":"Service name"},
            "provider":{"type":"STRING"},
            "token":{"type":"STRING","description":"OAuth token"},
            "api_key":{"type":"STRING","description":"API key alternative"},
            "email":{"type":"STRING"},
            "permission":{"type":"STRING","description":"ask|full|readonly|paused"}
        },
        "required":["action"]
    },
    "handler":manage_accounts
}
