from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import system_repair


def test_unknown_repair_is_rejected_without_execution(monkeypatch):
    called = []
    monkeypatch.setattr(system_repair.confirm, "request", lambda *args: called.append(args))

    message = system_repair.request_repair("run-any-command")

    assert "not supported" in message
    assert called == []
    with pytest.raises(ValueError, match="Unsupported"):
        system_repair.execute_repair("run-any-command")


def test_repair_is_staged_behind_nonforgeable_confirmation(monkeypatch):
    captured = {}
    def fake_request(key, title, detail, run):
        captured.update(key=key, title=title, detail=detail, run=run)
        return "[CONFIRMATION_PENDING] staged"
    monkeypatch.setattr(system_repair.confirm, "request", fake_request)

    message = system_repair.request_repair("shortcut")

    assert message.startswith("[CONFIRMATION_PENDING]")
    assert captured["key"] == "system-repair-shortcut"
    assert callable(captured["run"])


def test_apex_repair_endpoint_only_stages_confirmation(monkeypatch):
    from core.apex_bridge import ApexHudBridge
    monkeypatch.setattr(system_repair, "request_repair", lambda repair: "[CONFIRMATION_PENDING] " + repair)

    result = ApexHudBridge(None, port=0).handle_action({
        "action": "system_doctor", "operation": "repair", "repair": "shortcut"
    })

    assert result["ok"] is True
    assert result["message"] == "[CONFIRMATION_PENDING] shortcut"


def test_repair_status_reports_verified_outcome(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    shortcut = desktop / "JARVIS.lnk"
    monkeypatch.setattr(system_repair, "BACKUP_ROOT", tmp_path / "backups")
    monkeypatch.setattr(system_repair.desktop_shortcut, "shortcut_path", lambda: shortcut)
    monkeypatch.setattr(system_repair.desktop_shortcut, "create", lambda: shortcut.write_text("valid", encoding="utf-8"))
    monkeypatch.setattr(system_repair.desktop_shortcut, "verify", lambda: {"valid": True})

    system_repair.execute_repair("shortcut")
    status = system_repair.repair_status()

    assert status and status["ok"] is True and status["verified"] is True


def test_shortcut_repair_backs_up_and_verifies(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    shortcut = desktop / "JARVIS.lnk"
    shortcut.write_text("old target", encoding="utf-8")
    monkeypatch.setattr(system_repair, "BACKUP_ROOT", tmp_path / "backups")
    monkeypatch.setattr(system_repair.desktop_shortcut, "shortcut_path", lambda: shortcut)
    monkeypatch.setattr(system_repair.desktop_shortcut, "create", lambda: shortcut.write_text("new target", encoding="utf-8"))
    monkeypatch.setattr(system_repair.desktop_shortcut, "verify", lambda: {"valid": True})

    result = system_repair.execute_repair("shortcut")

    assert result.ok and result.verified
    assert shortcut.read_text(encoding="utf-8") == "new target"
    assert Path(result.backup).read_text(encoding="utf-8") == "old target"


def test_failed_shortcut_verification_rolls_back(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    shortcut = desktop / "JARVIS.lnk"
    shortcut.write_text("old target", encoding="utf-8")
    monkeypatch.setattr(system_repair, "BACKUP_ROOT", tmp_path / "backups")
    monkeypatch.setattr(system_repair.desktop_shortcut, "shortcut_path", lambda: shortcut)
    monkeypatch.setattr(system_repair.desktop_shortcut, "create", lambda: shortcut.write_text("bad target", encoding="utf-8"))
    monkeypatch.setattr(system_repair.desktop_shortcut, "verify", lambda: {"valid": False})

    result = system_repair.execute_repair("shortcut")

    assert not result.ok and result.rolled_back
    assert shortcut.read_text(encoding="utf-8") == "old target"


def test_hud_port_repair_selects_and_verifies_loopback_port(monkeypatch):
    monkeypatch.setenv("JARVIS_HUD_PORT", "invalid")

    result = system_repair.execute_repair("hud_port")

    assert result.ok and result.verified
    assert 1 <= int(system_repair.os.environ["JARVIS_HUD_PORT"]) <= 65535
    assert "next HUD start" in result.message


def test_soul_restore_validates_backup_and_preserves_current(monkeypatch, tmp_path):
    from core.soul.models import SoulState, utc_now_iso
    memory = tmp_path / "memory"
    memory.mkdir()
    current = memory / "soul.json"
    backup = memory / "soul.backup.json"
    current.write_text("corrupt current private content", encoding="utf-8")
    backup.write_text(json.dumps(SoulState.new(utc_now_iso()).to_dict()), encoding="utf-8")
    monkeypatch.setattr(system_repair, "ROOT", tmp_path)
    monkeypatch.setattr(system_repair, "BACKUP_ROOT", tmp_path / "repair_backups")

    result = system_repair.execute_repair("soul_backup")

    assert result.ok and result.verified
    assert json.loads(current.read_text(encoding="utf-8"))["schema_version"] >= 1
    assert Path(result.backup).read_text(encoding="utf-8") == "corrupt current private content"


def test_invalid_soul_backup_never_replaces_current(monkeypatch, tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    current = memory / "soul.json"
    backup = memory / "soul.backup.json"
    current.write_text('{"current": true}', encoding="utf-8")
    backup.write_text("invalid", encoding="utf-8")
    monkeypatch.setattr(system_repair, "ROOT", tmp_path)
    monkeypatch.setattr(system_repair, "BACKUP_ROOT", tmp_path / "repair_backups")

    result = system_repair.execute_repair("soul_backup")

    assert not result.ok and result.rolled_back
    assert current.read_text(encoding="utf-8") == '{"current": true}'
