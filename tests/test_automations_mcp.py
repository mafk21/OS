"""
End-to-end tests for Phase 4: Expanded SaaS Connectors (Linear, Outlook,
Dropbox, HubSpot, Calendly), Custom REST/Webhook Builder, MCP JSON-RPC 2.0
Client, and Recurring Automations Center.
"""

from __future__ import annotations

import json
import sys
from unittest.mock import patch

import pytest

from actions.cloud_integrations import cloud_integrations
from actions.custom_tools_runner import custom_connector
from core import automations, mcp_adapter
from core.apex_bridge import ApexHudBridge
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline as tl


@pytest.fixture()
def isolated_p4(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory" / "long_term.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    monkeypatch.setattr(mcp_adapter, "CUSTOM_TOOLS_FILE", tmp_path / "memory" / "custom_tools.json")
    monkeypatch.setattr(automations, "AUTOMATIONS_FILE", tmp_path / "memory" / "automations.json")
    return tmp_path


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_expanded_saas_connectors_and_onboarding_skip_options(isolated_p4):
    res = accounts.save_onboarding_integrations(
        {
            "linear": {"token": "lin_api_test123", "team_id": "TEAM-1"},
            "outlook": {"ignore": True},
            "dropbox": {"token": "sl.dropbox_tok"},
            "hubspot": {"ignore": True},
            "calendly": {"token": "cal_pat_123"},
        }
    )
    assert "linear" in res["saved"]
    assert "dropbox" in res["saved"]
    assert "calendly" in res["saved"]
    assert "outlook" in res["ignored"]
    assert "hubspot" in res["ignored"]

    # Ignored Outlook returns polite message
    assert "not connected" in cloud_integrations({"action": "outlook_unread"}).lower()

    # Connected Linear calls GraphQL cleanly
    with patch.object(
        accounts,
        "_http_json",
        return_value={
            "data": {
                "issues": {
                    "nodes": [
                        {
                            "identifier": "ENG-42",
                            "title": "Ship MCP bridge",
                            "state": {"name": "In Progress"},
                            "url": "https://linear.app/issue/ENG-42",
                        }
                    ]
                }
            }
        },
    ):
        out = cloud_integrations({"action": "linear_issues"})
        assert "ENG-42" in out
        assert "Ship MCP bridge" in out


def test_custom_rest_builder_and_stdio_mcp_jsonrpc_server(isolated_p4):
    # 1. Custom REST connector with {{query}} interpolation & token masking
    saved = mcp_adapter.save_rest_connector(
        {
            "name": "status_webhook",
            "method": "POST",
            "url": "https://hooks.example.com/ping?env={{env}}",
            "bearer_token": "sec-token-99",
            "body_template": '{"msg": "{{msg}}"}',
        }
    )
    assert saved["bearer_token"] == "••••••••"

    class _FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, *_a):
            return b'{"delivered": true}'

    with patch("urllib.request.urlopen", return_value=_FakeResp()) as m_open:
        r_out = custom_connector(
            {
                "action": "call_rest",
                "name": "status_webhook",
                "arguments": {"env": "prod", "msg": "green"},
            }
        )
        assert "[200]" in r_out
        assert '"delivered": true' in r_out
        req_sent = m_open.call_args[0][0]
        assert "env=prod" in req_sent.full_url
        assert req_sent.headers.get("Authorization") == "Bearer sec-token-99"

    # 2. Real stdio MCP JSON-RPC 2.0 server script
    mcp_script = isolated_p4 / "tiny_mcp.py"
    mcp_script.write_text(
        "import json, sys\n"
        "for line in sys.stdin:\n"
        "    msg = json.loads(line)\n"
        "    m = msg.get('method')\n"
        "    if m == 'initialize':\n"
        "        print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'result': {'capabilities': {}}}))\n"
        "    elif m == 'tools/list':\n"
        "        print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'result': {'tools': [{'name': 'echo_ping', 'description': 'Echo ping'}]}}))\n"
        "    elif m == 'tools/call':\n"
        "        arg = (msg.get('params') or {}).get('arguments', {}).get('word', '')\n"
        "        print(json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'result': {'content': [{'type': 'text', 'text': f'PONG:{arg}'}]}}))\n"
        "    sys.stdout.flush()\n",
        encoding="utf-8",
    )

    mcp_adapter.save_mcp_server(
        {
            "name": "local-echo-mcp",
            "transport": "stdio",
            "command": f"{sys.executable} {mcp_script}",
        }
    )
    disc = custom_connector({"action": "discover_mcp", "server": "local-echo-mcp"})
    assert "echo_ping" in disc

    called = custom_connector(
        {
            "action": "call_mcp",
            "server": "local-echo-mcp",
            "tool_name": "echo_ping",
            "arguments": {"word": "JARVIS"},
        }
    )
    assert "PONG:JARVIS" in called


def test_recurring_automations_scheduler_and_hud_api(isolated_p4):
    from fastapi.testclient import TestClient

    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        saved = client.post(
            "/api/hud/action",
            json={
                "action": "auto_save",
                "automation": {
                    "name": "Hourly Account Status Check",
                    "schedule_type": "interval",
                    "every_minutes": 30,
                    "steps": [{"tool": "cloud_integrations", "params": {"action": "status"}}],
                },
            },
        ).json()
        assert saved["ok"] is True
        aid = saved["automation"]["id"]

        ran = client.post(
            "/api/hud/action", json={"action": "auto_run_now", "id": aid}
        ).json()
        assert ran["ok"] is True
        assert ran["run"]["status"] == "success"
        assert "Connected & Optional Integrations" in ran["run"]["output"]

        # Verify output was archived into Brain Outputs
        assert any("Hourly Account Status Check" in o["title"] for o in tl.list_outputs())

        # Scheduler tick fires when elapsed >= every_minutes * 60
        sched = automations.AutomationScheduler()
        future_ts = automations.list_automations()[0]["last_run_ts"] + 31 * 60
        fired = sched.tick_once(now_ts=future_ts)
        assert aid in fired
