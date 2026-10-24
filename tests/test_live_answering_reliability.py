"""
Regression tests ensuring JARVIS ALWAYS connects and answers both voice & typed
messages (no 1007 empty-OBJECT tool schema rejections, v1beta behavior stripping,
Vault-encrypted API key reading, early text buffering, and Live/REST text reply).
"""

from __future__ import annotations

import ast
import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from actions.companion_os import companion_os
from actions.custom_tools_runner import _parse_json_obj as custom_parse_json
from core import automations, companions, security_vault
from core.action_loader import discover_actions, sanitize_tool_parameters
from core.plugin_loader import discover_plugins
from memory import accounts
from memory import config_manager as cfg
from memory import timeline as tl


def _load_main_with_mock_audio():
    if "main" in sys.modules:
        return sys.modules["main"]
    sys.modules.setdefault("sounddevice", MagicMock())
    import main as m
    return m


def _assert_gemini_safe_schema(tool_name: str, path: str, sch: dict, *, is_root: bool = False):
    assert isinstance(sch, dict), f"{tool_name} {path}: schema must be dict"
    stype = sch.get("type")
    if stype == "OBJECT":
        props = sch.get("properties")
        assert isinstance(props, dict), f"{tool_name} {path}: OBJECT missing properties dict"
        if not is_root:
            assert len(props) > 0, (
                f"{tool_name} {path}: nested OBJECT has empty properties "
                "(rejected by Gemini Live with WebSocket 1007 INVALID_ARGUMENT)"
            )
        for k, v in props.items():
            _assert_gemini_safe_schema(tool_name, f"{path}.{k}", v, is_root=False)
        for req_k in sch.get("required") or []:
            assert req_k in props, f"{tool_name} {path}: required key '{req_k}' missing from properties"
    elif stype == "ARRAY":
        items = sch.get("items")
        assert isinstance(items, dict), f"{tool_name} {path}: ARRAY missing items schema"
        _assert_gemini_safe_schema(tool_name, f"{path}[]", items, is_root=False)
    else:
        assert stype in ("STRING", "INTEGER", "BOOLEAN", "NUMBER"), (
            f"{tool_name} {path}: unsupported type {stype!r}"
        )


def test_zero_empty_nested_object_schemas_across_all_tools():
    root = Path(__file__).resolve().parent.parent
    reg = discover_actions(root / "actions", logger=lambda _: None)
    plug = discover_plugins(root / "plugins", core_tool_names=reg.names(), logger=lambda _: None)

    main_src = (root / "main.py").read_text(encoding="utf-8")
    tree = ast.parse(main_src)
    inline_decls = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TOOL_DECLARATIONS":
                    inline_decls = ast.literal_eval(node.value)

    all_decls = inline_decls + reg.get_tool_declarations() + plug.get_tool_declarations()
    assert len(all_decls) >= 55

    for decl in all_decls:
        params = sanitize_tool_parameters(decl.get("parameters", {}), is_root=True)
        _assert_gemini_safe_schema(decl["name"], "parameters", params, is_root=True)
        # Also verify raw action declarations already pass without needing fallback repair
        _assert_gemini_safe_schema(decl["name"], "raw_parameters", decl["parameters"], is_root=True)


def test_sanitize_tool_parameters_repairs_broken_plugin_schema():
    broken = {
        "type": "OBJECT",
        "properties": {
            "payload": {"type": "OBJECT", "description": "Arbitrary JSON"},
            "tags": {"type": "ARRAY"},
        },
        "required": ["payload", "nonexistent_field"],
    }
    fixed = sanitize_tool_parameters(broken, is_root=True)
    _assert_gemini_safe_schema("broken_plugin", "parameters", fixed, is_root=True)
    assert fixed["properties"]["payload"]["type"] == "STRING"
    assert fixed["properties"]["tags"]["items"]["type"] == "STRING"
    assert fixed["required"] == ["payload"]


