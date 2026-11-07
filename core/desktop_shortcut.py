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
import uuid
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
    # Keep python.exe on Windows. Unlike pythonw.exe it preserves diagnostics
    # when startup fails, and it behaves exactly like the verified
    # `py -3.12 main.py` launch path. The shortcut starts it minimized below.
    return executable, [str(executable), str(_MAIN)]


def exists() -> bool:
    return shortcut_path().is_file()


def verify() -> dict[str, object]:
    """Verify that the saved shortcut launches this exact installation."""
    path = shortcut_path()
    if not path.is_file():
        return {"valid": False, "path": str(path), "reason": "missing"}
    target, argv = _launch_target()
    system = platform.system()
    try:
        if system == "Windows":
            env = os.environ.copy()
            env["JARVIS_SHORTCUT"] = str(path)
            script = (
                "$ErrorActionPreference='Stop';"
                "$w=New-Object -ComObject WScript.Shell;"
                "$s=$w.CreateShortcut($env:JARVIS_SHORTCUT);"
                "[pscustomobject]@{target=$s.TargetPath;arguments=$s.Arguments;"
                "workdir=$s.WorkingDirectory}|ConvertTo-Json -Compress"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                check=True, capture_output=True, text=True, timeout=10, env=env,
            )
            import json
            saved = json.loads(result.stdout)
            expected_args = " ".join(_windows_shortcut_argument(Path(arg)) for arg in argv[1:])
            valid = (
                os.path.normcase(saved.get("target", "")) == os.path.normcase(str(target))
                and saved.get("arguments", "") == expected_args
                and os.path.normcase(saved.get("workdir", "")) == os.path.normcase(str(_ROOT))
            )
            return {"valid": valid, "path": str(path), "reason": "ok" if valid else "target_mismatch"}
        text = path.read_text(encoding="utf-8")
        if system == "Darwin":
            expected = "exec " + " ".join(shlex.quote(part) for part in argv)
            valid = expected in text and ("cd " + shlex.quote(str(_ROOT))) in text
        else:
            expected = "Exec=" + " ".join(_desktop_exec_arg(part) for part in argv)
            valid = expected in text and f"Path={_ROOT}" in text
        return {"valid": valid, "path": str(path), "reason": "ok" if valid else "target_mismatch"}
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return {"valid": False, "path": str(path), "reason": type(exc).__name__}


def create(*, allow_inactive: bool = False) -> Path:
    """Create or replace the shortcut for the explicitly active installation."""
    if not allow_inactive:
        from core.system_doctor import installation_identity
        from core import installation_registry
        identity = installation_identity()
        lifecycle = installation_registry.status(identity.installation_id)
        if not lifecycle["is_active"]:
            raise RuntimeError(
                "This JARVIS installation is not active; make it active before replacing the Desktop shortcut"
            )
    desktop = desktop_directory()
    desktop.mkdir(parents=True, exist_ok=True)
    destination = shortcut_path()
    target, argv = _launch_target()
    system = platform.system()

    if system == "Windows":
        # Build a new shortcut beside the destination, verify every launch
        # field through Windows' own shortcut API, and only then replace the
        # public shortcut. This prevents a stale same-named .lnk (for example
        # from another checkout) from surviving while creation reports success.
        temporary = destination.with_name(f".{APP_NAME}.{uuid.uuid4().hex}.lnk")
        env = os.environ.copy()
        env.update(
            JARVIS_SHORTCUT=str(destination),
            JARVIS_SHORTCUT_TEMP=str(temporary),
            JARVIS_TARGET=str(target),
            JARVIS_ARGUMENTS=" ".join(_windows_shortcut_argument(Path(arg)) for arg in argv[1:]),
            JARVIS_WORKDIR=str(_ROOT),
            JARVIS_ICON=str(_ICON),
        )
        script = (
            "$ErrorActionPreference='Stop';"
            "$w=New-Object -ComObject WScript.Shell;"
            "$s=$w.CreateShortcut($env:JARVIS_SHORTCUT_TEMP);"
            "$s.TargetPath=$env:JARVIS_TARGET;"
            "$s.Arguments=$env:JARVIS_ARGUMENTS;"
            "$s.WorkingDirectory=$env:JARVIS_WORKDIR;"
            "$s.WindowStyle=7;"
            "$s.Description=('Launch this JARVIS installation: '+$env:JARVIS_WORKDIR);"
            "if(Test-Path $env:JARVIS_ICON){$s.IconLocation=$env:JARVIS_ICON};"
            "$s.Save();"
            "$v=$w.CreateShortcut($env:JARVIS_SHORTCUT_TEMP);"
            "if(($v.TargetPath -ine $env:JARVIS_TARGET) -or "
            "($v.Arguments -cne $env:JARVIS_ARGUMENTS) -or "
            "($v.WorkingDirectory -ine $env:JARVIS_WORKDIR)){"
            "Remove-Item -LiteralPath $env:JARVIS_SHORTCUT_TEMP -Force -ErrorAction SilentlyContinue;"
            "throw 'Windows did not save the requested JARVIS installation target'};"
            "Move-Item -LiteralPath $env:JARVIS_SHORTCUT_TEMP "
            "-Destination $env:JARVIS_SHORTCUT -Force;"
            "$v=$w.CreateShortcut($env:JARVIS_SHORTCUT);"
            "if(($v.TargetPath -ine $env:JARVIS_TARGET) -or "
            "($v.Arguments -cne $env:JARVIS_ARGUMENTS) -or "
            "($v.WorkingDirectory -ine $env:JARVIS_WORKDIR)){"
            "throw 'The installed JARVIS shortcut points to a different installation'}"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
        finally:
            # PowerShell normally removes this via Move-Item. Clean it after an
            # interrupted or rejected creation without touching user folders.
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
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
