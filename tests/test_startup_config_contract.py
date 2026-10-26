"""Regression for the Windows startup ImportError after restoring a saved edition.

The constructor smoke executes the real JarvisUI.__init__ body with only the
Qt/window/server boundaries stubbed; it does not require a display or API key.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from memory import config_manager as cfg

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
    monkeypatch.setattr(cfg, 'CONFIG_FILE', tmp_path / 'api_keys.json')
    return cfg.CONFIG_FILE


@pytest.mark.parametrize('data,expected', [
    ({}, '#00d4ff'),
    ({'persona': 'male'}, '#00d4ff'),
    ({'persona': 'female'}, '#ff4db8'),
    ({'voice_name': 'Aoede'}, '#ff4db8'),
    ({'voice_name': 'Kore'}, '#ff4db8'),
    ({'persona': 'female', 'ui_color': ' #A1B2C3 '}, '#a1b2c3'),
    ({'persona': 'male', 'ui_color': '#123456'}, '#123456'),
    ({'persona': 'female', 'ui_color': ''}, '#ff4db8'),
    ({'persona': 'female', 'ui_color': None}, '#ff4db8'),
    ({'persona': 'female', 'ui_color': 123}, '#ff4db8'),
    ({'persona': 'female', 'ui_color': {'bad': True}}, '#ff4db8'),
    ({'persona': 'male', 'ui_color': '#gggggg'}, '#00d4ff'),
    ({'persona': 'male', 'ui_color': '#abc'}, '#00d4ff'),
    ({'persona': 'female', 'ui_color': 'red; background: url(x)'}, '#ff4db8'),
])
def test_ui_color_is_safe_persona_aware_and_read_only(config_file, data, expected):
    config_file.write_text(json.dumps(data), encoding='utf-8')
    before = config_file.read_bytes()
    assert cfg.get_ui_color() == expected
    assert config_file.read_bytes() == before


def test_missing_or_corrupt_configuration_cannot_break_color_read(config_file):
    assert cfg.get_ui_color() == cfg.MALE_UI_COLOR
    assert not config_file.exists()
    config_file.write_text('{malformed', encoding='utf-8')
    assert cfg.get_ui_color() == cfg.MALE_UI_COLOR
    assert config_file.read_text() == '{malformed'


@pytest.mark.parametrize('persona', ['male', 'female'])
def test_color_and_choice_survive_restart_without_touching_api_keys(config_file, persona):
    cfg.save_api_keys(gemini_api_key='test-placeholder-not-a-real-key')
    cfg.save_persona(persona)
    before = config_file.read_bytes()
    assert cfg.get_ui_color() == (cfg.FEMALE_UI_COLOR if persona == 'female' else cfg.MALE_UI_COLOR)
    assert cfg.is_persona_chosen()
    assert config_file.read_bytes() == before


def test_all_production_config_from_imports_resolve():
    paths = [ROOT / 'main.py', ROOT / 'ui.py']
    for folder in ('actions', 'core', 'memory'):
        paths.extend((ROOT / folder).glob('*.py'))
    missing = []
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
            if isinstance(node, ast.ImportFrom) and node.module == 'memory.config_manager':
                missing.extend(f'{path.name}:{node.lineno}: {name.name}' for name in node.names
                               if name.name != '*' and not hasattr(cfg, name.name))
    assert not missing, 'Missing config exports: ' + ', '.join(missing)


@pytest.mark.parametrize('classic', [False, True])
@pytest.mark.parametrize('persona', ['male', 'female'])
def test_actual_startup_constructor_restores_persona(classic, persona, config_file, monkeypatch):
    from core.apex_bridge import ApexHudBridge
    cfg.save_persona(persona)
    monkeypatch.setenv('JARVIS_CLASSIC_UI', '1' if classic else '0')
    monkeypatch.setenv('JARVIS_HUD_NO_LAUNCH', '1')
    monkeypatch.setenv('JARVIS_SKIP_INTEGRATIONS_PROMPT', '1')
    monkeypatch.delenv('JARVIS_SKIP_PERSONA_PROMPT', raising=False)
    monkeypatch.setattr(ApexHudBridge, 'start', lambda _: 'http://127.0.0.1:8765')

    app = Mock()
    win = Mock(_ready=True, _overlay=None)
    win.findChildren.return_value = []
    qt_application = SimpleNamespace(instance=lambda: app)
    qt_timer = SimpleNamespace(singleShot=Mock())
    self = SimpleNamespace(enter_background_mode=Mock(), _quit_from_hud=Mock(), select_persona=Mock())
    module = ast.parse((ROOT / 'ui.py').read_text(encoding='utf-8'))
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'JarvisUI')
    constructor = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    code = ast.Module(body=[constructor], type_ignores=[])
    namespace = {'QApplication': qt_application, 'QTimer': qt_timer,
                 'MainWindow': lambda _: win, '_RootShim': lambda a: a, 'os': os, 'sys': __import__('sys')}
    exec(compile(ast.fix_missing_locations(code), str(ROOT / 'ui.py'), 'exec'), namespace)
    namespace['__init__'](self, 'face.png')
    assert self._persona_selected is True
    assert self._classic_mode is classic
    win._preview_ui_color.assert_called_once_with(cfg.get_ui_color())
    if not classic:
        assert self._apex_bridge is not None
