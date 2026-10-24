#!/usr/bin/env python3
"""
1-Click Cross-Platform Installer & Native Launcher for JARVIS OS — Phase 6.

Zero external dependencies (stdlib only). Handles:
  • Python >= 3.10 environment & prebuilt `apex_ui/static_hud` verification
  • Virtual environment creation (`.venv`) + `requirements.txt` installation
  • Native 1-click desktop launcher generation (Windows `.bat`, macOS `.command`, Linux `.sh`)
  • Immediate boot into JARVIS (first-run Gemini API key + optional Integrations + Male/Female chooser)
"""

from __future__ import annotations

import argparse
import os
import platform
import stat
import subprocess
import sys
import venv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / ".venv"
REQ_FILE = BASE_DIR / "requirements.txt"
HUD_INDEX = BASE_DIR / "apex_ui" / "static_hud" / "index.html"


def venv_python(venv_dir: Path = VENV_DIR) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python3"


def check_environment() -> dict:
    py_ok = sys.version_info >= (3, 10)
    hud_ok = HUD_INDEX.is_file()
    req_ok = REQ_FILE.is_file()
    return {
        "ok": py_ok and hud_ok and req_ok,
        "python_version": platform.python_version(),
        "python_ok": py_ok,
        "prebuilt_hud_ready": hud_ok,
        "requirements_present": req_ok,
        "platform": platform.system(),
    }


def write_native_launchers(target_dir: Path = BASE_DIR) -> list[str]:
    created: list[str] = []
    win_bat = target_dir / "Start_JARVIS.bat"
    win_bat.write_text(
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "if exist \".venv\\Scripts\\pythonw.exe\" (\r\n"
        "    start \"\" \".venv\\Scripts\\pythonw.exe\" main.py\r\n"
        ") else if exist \".venv\\Scripts\\python.exe\" (\r\n"
        "    \".venv\\Scripts\\python.exe\" main.py\r\n"
        ") else (\r\n"
        "    python install_jarvis.py --install --launch\r\n"
        ")\r\n",
        encoding="utf-8",
    )
    created.append(str(win_bat))

    mac_cmd = target_dir / "Start_JARVIS.command"
    mac_cmd.write_text(
        "#!/usr/bin/env bash\n"
        "cd \"$(dirname \"$0\")\"\n"
        "if [ -x \".venv/bin/python3\" ]; then\n"
        "  exec \".venv/bin/python3\" main.py\n"
        "else\n"
        "  exec python3 install_jarvis.py --install --launch\n"
        "fi\n",
        encoding="utf-8",
    )
    try:
        os.chmod(mac_cmd, os.stat(mac_cmd).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass
    created.append(str(mac_cmd))
    return created


def ensure_venv_and_deps() -> Path:
    vpy = venv_python()
    if not vpy.is_file():
        print("[JARVIS Installer] Creating isolated .venv environment…")
        venv.create(str(VENV_DIR), with_pip=True)
    subprocess.run([str(vpy), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(vpy), "-m", "pip", "install", "-r", str(REQ_FILE)], check=True)
    return vpy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JARVIS 1-Click Native Installer & Launcher")
    parser.add_argument("--check", action="store_true", help="Verify environment & prebuilt HUD")
    parser.add_argument("--shortcuts", action="store_true", help="Generate native 1-click launchers")
    parser.add_argument("--install", action="store_true", help="Create .venv and install dependencies")
    parser.add_argument("--launch", action="store_true", help="Launch JARVIS after setup")
    args = parser.parse_args(argv)

    status = check_environment()
    if args.check:
        for k, v in status.items():
            print(f"{k}: {v}")
        return 0 if status["ok"] else 1

    if not status["python_ok"]:
        print("ERROR: Python 3.10 or newer is required.", file=sys.stderr)
        return 1

    if args.shortcuts:
        paths = write_native_launchers(BASE_DIR)
        print("Created native launchers:\n  " + "\n  ".join(paths))

    py_exec = Path(sys.executable)
    if args.install:
        py_exec = ensure_venv_and_deps()
        write_native_launchers(BASE_DIR)

    if args.launch:
        return subprocess.call([str(py_exec), str(BASE_DIR / "main.py")], cwd=str(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
