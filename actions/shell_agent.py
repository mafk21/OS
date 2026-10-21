"""
Shell + Background Agent — Phase 5.2
bash/PowerShell execution + long jobs in background.
"""
import platform, subprocess, shlex, pathlib, sys

def _run_once(cmd: str, cwd: str = "", timeout: int = 60) -> str:
    workdir = pathlib.Path(cwd).expanduser() if cwd else pathlib.Path.cwd()
    try:
        is_win = platform.system() == "Windows"
        shell = True
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, cwd=str(workdir), timeout=timeout)
        out = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        out = out.strip()
        if not out: out = f"(exit {result.returncode}, no output)"
        # Cap to avoid token blowup
        if len(out) > 6000: out = out[:6000] + "\n…[truncated]"
        return out
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s (try action=run_background for long jobs)"
    except Exception as e:
        return f"Shell error: {e}"

def shell_agent(parameters: dict, player=None, **_):
    action = str(parameters.get("action", "run") or "run").lower()
    cmd = str(parameters.get("command", "") or parameters.get("cmd", "") or "").strip()
    cwd = str(parameters.get("cwd", "") or parameters.get("workdir", "")).strip()
    if action in ("run", "exec", "shell"):
        if not cmd: return "Need command: e.g. {\"action\":\"run\",\"command\":\"ls -la\"}"
        out = _run_once(cmd, cwd=cwd, timeout=int(parameters.get("timeout", 60)))
        if player: player.show_content("SHELL", f"$ {cmd}\n{out[:4000]}")
        return out
    if action in ("run_background", "background", "start"):
        if not cmd: return "Need command for background run"
        from core.background_agent import start_job
        jid = start_job(cmd, cwd=cwd, timeout=int(parameters.get("timeout", 600)))
        if player: player.write_log(f"[Shell] Background job {jid}: {cmd[:60]}")
        return f"Background job {jid} started: {cmd}. Use action=log|list|kill with id={jid}"
    if action in ("list", "jobs"):
        from core.background_agent import list_jobs
        jobs = list_jobs()
        if not jobs: return "No background jobs"
        return "\n".join(f"{j['id']} [{j['status']}] {j['cmd']}" for j in jobs)
    if action == "log":
        jid = str(parameters.get("id", "") or parameters.get("job_id", "")).strip()
        if not jid: return "Need id for log"
        from core.background_agent import job_log
        return job_log(jid, last_n=int(parameters.get("lines", 100)))
    if action in ("kill", "stop"):
        jid = str(parameters.get("id", "") or parameters.get("job_id", "")).strip()
        if not jid: return "Need id to kill"
        from core.background_agent import kill_job
        return kill_job(jid)
    return "Actions: run|run_background|list|log|kill"

TOOL={
    "name":"shell_agent",
    "description":"Shell + Background Agent: run bash/PowerShell commands, or start long jobs in background while chatting. Actions: run, run_background, list, log, kill.",
    "parameters":{
        "type":"OBJECT",
        "properties":{
            "action":{"type":"STRING","description":"run|run_background|list|log|kill"},
            "command":{"type":"STRING","description":"Shell command"},
            "cmd":{"type":"STRING"},
            "cwd":{"type":"STRING","description":"Working directory"},
            "workdir":{"type":"STRING"},
            "timeout":{"type":"NUMBER","description":"Timeout seconds"},
            "id":{"type":"STRING","description":"Job id for log/kill"},
            "job_id":{"type":"STRING"},
            "lines":{"type":"NUMBER","description":"Last N log lines"}
        },
        "required":["action"]
    },
    "handler":shell_agent
}
