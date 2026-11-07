"""Cross-platform semantic desktop control through native accessibility APIs."""
from __future__ import annotations

from core.native_accessibility import MAX_NODES, execute, system_adapter


def accessibility_control(parameters: dict, player=None, **_):
    params = parameters or {}
    action = str(params.get("action") or "invoke").strip().lower()
    target = str(params.get("target") or params.get("name") or params.get("button") or "").strip()
    value = str(params.get("text") or params.get("value") or "")
    role = str(params.get("role") or "").strip()
    try:
        adapter = system_adapter()
    except Exception as exc:
        return f"Native accessibility unavailable: {type(exc).__name__}. No coordinate fallback was attempted."

    if action == "list":
        controls = []
        try:
            for index, node in enumerate(adapter.nodes()):
                if index >= min(MAX_NODES, 80):
                    break
                if node.name:
                    controls.append(f"{node.role or 'control'}: {node.name}")
        except Exception as exc:
            return f"Native accessibility discovery failed: {type(exc).__name__}."
        if not controls:
            return "No named native accessibility controls were observed."
        return "Observed native controls:\n" + "\n".join(f"- {row}" for row in controls[:80])

    result = execute(adapter, target, action, value=value, role=role)
    if not result.get("ok"):
        return f"Native accessibility action failed: {result.get('error', 'unknown failure')}. No coordinate fallback was attempted."
    control = result.get("control") or {}
    return (
        f"Native {result['action']} observed for {control.get('role') or 'control'} "
        f"'{control.get('name') or target}' ({result.get('match')}; verified={str(result.get('verified')).lower()})."
    )


TOOL = {
    "name": "accessibility_control",
    "description": (
        "Control the foreground application through Windows UI Automation, macOS Accessibility, or Linux AT-SPI. "
        "Uses semantic names and roles, rejects ambiguous matches, and never silently falls back to coordinates. "
        "Actions: invoke, set_value, toggle, select, list."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "invoke | set_value | toggle | select | list"},
            "target": {"type": "STRING", "description": "Exact accessible control name"},
            "role": {"type": "STRING", "description": "Optional accessible role used to disambiguate"},
            "text": {"type": "STRING", "description": "Value for set_value"},
            "name": {"type": "STRING"},
            "button": {"type": "STRING"},
            "value": {"type": "STRING"},
        },
        "required": ["action"],
    },
    "handler": accessibility_control,
    "safety": {
        "risk": "medium", "permission": "native_accessibility", "confirmation": "none",
        "side_effect": True, "reversible": False, "verification": "observed",
    },
}
