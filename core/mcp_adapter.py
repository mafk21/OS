"""
Custom REST / Webhook Connector Builder & Model Context Protocol (MCP) Client — Phase 4.

100% local-first stdlib implementation (stored in `memory/custom_tools.json`).
Supports:
  1. Point-and-click Custom REST / Webhook connectors (`GET`/`POST`/`PUT`/`DELETE`,
     Bearer/API-key headers, `{{param}}` template interpolation).
  2. MCP JSON-RPC 2.0 servers over HTTP POST or local stdio subprocesses
     (`initialize` -> `tools/list` -> `tools/call`).
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
CUSTOM_TOOLS_FILE = BASE_DIR / "memory" / "custom_tools.json"

_LOCK = threading.RLock()
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")


def _load() -> dict[str, Any]:
    with _LOCK:
        if not CUSTOM_TOOLS_FILE.exists():
            return {"rest_connectors": [], "mcp_servers": []}
        try:
            raw = json.loads(CUSTOM_TOOLS_FILE.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return {"rest_connectors": [], "mcp_servers": []}
            return {
                "rest_connectors": list(raw.get("rest_connectors") or []),
                "mcp_servers": list(raw.get("mcp_servers") or []),
            }
        except Exception:
            return {"rest_connectors": [], "mcp_servers": []}


def _save(state: dict[str, Any]) -> None:
    with _LOCK:
        CUSTOM_TOOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CUSTOM_TOOLS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(CUSTOM_TOOLS_FILE)


def _interpolate(template: str, params: dict[str, Any], url_encode: bool = False) -> str:
    def _rep(m: re.Match) -> str:
        k = m.group(1)
        val = str((params or {}).get(k, ""))
        return urllib.parse.quote_plus(val) if url_encode else val

    return _PLACEHOLDER_RE.sub(_rep, template or "")


# ── Custom REST / Webhook Connectors ──────────────────────────────────────────

def list_rest_connectors() -> list[dict[str, Any]]:
    out = []
    for c in _load()["rest_connectors"]:
        masked = dict(c)
        if masked.get("bearer_token"):
            masked["bearer_token"] = "••••••••"
        out.append(masked)
    return out


def save_rest_connector(data: dict[str, Any]) -> dict[str, Any]:
    name = str(data.get("name") or "").strip()
    url = str(data.get("url") or "").strip()
    if not name or not url:
        raise ValueError("Both connector 'name' and 'url' are required.")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")

    method = str(data.get("method") or "GET").strip().upper()
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
        method = "GET"

    cid = str(data.get("id") or "").strip() or f"rest-{uuid.uuid4().hex[:8]}"
    headers = data.get("headers") if isinstance(data.get("headers"), dict) else {}

    with _LOCK:
        st = _load()
        existing_tok = ""
        for ex in st["rest_connectors"]:
            if ex.get("id") == cid or ex.get("name", "").lower() == name.lower():
                cid = str(ex.get("id") or cid)
                existing_tok = str(ex.get("bearer_token") or "")
                break

        raw_tok = str(data.get("bearer_token") or "").strip()
        bearer = existing_tok if raw_tok in ("", "••••••••") else raw_tok

        rec = {
            "id": cid,
            "name": name[:64],
            "description": str(data.get("description") or "").strip()[:240],
            "method": method,
            "url": url,
            "headers": {str(k): str(v) for k, v in headers.items() if str(k).strip()},
            "bearer_token": bearer,
            "body_template": str(data.get("body_template") or ""),
        }
        st["rest_connectors"] = [
            c for c in st["rest_connectors"] if c.get("id") != cid
        ] + [rec]
        _save(st)

    masked = dict(rec)
    if masked["bearer_token"]:
        masked["bearer_token"] = "••••••••"
    return masked


def delete_rest_connector(connector_id_or_name: str) -> bool:
    key = (connector_id_or_name or "").strip().lower()
    with _LOCK:
        st = _load()
        before = len(st["rest_connectors"])
        st["rest_connectors"] = [
            c
            for c in st["rest_connectors"]
            if str(c.get("id", "")).lower() != key and str(c.get("name", "")).lower() != key
        ]
        if len(st["rest_connectors"]) != before:
            _save(st)
            return True
    return False


def invoke_rest_connector(
    connector_id_or_name: str, params: dict[str, Any] | None = None
) -> str:
    key = (connector_id_or_name or "").strip().lower()
    target = None
    for c in _load()["rest_connectors"]:
        if str(c.get("id", "")).lower() == key or str(c.get("name", "")).lower() == key:
            target = c
            break
    if target is None:
        raise ValueError(f"Custom REST connector '{connector_id_or_name}' not found.")

    p = params or {}
    final_url = _interpolate(target["url"], p, url_encode=True)
    headers = {"User-Agent": "JARVIS-OS-Connector/1.0", **dict(target.get("headers") or {})}
    if target.get("bearer_token"):
        headers["Authorization"] = f"Bearer {target['bearer_token']}"

    raw_body: bytes | None = None
    method = target.get("method", "GET")
    if method in ("POST", "PUT", "PATCH"):
        tmpl = target.get("body_template") or ""
        if tmpl.strip():
            rendered = _interpolate(tmpl, p, url_encode=False)
            raw_body = rendered.encode("utf-8")
        elif p:
            raw_body = json.dumps(p).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(final_url, data=raw_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=18.0) as resp:
            body_txt = resp.read(16384).decode("utf-8", errors="replace")
            return f"[{resp.status}] {body_txt[:4000]}"
    except urllib.error.HTTPError as e:
        err_txt = e.read(4096).decode("utf-8", errors="replace")
        return f"[HTTP {e.code}] {err_txt[:1200]}"


# ── Model Context Protocol (MCP) JSON-RPC 2.0 Client ──────────────────────────

def list_mcp_servers() -> list[dict[str, Any]]:
    out = []
    for s in _load()["mcp_servers"]:
        masked = dict(s)
        if masked.get("bearer_token"):
            masked["bearer_token"] = "••••••••"
        out.append(masked)
    return out


def save_mcp_server(data: dict[str, Any]) -> dict[str, Any]:
    name = str(data.get("name") or "").strip()
    transport = str(data.get("transport") or "http").strip().lower()
    if transport not in ("http", "stdio"):
        transport = "http"
    url = str(data.get("url") or "").strip()
    command = str(data.get("command") or "").strip()
    if not name:
        raise ValueError("MCP server 'name' is required.")
    if transport == "http" and not url:
        raise ValueError("HTTP MCP server requires 'url'.")
    if transport == "stdio" and not command:
        raise ValueError("Stdio MCP server requires 'command'.")

    sid = str(data.get("id") or "").strip() or f"mcp-{uuid.uuid4().hex[:8]}"
    with _LOCK:
        st = _load()
        existing_tok = ""
        existing_tools: list[dict[str, Any]] = []
        for ex in st["mcp_servers"]:
            if ex.get("id") == sid or ex.get("name", "").lower() == name.lower():
                sid = str(ex.get("id") or sid)
                existing_tok = str(ex.get("bearer_token") or "")
                existing_tools = list(ex.get("tools") or [])
                break
        raw_tok = str(data.get("bearer_token") or "").strip()
        bearer = existing_tok if raw_tok in ("", "••••••••") else raw_tok
        rec = {
            "id": sid,
            "name": name[:64],
            "transport": transport,
            "url": url,
            "command": command,
            "bearer_token": bearer,
            "tools": existing_tools,
        }
        st["mcp_servers"] = [s for s in st["mcp_servers"] if s.get("id") != sid] + [rec]
        _save(st)

    masked = dict(rec)
    if masked["bearer_token"]:
        masked["bearer_token"] = "••••••••"
    return masked


def delete_mcp_server(server_id_or_name: str) -> bool:
    key = (server_id_or_name or "").strip().lower()
    with _LOCK:
        st = _load()
        before = len(st["mcp_servers"])
        st["mcp_servers"] = [
            s
            for s in st["mcp_servers"]
            if str(s.get("id", "")).lower() != key and str(s.get("name", "")).lower() != key
        ]
        if len(st["mcp_servers"]) != before:
            _save(st)
            return True
    return False


def _mcp_rpc_http(server: dict[str, Any], method: str, params: dict[str, Any]) -> dict[str, Any]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if server.get("bearer_token"):
        headers["Authorization"] = f"Bearer {server['bearer_token']}"
    rpc = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    req = urllib.request.Request(
        server["url"],
        data=json.dumps(rpc).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=18.0) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _mcp_rpc_stdio(server: dict[str, Any], method: str, params: dict[str, Any]) -> dict[str, Any]:
    argv = shlex.split(server["command"])
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "jarvis-os", "version": "1.0.0"},
        },
    }
    notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    call_req = {"jsonrpc": "2.0", "id": 2, "method": method, "params": params}
    stdin_payload = (
        json.dumps(init_req) + "\n" + json.dumps(notif) + "\n" + json.dumps(call_req) + "\n"
    )
    proc = subprocess.run(
        argv,
        input=stdin_payload,
        text=True,
        capture_output=True,
        timeout=20.0,
    )
    for line in reversed((proc.stdout or "").splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            if obj.get("id") == 2 or "result" in obj or "error" in obj:
                return obj
        except Exception:
            continue
    raise RuntimeError(proc.stderr.strip() or "No JSON-RPC response from stdio MCP server.")


def _find_mcp_server(server_id_or_name: str) -> dict[str, Any]:
    key = (server_id_or_name or "").strip().lower()
    for s in _load()["mcp_servers"]:
        if str(s.get("id", "")).lower() == key or str(s.get("name", "")).lower() == key:
            return s
    raise ValueError(f"MCP server '{server_id_or_name}' not found.")


def discover_mcp_tools(server_id_or_name: str) -> list[dict[str, Any]]:
    srv = _find_mcp_server(server_id_or_name)
    res = (
        _mcp_rpc_http(srv, "tools/list", {})
        if srv.get("transport") == "http"
        else _mcp_rpc_stdio(srv, "tools/list", {})
    )
    tools = [
        {
            "name": str(t.get("name") or ""),
            "description": str(t.get("description") or "")[:200],
        }
        for t in ((res.get("result") or {}).get("tools") or [])
        if isinstance(t, dict) and t.get("name")
    ]
    with _LOCK:
        st = _load()
        for s in st["mcp_servers"]:
            if s.get("id") == srv.get("id"):
                s["tools"] = tools
        _save(st)
    return tools


def call_mcp_tool(
    server_id_or_name: str, tool_name: str, arguments: dict[str, Any] | None = None
) -> str:
    srv = _find_mcp_server(server_id_or_name)
    params = {"name": tool_name, "arguments": arguments or {}}
    res = (
        _mcp_rpc_http(srv, "tools/call", params)
        if srv.get("transport") == "http"
        else _mcp_rpc_stdio(srv, "tools/call", params)
    )
    if "error" in res:
        return f"MCP error: {res['error']}"
    result = res.get("result") or {}
    content = result.get("content")
    if isinstance(content, list):
        texts = [str(c.get("text") or c) for c in content if isinstance(c, dict)]
        if texts:
            return "\n".join(texts)[:4000]
    return json.dumps(result)[:4000]
