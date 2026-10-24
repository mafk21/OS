"""
End-to-end tests for Phase 2: Living 3D World View, Worker Orbs,
Live Activity Timeline, and Dual-Monitor Pop-Out Console.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.apex_bridge import ApexHudBridge
from core.subagents import SubagentManager, get_subagent_manager
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline as tl


@pytest.fixture()
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory" / "long_term.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    fresh_mgr = SubagentManager()
    monkeypatch.setattr("core.subagents._manager", fresh_mgr)
    return tmp_path


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_subagent_detailed_listeners_and_tool_activity_lifecycle(isolated_env):
    events = []
    mgr = get_subagent_manager()
    mgr.add_listener(lambda: events.append("changed"))

    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=0)

    # Spawn a parallel subagent
    aid = mgr.spawn("Research top 5 vector DB benchmarks", tools=["web_search"])
    mgr.start(aid)
    mgr.add_step(aid, "web_search", "Collected latency numbers for Qdrant & Milvus")

    # Simultaneously start a live tool call
    bridge.notify_tool_start("fc-99-deep_research", "deep_research", "query=AI chips")

    snap = bridge.get_activity_snapshot()
    ids = {w["id"] for w in snap}
    assert aid in ids
    assert "fc-99-deep_research" in ids
    assert len(events) >= 3

    # Cancel live tool task via HUD action and complete subagent
    res_cancel = bridge.handle_action({"action": "cancel_worker", "worker_id": "fc-99-deep_research"})
    assert res_cancel["ok"] is True
    assert bridge.is_task_cancelled("fc-99-deep_research") is True

    mgr.complete(aid, "Benchmark matrix compiled.")
    cleared = bridge.handle_action({"action": "clear_completed_workers"})
    assert cleared["ok"] is True
    assert cleared["removed"] >= 2
    assert bridge.get_activity_snapshot() == []


def test_hud_http_worker_spawn_step_cancel_male_and_female(isolated_env):
    from fastapi.testclient import TestClient

    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        for edition in ("male", "female"):
            client.post("/api/hud/action", json={"action": "set_persona", "persona": edition})
            r_spawn = client.post(
                "/api/hud/action",
                json={
                    "action": "spawn_worker",
                    "goal": f"Parallel audit ({edition})",
                    "tools": ["web_search", "brain_control"],
                },
            ).json()
            assert r_spawn["ok"] is True
            wid = r_spawn["worker_id"]

            r_step = client.post(
                "/api/hud/action",
                json={
                    "action": "step_worker",
                    "worker_id": wid,
                    "step_action": "web_search",
                    "step_result": "Fetched primary sources",
                },
            ).json()
            assert r_step["ok"] is True

            act = client.get("/api/hud/activity").json()
            assert any(w["id"] == wid and w["step_count"] == 1 for w in act["workers"])

            r_cancel = client.post(
                "/api/hud/action",
                json={"action": "cancel_worker", "worker_id": wid},
            ).json()
            assert r_cancel["ok"] is True


def test_world_view_and_dual_monitor_components_present():
    root = Path(__file__).resolve().parent.parent / "apex_ui"
    assert (root / "components" / "WorkerOrbsLayer.tsx").is_file()
    assert (root / "components" / "DualMonitorConsole.tsx").is_file()
    page_src = (root / "app" / "page.tsx").read_text(encoding="utf-8")
    assert 'params.get("view") === "console"' in page_src
    assert "DualMonitorConsole" in page_src
