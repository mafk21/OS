"""
Live Streaming Dev Terminal, Codebase File-Tree Map & Unified Git Diffs — Phase 5.

100% local-first stdlib implementation. Streams real-time stdout/stderr chunks
over `/ws/hud`, supports bidirectional stdin & 1-click process termination,
and renders safe workspace file trees + unified colorizable diffs.
"""

from __future__ import annotations

import os
import platform
import subprocess
import signal
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Callable

BASE_DIR = Path(__file__).resolve().parent.parent

_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".next",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    "static_hud",
}

_BINARY_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".mp3",
    ".wav",
    ".ogg",
    ".woff",
    ".woff2",
    ".ttf",
    ".pyc",
    ".db",
    ".sqlite",
}


class DevTerminalManager:
    """Manages streaming terminal sessions with live line callbacks & 1-click Stop."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._procs: dict[str, subprocess.Popen] = {}
        self._listeners: list[Callable[[dict[str, Any]], None]] = []

    def add_listener(self, cb: Callable[[dict[str, Any]], None]) -> None:
        if callable(cb) and cb not in self._listeners:
            self._listeners.append(cb)

    def _emit(self, session: dict[str, Any]) -> None:
        snap = self._serialize(session)
        for cb in list(self._listeners):
            try:
                cb(snap)
            except Exception:
                pass

    @staticmethod
    def _serialize(s: dict[str, Any]) -> dict[str, Any]:
        end_ts = s.get("ended_at") or time.time()
        return {
            "id": s["id"],
            "command": s["command"],
            "cwd": s["cwd"],
            "status": s["status"],
            "exit_code": s.get("exit_code"),
            "started_at": s["started_at"],
            "elapsed_s": round(max(0.0, float(end_ts) - float(s["started_at"])), 1),
            "output": "\n".join(s["lines"]),
        }

    def record_completed_run(self, command: str, cwd: str, output: str) -> str:
        """Mirror one-shot shell_agent commands into the HUD Dev Terminal history."""
        sid = f"term-{uuid.uuid4().hex[:8]}"
        now = time.time()
        lines: deque[str] = deque(maxlen=600)
        for ln in (output or "").splitlines()[:600]:
            lines.append(ln)
        rec = {
            "id": sid,
            "command": command,
            "cwd": cwd or str(BASE_DIR),
            "status": "completed",
            "exit_code": 0,
            "started_at": now,
            "ended_at": now,
            "lines": lines,
        }
        with self._lock:
            self._sessions[sid] = rec
            self._prune()
        self._emit(rec)
        return sid

    def _prune(self) -> None:
        if len(self._sessions) <= 20:
            return
        done = [
            k
            for k, v in self._sessions.items()
            if v.get("status") in ("completed", "failed", "stopped")
        ]
        for k in done[: len(self._sessions) - 20]:
            self._sessions.pop(k, None)

    def start_command(self, command: str, cwd: str = "") -> dict[str, Any]:
        cmd = (command or "").strip()
        if not cmd:
            raise ValueError("Terminal command cannot be empty.")
        workdir = Path(cwd).expanduser().resolve() if cwd else BASE_DIR
        if not workdir.is_dir():
            raise ValueError(f"Working directory does not exist: {workdir}")

        sid = f"term-{uuid.uuid4().hex[:8]}"
        lines: deque[str] = deque(maxlen=800)
        lines.append(f"$ {cmd}")
        rec: dict[str, Any] = {
            "id": sid,
            "command": cmd,
            "cwd": str(workdir),
            "status": "running",
            "exit_code": None,
            "started_at": time.time(),
            "ended_at": None,
            "lines": lines,
        }

        popen_kwargs: dict[str, Any] = {}
        if platform.system() == "Windows":
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        else:
            # A separate session lets Stop terminate the shell AND its children.
            popen_kwargs["start_new_session"] = True

        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(workdir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            **popen_kwargs,
        )

        with self._lock:
            self._sessions[sid] = rec
            self._procs[sid] = proc
            self._prune()
        self._emit(rec)

        def _reader() -> None:
            last_push = 0.0
            try:
                assert proc.stdout is not None
                for raw_line in proc.stdout:
                    with self._lock:
                        rec["lines"].append(raw_line.rstrip("\r\n"))
                    now_m = time.monotonic()
                    if now_m - last_push >= 0.06:
                        last_push = now_m
                        self._emit(rec)
            except Exception as exc:
                with self._lock:
                    rec["lines"].append(f"[stream error: {exc}]")
            finally:
                rc = proc.wait()
                with self._lock:
                    self._procs.pop(sid, None)
                    if rec["status"] != "stopped":
                        rec["status"] = "completed" if rc == 0 else "failed"
                    rec["exit_code"] = rc
                    rec["ended_at"] = time.time()
                self._emit(rec)

        threading.Thread(target=_reader, daemon=True, name=f"dev-{sid}").start()
        return self._serialize(rec)

    def send_stdin(self, session_id: str, text: str) -> bool:
        with self._lock:
            proc = self._procs.get(session_id)
            rec = self._sessions.get(session_id)
        if proc is None or proc.stdin is None or proc.poll() is not None:
            return False
        try:
            proc.stdin.write(text + ("\n" if not text.endswith("\n") else ""))
            proc.stdin.flush()
            if rec is not None:
                with self._lock:
                    rec["lines"].append(f"> {text.rstrip()}")
                self._emit(rec)
            return True
        except Exception:
            return False

    def stop_command(self, session_id: str) -> bool:
        with self._lock:
            proc = self._procs.get(session_id)
            rec = self._sessions.get(session_id)
            if rec is not None and rec.get("status") == "running":
                rec["status"] = "stopped"
                rec["ended_at"] = time.time()
                rec["lines"].append("[terminated by user]")
        if proc is None:
            return False
        try:
            if proc.poll() is None:
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   capture_output=True, timeout=5,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    if proc.poll() is None:
                        proc.terminate()
                else:
                    os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=1.5)
                except subprocess.TimeoutExpired:
                    if platform.system() == "Windows":
                        proc.kill()
                    else:
                        os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        if rec is not None:
            self._emit(rec)
        return True

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            items = [self._serialize(s) for s in self._sessions.values()]
        items.sort(key=lambda x: -float(x["started_at"]))
        return items


_TERM_MGR: DevTerminalManager | None = None


def get_terminal_manager() -> DevTerminalManager:
    global _TERM_MGR
    if _TERM_MGR is None:
        _TERM_MGR = DevTerminalManager()
    return _TERM_MGR


# ── Codebase File-Tree Explorer & Safe Reader ─────────────────────────────────

def _resolve_root(root_dir: str = "") -> Path:
    if not root_dir or not root_dir.strip():
        return BASE_DIR.resolve()
    p = Path(root_dir).expanduser().resolve()
    return p if p.is_dir() else BASE_DIR.resolve()


def build_codebase_tree(root_dir: str = "", max_entries: int = 350) -> dict[str, Any]:
    root = _resolve_root(root_dir)
    entries: list[dict[str, Any]] = []

    def _walk(cur: Path, depth: int) -> None:
        if len(entries) >= max_entries or depth > 5:
            return
        try:
            children = sorted(
                cur.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except Exception:
            return
        for ch in children:
            if len(entries) >= max_entries:
                return
            if ch.name in _IGNORED_DIRS or ch.name.startswith(".git"):
                continue
            rel = ch.relative_to(root).as_posix()
            is_dir = ch.is_dir()
            size = 0
            if not is_dir:
                try:
                    size = ch.stat().st_size
                except Exception:
                    size = 0
            entries.append(
                {
                    "path": rel,
                    "name": ch.name,
                    "type": "dir" if is_dir else "file",
                    "depth": depth,
                    "size": size,
                }
            )
            if is_dir:
                _walk(ch, depth + 1)

    _walk(root, 0)
    return {"root": str(root), "entries": entries}


def read_workspace_file(root_dir: str, rel_path: str, max_chars: int = 28000) -> dict[str, Any]:
    root = _resolve_root(root_dir)
    clean_rel = (rel_path or "").strip().lstrip("/")
    if not clean_rel:
        raise ValueError("File path is required.")
    target = (root / clean_rel).resolve()
    # Strict path-traversal protection
    target.relative_to(root)
    if not target.is_file():
        raise FileNotFoundError(f"File not found: {clean_rel}")
    if target.suffix.lower() in _BINARY_EXTS:
        return {
            "path": clean_rel,
            "binary": True,
            "content": f"[Binary file: {target.name} ({target.stat().st_size} bytes)]",
        }
    txt = target.read_text(encoding="utf-8", errors="replace")
    truncated = len(txt) > max_chars
    return {
        "path": clean_rel,
        "binary": False,
        "truncated": truncated,
        "content": txt[:max_chars],
    }


# ── Unified Git Diffs Inspector ───────────────────────────────────────────────

def get_workspace_diffs(root_dir: str = "") -> dict[str, Any]:
    root = _resolve_root(root_dir)
    try:
        st_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=8,
        )
        if st_proc.returncode != 0:
            return {"root": str(root), "is_git": False, "files": []}

        diff_proc = subprocess.run(
            ["git", "diff", "HEAD", "--unified=3"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        raw_diff = diff_proc.stdout or ""
    except Exception:
        return {"root": str(root), "is_git": False, "files": []}

    # Split unified diff per file
    patches_by_file: dict[str, str] = {}
    chunks = raw_diff.split("diff --git ")
    for ch in chunks[1:]:
        first_nl = ch.find("\n")
        header = ch[:first_nl] if first_nl != -1 else ch
        # Extract b/<path>
        parts = header.split(" b/")
        fpath = parts[-1].strip() if len(parts) >= 2 else header.strip()
        patches_by_file[fpath] = ("diff --git " + ch)[:18000]

    files: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in (st_proc.stdout or "").splitlines():
        if len(line) < 4:
            continue
        code = line[:2].strip() or "M"
        fpath = line[3:].strip().strip('"')
        if " -> " in fpath:
            fpath = fpath.split(" -> ")[-1].strip()
        seen.add(fpath)
        patch_txt = patches_by_file.get(fpath, "")
        if not patch_txt and code == "??":
            # Untracked text file preview as all additions
            try:
                preview = read_workspace_file(str(root), fpath, max_chars=8000)
                if not preview["binary"]:
                    added_lines = "\n".join("+" + ln for ln in preview["content"].splitlines()[:150])
                    patch_txt = f"--- /dev/null\n+++ b/{fpath}\n@@ -0,0 +1 @@\n{added_lines}"
            except Exception:
                pass
        adds = sum(
            1
            for ln in patch_txt.splitlines()
            if ln.startswith("+") and not ln.startswith("+++")
        )
        dels = sum(
            1
            for ln in patch_txt.splitlines()
            if ln.startswith("-") and not ln.startswith("---")
        )
        files.append(
            {
                "path": fpath,
                "status": code,
                "additions": adds,
                "deletions": dels,
                "patch": patch_txt,
            }
        )

    return {"root": str(root), "is_git": True, "files": files[:80]}
