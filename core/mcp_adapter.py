"""
MCP adapter — wraps existing plugin system to expose MCP servers as tools.
Keeps .py plugin system intact; MCP servers are listed in memory/mcp_servers.json.
"""
import json, pathlib

MCP_CONFIG = pathlib.Path("memory/mcp_servers.json")

def list_servers():
    if not MCP_CONFIG.exists(): return []
    try: return json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    except: return []

def discover_mcp_tools():
    """Stub: enumerate MCP tools. Real impl calls MCP SDK to list_tools()."""
    servers = list_servers()
    if not servers: return []
    # Return synthetic tool stubs so UI shows them
    tools=[]
    for name, cfg in servers.items():
        tools.append({"name": f"mcp_{name}_ping", "description": f"Ping MCP server {name} ({cfg.get('transport','sse')})", "server": name})
    return tools
