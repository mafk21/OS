from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_external_chromium_hud_bypasses_system_proxy():
    source=(ROOT/'core'/'apex_bridge.py').read_text(encoding='utf-8')
    assert '"--no-proxy-server"' in source

def test_embedded_webengine_hud_bypasses_system_proxy():
    source=(ROOT/'ui.py').read_text(encoding='utf-8')
    assert 'QNetworkProxy.ProxyType.NoProxy' in source
    assert 'QTWEBENGINE_CHROMIUM_FLAGS' in source

def test_windows_uses_dedicated_browser_shell_not_unreliable_qt_webengine():
    source=(ROOT/'ui.py').read_text(encoding='utf-8')
    assert 'use_embedded_hud = os.name != "nt"' in source
    assert 'setQuitOnLastWindowClosed(False)' in source

def test_failed_embedded_hud_retries_then_falls_back_without_quitting():
    source=(ROOT/'ui.py').read_text(encoding='utf-8')
    assert 'setQuitOnLastWindowClosed(False)' in source
    assert 'web.loadFinished.connect(_hud_load_finished)' in source
    assert 'QTimer.singleShot(250, web.reload)' in source
    assert 'launch_app_window(hud_url)' in source
