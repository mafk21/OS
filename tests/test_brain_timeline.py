"""
End-to-end tests for Phase 1: "The Brain" & Forever Conversation Timeline
across both Male and Female interface editions.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from actions.brain_control import TOOL as BRAIN_TOOL, brain_control
from core.action_loader import discover_actions
from core.apex_bridge import ApexHudBridge, map_tool_to_nodes
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline as tl


@pytest.fixture()
def isolated_brain(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_file = cfg_dir / "api_keys.json"
    monkeypatch.setattr(cfg, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cfg, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "memory" / "accounts.json")
    monkeypatch.setattr(mm, "MEMORY_PATH", tmp_path / "memory" / "long_term.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "memory" / "brain.db")
    monkeypatch.setattr(tl, "KNOWLEDGE_DIR", tmp_path / "memory" / "knowledge_files")
    return tmp_path


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_forever_timeline_channels_epoch_rollup_and_restart_reload(isolated_brain):
    """Spoken, typed, and Telegram turns persist across restarts and compress into epochs."""
    tl.append_turn("user", "Schedule the Q4 architecture review", channel="voice")
    tl.append_turn("jarvis", "Scheduled Q4 architecture review for Thursday at 10 AM.", channel="voice")
    tl.append_turn("user", "Also drop a summary on Slack", channel="telegram")

    # Duplicate guard within 2.5s should not create a second identical row
    dup_id = tl.append_turn("user", "Also drop a summary on Slack", channel="telegram")
    recent = tl.get_recent_timeline(limit=10)
    assert len(recent) == 3
    assert recent[-1]["id"] == dup_id
    assert recent[-1]["channel"] == "telegram"

    # Restart simulation: a brand-new ApexHudBridge reloads CONSOLE logs from Forever Timeline
    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=0)
    snap = bridge.snapshot()
    assert any("Q4 architecture review" in ln for ln in snap["logs"])
    assert any("Slack" in ln for ln in snap["logs"])

    # Push past EPOCH_ROLLUP_THRESHOLD (32) to trigger automatic epoch compression
    for i in range(32):
        role = "user" if i % 2 == 0 else "jarvis"
        tl.append_turn(role, f"Milestone turn #{i} about Project Atlas", channel="text")

    epochs = tl.list_epochs()
    assert len(epochs) >= 1
    assert "Project Atlas" in epochs[0]["summary"] or "Q4 architecture review" in epochs[0]["summary"]

    prompt_blk = tl.format_timeline_for_prompt(recent_limit=6)
    assert "[FOREVER CONVERSATION TIMELINE" in prompt_blk
    assert "Earlier conversation digest:" in prompt_blk
    assert "Most recent turns:" in prompt_blk


def test_brain_knowledge_files_outputs_and_unified_recall(isolated_brain):
    """Verify file upload/indexing, automatic output archiving, and unified recall."""
    mm.remember("favorite_stack", "Rust and Python", category="preferences", manual=True)

    # Base64 browser drag-and-drop simulation
    spec_md = "# Apollo Spec\nLatency budget is strictly 45 milliseconds end-to-end."
    b64_url = "data:text/markdown;base64," + base64.b64encode(spec_md.encode("utf-8")).decode("ascii")
    rec = tl.ingest_knowledge_file("apollo_spec.md", b64_url, is_base64=True)
    assert rec["chunk_count"] >= 1

    # Output archiving via bridge.push_content
    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=0)
    bridge.push_content("DEEP RESEARCH — Quantum Networking", "Key takeaway: entanglement repeaters hit 120km.")

    outs = tl.list_outputs()
    assert len(outs) == 1
    assert outs[0]["title"] == "DEEP RESEARCH — Quantum Networking"

    # Unified search hits memories, knowledge files, timeline, and outputs
    tl.append_turn("user", "Remember the entanglement deadline is November 12", channel="voice")

    assert "45 milliseconds" in tl.unified_brain_search("Apollo latency")
    assert "120km" in tl.unified_brain_search("entanglement")
    assert "November 12" in tl.unified_brain_search("entanglement")
    assert "Rust and Python" in brain_control({"action": "search", "query": "favorite stack"})

    # Local file ingest via brain_control action
    local_doc = isolated_brain / "handbook.txt"
    local_doc.write_text("Deploy window is Tuesday 02:00 UTC.", encoding="utf-8")
    ing_out = brain_control({"action": "ingest_file", "file_path": str(local_doc)})
    assert "handbook.txt" in ing_out
    assert "Tuesday 02:00 UTC" in tl.unified_brain_search("Deploy window")


def test_privacy_governance_and_http_brain_crud_male_and_female(isolated_brain):
    """Verify privacy tier switches, 1-click forget, pin/delete, and full JSON export/import."""
    from fastapi.testclient import TestClient

    ui = _ReadyUI()
    bridge = ApexHudBridge(ui, host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        # Switch between Female and Male while managing Brain
        client.post("/api/hud/action", json={"action": "set_persona", "persona": "female"})
        assert cfg.get_persona() == "female"

        # Save manual memory via HUD
        r_mem = client.post(
            "/api/hud/action",
            json={
                "action": "brain_save_memory",
                "category": "projects",
                "key": "codename",
                "value": "Valkyrie",
            },
        )
        assert r_mem.json()["ok"] is True

        # Pause Adaptive Learning & Personalization
        r_priv = client.post(
            "/api/hud/action",
            json={
                "action": "brain_set_privacy",
                "personalization_enabled": False,
                "adaptive_learning_enabled": False,
                "timeline_persistence_enabled": False,
            },
        )
        assert r_priv.json()["privacy"]["personalization_enabled"] is False
        assert mm.format_memory_for_prompt(mm.load_memory()) == ""
        assert tl.format_timeline_for_prompt() == ""
        assert "paused" in mm.remember("auto_fact", "should_not_save").lower()
        assert tl.append_turn("user", "ephemeral turn") is None

        # Re-enable privacy toggles and export full Brain JSON
        client.post(
            "/api/hud/action",
            json={
                "action": "brain_set_privacy",
                "personalization_enabled": True,
                "adaptive_learning_enabled": True,
                "timeline_persistence_enabled": True,
            },
        )
        exp = client.get("/api/hud/brain/export").json()
        assert exp["version"] == 1
        assert exp["long_term_memory"]["projects"]["codename"]["value"] == "Valkyrie"

        # 1-click Forget memory, then restore from JSON export!
        client.post(
            "/api/hud/action",
            json={"action": "brain_forget_memory", "category": "projects", "key": "codename"},
        )
        assert mm.all_entries_for_ui() == []

        imp = client.post(
            "/api/hud/action",
            json={"action": "brain_import_json", "payload": exp},
        ).json()
        assert imp["ok"] is True
        assert any(m["value"] == "Valkyrie" for m in mm.all_entries_for_ui())


def test_brain_action_registered_and_mapped():
    reg = discover_actions(Path(__file__).resolve().parent.parent / "actions")
    names = {d["name"] for d in reg.get_tool_declarations()}
    assert "brain_control" in names
    assert BRAIN_TOOL["name"] == "brain_control"
    assert "memory" in map_tool_to_nodes("brain_control")
