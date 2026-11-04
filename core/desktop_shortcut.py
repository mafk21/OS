"""Cross-platform JARVIS desktop shortcut management.

The shortcut always points at the installed application (when frozen) or the
repository's supported launch script.  No user-provided command is embedded.
"""
from __future__ import annotations

import os
import platform
import shlex
import stat
import subprocess
import sys
from pathlib import Path

APP_NAME = "JARVIS"
_ROOT = Path(__file__).resolve().parent.parent
_ICON = _ROOT / "config" / "jarvis.ico"
_LINUX_ICON = _ROOT / "docs" / "assets" / "jarvis-logo.png"


def _desktop_exec_arg(value: str) -> str:
    """Quote one freedesktop Exec argument (this is not shell syntax)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def desktop_directory() -> Path:
    """Return the user's real Desktop folder, respecting XDG when available."""
    if platform.system() == "Linux":
        config = Path.home() / ".config" / "user-dirs.dirs"
        try:
            for line in config.read_text(encoding="utf-8").splitlines():
                if line.startswith("XDG_DESKTOP_DIR="):
                    value = line.split("=", 1)[1].strip().strip('"')
                    return Path(value.replace("$HOME", str(Path.home()))).expanduser()
        except OSError:
            pass
    return Path.home() / "Desktop"


def shortcut_path() -> Path:
    suffix = {"Windows": ".lnk", "Darwin": ".command"}.get(platform.system(), ".desktop")
    return desktop_directory() / f"{APP_NAME}{suffix}"


def _launch_target() -> tuple[Path, list[str]]:
    if getattr(sys, "frozen", False):
        executable = Path(sys.executable).resolve()
        return executable, [str(executable)]
    script_name = {
        "Windows": "Start_JARVIS.bat",
        "Darwin": "Start_JARVIS.command",
    }.get(platform.system(), "Start_JARVIS.sh")
    script = (_ROOT / script_name).resolve()
    if not script.is_file():
        raise FileNotFoundError(f"JARVIS launcher not found: {script}")
    return script, [str(script)]


def exists() -> bool:
    return shortcut_path().is_file()


def create() -> Path:
    """Create or replace the current user's desktop shortcut."""
    desktop = desktop_directory()
    desktop.mkdir(parents=True, exist_ok=True)
    destination = shortcut_path()
    target, argv = _launch_target()
    system = platform.system()

    if system == "Windows":
        # WScript.Shell is the native Windows shortcut API. Values travel over
        # environment variables, not interpolated PowerShell source.
        env = os.environ.copy()
        env.update(
            JARVIS_SHORTCUT=str(destination),
            JARVIS_TARGET=str(target),
            JARVIS_WORKDIR=str(target.parent),
            JARVIS_ICON=str(_ICON),
        )
        script = (
            "$w=New-Object -ComObject WScript.Shell;"
            "$s=$w.CreateShortcut($env:JARVIS_SHORTCUT);"
            "$s.TargetPath=$env:JARVIS_TARGET;"
            "$s.WorkingDirectory=$env:JARVIS_WORKDIR;"
            "$s.Description='Launch JARVIS';"
            "if(Test-Path $env:JARVIS_ICON){$s.IconLocation=$env:JARVIS_ICON};"
            "$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
    elif system == "Darwin":
        command = " ".join(shlex.quote(part) for part in argv)
        destination.write_text(
            "#!/bin/sh\ncd " + shlex.quote(str(target.parent)) + "\nexec " + command + "\n",
            encoding="utf-8",
        )
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR)
    else:
        command = " ".join(_desktop_exec_arg(part) for part in argv)
        icon_line = f"Icon={_LINUX_ICON}\n" if _LINUX_ICON.is_file() else ""
        destination.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=JARVIS\n"
            "Comment=Launch JARVIS\n"
            f"Exec={command}\n"
            f"Path={target.parent}\n"
            f"{icon_line}"
            "Terminal=false\n"
            "Categories=Utility;\n",
            encoding="utf-8",
        )
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR)
    return destination


def remove() -> bool:
    path = shortcut_path()
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False


def status() -> dict[str, object]:
    path = shortcut_path()
    return {"exists": path.is_file(), "path": str(path), "supported": True}
