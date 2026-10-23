"""Tests for the APEX-UI full desktop HUD bridge (core/apex_bridge.py + ui.py + main.py)."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from fastapi.testclient import TestClient

from core import confirm as confirm_gate
from core.apex_bridge import (
    STATIC_HUD_DIR,
    ApexHudBridge,
    map_tool_to_nodes,
)

VALID_REASONING_NODES = {
    "memory",
    "chief_of_staff",
    "strategist",
    "researcher",
    "analytics",
    "finance",
    "sales",
    "developer",
    "ops",
    "engineering",
    "design",
    "editor",
    "social_media",
    "email",
    "calendar",
    "drive",
    "slack",
    "github",
}


class _DummyWin:
    def __init__(self) -> None:
        self._ready = True
        self._paused_ui = False

    def _on_setup_done(self, key: str, os_name: str) -> None:
        self._ready = True


class _DummyUI:
    def __init__(self) -> None:
        self._win = _DummyWin()
        self.muted = False
        self.paused = False
        self.commands: list[str] = []
        self.interrupted = False
        self.stopped_all = False
        self.woken = False

        self.on_text_command = lambda t: self.commands.append(t)
        self.on_interrupt = self._do_interrupt
        self.on_stop_all = self._do_stop_all
        self.on_wake_manual = self._do_wake
        self.get_pause_state = lambda: self.paused
        self.on_pause_toggle = self._do_pause

    def _do_interrupt(self) -> None:
        self.interrupted = True

    def _do_stop_all(self) -> None:
        self.stopped_all = True

    def _do_wake(self) -> None:
        self.woken = True

    def _do_pause(self) -> bool:
        self.paused = not self.paused
        return self.paused


def test_static_hud_bundle_built():
    index_html = STATIC_HUD_DIR / "index.html"
    assert index_html.is_file(), "apex_ui/static_hud/index.html must exist"
    html = index_html.read_text(encoding="utf-8")
    assert "_next/static" in html


def test_tool_to_constellation_node_mapping():
    for tool in (
        "web_search",
        "desktop_control",
        "cmd_control",
        "system_doctor",
        "morning_briefing",
        "clipboard_intelligence",
        "code_helper",
        "gmail_control",
        "calendar_control",
        "excel_writer",
        "save_memory",
        "custom_unknown_plugin",
    ):
        nodes = map_tool_to_nodes(tool)
        assert len(nodes) >= 1
        for n in nodes:
            assert n in VALID_REASONING_NODES, f"Invalid node {n} for {tool}"


def test_http_endpoints_and_static_serving():
    ui = _DummyUI()
    bridge = ApexHudBridge(ui, port=0)
    app = bridge._build_app()

    with TestClient(app) as client:
        root_res = client.get("/")
        assert root_res.status_code == 200
        assert "text/html" in root_res.headers.get("content-type", "")

        boot_res = client.get("/api/hud/bootstrap")
        assert boot_res.status_code == 200
        boot = boot_res.json()
        assert boot["type"] == "bootstrap"
        assert boot["ready"] is True
        assert boot["raw_state"] == "LISTENING"
        assert isinstance(boot["voices"], list) and len(boot["voices"]) > 0

        act_res = client.post(
            "/api/hud/action",
            json={"action": "toggle_mute"},
        )
        assert act_res.status_code == 200
        assert act_res.json()["muted"] is True
        assert ui.muted is True

        pause_res = client.post(
            "/api/hud/action",
            json={"action": "toggle_pause"},
        )
        assert pause_res.status_code == 200
        assert pause_res.json()["paused"] is True
        assert ui.paused is True


def test_websocket_bidirectional_events_and_confirm_gate():
    ui = _DummyUI()
    bridge = ApexHudBridge(ui, port=0)
    app = bridge._build_app()

    with TestClient(app) as client:
        with client.websocket_connect("/ws/hud") as ws:
            # TestClient runs an internal loop; grab it so threadsafe pushes deliver
            first = json.loads(ws.receive_text())
            assert first["type"] == "bootstrap"

            # Send text_command over WS -> triggers JARVIS callback
            ws.send_text(json.dumps({"action": "text_command", "text": "open notepad"}))
            # Wait briefly for background thread dispatch
            for _ in range(40):
                if ui.commands:
                    break
                threading.Event().wait(0.02)
            assert ui.commands == ["open notepad"]

            # Push live state + tool trace from server -> client over WS
            bridge.push_state("SPEAKING")
            for _ in range(8):
                msg_state = json.loads(ws.receive_text())
                if msg_state.get("type") == "state" and msg_state.get("raw_state") == "SPEAKING":
                    break
            assert msg_state["type"] == "state"
            assert msg_state["raw_state"] == "SPEAKING"

            bridge.push_tool_trace("web_search")
            for _ in range(6):
                msg_trace = json.loads(ws.receive_text())
                if msg_trace.get("type") == "trace":
                    break
            assert msg_trace["type"] == "trace"
            assert "researcher" in msg_trace["nodes"]

            # Test unforgeable confirm gate resolution from HUD action
            confirm_gate.bind(
                show=bridge.push_confirm,
                hide=bridge.hide_confirm,
            )
            ran: list[str] = []
            ret = confirm_gate.request(
                "delete",
                "Delete temp files",
                "Remove 12 files",
                lambda: (ran.append("deleted_ok"), "done")[1],
            )
            assert "[CONFIRMATION_PENDING]" in ret

            snap = bridge.snapshot()
            assert snap["confirm"] == {
                "title": "Delete temp files",
                "detail": "Remove 12 files",
            }

            ws.send_text(json.dumps({"action": "confirm_decision", "approved": True}))
            for _ in range(40):
                if ran:
                    break
                threading.Event().wait(0.02)
            assert ran == ["deleted_ok"]
            assert bridge.snapshot()["confirm"] is None


def test_ui_and_main_source_wired_to_apex_bridge():
    root = Path(__file__).resolve().parent.parent
    ui_src = (root / "ui.py").read_text(encoding="utf-8")
    main_src = (root / "main.py").read_text(encoding="utf-8")

    assert "ApexHudBridge" in ui_src
    assert "JARVIS_CLASSIC_UI" in ui_src
    assert "def notify_tool_call" in ui_src
    assert "notify_tool_call" in main_src
