"""Check for and safely install owner-confirmed JARVIS updates."""
from __future__ import annotations

from core import update_manager


def jarvis_update(parameters=None, player=None, **_kwargs) -> str:
    action = str((parameters or {}).get("action") or "check").strip().lower()
    if action not in {"check", "update"}:
        return "Choose check or update."
    status = update_manager.check_for_updates(fetch=True)
    if not status.available:
        return status.message
    # Even an explicit spoken update request goes through the HUD confirmation:
    # repository code changes and a process restart must remain human-approved.
    return update_manager.request_update(status, player=player)


TOOL = {
    "name": "jarvis_update",
    "description": (
        "Check whether this Git installation of JARVIS has an update on origin/main. "
        "Use when the user asks to check for updates or update JARVIS. Available "
        "updates always require the owner to press the HUD confirmation before "
        "installation and restart; never claim an update completed while confirmation is pending."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["check", "update"],
                "description": "Check for an update and, when available, offer the confirmed update flow.",
            }
        },
        "required": ["action"],
    },
    "handler": jarvis_update,
}
