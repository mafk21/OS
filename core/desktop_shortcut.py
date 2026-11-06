"""Cross-platform JARVIS desktop shortcut management.

Shortcuts launch the exact Python interpreter currently running JARVIS, rather
than relying on the machine's ambiguous ``python`` command. No user-provided
command is embedded in a launcher.
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
_MAIN = _ROOT / "main.py"
_ICON = _ROOT / "config" / "jarvis.ico"
_LINUX_ICON = _ROOT / "docs" / "assets" / "jarvis-logo.png"


def _desktop_exec_arg(value: str) -> str:
    """Quote one freedesktop Exec argument (this is not shell syntax)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _windows_shortcut_argument(value: Path) -> str:
    """Quote a trusted local path for WScript.Shell Shortcut.Arguments."""
    text = str(value)
    if '"' in text:
        raise ValueError("Invalid quote in JARVIS launch path")
    return f'"{text}"'


def _windows_desktop_directory() -> Path | None:
    """Read Windows' redirected Desktop path (including OneDrive Desktop)."""
    try:
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Desktop")
        expanded = os.path.expandvars(str(value)).strip()
        return Path(expanded) if expanded else None
    except (ImportError, OSError, TypeError):
        return None


def desktop_directory() -> Path:
    """Return the user's real Desktop folder, including OS redirection."""
    system = platform.system()
    if system == "Windows":
        known = _windows_desktop_directory()
        if known is not None:
            return known
        # Useful fallback for OneDrive systems whose registry lookup is blocked.
        one_drive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
        if one_drive and (Path(one_drive) / "Desktop").is_dir():
            return Path(one_drive) / "Desktop"
    elif system == "Linux":
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
    """Return a stable executable and argv for the current installation."""
    executable = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        return executable, [str(executable)]
    if not _MAIN.is_file():
        raise FileNotFoundError(f"JARVIS entry point not found: {_MAIN}")
    if not executable.is_file():
        raise FileNotFoundError(f"Python interpreter not found: {executable}")
    if platform.system() == "Windows":
        # A .lnk can launch pythonw directly, avoiding both a console flash and
        # the wrong Python selected by the global `python` command.
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.is_file():
            executable = pythonw
    return executable, [str(executable), str(_MAIN)]


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
            JARVIS_ARGUMENTS=" ".join(_windows_shortcut_argument(Path(arg)) for arg in argv[1:]),
            JARVIS_WORKDIR=str(_ROOT),
            JARVIS_ICON=str(_ICON),
        )
        script = (
            "$w=New-Object -ComObject WScript.Shell;"
            "$s=$w.CreateShortcut($env:JARVIS_SHORTCUT);"
            "$s.TargetPath=$env:JARVIS_TARGET;"
            "$s.Arguments=$env:JARVIS_ARGUMENTS;"
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
            "#!/bin/sh\ncd " + shlex.quote(str(_ROOT)) + "\nexec " + command + "\n",
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
            f"Path={_ROOT}\n"
            f"{icon_line}"
            "Terminal=false\n"
            "Categories=Utility;\n",
            encoding="utf-8",
        )
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR)
    if not destination.exists():
        raise OSError(f"Shortcut was not created at {destination}")
    return destination


def remove() -> bool:
    path = shortcut_path()
    try:
        # A shortcut is a file. Never recursively delete a same-named folder
        # because it can contain unrelated user data.
        path.unlink()
        return True
    except (FileNotFoundError, IsADirectoryError):
        return False


def status() -> dict[str, object]:
    path = shortcut_path()
    return {"exists": path.exists(), "path": str(path), "supported": True}
