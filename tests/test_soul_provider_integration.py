"""Phase 5 Soul lifecycle, rollback flag, and provider-path integration tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.soul import COMPANIONS_IMPORT_ID, SoulService, SoulStore
from core.soul import service as soul_service
from memory import config_manager as cfg

NOW = "2026-10-27T12:00:00+03:00"


@pytest.fixture()
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    cfg.invalidate_config_cache()
    yield tmp_path
    cfg.invalidate_config_cache()
    soul_service.reset_default_service_for_tests()


def test_soul_feature_flag_defaults_off_and_persists(isolated_config) -> None:
    assert cfg.get_soul_enabled() is False
    cfg.save_soul_enabled(True)
    assert cfg.get_soul_enabled() is True
    cfg.save_soul_enabled(False)
    assert cfg.get_soul_enabled() is False


def test_disabled_runtime_context_does_not_initialize_store(isolated_config, tmp_path, monkeypatch) -> None:
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "memory" / "companions.json")
    monkeypatch.setattr(soul_service, "_DEFAULT_SERVICE", service)
    assert soul_service.build_runtime_context() == ""
    assert not store.path.exists()


def test_enabled_runtime_context_initializes_male_soul_and_respects_privacy(isolated_config, tmp_path, monkeypatch) -> None:
    cfg.save_soul_enabled(True)
    cfg.save_personalization_enabled(False)
    cfg.save_assistant_config("JARVIS", "Alex")
    cfg.save_persona("male", voice_name="Charon")
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "memory" / "companions.json")
    monkeypatch.setattr(soul_service, "_DEFAULT_SERVICE", service)
    text = soul_service.build_runtime_context()
    assert text.startswith("[CONSTITUTION]")
    assert "Brother-Guardian" in text
    assert "Edition: male" in text
    assert "commanding" in text
    assert '"Alex"' in text
    assert "Personalization is disabled" in text
    assert store.path.exists()


def test_service_imports_existing_companion_preferences_once(tmp_path) -> None:
    companions = tmp_path / "memory" / "companions.json"
    companions.parent.mkdir(parents=True)
    companions.write_text(json.dumps({
        "active_companion_id": "default",
        "interview": {"tone": "Concise & Tactical"},
        "learned_rules": [{"id": "rule-1", "rule": "Call me bro.", "ts": "2026-10-20 10:00"}],
        "companions": [], "theme": {"preset": "default"},
    }), encoding="utf-8")
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    first_service = SoulService(store, companions_path=companions)
    first = first_service.initialize()
    assert COMPANIONS_IMPORT_ID in first.completed_migrations
    assert len(first.learned_traits) == 2
    assert first.revision == 1

    second_service = SoulService(store, companions_path=companions)
    second = second_service.initialize()
    assert second == first
    assert len(second.learned_traits) == 2
    migration_events = [event for event in store.read_events() if event.event == "soul.migrated"]
    assert len(migration_events) == 1


def test_malformed_companion_file_cannot_block_soul_startup(tmp_path) -> None:
    companions = tmp_path / "memory" / "companions.json"
    companions.parent.mkdir(parents=True)
    companions.write_text("not-json", encoding="utf-8")
    messages: list[str] = []
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=companions, logger=messages.append)
    state = service.initialize()
    assert state.identity.archetype == "Brother-Guardian"
    assert COMPANIONS_IMPORT_ID not in state.completed_migrations
    assert service.degraded_reason is not None
    assert messages


def test_flag_rollback_preserves_state_for_reenable(isolated_config, tmp_path, monkeypatch) -> None:
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "memory" / "companions.json")
    monkeypatch.setattr(soul_service, "_DEFAULT_SERVICE", service)
    cfg.save_soul_enabled(True)
    first = soul_service.build_runtime_context()
    saved = store.path.read_bytes()
    cfg.save_soul_enabled(False)
    assert soul_service.build_runtime_context() == ""
    assert store.path.read_bytes() == saved
    cfg.save_soul_enabled(True)
    assert soul_service.build_runtime_context() == first


def test_runtime_context_failure_returns_empty_for_immediate_rollback(isolated_config, monkeypatch) -> None:
    cfg.save_soul_enabled(True)

    class BrokenService:
        def build_context(self, _inputs):
            raise OSError("disk unavailable")

    monkeypatch.setattr(soul_service, "get_default_service", lambda: BrokenService())
    assert soul_service.build_runtime_context() == ""


def test_telegram_sends_soul_as_system_instruction_not_user_text(monkeypatch, tmp_path) -> None:
    from core import provider, telegram_bot
    from memory import memory_manager, timeline

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(memory_manager, "format_memory_for_prompt", lambda _memory: "")
    monkeypatch.setattr(timeline, "format_timeline_for_prompt", lambda recent_limit=4: "")
    monkeypatch.setattr(timeline, "append_turn", lambda *args, **kwargs: None)
    captured = {}

    def fake_text(contents, **kwargs):
        captured["contents"] = contents
        captured.update(kwargs)
        return "Got it, bro."

    monkeypatch.setattr(provider, "text", fake_text)
    monkeypatch.setattr(soul_service, "build_runtime_context", lambda: "[CONSTITUTION]\nSOUL-MARKER")
    reply = telegram_bot.handle_inbound("Keep me accountable", user_id=77)
    assert reply == "Got it, bro."
    assert captured["contents"] == "Keep me accountable"
    system = captured["config"]["system_instruction"]
    assert system.startswith("[CONSTITUTION]\nSOUL-MARKER")
    assert "Telegram" in system
    assert "Keep me accountable" not in system


def test_openai_live_rest_and_local_adapters_preserve_canonical_system_context(monkeypatch) -> None:
    from types import SimpleNamespace
    from core import llm_client, openai_compat, openai_live, provider

    soul = "[CONSTITUTION]\nSOUL-PROVIDER-MARKER"
    extracted, _tools = openai_live.extract_live_instructions_and_tools(
        SimpleNamespace(system_instruction=soul, tools=[])
    )
    assert extracted == soul
    assert openai_compat._extract_config_options({"system_instruction": soul})["system"] == soul

    captured = {}

    def fake_call(messages, timeout):
        captured["messages"] = messages
        captured["timeout"] = timeout
        return {"content": "local reply"}

    monkeypatch.setattr(llm_client, "call_llm", fake_call)
    response = provider._local_call("hello", "fast", {"system_instruction": soul}, 5_000)
    assert response.text == "local reply"
    assert captured["messages"][0] == {"role": "system", "content": soul}
    assert captured["messages"][1]["role"] == "user"


def test_main_and_telegram_source_use_canonical_context_with_legacy_fallback() -> None:
    main_source = Path("main.py").read_text(encoding="utf-8")
    telegram_source = Path("core/telegram_bot.py").read_text(encoding="utf-8")
    assert "soul_ctx if soul_ctx else identity_ctx" in main_source
    assert 'system_prompt = soul_ctx + "\\n\\n" + system_prompt' in main_source
    assert "config={\"system_instruction\": sys_hint}" in telegram_source
    assert "build_runtime_context" in telegram_source
