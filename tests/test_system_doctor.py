from __future__ import annotations

import json
from pathlib import Path

from actions import diagnostics
from core import system_doctor


def test_installation_identity_is_stable_and_checkout_specific(monkeypatch, tmp_path):
    root = tmp_path / "JARVIS current"
    root.mkdir()
    (root / "main.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(system_doctor, "ROOT", root)
    monkeypatch.setattr(system_doctor, "_revision", lambda: "abc123")

    first = system_doctor.installation_identity()
    second = system_doctor.installation_identity()

    assert first.installation_id == second.installation_id
    assert len(first.installation_id) == 16
    assert first.root == str(root.resolve())
    assert first.entrypoint == str((root / "main.py").resolve())
    assert first.revision == "abc123"


def test_doctor_contains_failed_checks_and_never_aborts(monkeypatch):
    monkeypatch.setattr(system_doctor, "installation_identity", lambda: system_doctor.InstallationIdentity(
        installation_id="install", root="/safe", executable="/python", entrypoint="/safe/main.py",
        install_type="source", revision="rev", platform="Test", python="3.12.0",
    ))

    def broken():
        raise RuntimeError("private detail")

    report = system_doctor.run_doctor([broken])

    assert report["overall"] == "error"
    assert report["counts"] == {"ok": 0, "warning": 0, "error": 1}
    assert report["results"][0]["summary"] == "The health check failed safely."
    assert "private detail" not in json.dumps(report)


def test_configuration_check_does_not_return_secret_content(monkeypatch, tmp_path):
    config = tmp_path / "config"
    config.mkdir()
    secret = "provider-secret-value"
    (config / "api_keys.json").write_text(json.dumps({"api_key": secret}), encoding="utf-8")
    monkeypatch.setattr(system_doctor, "ROOT", tmp_path)

    result = system_doctor._config_check()

    assert result.status == "ok"
    assert secret not in json.dumps(result.to_dict())


def test_system_doctor_is_available_through_existing_diagnostics_tool(monkeypatch):
    report = {
        "overall": "warning",
        "counts": {"ok": 1, "warning": 1, "error": 0},
        "installation": {
            "installation_id": "current-install", "install_type": "git", "revision": "abc",
            "python": "3.12.0", "platform": "Windows",
        },
        "results": [{
            "check": "shortcut", "status": "warning", "summary": "No shortcut.",
            "evidence": "", "remediation": "Create it from Settings.",
        }],
    }
    monkeypatch.setattr(system_doctor, "run_doctor", lambda: report)

    output = diagnostics.diagnostics_check({"action": "system"})

    assert "current-install" in output
    assert "Create it from Settings" in output
    assert "WARNING" in output


def test_api_key_check_never_discloses_key_prefixes(monkeypatch):
    import memory.config_manager as config
    gemini = "gemini-private-material"
    openai = "openai-private-material"
    monkeypatch.setattr(config, "get_gemini_key", lambda: gemini)
    monkeypatch.setattr(config, "get_openai_key", lambda: openai)
    monkeypatch.setattr(config, "get_anthropic_key", lambda: None)

    status, detail = diagnostics._check_api_key()

    assert status == "ok"
    assert gemini[:6] not in detail
    assert openai[:7] not in detail
    assert detail == "Gemini configured | OpenAI configured"