def test_companion_os_and_custom_connector_accept_json_string_and_dict(tmp_path, monkeypatch):
    monkeypatch.setattr(automations, "AUTOMATIONS_FILE", tmp_path / "automations.json")
    msg = companion_os(
        {
            "action": "automation_save",
            "name": "JSON String Test",
            "schedule_type": "interval",
            "every_minutes": 30,
            "tool": "cloud_integrations",
            "tool_params": '{"action": "status"}',
        }
    )
    assert "JSON String Test" in msg
    saved = automations.list_automations()
    assert saved[0]["steps"][0]["params"] == {"action": "status"}
    assert custom_parse_json('{"hello": "world"}') == {"hello": "world"}
    assert custom_parse_json({"hello": "dict"}) == {"hello": "dict"}


def test_get_api_key_decrypts_vault_secret(tmp_path, monkeypatch):
    m = _load_main_with_mock_audio()
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(m, "API_CONFIG_PATH", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(security_vault, "VAULT_KEY_FILE", tmp_path / "config" / ".vault.key")

    cfg.ensure_config_dir()
    enc = security_vault.encrypt_secret("AIzaSyVaultPlaintextKey999999")
    (tmp_path / "config" / "api_keys.json").write_text(
        json.dumps({"gemini_api_key": enc, "vault_encrypt_api_keys": True}),
        encoding="utf-8",
    )
    assert m._get_api_key() == "AIzaSyVaultPlaintextKey999999"


def test_build_config_strips_behavior_on_v1beta_fallback(tmp_path, monkeypatch):
    m = _load_main_with_mock_audio()
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(accounts, "ACCOUNTS_FILE", tmp_path / "accounts.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(companions, "COMPANIONS_FILE", tmp_path / "companions.json")

    dummy_ui = SimpleNamespace(
        _win=SimpleNamespace(_ready=True, _muted=False),
        muted=False,
        current_file=None,
        _apex_bridge=MagicMock(),
        write_log=lambda *a, **k: None,
        set_state=lambda *a, **k: None,
    )
    jl = m.JarvisLive(dummy_ui)

    # On older model + _enhanced_live=False (v1beta), behavior must be stripped
    monkeypatch.setattr(m, "LIVE_MODEL", "models/gemini-2.5-flash-native-audio-preview-12-2025")
    jl._enhanced_live = False
    c_v1beta = jl._build_config()
    fds = c_v1beta.tools[0].function_declarations
    assert all(getattr(fd, "behavior", None) is None for fd in fds)


def test_typed_command_auto_wakes_and_uses_fallback_when_no_live_session(tmp_path, monkeypatch):
    m = _load_main_with_mock_audio()
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(companions, "COMPANIONS_FILE", tmp_path / "companions.json")

    logged: list[str] = []
    states: list[str] = []
    dummy_ui = SimpleNamespace(
        _win=SimpleNamespace(_ready=True, _muted=False),
        muted=False,
        current_file=None,
        _apex_bridge=MagicMock(),
        write_log=lambda msg: logged.append(msg),
        set_state=lambda st: states.append(st),
    )
    jl = m.JarvisLive(dummy_ui)
    jl._wake_enabled = True
    jl._awake = False

    # Avoid 6s wait in unit test by patching time.sleep inside main
    monkeypatch.setattr(m.time, "sleep", lambda _s: None)
    monkeypatch.setattr(m._gemini, "text", lambda prompt, *a, **k: f"Echo: {prompt}")

    jl._on_text_command("Hello there!")
    assert jl._awake is True
    assert any("JARVIS: Echo: Hello there!" in ln for ln in logged)
    assert states[-1] == "LISTENING"


@pytest.mark.asyncio
async def test_typed_command_delivers_to_live_session_when_connected(tmp_path, monkeypatch):
    m = _load_main_with_mock_audio()
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(tl, "DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(companions, "COMPANIONS_FILE", tmp_path / "companions.json")

    dummy_ui = SimpleNamespace(
        _win=SimpleNamespace(_ready=True, _muted=False),
        muted=False,
        current_file=None,
        _apex_bridge=MagicMock(),
        write_log=lambda *a, **k: None,
        set_state=lambda *a, **k: None,
    )
    jl = m.JarvisLive(dummy_ui)
    jl._loop = asyncio.get_running_loop()
    mock_session = SimpleNamespace(send_client_content=AsyncMock())
    jl.session = mock_session

    await asyncio.to_thread(jl._on_text_command, "Status report")
    mock_session.send_client_content.assert_awaited_once()
