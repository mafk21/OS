"""Tests — 11 Default Ship-With Skills + Improved Backing Actions."""

from pathlib import Path
from unittest.mock import patch

import actions.computer_use as cu
import actions.diagnostics as diag
import actions.github_automation as gh_auto
import actions.productivity_routines as routines
import actions.rag_docs as rag
import actions.weather_report as wx
from core.skill_loader import _DESC_IN_LISTING, discover_skills

EXPECTED_DEFAULT_SKILLS = {
    "code-ship",
    "daily-briefing",
    "deep-research",
    "focus-mode",
    "gui-autopilot",
    "meeting-copilot",
    "safe-file-organizer",
    "second-brain",
    "system-doctor",
    "workspace-comms",
    "topic-learning",
}


# ── Default SKILL.md Playbooks ─────────────────────────────────────────

def test_all_default_skills_discover_cleanly():
    logs: list[str] = []
    reg = discover_skills(Path("skills"), logger=logs.append)
    assert reg.names() == EXPECTED_DEFAULT_SKILLS
    assert len(reg) == 11
    assert not any("rejected" in line.lower() for line in logs)


def test_every_default_skill_fits_listing_and_has_full_structure():
    reg = discover_skills(Path("skills"), logger=lambda _: None)
    listing = reg.get_listing()

    for name in sorted(EXPECTED_DEFAULT_SKILLS):
        rec = reg._skills[name]
        # Every trigger description fits cleanly inside Level-1 prompt cap
        assert 20 <= len(rec.description) <= _DESC_IN_LISTING, (
            f"{name} description length {len(rec.description)} exceeds {_DESC_IN_LISTING}"
        )
        assert f"- {name}: {rec.description}" in listing

        body = reg.read(name)
        for section in ("## When to use", "## Procedure", "## Pitfalls", "## Verification"):
            assert section in body, f"{name} missing {section}"


def test_bundled_level3_references_readable():
    reg = discover_skills(Path("skills"), logger=lambda _: None)
    rubric = reg.read("deep-research", "references/source-rubric.md")
    assert "Primary over secondary" in rubric
    checklist = reg.read("code-ship", "references/pr-checklist.md")
    assert "Zero secrets" in checklist


# ── Improved Existing Backing Actions ─────────────────────────────────────

def test_computer_use_resolves_cached_som_element_center():
    cu.clear_last_id_map()
    try:
        cu._LAST_ID_MAP["1"] = {"x": 100, "y": 200, "width": 60, "height": 40}
        assert cu.get_last_id_map()["1"]["x"] == 100
        assert cu._resolve_element_center("1") == (130, 220)
        # Click by cached ID routes to center coordinates (graceful without PyAutoGUI)
        res = cu.computer_use({"action": "click_by_id", "element_id": "1"})
        assert "som_capture first" not in res
    finally:
        cu.clear_last_id_map()


def test_weather_report_open_meteo_parsing():
    fake_geo = {"results": [{"name": "Riyadh", "country": "Saudi Arabia", "latitude": 24.7, "longitude": 46.7}]}
    fake_wx = {
        "current": {
            "temperature_2m": 31.5,
            "apparent_temperature": 30.0,
            "relative_humidity_2m": 22,
            "weather_code": 0,
            "wind_speed_10m": 12.4,
        },
        "daily": {
            "time": ["2026-10-22", "2026-10-23"],
            "temperature_2m_max": [33.0, 32.0],
            "temperature_2m_min": [20.0, 19.5],
            "weather_code": [0, 1],
        },
    }
    responses = [fake_geo, fake_wx]
    with patch.object(wx, "_http_json", side_effect=lambda *a, **k: responses.pop(0)):
        out = wx.weather_action({"city": "Riyadh"})
    assert "Riyadh, Saudi Arabia" in out
    assert "Clear sky" in out
    assert "31.5°C" in out
    assert "3-day outlook:" in out


def test_github_automation_local_git_status_and_diff():
    st = gh_auto.github_automation({"action": "git_status"})
    assert "##" in st or "Clean" in st
    df = gh_auto.github_automation({"action": "git_diff"})
    assert isinstance(df, str) and len(df) > 0


def test_rag_docs_multi_ext_index_and_ranked_search(tmp_path, monkeypatch):
    monkeypatch.setattr(rag, "INDEX", tmp_path / "rag_index.json")
    docs = tmp_path / "vault"
    docs.mkdir()
    (docs / "architecture.md").write_text("Gemini Live session recycle handles GoAway frames.", encoding="utf-8")
    (docs / "helper.py").write_text("def compute_viseme_formant(): return 50", encoding="utf-8")

    idx_out = rag.rag_docs({"action": "index", "path": str(docs)})
    assert "2 files" in idx_out

    hit = rag.rag_docs({"action": "search", "query": "GoAway frames"})
    assert "architecture.md" in hit

    py_hit = rag.rag_docs({"action": "search", "query": "compute_viseme_formant"})
    assert "helper.py" in py_hit


def test_diagnostics_targeted_skills_and_storage():
    out = diag.diagnostics_check({"action": "storage"})
    assert "storage: ok" in out or "GB free" in out
    assert "11 active skill(s)" in out


def test_routines_run_renders_steps():
    routines.manage_routines({
        "action": "add",
        "name": "TempFocus",
        "trigger": "temp focus trigger",
        "steps": ["50m focus timer", "review architecture notes"],
    })
    try:
        out = routines.manage_routines({"action": "run", "trigger": "temp focus trigger", "execute": False})
        assert "TempFocus" in out
        assert "50m focus timer" in out
    finally:
        routines.manage_routines({"action": "delete", "name": "TempFocus"})


def test_removed_video_generator_is_not_discoverable():
    from core.action_loader import discover_actions
    skills = discover_skills(Path("skills"), logger=lambda _: None)
    actions = discover_actions(Path("actions"), logger=lambda _: None)
    assert "brag" not in skills.names()
    assert not actions.has("brag_video")
    for removed in ("skills/brag", "actions/brag_video.py", "core/brag_video.py",
                    "core/brag_full.py", "tools/brag-runtime"):
        assert not Path(removed).exists()
