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
    assert "wait_for_persona" in ui_src
    assert "wait_for_persona" in main_src


def test_male_and_female_persona_startup_and_switching(monkeypatch, tmp_path):
    from memory import config_manager as cfg

    fake_cfg = tmp_path / "api_keys.json"
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cfg, "CONFIG_FILE", fake_cfg)

    ui = _DummyUI()
    ui._win._ready = False
    ui._persona_selected = False
    voice_rebuilds: list[str] = []
    ui.on_voice_change = lambda v="": voice_rebuilds.append(v)

    bridge = ApexHudBridge(ui, port=0)
    app = bridge._build_app()

    with TestClient(app) as client:
        # 1. Fresh install: setup not done yet -> ready=False, persona_chosen=False
        boot0 = client.get("/api/hud/bootstrap").json()
        assert boot0["ready"] is False
        assert boot0["persona_chosen"] is False
        assert boot0["persona"] == "male"

        # 2. Complete API key setup -> ready=True, persona_chosen STILL False so
        #    the Male/Female version chooser opens immediately after setup!
        r_key = client.post(
            "/api/hud/action",
            json={"action": "save_api_key", "key": "AIzaSyTestKey_1234567890"},
        )
        assert r_key.status_code == 200 and r_key.json()["ok"] is True

        boot1 = client.get("/api/hud/bootstrap").json()
        assert boot1["ready"] is True
        assert boot1["persona_chosen"] is False

        # 3. User picks Female version on launch -> Aoede voice + rose color,
        #    unblocks startup (_persona_selected=True) without premature reconnect
        r_fem = client.post(
            "/api/hud/action",
            json={"action": "set_persona", "persona": "female"},
        )
        assert r_fem.status_code == 200
        fem_data = r_fem.json()
        assert fem_data["ok"] is True
        assert fem_data["persona"] == "female"
        assert fem_data["voice"] == "Aoede"
        assert fem_data["ui_color"] == "#ff4db8"
        assert ui._persona_selected is True
        assert voice_rebuilds == []

        boot2 = client.get("/api/hud/bootstrap").json()
        assert boot2["persona"] == "female"
        assert boot2["persona_chosen"] is True
        assert boot2["voice"] == "Aoede"

        # 4. Mid-session switch back to Male version -> Charon voice + cyan color
        #    AND triggers on_voice_change to rebuild the active Live session!
        r_male = client.post(
            "/api/hud/action",
            json={"action": "set_persona", "persona": "male"},
        )
        assert r_male.status_code == 200
        male_data = r_male.json()
        assert male_data["persona"] == "male"
        assert male_data["voice"] == "Charon"
        assert male_data["ui_color"] == "#00d4ff"
        for _ in range(30):
            if voice_rebuilds:
                break
            threading.Event().wait(0.02)
        assert voice_rebuilds == ["Charon"]

        # 5. Preserves secondary female voice ('Kore') when re-selecting female
        cfg.save_voice("Kore")
        res_kore = cfg.save_persona("female")
        assert res_kore["voice"] == "Kore"


def test_static_hud_bundle_contains_male_and_female_editions():
    js_files = list((STATIC_HUD_DIR / "_next").rglob("*.js"))
    combined = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in js_files)
    assert "FEMALE EDITION" in combined
    assert "MALE EDITION" in combined
    assert "CHOOSE INTERFACE VERSION" in combined


def test_persona_choice_remembered_across_restarts_and_changeable_anytime(
    tmp_path, monkeypatch
):
    import json

    from actions.companion_os import companion_os
    from memory import config_manager as cfg

    fake_cfg = tmp_path / "api_keys.json"
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cfg, "CONFIG_FILE", fake_cfg)
    monkeypatch.delenv("JARVIS_SKIP_PERSONA_PROMPT", raising=False)

    # 1. Fresh install: API key saved, but persona NOT chosen yet -> asks once
    cfg.save_api_keys(gemini_api_key="AIzaSyFreshInstallTestKey12345")
    assert cfg.is_persona_chosen() is False

    # 2. User selects Female edition on first run -> persisted to disk
    res_f = cfg.save_persona("female")
    assert res_f["persona"] == "female"
    assert cfg.is_persona_chosen() is True
    saved_disk = json.loads(fake_cfg.read_text(encoding="utf-8"))
    assert saved_disk["persona"] == "female"
    assert saved_disk["persona_chosen"] is True

    # 3. Simulate app restart (new bridge / new JarvisUI session): remembered automatically!
    restarted_ui = _DummyUI()
    restarted_ui._win._ready = True
    restarted_ui._persona_selected = cfg.is_persona_chosen()
    assert restarted_ui._persona_selected is True

    bridge = ApexHudBridge(restarted_ui, port=0)
    boot_after_restart = bridge.snapshot()
    assert boot_after_restart["persona_chosen"] is True
    assert boot_after_restart["persona"] == "female"

    # 4. Legacy config upgrade: even if an older api_keys.json only had `"persona": "male"`
    #    (without `"persona_chosen"`), it is still remembered without re-prompting!
    fake_cfg.write_text(
        json.dumps({"gemini_api_key": "AIzaSyLegacyKey1234567890", "persona": "male"}),
        encoding="utf-8",
    )
    assert cfg.is_persona_chosen() is True
    assert cfg.get_persona() == "male"

    # 5. User can still switch anytime later (via HUD action OR voice/text `companion_os`)
    out_voice = companion_os({"action": "set_persona", "persona": "female"})
    assert "Female edition" in out_voice
    assert cfg.get_persona() == "female"
    assert cfg.is_persona_chosen() is True

    r_hud = bridge.handle_action({"action": "set_persona", "persona": "male"})
    assert r_hud["ok"] is True
    assert cfg.get_persona() == "male"
    assert cfg.is_persona_chosen() is True


