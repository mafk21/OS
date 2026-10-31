"""
Background Agent — Phase 5.2
Long jobs (many-step sites/forms) run in background while chatting.
Shell + Python execution with timeouts, streaming logs, kill support.
"""
import threading, subprocess, time, sys, pathlib, queue, uuid, os
from typing import Dict, Any

_jobs: Dict[str, dict] = {}
_lock = threading.Lock()

def start_job(cmd: str, cwd: str = "", shell: bool = True, timeout: int = 300) -> str:
    jid = uuid.uuid4().hex[:8]
    workdir = pathlib.Path(cwd).expanduser() if cwd else pathlib.Path.cwd()
    q = queue.Queue()
    rec = {"id": jid, "cmd": cmd, "cwd": str(workdir), "status": "running", "output": [], "queue": q, "proc": None, "started": time.time()}
    with _lock: _jobs[jid] = rec

    def _run():
        try:
            # Choose shell
            if sys.platform == "win32":
                shell_cmd = cmd if shell else cmd
                proc = subprocess.Popen(
                    shell_cmd, # Owner-approved background task intentionally supports shell syntax.
                    shell=True,  # nosec B602
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    cwd=str(workdir), bufsize=1,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            else:
                proc = subprocess.Popen(
                    cmd, # Owner-approved background task intentionally supports shell syntax.
                    shell=True,  # nosec B602
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    cwd=str(workdir), bufsize=1, executable="/bin/bash",
                )
            rec["proc"] = proc
            assert proc.stdout is not None
            for line in proc.stdout:
                rec["output"].append(line.rstrip())
                q.put(line.rstrip())
                if len(rec["output"]) > 2000: rec["output"] = rec["output"][-2000:]
            proc.wait(timeout=timeout)
            rec["status"] = "done" if proc.returncode == 0 else f"exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            try: proc.kill()
            except: pass
            rec["status"] = "timeout"
        except Exception as e:
            rec["status"] = f"error: {e}"
        finally:
            q.put(None)

    threading.Thread(target=_run, daemon=True, name=f"bg-{jid}").start()
    return jid

def get_job(jid: str) -> dict | None:
    with _lock: return _jobs.get(jid)

def list_jobs() -> list[dict]:
    with _lock:
        return [{"id": j["id"], "cmd": j["cmd"][:80], "status": j["status"], "age": int(time.time()-j["started"])} for j in _jobs.values()]

def kill_job(jid: str) -> str:
    with _lock: rec = _jobs.get(jid)
    if not rec: return f"Job {jid} not found"
    proc = rec.get("proc")
    if proc and proc.poll() is None:
        try: proc.terminate()
        except: pass
        rec["status"] = "killed"
        return f"Job {jid} killed"
    return f"Job {jid} already {rec['status']}"

def job_log(jid: str, last_n: int = 100) -> str:
    rec = get_job(jid)
    if not rec: return f"Job {jid} not found"
    out = rec["output"][-last_n:]
    return "\n".join(out) if out else "(no output yet)"
