from pathlib import Path

import install_jarvis
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


def test_windows_resolves_redirected_onedrive_desktop(monkeypatch, tmp_path):
    redirected = tmp_path / "OneDrive" / "Desktop"
    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Windows")
    monkeypatch.setattr(desktop_shortcut, "_windows_desktop_directory", lambda: redirected)

    assert desktop_shortcut.desktop_directory() == redirected
    assert desktop_shortcut.shortcut_path() == redirected / "JARVIS.lnk"


def test_windows_launch_target_uses_current_python_and_main(monkeypatch, tmp_path):
    python = tmp_path / "Python312" / "python.exe"
    main = tmp_path / "jarvis" / "main.py"
    python.parent.mkdir(parents=True)
    main.parent.mkdir(parents=True)
    python.write_text("", encoding="utf-8")
    main.write_text("", encoding="utf-8")
    monkeypatch.setattr(desktop_shortcut.platform, "system", lambda: "Windows")
    monkeypatch.setattr(desktop_shortcut.sys, "executable", str(python))
    monkeypatch.setattr(desktop_shortcut.sys, "frozen", False, raising=False)
    monkeypatch.setattr(desktop_shortcut, "_MAIN", main)

    target, argv = desktop_shortcut._launch_target()

    assert target == python.resolve()
    assert argv == [str(python.resolve()), str(main)]


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
    main = tmp_path / "main.py"
    monkeypatch.setattr(desktop_shortcut, "_launch_target", lambda: (launcher, [str(launcher), str(main)]))
    monkeypatch.setattr(desktop_shortcut.subprocess, "run", fake_run)

    path = desktop_shortcut.create()

    assert path.name == "JARVIS.lnk"
    assert str(launcher) not in captured["argv"][-1]
    assert captured["kwargs"]["env"]["JARVIS_TARGET"] == str(launcher)
    assert str(main) in captured["kwargs"]["env"]["JARVIS_ARGUMENTS"]
    assert "$s.WindowStyle=7" in captured["argv"][-1]
    assert "JARVIS_SHORTCUT_TEMP" in captured["kwargs"]["env"]
    assert "Move-Item" in captured["argv"][-1]
    assert "points to a different installation" in captured["argv"][-1]
    assert captured["kwargs"]["env"]["JARVIS_WORKDIR"] == str(desktop_shortcut._ROOT)
    assert captured["kwargs"]["check"] is True


def test_windows_fallback_launcher_uses_supported_python(tmp_path):
    install_jarvis.write_native_launchers(tmp_path)
    launcher = (tmp_path / "Start_JARVIS.bat").read_text(encoding="utf-8")
    assert "py -3.12 main.py" in launcher
    assert "python install_jarvis.py" not in launcher


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
