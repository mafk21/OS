from __future__ import annotations

import json

import pytest

from core import provider
from core import security_vault as vault
from memory import config_manager as cfg


@pytest.fixture()
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config" / "api_keys.json")
    monkeypatch.setattr(vault, "VAULT_KEY_FILE", tmp_path / "config" / ".vault.key")
    cfg.invalidate_config_cache()
    return tmp_path


def test_anthropic_key_is_encrypted_and_configures_app(isolated_config):
    cfg.save_anthropic_cfg("sk-ant-owner-secret-value", "claude-test-model")
    raw = cfg.CONFIG_FILE.read_text(encoding="utf-8")
    assert "sk-ant-owner-secret-value" not in raw
    assert "enc:v1:" in raw
    assert cfg.get_anthropic_key() == "sk-ant-owner-secret-value"
    assert cfg.get_anthropic_cfg()["model"] == "claude-test-model"
    assert cfg.is_configured() is True


def test_anthropic_native_messages_request(isolated_config, monkeypatch):
    cfg.save_anthropic_cfg("sk-ant-owner-secret-value", "claude-test-model")
    cfg.save_provider("anthropic")
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"content": [{"type": "text", "text": "Claude response"}]}

    def fake_post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return Response()

    import httpx
    monkeypatch.setattr(httpx, "post", fake_post)
    result = provider.text(
        "Explain this safely",
        config={"system_instruction": "You are JARVIS."},
        timeout_ms=5000,
    )

    assert result == "Claude response"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "sk-ant-owner-secret-value"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert captured["json"]["model"] == "claude-test-model"
    assert captured["json"]["system"] == "You are JARVIS."
    assert captured["json"]["messages"][0]["content"] == "Explain this safely"


def test_anthropic_error_does_not_log_key(isolated_config, monkeypatch, capsys):
    secret = "sk-ant-never-print-this-value"
    cfg.save_anthropic_cfg(secret, "claude-test-model")
    cfg.save_provider("anthropic")

    import httpx
    def fail(*_args, **_kwargs):
        raise httpx.HTTPError(f"request failed while using {secret}")
    monkeypatch.setattr(httpx, "post", fail)

    assert provider.text("hello", default="fallback") == "fallback"
    assert secret not in capsys.readouterr().out


def test_provider_allowlist_includes_anthropic(isolated_config):
    cfg.save_provider("anthropic")
    assert cfg.get_provider() == "anthropic"
