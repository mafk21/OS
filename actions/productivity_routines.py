"""Voice Routines — save & execute multi-step triggers (e.g. 'study mode', 'focus mode')."""

from __future__ import annotations

import json
import re


def _try_execute_step(step: str, player=None) -> str:
    """Execute safe local routine steps (app launch) and tag follow-up steps."""
    s = step.strip()
    m = re.match(r"^(?:open|launch|start)\s+([a-zA-Z0-9_. +\-]+)$", s, re.IGNORECASE)
    if m:
        app_name = m.group(1).strip()
        if not any(tok in app_name.lower() for tok in ("timer", "minute", "hour", "mode")):
            try:
                from actions.open_app import open_app_action
                res = open_app_action({"app_name": app_name}, player=player)
                return f"{s} → {res}"
            except Exception:
                pass
    return f"{s} → [follow-up step ready]"


def manage_routines(parameters: dict, player=None, **_) -> str:
    import memory.productivity as prod

    action = str((parameters or {}).get("action", "list") or "list").strip().lower()
    try:
        if action in ("add", "create", "save"):
            name = str(parameters.get("name") or parameters.get("title") or "").strip()
            trigger = str(parameters.get("trigger") or "").strip()
            steps = parameters.get("steps")
            if isinstance(steps, str):
                try:
                    steps = json.loads(steps)
                except Exception:
                    steps = [p.strip() for p in steps.split(",") if p.strip()]
            if not name or not trigger or not steps:
                return (
                    "Need name, trigger, and steps. Example: add routine "
                    "'Study mode' trigger 'study mode' "
                    "steps=['close Discord','open Obsidian','50m timer']"
                )
            res = prod.add_routine(name, trigger, steps, str(parameters.get("description", "")))
            if player and hasattr(player, "write_log"):
                player.write_log(f"[Routines] + {name} -> {trigger}")
            return f"Routine '{name}' saved for trigger '{trigger}' ({len(steps)} steps)."

        if action == "list":
            rows = prod.list_routines()
            if not rows:
                return "No routines yet. Say 'when I say study mode, close Discord, open notes, set a 50m timer'."
            lines = ["Routines:"]
            for r in rows:
                lines.append(f"  {r['name']} — trigger '{r['trigger']}' — {len(r['steps'])} steps")
            if player and hasattr(player, "show_content"):
                player.show_content("ROUTINES", "\n".join(lines))
            return "\n".join(lines)

        if action == "run":
            trigger = str(parameters.get("trigger") or parameters.get("name") or "").strip()
            r = prod.get_routine_by_trigger(trigger.lower())
            if not r:
                return f"No routine for trigger '{trigger}'."
            execute = bool(parameters.get("execute", True))
            out = [f"Running routine '{r['name']}' (trigger: '{r['trigger']}'):"]
            for i, step in enumerate(r["steps"], 1):
                detail = _try_execute_step(step, player=player) if execute else step
                out.append(f"  {i}. {detail}")
            out.append("Complete any remaining [follow-up step ready] items with their matching tools.")
            rendered = "\n".join(out)
            if player and hasattr(player, "show_content"):
                player.show_content(f"ROUTINE — {r['name'].upper()}", rendered)
            return rendered

        if action in ("delete", "remove"):
            name = str(parameters.get("name") or "").strip()
            return prod.delete_routine(name)

        return "Actions: add/list/run/delete"
    except Exception as e:
        return f"Routines error: {e}"


TOOL = {
    "name": "manage_routines",
    "description": (
        "Manage multi-step voice routines: add/list/run/delete. Routines map "
        "a trigger phrase ('study mode', 'focus mode') to ordered steps and "
        "execute app-launch steps automatically when run."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "add|list|run|delete"},
            "name": {"type": "STRING", "description": "Routine name"},
            "trigger": {"type": "STRING", "description": "Voice trigger phrase lowercased"},
            "steps": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Ordered step strings or JSON array",
            },
            "description": {"type": "STRING"},
            "execute": {"type": "BOOLEAN", "description": "Execute safe local steps on run (default true)"},
        },
        "required": ["action"],
    },
    "handler": manage_routines,
}
