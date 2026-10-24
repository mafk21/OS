"""
actions/companion_os.py — Voice & Live-Session Tool Parity for Recurring
Automations, Specialist Companions, Revocable Guest Portals, and Audit Chain.

Lets the user control every HUD Studio / Automate / Shield capability naturally
by voice or text across both Male and Female editions.
"""

from __future__ import annotations

import json
from typing import Any

from core import automations, companions, security_vault
from memory import timeline


def _parse_json_obj(val: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(val, dict):
        return val
    if isinstance(val, str) and val.strip():
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return dict(default) if default is not None else {}


def companion_os(parameters: dict[str, Any] | None = None, player=None, **_kwargs) -> str:
    params = parameters or {}
    action = str(params.get("action") or "status").strip().lower()

    try:
        # ── Recurring Automations ─────────────────────────────────────────
        if action == "automation_list":
            items = automations.list_automations()
            if not items:
                return "No recurring automations scheduled yet."
            lines = [f"Automations ({len(items)}):"]
            for a in items:
                sched = (
                    f"every {a['every_minutes']}m"
                    if a["schedule_type"] == "interval"
                    else f"daily @ {a['daily_at']}"
                    if a["schedule_type"] == "daily"
                    else "manual"
                )
                state = "ACTIVE" if a.get("enabled", True) else "PAUSED"
                lines.append(f"  • [{a['id']}] {a['name']} ({sched}, {state})")
            return "\n".join(lines)

        if action == "automation_save":
            rec = automations.save_automation(
                {
                    "name": str(params.get("name") or params.get("title") or "").strip(),
                    "schedule_type": str(params.get("schedule_type") or "interval"),
                    "every_minutes": int(params.get("every_minutes") or 60),
                    "daily_at": str(params.get("daily_at") or "09:00"),
                    "tool": str(params.get("tool") or "cloud_integrations"),
                    "params": _parse_json_obj(
                        params.get("tool_params"), default={"action": "status"}
                    ),
                }
            )
            return f"Saved automation '{rec['name']}' (id={rec['id']}, {rec['schedule_type']})."

        if action == "automation_run":
            aid = str(params.get("id") or "").strip()
            if not aid:
                # Match by name substring if id omitted
                q = str(params.get("name") or "").strip().lower()
                for a in automations.list_automations():
                    if q and q in a["name"].lower():
                        aid = a["id"]
                        break
            if not aid:
                return "Provide automation 'id' or 'name' to run."
            run_rec = automations.run_automation_now(aid)
            if player and hasattr(player, "show_content"):
                player.show_content("AUTOMATION RUN", run_rec["output"])
            return f"Automation {aid} finished ({run_rec['status']}):\n{run_rec['output'][:900]}"

        if action == "automation_toggle":
            aid = str(params.get("id") or "").strip()
            toggled = automations.toggle_automation(aid, enabled=params.get("enabled"))
            if not toggled:
                return f"Automation '{aid}' not found."
            return f"Automation '{toggled['name']}' is now {'ACTIVE' if toggled['enabled'] else 'PAUSED'}."

        if action == "automation_delete":
            aid = str(params.get("id") or "").strip()
            ok = automations.delete_automation(aid)
            return f"Deleted automation {aid}." if ok else f"Automation '{aid}' not found."

        # ── Specialist Companions ─────────────────────────────────────────
        if action == "companion_list":
            active = companions.get_active_companion()
            rows = companions.list_companions()
            lines = [f"Specialist Companions (active: {active['name']}):"]
            for c in rows:
                mark = "★ " if c["id"] == active["id"] else "  "
                lines.append(f"{mark}[{c['id']}] {c['name']} — {c['role']} ({c['persona']}/{c['voice']})")
            return "\n".join(lines)

        if action == "companion_activate":
            target = str(params.get("id") or params.get("name") or "default").strip()
            cid = target
            if target.lower() != "default":
                for c in companions.list_companions():
                    if c["id"] == target or c["name"].lower() == target.lower():
                        cid = c["id"]
                        break
            comp = companions.set_active_companion(cid)
            return f"Switched active companion to {comp['name']} ({comp['role']}, {comp['persona']} edition)."

        if action == "companion_create":
            comp = companions.save_companion(
                {
                    "name": str(params.get("name") or "").strip(),
                    "role": str(params.get("role") or "Specialist Companion").strip(),
                    "persona": str(params.get("persona") or "male"),
                    "voice": str(params.get("voice") or ""),
                    "instructions": str(params.get("instructions") or ""),
                    "allowed_tools": params.get("allowed_tools")
                    if isinstance(params.get("allowed_tools"), list)
                    else [],
                }
            )
            return f"Created specialist companion '{comp['name']}' (id={comp['id']})."

        # ── Revocable Guest Portals & Audit Chain ─────────────────────────
        if action == "portal_create":
            title = str(params.get("title") or params.get("name") or "").strip()
            body = str(params.get("content") or params.get("body") or "").strip()
            if not body:
                outs = timeline.list_outputs(limit=1)
                if outs:
                    title = title or outs[0]["title"]
                    body = str(outs[0].get("content") or outs[0].get("body") or "")
            if not body:
                return "Provide 'content' to share, or generate a report first."
            p = security_vault.create_portal(
                title=title or "Shared Deliverable",
                content_body=body,
                expires_hours=float(params.get("expires_hours") or 24.0),
                max_views=int(params.get("max_views") or 50),
            )
            if player and hasattr(player, "show_content"):
                player.show_content("GUEST PORTAL CREATED", f"Title: {p['title']}\nPath: {p['path']}")
            return f"Created revocable Guest Portal '{p['title']}' (id={p['id']}): {p['path']}"

        if action == "portal_list":
            plist = security_vault.list_portals()
            if not plist:
                return "No Guest Portals created."
            return "Guest Portals:\n" + "\n".join(
                f"  • [{p['id']}] {p['title']} — {'LIVE' if p['active'] else 'CLOSED'} (views {p['view_count']}/{p['max_views']})"
                for p in plist
            )

        if action == "portal_revoke":
            pid = str(params.get("id") or "").strip()
            ok = security_vault.revoke_portal(pid)
            return f"Revoked portal {pid}." if ok else f"Portal '{pid}' not found."

        if action == "portal_revoke_all":
            cnt = security_vault.revoke_all_portals()
            return f"Shut off {cnt} active Guest Portal(s)."

        if action == "audit_verify":
            ch = security_vault.verify_audit_chain()
            if ch["valid"]:
                return f"Security audit SHA-256 hash chain verified: {ch['checked']} entries intact."
            return f"ALERT: Audit hash chain broken at entry #{ch['broken_at_id']} ({ch.get('reason')})."

        return (
            "Supported companion_os actions: automation_list, automation_save, automation_run, "
            "automation_toggle, automation_delete, companion_list, companion_activate, "
            "companion_create, portal_create, portal_list, portal_revoke, portal_revoke_all, audit_verify."
        )
    except Exception as exc:
        return f"companion_os error: {exc}"


TOOL = {
    "name": "companion_os",
    "description": (
        "Manage recurring Automations, switch or create Specialist Companions, create or "
        "revoke read-only Guest Portal share links, and verify the SHA-256 Action Audit Chain "
        "by voice or text. Actions: automation_list | automation_save | automation_run | "
        "automation_toggle | automation_delete | companion_list | companion_activate | "
        "companion_create | portal_create | portal_list | portal_revoke | portal_revoke_all | audit_verify."
    ),
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action name (see tool description)"},
            "id": {"type": "STRING", "description": "Automation, Companion, or Portal ID"},
            "name": {"type": "STRING", "description": "Name or title"},
            "title": {"type": "STRING", "description": "Portal or automation title"},
            "content": {"type": "STRING", "description": "Body content for portal_create (defaults to latest output)"},
            "schedule_type": {"type": "STRING", "description": "interval | daily | manual"},
            "every_minutes": {"type": "INTEGER", "description": "Interval minutes for automation_save"},
            "daily_at": {"type": "STRING", "description": "HH:MM time for daily automation_save"},
            "tool": {"type": "STRING", "description": "Target action tool name for automation_save"},
            "tool_params": {
                "type": "STRING",
                "description": "Optional JSON object string of parameters for automation_save, e.g. '{\"action\": \"status\"}'",
            },
            "role": {"type": "STRING", "description": "Specialist companion role"},
            "persona": {"type": "STRING", "description": "male | female"},
            "voice": {"type": "STRING", "description": "Voice name (e.g. Charon, Aoede)"},
            "instructions": {"type": "STRING", "description": "Specialist companion instructions"},
            "allowed_tools": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Scoped tool whitelist"},
            "expires_hours": {"type": "NUMBER", "description": "Guest portal expiry hours (default 24)"},
            "max_views": {"type": "INTEGER", "description": "Guest portal max views (default 50)"},
            "enabled": {"type": "BOOLEAN", "description": "Explicit enable/pause boolean"},
        },
        "required": ["action"],
    },
    "handler": companion_os,
}
