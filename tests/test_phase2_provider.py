"""Phase 2 — Offline & Multi-Provider — offline unit tests."""
import pathlib

def test_config_provider_roundtrip():
    import memory.config_manager as cm
    orig = cm.get_provider()
    try:
        cm.save_provider("local")
        assert cm.get_provider() == "local"
        cm.save_provider("openai")
        assert cm.get_provider() == "openai"
        cm.save_provider("auto")
        assert cm.get_provider() == "auto"
        cm.save_provider("gemini")
        assert cm.get_provider() == "gemini"
        # invalid collapses to auto
        cm.save_provider("invalid_xyz")
        assert cm.get_provider() == "auto"
    finally:
        cm.save_provider(orig)

def test_config_offline_roundtrip():
    import memory.config_manager as cm
    orig = cm.get_offline_fallback_enabled()
    try:
        cm.save_offline_fallback_enabled(False)
        assert cm.get_offline_fallback_enabled() is False
        cm.save_offline_fallback_enabled(True)
        assert cm.get_offline_fallback_enabled() is True
    finally:
        cm.save_offline_fallback_enabled(orig)

def test_config_local_voice_flags():
    import memory.config_manager as cm
    orig_stt = cm.get_local_stt_enabled()
    orig_tts = cm.get_local_tts_enabled()
    try:
        cm.save_local_stt_enabled(True)
        assert cm.get_local_stt_enabled() is True
        cm.save_local_tts_enabled(True)
        assert cm.get_local_tts_enabled() is True
        cm.save_local_stt_enabled(False)
        cm.save_local_tts_enabled(False)
        assert cm.get_local_stt_enabled() is False
        assert cm.get_local_tts_enabled() is False
    finally:
        cm.save_local_stt_enabled(orig_stt)
        cm.save_local_tts_enabled(orig_tts)

def test_provider_module_exists():
    import core.provider as prov
    assert hasattr(prov, "call")
    assert hasattr(prov, "text")
    assert hasattr(prov, "as_json")
    assert hasattr(prov, "get_provider")
    assert hasattr(prov, "get_offline_fallback_enabled")
    # Should not crash without keys
    cfg = prov.get_openai_cfg()
    assert isinstance(cfg, dict)

def test_local_voice_probe_no_crash():
    import core.local_voice as lv
    caps = lv.probe_capabilities()
    assert isinstance(caps, dict)
    assert "stt" in caps
    assert "tts" in caps
    assert "details" in caps

def test_ui_has_offline_controls():
    txt = pathlib.Path("ui.py").read_text(encoding="utf-8")
    assert "PROVIDER" in txt
    assert "OFFLINE FALLBACK" in txt
    assert "LOCAL STT" in txt
    assert "LOCAL TTS" in txt
    assert "set_offline" in txt

def test_main_offline_wiring():
    txt = pathlib.Path("main.py").read_text(encoding="utf-8")
    assert "_run_offline_mode" in txt
    assert "_exit_offline_mode" in txt
    assert "_offline_mode" in txt
    assert "get_offline_fallback_enabled" in txt
