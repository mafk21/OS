from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_external_chromium_hud_bypasses_system_proxy():
    source=(ROOT/'core'/'apex_bridge.py').read_text(encoding='utf-8')
    assert '"--no-proxy-server"' in source

def test_embedded_webengine_hud_bypasses_system_proxy():
    source=(ROOT/'ui.py').read_text(encoding='utf-8')
    assert 'QNetworkProxy.ProxyType.NoProxy' in source
    assert 'QTWEBENGINE_CHROMIUM_FLAGS' in source
