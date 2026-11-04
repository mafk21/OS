"""Explicit owner controls for the private JARVIS taste profile."""
from __future__ import annotations

from memory import taste_manager


def taste_profile(parameters=None, **_kwargs) -> str:
    p = parameters or {}
    action = str(p.get("action") or "list").strip().lower()
    try:
        if action == "add":
            entry = taste_manager.add_preference(
                p.get("domain", "other"), p.get("item", ""),
                p.get("sentiment", "like"), p.get("contexts") or [],
                kind=p.get("kind", "preference"),
            )
            return f"Saved explicit {entry['domain']} taste: {entry['item']} ({entry['sentiment']})."
        if action == "remove":
            ok = taste_manager.remove_preference(str(p.get("entry_id") or ""))
            return "Taste entry removed." if ok else "That taste entry was not found."
        if action == "set_discovery":
            taste_manager.set_discovery(p.get("domain", "other"), p.get("mode", "balanced"))
            return f"Taste discovery mode updated to {p.get('mode', 'balanced')}."
        if action == "list":
            state = taste_manager.status()
            if not state["entries"]:
                return "No taste preferences are saved yet. The user can set them in Taste settings or tell me explicitly."
            lines = [
                f"{e['id']}: {e['domain']} / {e['sentiment']} / {e['item']}"
                for e in state["entries"][:40]
            ]
            return "Saved explicit taste profile:\n" + "\n".join(lines)
        return "Use add, remove, list, or set_discovery for the taste profile."
    except ValueError as exc:
        return f"Taste profile was not changed: {exc}"


TOOL = {
    "name": "taste_profile",
    "description": (
        "Manage the owner's explicit personal taste in music, food, drinks, entertainment, "
        "style, travel, and other recommendations. Use only when the user explicitly states "
        "a preference, asks what is remembered, asks to forget one, or changes discovery mode. "
        "Never infer protected traits, allergies, or medical facts."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "enum": ["add", "remove", "list", "set_discovery"]},
            "domain": {"type": "STRING", "enum": list(taste_manager.DOMAINS)},
            "item": {"type": "STRING", "description": "Exact preference stated by the user."},
            "sentiment": {"type": "STRING", "enum": list(taste_manager.SENTIMENTS)},
            "kind": {"type": "STRING", "enum": ["preference", "restriction"]},
            "contexts": {"type": "ARRAY", "items": {"type": "STRING"}},
            "entry_id": {"type": "STRING"},
            "mode": {"type": "STRING", "enum": list(taste_manager.DISCOVERY_MODES)},
        },
        "required": ["action"],
    },
    "handler": taste_profile,
}
