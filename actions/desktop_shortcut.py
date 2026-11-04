"""Create or remove the JARVIS desktop shortcut on the user's request."""
from __future__ import annotations

from core import desktop_shortcut


def manage_desktop_shortcut(parameters=None, **_kwargs) -> str:
    params = parameters or {}
    action = str(params.get("action") or "create").strip().lower()
    if action in {"create", "add", "install"}:
        path = desktop_shortcut.create()
        return f"JARVIS desktop shortcut created at {path}."
    if action in {"remove", "delete", "uninstall"}:
        removed = desktop_shortcut.remove()
        return "JARVIS desktop shortcut removed." if removed else "No JARVIS desktop shortcut was present."
    if action in {"status", "check"}:
        state = desktop_shortcut.status()
        return (
            f"The JARVIS desktop shortcut exists at {state['path']}."
            if state["exists"]
            else "The JARVIS desktop shortcut is not installed."
        )
    return "Choose create, remove, or status for the JARVIS desktop shortcut."


TOOL = {
    "name": "desktop_shortcut",
    "description": (
        "Creates, removes, or checks the JARVIS Desktop shortcut. Use this when "
        "the user asks to add JARVIS to the Desktop, create an app icon/shortcut, "
        "remove that shortcut, or check whether it exists."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "enum": ["create", "remove", "status"],
                "description": "Desktop shortcut operation.",
            }
        },
        "required": ["action"],
    },
    "handler": manage_desktop_shortcut,
}
