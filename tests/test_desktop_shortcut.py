from pathlib import Path

from actions.desktop_shortcut import manage_desktop_shortcut
from core import desktop_shortcut


def test_linux_shortcut_uses_supported_launcher(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    launcher = tmp_path / "Start_JARVIS.sh"
    launcher.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop_shortcut, "desktop_directory", lambda: desktop)
    monkeypatch.setattr(desktop_shortcut, "_launch_target", lambda: (launcher, [str(launcher)]))

    path = desktop_shortcut.create()

    assert path == desktop / "JARVIS.desktop"
    text = path.read_text(encoding="utf-8")
    assert "Type=Application" in text
    assert f'Exec="{launcher}"' in text
    assert path.stat().st_mode & 0o100


def test_macos_shortcut_is_executable(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    launcher = tmp_path / "Start JARVIS.command"
    launcher.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(desktop_shortcut, "desktop_directory", lambda: desktop)
    monkeypatch.setattr(desktop_shortcut, "_launch_target", lambda: (launcher, [str(launcher)]))

    path = desktop_shortcut.create()

    assert path.name == "JARVIS.command"
    assert "exec '" in path.read_text(encoding="utf-8")
    assert path.stat().st_mode & 0o100


def test_windows_uses_native_shortcut_api_without_source_interpolation(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    launcher = tmp_path / "Start_JARVIS.bat"
    launcher.write_text("", encoding="utf-8")
    captured = {}

    def fake_run(argv, **kwargs):
        captured.update(argv=argv, kwargs=kwargs)
        (desktop / "JARVIS.lnk").write_text("shortcut", encoding="utf-8")

    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Windows")
    monkeypatch.setattr(desktop_shortcut, "desktop_directory", lambda: desktop)
    monkeypatch.setattr(desktop_shortcut, "_launch_target", lambda: (launcher, [str(launcher)]))
    monkeypatch.setattr(desktop_shortcut.subprocess, "run", fake_run)

    path = desktop_shortcut.create()

    assert path.name == "JARVIS.lnk"
    assert str(launcher) not in captured["argv"][-1]
    assert captured["kwargs"]["env"]["JARVIS_TARGET"] == str(launcher)
    assert captured["kwargs"]["check"] is True


def test_tool_create_status_and_remove(monkeypatch, tmp_path):
    desktop = tmp_path / "Desktop"
    launcher = tmp_path / "Start_JARVIS.sh"
    launcher.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop_shortcut, "desktop_directory", lambda: desktop)
    monkeypatch.setattr(desktop_shortcut, "_launch_target", lambda: (launcher, [str(launcher)]))

    assert "created" in manage_desktop_shortcut({"action": "create"}).lower()
    assert "exists" in manage_desktop_shortcut({"action": "status"}).lower()
    assert "removed" in manage_desktop_shortcut({"action": "remove"}).lower()
