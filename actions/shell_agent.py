"""
Shell + Background Agent — Phase 5.2 (Upgraded with PowerShell auto-routing
and visible interactive terminal launching).
"""

from __future__ import annotations

import pathlib
import platform
import re
import shutil
import subprocess

from core.os_control import open_interactive_terminal

_SYSTEM = platform.system()
_WIN_HIDE = (
    {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    if _SYSTEM == "Windows"
    else {}
)

_PS_CMDLET_RE = re.compile(
    r"(\b(Get|Set|New|Remove|Start|Stop|Restart|Invoke|Select|Where|ForEach|Test|Out)-[A-Z][A-Za-z]+\b"
    r"|\$PSVersionTable|\$env:|\$_|\|\s*(Select-Object|Where-Object|Sort-Object|Format-Table))",
)


def _should_use_powershell(cmd: str, shell_pref: str = "") -> bool:
    if _SYSTEM != "Windows":
        return False
    pref = (shell_pref or "").strip().lower()
    if pref in ("powershell", "pwsh", "ps1"):
        return True
    if pref in ("cmd", "cmd.exe"):
        return False
    return bool(_PS_CMDLET_RE.search(cmd or ""))


def _run_once(cmd: str, cwd: str = "", timeout: int = 60, shell_pref: str = "") -> str:
    workdir = pathlib.Path(cwd).expanduser() if cwd else pathlib.Path.cwd()
    if not workdir.is_dir():
        return f"Shell error: working directory does not exist: {workdir}"
    try:
        if _should_use_powershell(cmd, shell_pref):
            ps_bin = (
                shutil.which("pwsh")
                if shell_pref.strip().lower() == "pwsh" and shutil.which("pwsh")
                else (shutil.which("powershell") or "powershell")
            )
            result = subprocess.run(
                [ps_bin, "-NoProfile", "-NonInteractive", "-Command", cmd],
                capture_output=True,
                text=True,
                cwd=str(workdir),
                timeout=timeout,
                **_WIN_HIDE,
            )
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(workdir),
                timeout=timeout,
                **_WIN_HIDE,
            )
        out = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        out = out.strip()
        if not out:
            out = f"(exit {result.returncode}, no output)"
        elif result.returncode != 0:
            out = f"[exit {result.returncode}]\n{out}"
        if len(out) > 6000:
            out = out[:6000] + "\n…[truncated]"
        return out
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s (try action=run_background for long jobs)"
    except Exception as e:
        return f"Shell error: {e}"


def shell_agent(parameters: dict, player=None, **_):
    params = parameters or {}
    action = str(params.get("action", "run") or "run").strip().lower()
    cmd = str(params.get("command", "") or params.get("cmd", "") or "").strip()
    cwd = str(params.get("cwd", "") or params.get("workdir", "") or "").strip()
    shell_pref = str(params.get("shell", "") or "").strip()

    if action in ("open_terminal", "interactive", "visible", "powershell_window"):
        res = open_interactive_terminal(
            shell_name=shell_pref or "powershell",
            cwd=cwd,
            command=cmd,
            admin=bool(params.get("admin", False)),
        )
        if player and hasattr(player, "write_log"):
            player.write_log(f"[Shell] open_terminal ({shell_pref or 'powershell'}): {res['ok']}")
        return res["message"]

    if action in ("run", "exec", "shell"):
        if not cmd:
            return 'Need command: e.g. {"action":"run","command":"Get-Process"}'
        out = _run_once(
            cmd,
            cwd=cwd,
            timeout=int(params.get("timeout", 60) or 60),
            shell_pref=shell_pref,
        )
        try:
            from core.dev_workspace import get_terminal_manager
            get_terminal_manager().record_completed_run(cmd, cwd, out)
        except Exception:
            pass
        if player and hasattr(player, "show_content"):
            player.show_content("SHELL", f"$ {cmd}\n{out[:4000]}")
        return out

    if action in ("run_background", "background", "start"):
        if not cmd:
            return "Need command for background run"
        from core.background_agent import start_job
        jid = start_job(cmd, cwd=cwd, timeout=int(params.get("timeout", 600) or 600))
        if player and hasattr(player, "write_log"):
            player.write_log(f"[Shell] Background job {jid}: {cmd[:60]}")
        return f"Background job {jid} started: {cmd}. Use action=log|list|kill with id={jid}"

    if action in ("list", "jobs"):
        from core.background_agent import list_jobs
        jobs = list_jobs()
        if not jobs:
            return "No background jobs"
        return "\n".join(f"{j['id']} [{j['status']}] {j['cmd']}" for j in jobs)

    if action == "log":
        jid = str(params.get("id", "") or params.get("job_id", "")).strip()
        if not jid:
            return "Need id for log"
        from core.background_agent import job_log
        return job_log(jid, last_n=int(params.get("lines", 100) or 100))

    if action in ("kill", "stop"):
        jid = str(params.get("id", "") or params.get("job_id", "")).strip()
        if not jid:
            return "Need id to kill"
        from core.background_agent import kill_job
        return kill_job(jid)

    return "Actions: run|open_terminal|run_background|list|log|kill"


TOOL = {
    "name": "shell_agent",
    "description": (
        "Shell + Background Agent: run headless bash/PowerShell/CMD commands "
        "(`action='run'`), open a REAL VISIBLE interactive terminal/PowerShell "
        "window on the user's screen (`action='open_terminal'`), or manage "
        "background jobs (`run_background`, `list`, `log`, `kill`). Note: `run` "
        "is headless — when the user asks to OPEN PowerShell/CMD/Terminal so "
        "they can see it, always use `action='open_terminal'` or `open_app`."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "run|open_terminal|run_background|list|log|kill"},
            "command": {"type": "STRING", "description": "Shell command (optional for open_terminal)"},
            "cmd": {"type": "STRING"},
            "shell": {"type": "STRING", "description": "Optional shell: powershell|pwsh|cmd|wt|wsl|bash"},
            "cwd": {"type": "STRING", "description": "Working directory"},
            "workdir": {"type": "STRING"},
            "admin": {"type": "BOOLEAN", "description": "For open_terminal: launch elevated if user requested"},
            "timeout": {"type": "NUMBER", "description": "Timeout seconds"},
            "id": {"type": "STRING", "description": "Job id for log/kill"},
            "job_id": {"type": "STRING"},
            "lines": {"type": "NUMBER", "description": "Last N log lines"},
        },
        "required": ["action"],
    },
    "handler": shell_agent,
}
