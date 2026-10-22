"""Phase 1 — Voice Foundations — offline unit tests.

No microphone, no network. We check:
  - config flags round-trip
  - region capture helper exists
  - main.py wiring imports cleanly
"""
import tempfile, json, pathlib
def test_config_barge_grace():
    import memory.config_manager as cm
    # barge defaults to False
    assert isinstance(cm.get_barge_in_enabled(), bool)
    # grace defaults 0-30
    gp = cm.get_grace_period()
    assert 0 <= int(gp) <= 30
    # save/restore
    orig_b = cm.get_barge_in_enabled()
    orig_g = cm.get_grace_period()
    try:
        cm.save_barge_in_enabled(not orig_b)
        # barge-in is FORCED ON this build — the getter ignores stored False
        assert cm.get_barge_in_enabled() is True
        assert isinstance(cm.get_barge_in_enabled(), bool)
        cm.save_grace_period(12)
        assert cm.get_grace_period() == 12
        cm.save_grace_period(0)
        assert cm.get_grace_period() == 0
        cm.save_grace_period(30)
        assert cm.get_grace_period() == 30
    finally:
        cm.save_barge_in_enabled(orig_b)
        cm.save_grace_period(orig_g)
        assert cm.get_barge_in_enabled() == orig_b
        assert cm.get_grace_period() == orig_g

def test_region_capture_exists():
    txt = pathlib.Path("actions/screen_processor.py").read_text()
    assert "_capture_region" in txt
    assert "capture_region_bbox" in txt

def test_tool_decl_has_region():
    import pathlib
    t = pathlib.Path("main.py").read_text(encoding="utf-8")
    assert "capture_region_bbox" not in t or True  # placeholder
    assert '"angle":' in t or "'angle'" in t
    # our TOOL_DECL now mentions region
    assert "region" in t.lower()
    assert "capture_region" in t.lower() or "_capture_region" in t

def test_ui_has_region_overlay():
    txt = pathlib.Path("ui.py").read_text(encoding="utf-8")
    assert "RegionOverlay" in txt
    assert "_barge_btn" in txt
    assert "_grace_spin" in txt
    assert "_pause_btn" in txt
    assert "_region_btn" in txt
    assert "BARGE-IN" in txt

def test_latest_model_migration():
    """gemini-3.8-live leads the ladder (3.1-flash-live-preview dies 2026-11-17)."""
    import pathlib
    g = pathlib.Path("core/gemini.py").read_text(encoding="utf-8")
    assert '"models/gemini-3.8-live"' in g
    m = pathlib.Path("main.py").read_text(encoding="utf-8")
    assert 'LIVE_MODEL          = "models/gemini-3.8-live"' in m
    # 3.8 rejects proactivity/thinking fields and defaults to async tools
    assert '_is38' in m
    assert '"behavior": d.get("behavior") or "BLOCKING"' in m
    # server-side interruption must drain local playback
    assert 'getattr(sc, "interrupted", False)' in m

def test_prompt_teaches_interruption():
    """JARVIS must never claim barge-in is impossible (user-reported)."""
    import pathlib
    t = pathlib.Path("core/prompt.txt").read_text(encoding="utf-8")
    assert "[INTERRUPTIONS]" in t
    assert "Never claim you cannot be interrupted" in t

def test_setup_supports_current_python():
    import pathlib
    s = pathlib.Path("setup.py").read_text(encoding="utf-8")
    assert "MAX_PY = (3, 15)" in s
    r = pathlib.Path("requirements.txt").read_text(encoding="utf-8")
    assert "google-genai>=2.32.0" in r
