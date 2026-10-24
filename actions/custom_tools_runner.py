"""
actions/custom_tools_runner.py — Unified tool plugin for Custom REST/Webhook
connectors and Model Context Protocol (MCP) servers created in HUD -> Automate.
"""

from __future__ import annotations

from typing import Any

from core import mcp_adapter


def custom_connector(parameters: dict[str, Any] | None = None, **_kwargs) -> str:
    params = parameters or {}
    action = str(params.get("action") or "list").strip().lower()

    try:
        if action == "list":
            rest = mcp_adapter.list_rest_connectors()
            mcps = mcp_adapter.list_mcp_servers()
            lines = ["Custom Connectors & MCP Servers:"]
            for c in rest:
                lines.append(f"  • [REST {c['method']}] {c['name']} — {c.get('description') or c['url']}")
            for s in mcps:
                tnames = ", ".join(t["name"] for t in (s.get("tools") or [])) or "run discover_mcp"
                lines.append(f"  • [MCP/{s['transport']}] {s['name']} — tools: {tnames}")
            return "\n".join(lines) if (rest or mcps) else "No custom REST connectors or MCP servers configured yet."

        if action == "call_rest":
            name = str(params.get("name") or "").strip()
            args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            return mcp_adapter.invoke_rest_connector(name, args)

        if action == "discover_mcp":
            name = str(params.get("server") or params.get("name") or "").strip()
            tools = mcp_adapter.discover_mcp_tools(name)
            return f"Discovered {len(tools)} MCP tools on '{name}': " + ", ".join(t["name"] for t in tools)

        if action == "call_mcp":
            srv = str(params.get("server") or "").strip()
            tname = str(params.get("tool_name") or params.get("name") or "").strip()
            args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            return mcp_adapter.call_mcp_tool(srv, tname, args)

        return "Unknown action. Use: list | call_rest | discover_mcp | call_mcp."
    except Exception as exc:
        return f"custom_connector error: {exc}"


TOOL = {
    "name": "custom_connector",
    "description": (
        "List and invoke user-created Custom REST/Webhook APIs and MCP (Model Context Protocol) "
        "servers configured in the HUD Builder. Actions: 'list', 'call_rest', 'discover_mcp', 'call_mcp'."
    ),
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "list | call_rest | discover_mcp | call_mcp"},
            "name": {"type": "STRING", "description": "REST connector name/id or MCP tool name"},
            "server": {"type": "STRING", "description": "MCP server name/id"},
            "tool_name": {"type": "STRING", "description": "MCP tool name for call_mcp"},
            "arguments": {"type": "OBJECT", "description": "JSON arguments/parameters"},
        },
        "required": ["action"],
    },
    "handler": custom_connector,
}
