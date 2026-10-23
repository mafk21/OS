"""
Cross-platform OS inspection, verified application/terminal launching, and
window/process/port/hardware control.

Why this module exists
----------------------
Previously:
1. `main.py` patched `subprocess.Popen` on Windows with `CREATE_NO_WINDOW`, which
   caused console apps (`powershell.exe`, `cmd.exe`, `wt.exe`, `wsl.exe`) opened
   via `open_app` to spawn invisibly with zero window while JARVIS reported
   "Opened PowerShell."
2. `open_app` used `Popen(..., shell=True)` and blind `Win + type + Enter`
   without checking whether any process or visible window ever appeared.
3. `close_app` pressed `Alt+F4` blindly on whatever window had focus (sometimes
   closing JARVIS itself), and `focus_window` reported success even when no
   matching window existed.

Every launcher and window operation here checks actual OS ground truth (visible
top-level windows + live PIDs) before claiming an app or terminal is open.
"""

from __future__ import annotations

import ctypes
import csv
import io
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore
    _PSUTIL = True
except ImportError:
    psutil = None  # type: ignore
    _PSUTIL = False

_SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"

_WIN_HIDE: dict[str, Any] = (
    {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    if _SYSTEM == "Windows"
    else {}
)

# Protected system processes that JARVIS must never terminate
PROTECTED_PROCESS_STEMS = frozenset({
    "system", "idle", "registry", "smss", "csrss", "wininit", "services",
    "lsass", "svchost", "winlogon", "dwm", "fontdrvhost", "sihost",
    "explorer", "systemd", "init", "kthreadd", "launchd", "windowserver",
    "kernel_task", "loginwindow",
})

# Terminal / shell identifiers that MUST open in a visible interactive console
TERMINAL_KEYS = frozenset({
    "powershell", "powershell.exe", "windows powershell", "powershell 7",
    "pwsh", "pwsh.exe", "cmd", "cmd.exe", "command prompt",
    "wt", "wt.exe", "terminal", "windows terminal",
    "wsl", "wsl.exe", "ubuntu", "git-bash", "git bash", "git-bash.exe",
    "x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal",
    "alacritty", "kitty", "xterm",
})

WINDOW_MATCH_SYNONYMS: dict[str, tuple[str, ...]] = {
    "powershell": ("powershell", "pwsh", "windows powershell", "windowsterminal"),
    "pwsh": ("pwsh", "powershell", "windowsterminal"),
    "cmd": ("cmd", "command prompt", "windowsterminal"),
    "command prompt": ("cmd", "command prompt", "windowsterminal"),
    "terminal": (
        "windowsterminal", "wt", "powershell", "pwsh", "cmd", "terminal",
        "gnome-terminal", "konsole", "xfce4-terminal", "alacritty", "kitty", "xterm",
    ),
    "wt": ("windowsterminal", "wt", "powershell", "cmd"),
    "windows terminal": ("windowsterminal", "wt", "powershell", "cmd"),
    "wsl": ("wsl", "ubuntu", "linux", "windowsterminal"),
    "code": ("visual studio code", "code"),
    "vscode": ("visual studio code", "code"),
    "chrome": ("google chrome", "chrome"),
    "edge": ("microsoft edge", "msedge"),
    "msedge": ("microsoft edge", "msedge"),
    "explorer": ("file explorer", "explorer"),
    "file explorer": ("file explorer", "explorer"),
    "taskmgr": ("task manager", "taskmgr"),
    "task manager": ("task manager", "taskmgr"),
    "settings": ("settings", "system settings", "system preferences", "applicationframehost"),
    "calc": ("calculator", "calc", "applicationframehost"),
    "calculator": ("calculator", "calc", "applicationframehost"),
    "notepad": ("notepad",),
}


def unpatched_popen(*args: Any, **kwargs: Any) -> subprocess.Popen:
    """Invoke the real OS Popen without `main.py`'s CREATE_NO_WINDOW override."""
    real_popen = getattr(subprocess, "_OrigPopen", subprocess.Popen)
    return real_popen(*args, **kwargs)


def _jarvis_pids() -> set[int]:
    pids = {os.getpid()}
    ppid = os.getppid()
    if ppid > 1:
        pids.add(ppid)
    return pids


# ── Process Inspection ───────────────────────────────────────────────────────

def list_processes_snapshot() -> list[dict[str, Any]]:
    """Return running processes using psutil or stdlib OS fallbacks."""
    out: list[dict[str, Any]] = []
    if _PSUTIL:
        for proc in psutil.process_iter(["pid", "name", "exe", "cpu_percent", "memory_info", "cmdline", "status"]):
            try:
                info = proc.info
                status = str(info.get("status") or "")
                if status == getattr(psutil, "STATUS_ZOMBIE", "zombie"):
                    continue
                mem_info = info.get("memory_info")
                mem_mb = (mem_info.rss / (1024 * 1024)) if mem_info else 0.0
                cmdline_list = info.get("cmdline") or []
                out.append({
                    "pid": int(info["pid"]),
                    "name": str(info.get("name") or ""),
                    "exe": str(info.get("exe") or ""),
                    "cpu": float(info.get("cpu_percent") or 0.0),
                    "memory_mb": round(mem_mb, 1),
                    "cmdline": " ".join(cmdline_list)[:240] if isinstance(cmdline_list, list) else "",
                })
            except Exception:
                continue
        return out

    # Stdlib fallbacks when psutil is not installed
    if _SYSTEM == "Windows":
        try:
            r = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=5, **_WIN_HIDE,
            )
            for row in csv.reader(io.StringIO(r.stdout or "")):
                if len(row) >= 5:
                    name, pid_s, _sess, _snum, mem_s = row[:5]
                    digits = re.sub(r"[^\d]", "", mem_s)
                    mem_kb = float(digits) if digits else 0.0
                    out.append({
                        "pid": int(pid_s),
                        "name": name,
                        "exe": name,
                        "cpu": 0.0,
                        "memory_mb": round(mem_kb / 1024.0, 1),
                        "cmdline": "",
                    })
        except Exception:
            pass
    elif _SYSTEM == "Linux" and Path("/proc").is_dir():
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                pid = int(entry.name)
                stat_txt = (entry / "status").read_text(encoding="utf-8", errors="ignore")
                if "State:\tZ" in stat_txt:
                    continue
                name = (entry / "comm").read_text(encoding="utf-8", errors="ignore").strip()
                rss_kb = 0.0
                m = re.search(r"^VmRSS:\s+(\d+)\s+kB", stat_txt, re.MULTILINE)
                if m:
                    rss_kb = float(m.group(1))
                raw_cmd = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
                out.append({
                    "pid": pid,
                    "name": name,
                    "exe": name,
                    "cpu": 0.0,
                    "memory_mb": round(rss_kb / 1024.0, 1),
                    "cmdline": raw_cmd[:240],
                })
            except Exception:
                continue
    elif _SYSTEM == "Darwin":
        try:
            r = subprocess.run(
                ["ps", "-axo", "pid=,pcpu=,rss=,comm="],
                capture_output=True, text=True, timeout=5,
            )
            for line in (r.stdout or "").splitlines():
                parts = line.strip().split(None, 3)
                if len(parts) == 4 and parts[0].isdigit():
                    out.append({
                        "pid": int(parts[0]),
                        "name": Path(parts[3]).name,
                        "exe": parts[3],
                        "cpu": float(parts[1] or 0.0),
                        "memory_mb": round(float(parts[2] or 0.0) / 1024.0, 1),
                        "cmdline": parts[3],
                    })
        except Exception:
            pass
    return out


def _pid_name_map() -> dict[int, str]:
    return {p["pid"]: p["name"] for p in list_processes_snapshot()}


# ── Visible Window Enumeration & Control ─────────────────────────────────────

def _is_win32_window_cloaked(hwnd: int) -> bool:
    """Return True if DWM marks this Win10/11 window as cloaked (invisible UWP shell)."""
    try:
        dwmapi = getattr(ctypes.windll, "dwmapi", None)
        if dwmapi is None:
            return False
        cloaked = ctypes.c_int(0)
        hr = dwmapi.DwmGetWindowAttribute(
            ctypes.c_void_p(hwnd),
            ctypes.c_uint(14),  # DWMWA_CLOAKED
            ctypes.byref(cloaked),
            ctypes.sizeof(cloaked),
        )
        return hr == 0 and cloaked.value != 0
    except Exception:
        return False


def list_visible_windows() -> list[dict[str, Any]]:
    """List genuinely visible top-level windows across Windows, macOS, and Linux."""
    windows: list[dict[str, Any]] = []

    if _SYSTEM == "Windows":
        try:
            user32 = ctypes.windll.user32
            fg_hwnd = int(user32.GetForegroundWindow() or 0)
            pid_names = _pid_name_map()
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080

            def _cb(hwnd_ptr, _lparam):
                hwnd = int(hwnd_ptr or 0)
                if not hwnd or not user32.IsWindowVisible(hwnd):
                    return True
                length = int(user32.GetWindowTextLengthW(hwnd) or 0)
                if length <= 0:
                    return True
                exstyle = int(user32.GetWindowLongW(hwnd, GWL_EXSTYLE) or 0)
                if exstyle & WS_EX_TOOLWINDOW:
                    return True
                if _is_win32_window_cloaked(hwnd):
                    return True
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if not title or title in ("Program Manager", "Windows Input Experience"):
                    return True
                pid_c = ctypes.c_ulong(0)
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_c))
                pid = int(pid_c.value)
                windows.append({
                    "id": hwnd,
                    "title": title,
                    "pid": pid,
                    "process": pid_names.get(pid, ""),
                    "active": hwnd == fg_hwnd,
                    "minimized": bool(user32.IsIconic(hwnd)),
                    "maximized": bool(user32.IsZoomed(hwnd)),
                })
                return True

            user32.EnumWindows(WNDENUMPROC(_cb), 0)
        except Exception:
            pass
        return windows

    if _SYSTEM == "Darwin":
        script = (
            'set out to ""\n'
            'tell application "System Events"\n'
            '  repeat with p in (every application process whose background only is false)\n'
            '    set pName to name of p\n'
            '    set pPid to unix id of p\n'
            '    set isFront to frontmost of p\n'
            '    try\n'
            '      set wNames to name of every window of p\n'
            '      if (count of wNames) > 0 then\n'
            '        repeat with w in wNames\n'
            '          set out to out & pPid & "\\t" & isFront & "\\t" & pName & "\\t" & (w as text) & "\\n"\n'
            '        end repeat\n'
            '      else\n'
            '        set out to out & pPid & "\\t" & isFront & "\\t" & pName & "\\t" & pName & "\\n"\n'
            '      end if\n'
            '    end try\n'
            '  end repeat\n'
            'end tell\n'
            'return out'
        )
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            for line in (r.stdout or "").splitlines():
                parts = line.split("\t", 3)
                if len(parts) == 4:
                    pid_s, front_s, proc_name, w_title = parts
                    windows.append({
                        "id": f"{proc_name}:{w_title}",
                        "title": w_title.strip() or proc_name.strip(),
                        "pid": int(pid_s) if pid_s.strip().isdigit() else 0,
                        "process": proc_name.strip(),
                        "active": front_s.strip().lower() == "true",
                        "minimized": False,
                        "maximized": False,
                    })
        except Exception:
            pass
        return windows

    # Linux (X11 / XWayland via wmctrl or xdotool)
    if shutil.which("wmctrl"):
        try:
            active_hex = ""
            if shutil.which("xprop"):
                xr = subprocess.run(
                    ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
                    capture_output=True, text=True, timeout=2,
                )
                m = re.search(r"0x[0-9a-fA-F]+", xr.stdout or "")
                if m:
                    active_hex = int(m.group(0), 16)
            pid_names = _pid_name_map()
            r = subprocess.run(["wmctrl", "-lp"], capture_output=True, text=True, timeout=3)
            for line in (r.stdout or "").splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    wid_hex, _desk, pid_s, _host, title = parts
                    pid = int(pid_s) if pid_s.isdigit() else 0
                    wid_int = int(wid_hex, 16) if wid_hex.startswith("0x") else 0
                    windows.append({
                        "id": wid_hex,
                        "title": title.strip(),
                        "pid": pid,
                        "process": pid_names.get(pid, ""),
                        "active": bool(active_hex and wid_int == active_hex),
                        "minimized": False,
                        "maximized": False,
                    })
        except Exception:
            pass
    elif shutil.which("xdotool"):
        try:
            pid_names = _pid_name_map()
            r = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", "."],
                capture_output=True, text=True, timeout=3,
            )
            for wid in (r.stdout or "").splitlines():
                wid = wid.strip()
                if not wid:
                    continue
                tn = subprocess.run(["xdotool", "getwindowname", wid], capture_output=True, text=True, timeout=1)
                tp = subprocess.run(["xdotool", "getwindowpid", wid], capture_output=True, text=True, timeout=1)
                title = (tn.stdout or "").strip()
                if not title:
                    continue
                pid = int(tp.stdout.strip()) if (tp.stdout or "").strip().isdigit() else 0
                windows.append({
                    "id": wid,
                    "title": title,
                    "pid": pid,
                    "process": pid_names.get(pid, ""),
                    "active": False,
                    "minimized": False,
                    "maximized": False,
                })
        except Exception:
            pass
    return windows


def _search_tokens_for(query: str) -> tuple[str, ...]:
    q = re.sub(r"^(the|a|an|my|app|application|window)\s+", "", (query or "").strip().lower()).strip()
    if not q:
        return ()
    stem = q[:-4] if q.endswith(".exe") else q
    syns = WINDOW_MATCH_SYNONYMS.get(q) or WINDOW_MATCH_SYNONYMS.get(stem)
    if syns:
        return tuple(dict.fromkeys((q, stem, *syns)))
    return tuple(dict.fromkeys((q, stem)))


def find_windows(query: str, windows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Find visible windows matching `query` by window title or owning process."""
    tokens = _search_tokens_for(query)
    if not tokens:
        return []
    pool = windows if windows is not None else list_visible_windows()
    scored: list[tuple[int, dict[str, Any]]] = []
    for w in pool:
        title_l = str(w.get("title") or "").lower()
        proc_l = str(w.get("process") or "").lower()
        proc_stem = proc_l[:-4] if proc_l.endswith(".exe") else proc_l
        best = 0
        for tok in tokens:
            if not tok:
                continue
            if proc_stem == tok or title_l == tok:
                best = max(best, 100)
            elif re.search(rf"\b{re.escape(tok)}\b", title_l) or re.search(rf"\b{re.escape(tok)}\b", proc_stem):
                best = max(best, 80)
            elif len(tok) >= 3 and (tok in title_l or tok in proc_stem):
                best = max(best, 55)
        if best > 0:
            if w.get("active"):
                best += 5
            scored.append((best, w))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [w for _, w in scored]


def focus_win32_hwnd(hwnd: int) -> bool:
    """Bring a Win32 HWND reliably into the foreground (unlocking ForegroundLockTimeout)."""
    if _SYSTEM != "Windows" or not hwnd:
        return False
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        SW_RESTORE = 9
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        fg = int(user32.GetForegroundWindow() or 0)
        cur_tid = int(kernel32.GetCurrentThreadId())
        fg_tid = int(user32.GetWindowThreadProcessId(fg, None)) if fg else 0
        attached = False
        if fg_tid and fg_tid != cur_tid:
            attached = bool(user32.AttachThreadInput(cur_tid, fg_tid, True))
        try:
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        finally:
            if attached:
                user32.AttachThreadInput(cur_tid, fg_tid, False)
        return True
    except Exception:
        return False


def control_window(target: str, op: str) -> tuple[bool, str]:
    """Perform `focus | minimize | maximize | restore | close | snap_left | snap_right` on a named window."""
    op = (op or "focus").strip().lower()
    matches = find_windows(target)
    if not matches:
        return False, f"No visible window matching '{target}' is currently open."

    win = matches[0]
    wid = win["id"]
    title = win["title"]
    pid = int(win.get("pid") or 0)

    if op == "close" and pid in _jarvis_pids():
        return False, "Refusing to close JARVIS's own window via close_window (say shutdown_jarvis to exit)."

    if _SYSTEM == "Windows":
        try:
            user32 = ctypes.windll.user32
            hwnd = int(wid)
            SW_MINIMIZE = 6
            SW_MAXIMIZE = 3
            SW_RESTORE = 9
            WM_CLOSE = 0x0010

            if op == "focus":
                ok = focus_win32_hwnd(hwnd)
                return ok, (f"Focused window '{title}' (PID {pid})." if ok else f"Could not focus '{title}'.")
            if op == "minimize":
                user32.ShowWindow(hwnd, SW_MINIMIZE)
                return True, f"Minimized '{title}'."
            if op == "maximize":
                user32.ShowWindow(hwnd, SW_MAXIMIZE)
                focus_win32_hwnd(hwnd)
                return True, f"Maximized '{title}'."
            if op == "restore":
                user32.ShowWindow(hwnd, SW_RESTORE)
                focus_win32_hwnd(hwnd)
                return True, f"Restored '{title}'."
            if op == "close":
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                time.sleep(0.35)
                still_open = bool(user32.IsWindow(hwnd) and user32.IsWindowVisible(hwnd))
                if still_open:
                    return True, f"Sent close request to '{title}' (window may have an unsaved-changes prompt)."
                return True, f"Closed window '{title}'."
            if op in ("snap_left", "snap_right"):
                class RECT(ctypes.Structure):
                    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
                rc = RECT()
                SPI_GETWORKAREA = 0x0030
                user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rc), 0)
                w_half = max(400, (rc.right - rc.left) // 2)
                h_full = max(300, rc.bottom - rc.top)
                x = rc.left if op == "snap_left" else (rc.left + w_half)
                user32.ShowWindow(hwnd, SW_RESTORE)
                user32.SetWindowPos(hwnd, 0, x, rc.top, w_half, h_full, 0x0040)
                focus_win32_hwnd(hwnd)
                side = "left" if op == "snap_left" else "right"
                return True, f"Snapped '{title}' to the {side} half of the screen."
        except Exception as e:
            return False, f"Window operation '{op}' on '{title}' failed: {e}"

    if _SYSTEM == "Darwin":
        proc = win.get("process") or target
        try:
            if op == "focus":
                subprocess.run(
                    ["osascript", "-e", f'tell application "{proc}" to activate'],
                    capture_output=True, timeout=5,
                )
                return True, f"Focused '{title}' ({proc})."
            if op == "close":
                subprocess.run(
                    ["osascript", "-e", f'tell application "{proc}" to close window 1'],
                    capture_output=True, timeout=5,
                )
                return True, f"Closed front window of {proc}."
            if op == "minimize":
                subprocess.run(
                    ["osascript", "-e", f'tell application "System Events" to tell process "{proc}" to set miniaturized of window 1 to true'],
                    capture_output=True, timeout=5,
                )
                return True, f"Minimized '{title}'."
        except Exception as e:
            return False, f"macOS window '{op}' failed: {e}"

    if _SYSTEM == "Linux" and shutil.which("wmctrl"):
        try:
            wid_s = str(wid)
            if op == "focus":
                subprocess.run(["wmctrl", "-i", "-a", wid_s], capture_output=True, timeout=3)
                return True, f"Focused '{title}'."
            if op == "close":
                subprocess.run(["wmctrl", "-i", "-c", wid_s], capture_output=True, timeout=3)
                return True, f"Closed '{title}'."
            if op == "maximize":
                subprocess.run(["wmctrl", "-i", "-r", wid_s, "-b", "add,maximized_vert,maximized_horz"], capture_output=True, timeout=3)
                return True, f"Maximized '{title}'."
            if op == "minimize":
                if shutil.which("xdotool"):
                    subprocess.run(["xdotool", "windowminimize", wid_s], capture_output=True, timeout=3)
                    return True, f"Minimized '{title}'."
        except Exception as e:
            return False, f"Linux window '{op}' failed: {e}"

    return False, f"Window action '{op}' is not supported on this display server."


# ── Post-Launch Verification ─────────────────────────────────────────────────

def verify_launch(
    query: str,
    before_pids: set[int],
    before_win_ids: set[Any],
    spawned_pid: int | None = None,
    timeout: float = 3.2,
) -> dict[str, Any]:
    """Poll OS windows & process table to confirm an app/terminal genuinely opened."""
    tokens = _search_tokens_for(query)
    deadline = time.monotonic() + max(0.3, timeout)
    found_proc: dict[str, Any] | None = None

    while time.monotonic() < deadline:
        wins = list_visible_windows()
        # 1. Brand-new visible window matching the app (ideal confirmation!)
        new_wins = [w for w in wins if w["id"] not in before_win_ids]
        matched_new = find_windows(query, new_wins)
        if matched_new:
            w = matched_new[0]
            if _SYSTEM == "Windows":
                focus_win32_hwnd(int(w["id"]))
            return {
                "verified": True,
                "window_title": w["title"],
                "pid": w.get("pid") or spawned_pid,
                "process": w.get("process") or "",
                "new_window": True,
            }
        if spawned_pid:
            by_pid = [w for w in new_wins if int(w.get("pid") or 0) == spawned_pid]
            if by_pid:
                w = by_pid[0]
                if _SYSTEM == "Windows":
                    focus_win32_hwnd(int(w["id"]))
                return {
                    "verified": True,
                    "window_title": w["title"],
                    "pid": spawned_pid,
                    "process": w.get("process") or "",
                    "new_window": True,
                }

        # 2. Existing visible window for single-instance apps (Chrome, Explorer, Settings, VS Code)
        matched_existing = find_windows(query, wins)
        procs = list_processes_snapshot()
        new_procs = [p for p in procs if p["pid"] not in before_pids]
        for p in new_procs:
            pname = p["name"].lower()
            pstem = pname[:-4] if pname.endswith(".exe") else pname
            if spawned_pid and p["pid"] == spawned_pid:
                found_proc = p
                break
            if any(tok and (pstem == tok or tok in pname or tok in p.get("cmdline", "").lower()) for tok in tokens):
                found_proc = p
                break

        if matched_existing and (found_proc is not None or time.monotonic() + 0.6 >= deadline):
            w = matched_existing[0]
            if _SYSTEM == "Windows":
                focus_win32_hwnd(int(w["id"]))
            return {
                "verified": True,
                "window_title": w["title"],
                "pid": w.get("pid") or (found_proc["pid"] if found_proc else spawned_pid),
                "process": w.get("process") or (found_proc["name"] if found_proc else ""),
                "new_window": False,
            }

        time.sleep(0.18)

    # Final check: did a process stay alive without a top-level window (e.g. tray app or headless)?
    if found_proc is not None:
        live_pids = {p["pid"] for p in list_processes_snapshot()}
        if found_proc["pid"] in live_pids:
            return {
                "verified": True,
                "window_title": None,
                "pid": found_proc["pid"],
                "process": found_proc["name"],
                "new_window": False,
            }

    return {
        "verified": False,
        "window_title": None,
        "pid": None,
        "process": None,
        "new_window": False,
    }


# ── Windows Target Resolution (No Blind Start-Menu Bing Searches!) ───────────

def _find_windows_app_path_registry(exe_name: str) -> str | None:
    if _SYSTEM != "Windows":
        return None
    try:
        import winreg
        cand = exe_name if exe_name.lower().endswith(".exe") else f"{exe_name}.exe"
        subkey = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{cand}"
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, subkey) as k:
                    val, _ = winreg.QueryValueEx(k, "")
                    if val:
                        p = val.strip('"')
                        if Path(p).exists():
                            return p
            except OSError:
                continue
    except Exception:
        pass
    return None


def _find_windows_start_shortcut(app_name: str) -> str | None:
    if _SYSTEM != "Windows":
        return None
    needle = re.sub(r"[^a-z0-9]+", " ", app_name.lower()).strip()
    if not needle:
        return None
    roots = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path.home() / "Desktop",
    ]
    best_match: tuple[int, str] | None = None
    for root in roots:
        if not root.is_dir():
            continue
        try:
            for lnk in root.rglob("*.lnk"):
                stem = re.sub(r"[^a-z0-9]+", " ", lnk.stem.lower()).strip()
                if "uninstall" in stem:
                    continue
                score = 0
                if stem == needle:
                    score = 100
                elif needle in stem.split():
                    score = 85
                elif len(needle) >= 4 and needle in stem:
                    score = 65
                if score and (best_match is None or score > best_match[0]):
                    best_match = (score, str(lnk))
                    if score == 100:
                        return str(lnk)
        except Exception:
            continue
    return best_match[1] if best_match else None


def _find_windows_uwp_appid(app_name: str) -> str | None:
    """Query Get-StartApps for Store/UWP/MSIX AppIDs (e.g. WhatsApp, Spotify, Calculator)."""
    if _SYSTEM != "Windows":
        return None
    safe = re.sub(r"[^a-zA-Z0-9 ._-]", "", app_name).strip()
    if not safe:
        return None
    ps_cmd = (
        f"$q = '{safe}'.ToLower(); "
        "Get-StartApps | Where-Object { $_.Name.ToLower() -eq $q -or $_.Name.ToLower().Contains($q) } "
        "| Select-Object -First 1 -ExpandProperty AppID"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=4, **_WIN_HIDE,
        )
        appid = (r.stdout or "").strip().splitlines()
        if appid and appid[0].strip():
            return f"shell:AppsFolder\\{appid[0].strip()}"
    except Exception:
        pass
    return None


def _win32_shell_execute(
    target: str,
    params: str = "",
    cwd: str = "",
    admin: bool = False,
) -> tuple[bool, str]:
    """Launch `target` via ShellExecuteW with SW_SHOWNORMAL=1 (guaranteed visible window)."""
    if _SYSTEM != "Windows":
        return False, "ShellExecuteW is Windows-only"
    try:
        verb = "runas" if admin else "open"
        workdir = str(Path(cwd).expanduser()) if cwd else None
        SW_SHOWNORMAL = 1
        res = ctypes.windll.shell32.ShellExecuteW(
            None,
            verb,
            str(target),
            params if params else None,
            workdir,
            SW_SHOWNORMAL,
        )
        # ShellExecuteW returns HINSTANCE > 32 on success
        if int(res) > 32:
            return True, "ShellExecuteW succeeded"
        return False, f"ShellExecuteW returned error code {int(res)}"
    except Exception as e:
        return False, str(e)


# ── Interactive Terminal / PowerShell Launcher ───────────────────────────────

def _resolve_windows_terminal_exe(shell_name: str) -> tuple[str | None, str]:
    key = (shell_name or "powershell").strip().lower()
    sys_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    local_app = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))

    if key in ("pwsh", "pwsh.exe", "powershell 7", "powershell7"):
        exe = shutil.which("pwsh.exe") or shutil.which("pwsh")
        if exe:
            return exe, "pwsh"
        # Fall back to Windows PowerShell if PowerShell 7 isn't installed
        key = "powershell"

    if key in ("powershell", "powershell.exe", "windows powershell"):
        exe = shutil.which("powershell.exe") or shutil.which("powershell")
        fallback = sys_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        if not exe and fallback.exists():
            exe = str(fallback)
        return exe, "powershell"

    if key in ("cmd", "cmd.exe", "command prompt"):
        exe = shutil.which("cmd.exe") or shutil.which("cmd")
        fallback = sys_root / "System32" / "cmd.exe"
        if not exe and fallback.exists():
            exe = str(fallback)
        return exe, "cmd"

    if key in ("wt", "wt.exe", "windows terminal", "terminal"):
        exe = shutil.which("wt.exe") or shutil.which("wt")
        wt_alias = local_app / "Microsoft" / "WindowsApps" / "wt.exe"
        if not exe and wt_alias.exists():
            exe = str(wt_alias)
        if exe:
            return exe, "wt"
        # Fall back cleanly to Windows PowerShell when Windows Terminal isn't installed
        ps_exe, _ = _resolve_windows_terminal_exe("powershell")
        return ps_exe, "powershell"

    if key in ("wsl", "wsl.exe", "ubuntu"):
        exe = shutil.which("wsl.exe") or shutil.which("wsl")
        fallback = sys_root / "System32" / "wsl.exe"
        if not exe and fallback.exists():
            exe = str(fallback)
        return exe, "wsl"

    if key in ("git-bash", "git bash", "git-bash.exe"):
        exe = shutil.which("git-bash.exe") or shutil.which("git-bash")
        for cand in (
            Path(r"C:\Program Files\Git\git-bash.exe"),
            local_app / "Programs" / "Git" / "git-bash.exe",
        ):
            if not exe and cand.exists():
                exe = str(cand)
        return exe, "git-bash"

    exe = shutil.which(shell_name)
    return exe, key


def open_interactive_terminal(
    shell_name: str = "powershell",
    cwd: str = "",
    command: str = "",
    admin: bool = False,
    verify_timeout: float = 3.5,
) -> dict[str, Any]:
    """Open a VISIBLE interactive terminal/PowerShell window and verify it appeared."""
    workdir = ""
    if cwd:
        p = Path(cwd).expanduser()
        if not p.is_dir():
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": f"Failed to open terminal: directory does not exist: {cwd}",
            }
        workdir = str(p.resolve())

    before_pids = {p["pid"] for p in list_processes_snapshot()}
    before_wins = {w["id"] for w in list_visible_windows()}

    if _SYSTEM == "Windows":
        exe, kind = _resolve_windows_terminal_exe(shell_name)
        if not exe:
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": f"Failed to open '{shell_name}': executable is not installed on this Windows machine.",
            }

        params_list: list[str] = []
        if kind in ("powershell", "pwsh"):
            params_list.append("-NoExit")
            if workdir and not command:
                params_list.extend(["-Command", f"Set-Location -LiteralPath '{workdir}'"])
            elif command:
                cd_prefix = f"Set-Location -LiteralPath '{workdir}'; " if workdir else ""
                params_list.extend(["-Command", f"{cd_prefix}{command}"])
        elif kind == "cmd":
            if command:
                params_list.extend(["/K", command])
        elif kind == "wt":
            if workdir:
                params_list.extend(["-d", workdir])
            if command:
                params_list.extend(["powershell", "-NoExit", "-Command", command])
        elif kind == "wsl":
            if workdir:
                params_list.extend(["--cd", workdir])

        params_str = subprocess.list2cmdline(params_list) if params_list else ""
        spawned_pid: int | None = None

        ok_shell, shell_err = _win32_shell_execute(
            exe, params=params_str, cwd=workdir, admin=admin
        )
        if not ok_shell and not admin:
            try:
                CREATE_NEW_CONSOLE = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010)
                proc = unpatched_popen(
                    [exe, *params_list],
                    cwd=workdir or None,
                    creationflags=CREATE_NEW_CONSOLE,
                    close_fds=True,
                )
                spawned_pid = proc.pid
                ok_shell = True
            except Exception as e:
                shell_err = str(e)

        if not ok_shell:
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": f"Failed to open {shell_name}: {shell_err}",
            }

        ver = verify_launch(
            kind,
            before_pids=before_pids,
            before_win_ids=before_wins,
            spawned_pid=spawned_pid,
            timeout=verify_timeout,
        )
        if ver["verified"] and ver["window_title"]:
            return {
                "ok": True,
                "verified_window": ver["window_title"],
                "pid": ver["pid"],
                "message": (
                    f"Opened {shell_name} — verified visible window "
                    f"'{ver['window_title']}' (PID {ver['pid']})."
                ),
            }
        if ver["verified"]:
            return {
                "ok": True,
                "verified_window": None,
                "pid": ver["pid"],
                "message": (
                    f"Started {shell_name} process (PID {ver['pid']}), though no "
                    f"foreground window title was detected yet."
                ),
            }
        return {
            "ok": False,
            "verified_window": None,
            "pid": None,
            "message": (
                f"Failed to confirm {shell_name} opened — no visible window or "
                f"running {kind} process appeared on screen."
            ),
        }

    if _SYSTEM == "Darwin":
        cmd_parts = []
        if workdir:
            cmd_parts.append(f"cd {subprocess.list2cmdline([workdir])}")
        if command:
            cmd_parts.append(command)
        do_line = "; ".join(cmd_parts)
        escaped = do_line.replace("\\", "\\\\").replace('"', '\\"')
        script = (
            'tell application "Terminal"\n'
            '  activate\n'
            f'  do script "{escaped}"\n'
            'end tell'
        )
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=6)
            if r.returncode != 0:
                return {
                    "ok": False,
                    "verified_window": None,
                    "pid": None,
                    "message": f"Failed to open macOS Terminal: {(r.stderr or '').strip()}",
                }
            ver = verify_launch("terminal", before_pids, before_wins, timeout=verify_timeout)
            return {
                "ok": True,
                "verified_window": ver.get("window_title") or "Terminal",
                "pid": ver.get("pid"),
                "message": f"Opened macOS Terminal (window '{ver.get('window_title') or 'Terminal'}').",
            }
        except Exception as e:
            return {"ok": False, "verified_window": None, "pid": None, "message": f"Failed to open Terminal: {e}"}

    # Linux
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if not has_display:
        return {
            "ok": False,
            "verified_window": None,
            "pid": None,
            "message": (
                f"Cannot open a visible '{shell_name}' window: no graphical display "
                f"(DISPLAY / WAYLAND_DISPLAY) is active. Use shell_agent(action='run') "
                f"to run commands in this session instead."
            ),
        }

    term_candidates = [
        "x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal",
        "alacritty", "kitty", "tilix", "mate-terminal", "lxterminal", "xterm",
    ]
    chosen = None
    for cand in term_candidates:
        if shutil.which(cand):
            chosen = cand
            break
    if not chosen:
        return {
            "ok": False,
            "verified_window": None,
            "pid": None,
            "message": "No graphical terminal emulator is installed on this Linux system.",
        }

    argv = [chosen]
    if command:
        argv.extend(["-e", "bash", "-lc", f"{command}; exec bash"])
    try:
        proc = unpatched_popen(
            argv,
            cwd=workdir or None,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        ver = verify_launch("terminal", before_pids, before_wins, spawned_pid=proc.pid, timeout=verify_timeout)
        if proc.poll() is not None and not ver["verified"]:
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": f"Terminal '{chosen}' exited immediately without opening a window.",
            }
        return {
            "ok": True,
            "verified_window": ver.get("window_title"),
            "pid": ver.get("pid") or proc.pid,
            "message": f"Opened terminal '{chosen}' (PID {ver.get('pid') or proc.pid}).",
        }
    except Exception as e:
        return {"ok": False, "verified_window": None, "pid": None, "message": f"Failed to open terminal: {e}"}


# ── General Application / Folder / URI Launcher with Verification ────────────

SPECIAL_USER_FOLDERS: dict[str, str] = {
    "downloads": "Downloads",
    "downloads folder": "Downloads",
    "documents": "Documents",
    "documents folder": "Documents",
    "my documents": "Documents",
    "pictures": "Pictures",
    "photos folder": "Pictures",
    "videos": "Videos",
    "music": "Music",
    "desktop": "Desktop",
    "desktop folder": "Desktop",
    "home": "",
    "home folder": "",
}


def launch_application(
    app_name: str,
    normalized: str = "",
    args: str = "",
    cwd: str = "",
    command: str = "",
    admin: bool = False,
    verify_timeout: float = 3.2,
) -> dict[str, Any]:
    """Launch an application, console, folder, or URI and verify OS ground truth."""
    raw = (app_name or "").strip()
    clean_key = re.sub(r"^(the|a|an|my)\s+", "", raw.lower()).strip()
    target = (normalized or raw).strip()
    target_low = target.lower()

    # 1. Interactive terminals / shells ALWAYS go through open_interactive_terminal
    if clean_key in TERMINAL_KEYS or target_low in TERMINAL_KEYS:
        shell_choice = clean_key if clean_key in TERMINAL_KEYS else target_low
        return open_interactive_terminal(
            shell_name=shell_choice,
            cwd=cwd,
            command=command or args,
            admin=admin,
            verify_timeout=verify_timeout,
        )

    # 2. Special user folders ("Downloads", "Documents", etc.) or explicit paths
    if clean_key in SPECIAL_USER_FOLDERS:
        sub = SPECIAL_USER_FOLDERS[clean_key]
        folder = (Path.home() / sub) if sub else Path.home()
        if folder.exists():
            return open_path_verified(str(folder), label=raw)

    expanded_path = Path(raw).expanduser()
    if ("/" in raw or "\\" in raw or raw.startswith("~")) and expanded_path.exists():
        return open_path_verified(str(expanded_path), label=raw)

    before_pids = {p["pid"] for p in list_processes_snapshot()}
    before_wins = {w["id"] for w in list_visible_windows()}

    # 3. Windows launch pipeline (deterministic resolution -> ShellExecuteW -> verify)
    if _SYSTEM == "Windows":
        # URI schemes (ms-settings:, ms-windows-store:, https://, spotify:, etc.)
        if ":" in target and not re.match(r"^[a-zA-Z]:[\\/]", target):
            ok, err = _win32_shell_execute(target)
            if not ok:
                try:
                    os.startfile(target)  # type: ignore[attr-defined]
                    ok = True
                except Exception as e:
                    err = str(e)
            if not ok:
                return {"ok": False, "verified_window": None, "pid": None, "message": f"Failed to open '{raw}' ({target}): {err}"}
            q_hint = "settings" if target_low.startswith("ms-settings:") else raw
            ver = verify_launch(q_hint, before_pids, before_wins, timeout=verify_timeout)
            if ver["verified"]:
                w_info = f"window '{ver['window_title']}'" if ver["window_title"] else f"PID {ver['pid']}"
                return {"ok": True, "verified_window": ver["window_title"], "pid": ver["pid"], "message": f"Opened {raw} — verified ({w_info})."}
            return {"ok": True, "verified_window": None, "pid": None, "message": f"Dispatched URI '{target}' for {raw}."}

        resolved = (
            shutil.which(target)
            or (shutil.which(f"{target}.exe") if not target_low.endswith((".exe", ".msc", ".cpl")) else None)
            or _find_windows_app_path_registry(target)
            or _find_windows_start_shortcut(raw)
            or (
                _find_windows_start_shortcut(target)
                if target_low != raw.lower()
                else None
            )
            or _find_windows_uwp_appid(raw)
            or (
                _find_windows_uwp_appid(target)
                if target_low != raw.lower()
                else None
            )
        )

        # System32 .msc / .cpl snap-ins (devmgmt.msc, services.msc, control.exe, etc.)
        if not resolved and target_low.endswith((".msc", ".cpl")):
            sys32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / target
            if sys32.exists():
                resolved = str(sys32)

        if not resolved:
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": (
                    f"Could not open '{raw}': application was not found in PATH, "
                    f"Windows App Paths registry, Start Menu shortcuts, or Microsoft Store apps."
                ),
            }

        ok, err = _win32_shell_execute(resolved, params=args, cwd=cwd, admin=admin)
        spawned_pid: int | None = None
        if not ok and not resolved.startswith("shell:"):
            try:
                argv = [resolved] + ([args] if args else [])
                proc = unpatched_popen(argv, cwd=cwd or None, close_fds=True)
                spawned_pid = proc.pid
                ok = True
            except Exception as e:
                err = str(e)

        if not ok:
            return {
                "ok": False,
                "verified_window": None,
                "pid": None,
                "message": f"Failed to launch '{raw}' ({resolved}): {err}",
            }

        ver = verify_launch(raw, before_pids, before_wins, spawned_pid=spawned_pid, timeout=verify_timeout)
        if not ver["verified"] and target_low != raw.lower():
            ver = verify_launch(target, before_pids, before_wins, spawned_pid=spawned_pid, timeout=0.8)

        if ver["verified"]:
            if ver["window_title"]:
                return {
                    "ok": True,
                    "verified_window": ver["window_title"],
                    "pid": ver["pid"],
                    "message": f"Opened {raw} — verified visible window '{ver['window_title']}' (PID {ver['pid']}).",
                }
            return {
                "ok": True,
                "verified_window": None,
                "pid": ver["pid"],
                "message": f"Started {raw} (process '{ver['process']}', PID {ver['pid']}; no foreground window title yet).",
            }

        return {
            "ok": False,
            "verified_window": None,
            "pid": None,
            "message": (
                f"Attempted to launch '{raw}' ({resolved}), but no running process or "
                f"visible window appeared."
            ),
        }

    # 4. macOS launch pipeline
    if _SYSTEM == "Darwin":
        for candidate in dict.fromkeys([target, raw, f"{target}.app"]):
            try:
                cmd = ["open", "-a", candidate]
                if args:
                    cmd.extend(["--args", *args.split()])
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                if r.returncode == 0:
                    ver = verify_launch(raw, before_pids, before_wins, timeout=verify_timeout)
                    w_txt = f"window '{ver['window_title']}'" if ver.get("window_title") else "app activated"
                    return {
                        "ok": True,
                        "verified_window": ver.get("window_title"),
                        "pid": ver.get("pid"),
                        "message": f"Opened {raw} ({w_txt}).",
                    }
            except Exception:
                continue

        binary = shutil.which(target) or shutil.which(raw.lower())
        if binary:
            try:
                proc = unpatched_popen([binary], cwd=cwd or None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                ver = verify_launch(raw, before_pids, before_wins, spawned_pid=proc.pid, timeout=verify_timeout)
                if ver["verified"]:
                    return {"ok": True, "verified_window": ver.get("window_title"), "pid": ver.get("pid") or proc.pid, "message": f"Opened {raw} (PID {ver.get('pid') or proc.pid})."}
            except Exception:
                pass

        return {
            "ok": False,
            "verified_window": None,
            "pid": None,
            "message": f"Could not open '{raw}': application is not installed in /Applications or PATH.",
        }

    # 5. Linux launch pipeline
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    candidates = list(dict.fromkeys([
        target,
        raw,
        raw.lower(),
        raw.lower().replace(" ", "-"),
        raw.lower().replace(" ", "_"),
    ]))

    for cand in candidates:
        parts = cand.split()
        binary = shutil.which(parts[0])
        if binary:
            if not has_display:
                return {
                    "ok": False,
                    "verified_window": None,
                    "pid": None,
                    "message": (
                        f"'{raw}' ({binary}) is installed, but no graphical display "
                        f"(DISPLAY / WAYLAND_DISPLAY) is active to open a GUI window."
                    ),
                }
            try:
                argv = [binary, *parts[1:]] + (args.split() if args else [])
                proc = unpatched_popen(
                    argv,
                    cwd=cwd or None,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                ver = verify_launch(raw, before_pids, before_wins, spawned_pid=proc.pid, timeout=verify_timeout)
                if proc.poll() is not None and not ver["verified"]:
                    return {
                        "ok": False,
                        "verified_window": None,
                        "pid": None,
                        "message": f"'{raw}' exited immediately (code {proc.returncode}) without opening a window.",
                    }
                return {
                    "ok": True,
                    "verified_window": ver.get("window_title"),
                    "pid": ver.get("pid") or proc.pid,
                    "message": f"Opened {raw} (PID {ver.get('pid') or proc.pid}).",
                }
            except Exception:
                continue

    if shutil.which("gtk-launch") and has_display:
        for desk in (raw.lower(), raw.lower().replace(" ", "-")):
            try:
                r = subprocess.run(["gtk-launch", desk], capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    ver = verify_launch(raw, before_pids, before_wins, timeout=verify_timeout)
                    return {"ok": True, "verified_window": ver.get("window_title"), "pid": ver.get("pid"), "message": f"Opened {raw} via desktop entry '{desk}'."}
            except Exception:
                continue

    return {
        "ok": False,
        "verified_window": None,
        "pid": None,
        "message": f"Could not open '{raw}': application was not found on this machine.",
    }


def open_path_verified(path_str: str, label: str = "") -> dict[str, Any]:
    """Open a local folder or file in the OS file manager / default viewer."""
    p = Path(path_str).expanduser()
    if not p.exists():
        return {"ok": False, "verified_window": None, "pid": None, "message": f"Path does not exist: {path_str}"}
    resolved = str(p.resolve())
    disp = label or p.name or resolved
    before_pids = {pr["pid"] for pr in list_processes_snapshot()}
    before_wins = {w["id"] for w in list_visible_windows()}

    if _SYSTEM == "Windows":
        ok, err = _win32_shell_execute(resolved)
        if not ok:
            try:
                os.startfile(resolved)  # type: ignore[attr-defined]
                ok = True
            except Exception as e:
                err = str(e)
        if not ok:
            return {"ok": False, "verified_window": None, "pid": None, "message": f"Failed to open '{disp}': {err}"}
        ver = verify_launch(p.name or "explorer", before_pids, before_wins, timeout=2.5)
        w_note = f" (window '{ver['window_title']}')" if ver.get("window_title") else ""
        return {"ok": True, "verified_window": ver.get("window_title"), "pid": ver.get("pid"), "message": f"Opened '{disp}'{w_note}."}

    if _SYSTEM == "Darwin":
        r = subprocess.run(["open", resolved], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return {"ok": True, "verified_window": disp, "pid": None, "message": f"Opened '{disp}'."}
        return {"ok": False, "verified_window": None, "pid": None, "message": f"Failed to open '{disp}': {(r.stderr or '').strip()}"}

    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return {"ok": False, "verified_window": None, "pid": None, "message": f"Path '{resolved}' exists, but no graphical display is active to open a file manager window."}
    if shutil.which("xdg-open"):
        r = subprocess.run(["xdg-open", resolved], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return {"ok": True, "verified_window": disp, "pid": None, "message": f"Opened '{disp}'."}
    return {"ok": False, "verified_window": None, "pid": None, "message": f"Could not open '{disp}' (xdg-open unavailable)."}


# ── Port, Disk, Battery, Network & Installed-App Inspection ──────────────────

def list_listening_ports(port_filter: int | None = None) -> list[dict[str, Any]]:
    """Return listening TCP/UDP ports with owning PID & process name."""
    results: list[dict[str, Any]] = []
    pid_names = _pid_name_map()

    if _PSUTIL:
        try:
            for c in psutil.net_connections(kind="inet"):
                status = str(getattr(c, "status", "") or "")
                if status and status not in ("LISTEN", "NONE"):
                    continue
                if not c.laddr:
                    continue
                lport = int(c.laddr.port)
                if port_filter is not None and lport != int(port_filter):
                    continue
                pid = int(c.pid or 0)
                results.append({
                    "port": lport,
                    "ip": str(c.laddr.ip),
                    "proto": "tcp" if c.type == socket.SOCK_STREAM else "udp",
                    "pid": pid,
                    "process": pid_names.get(pid, ""),
                })
            if results:
                results.sort(key=lambda r: (r["port"], r["pid"]))
                return results
        except Exception:
            pass

    # Fallback via netstat / ss
    if _SYSTEM == "Windows":
        try:
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5, **_WIN_HIDE)
            for line in (r.stdout or "").splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[0].upper() == "TCP" and parts[3].upper() == "LISTENING":
                    host_port = parts[1]
                    if ":" in host_port:
                        ip, p_str = host_port.rsplit(":", 1)
                        if p_str.isdigit():
                            p_num = int(p_str)
                            if port_filter is None or p_num == int(port_filter):
                                pid = int(parts[4]) if parts[4].isdigit() else 0
                                results.append({
                                    "port": p_num, "ip": ip, "proto": "tcp",
                                    "pid": pid, "process": pid_names.get(pid, ""),
                                })
        except Exception:
            pass
    elif shutil.which("ss"):
        try:
            r = subprocess.run(["ss", "-tulnp"], capture_output=True, text=True, timeout=4)
            for line in (r.stdout or "").splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    local = parts[4]
                    if ":" in local:
                        ip, p_str = local.rsplit(":", 1)
                        if p_str.isdigit():
                            p_num = int(p_str)
                            if port_filter is None or p_num == int(port_filter):
                                m_pid = re.search(r"pid=(\d+)", line)
                                pid = int(m_pid.group(1)) if m_pid else 0
                                m_nm = re.search(r'\("([^"]+)"', line)
                                pname = m_nm.group(1) if m_nm else pid_names.get(pid, "")
                                results.append({
                                    "port": p_num, "ip": ip, "proto": parts[0].lower(),
                                    "pid": pid, "process": pname,
                                })
        except Exception:
            pass

    results.sort(key=lambda r: (r["port"], r["pid"]))
    return results


def get_disks_summary() -> list[dict[str, Any]]:
    """Return disk space info across mounted drives/partitions."""
    disks: list[dict[str, Any]] = []
    seen_mounts: set[str] = set()

    if _PSUTIL:
        try:
            for part in psutil.disk_partitions(all=False):
                if _SYSTEM != "Windows" and part.fstype in ("squashfs", "tmpfs", "devtmpfs", "overlay"):
                    pass
                mp = part.mountpoint
                if mp in seen_mounts:
                    continue
                try:
                    u = psutil.disk_usage(mp)
                except Exception:
                    continue
                if u.total <= 0:
                    continue
                seen_mounts.add(mp)
                disks.append({
                    "mount": mp,
                    "fstype": part.fstype,
                    "total_gb": round(u.total / (1024 ** 3), 1),
                    "used_gb": round(u.used / (1024 ** 3), 1),
                    "free_gb": round(u.free / (1024 ** 3), 1),
                    "percent": round(u.percent, 1),
                })
            if disks:
                return disks
        except Exception:
            pass

    # Stdlib fallback
    candidates = [f"{c}:\\" for c in "CDEFGH"] if _SYSTEM == "Windows" else ["/"]
    for mp in candidates:
        if not Path(mp).exists():
            continue
        try:
            u = shutil.disk_usage(mp)
            if u.total > 0:
                disks.append({
                    "mount": mp,
                    "fstype": "",
                    "total_gb": round(u.total / (1024 ** 3), 1),
                    "used_gb": round(u.used / (1024 ** 3), 1),
                    "free_gb": round(u.free / (1024 ** 3), 1),
                    "percent": round((u.used / u.total) * 100.0, 1),
                })
        except Exception:
            continue
    return disks


def get_battery_summary() -> dict[str, Any]:
    """Return battery percentage, AC plug status, and time left (or desktop indicator)."""
    if _PSUTIL and hasattr(psutil, "sensors_battery"):
        try:
            bat = psutil.sensors_battery()
            if bat is not None:
                mins = (
                    round(bat.secsleft / 60)
                    if bat.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN) and bat.secsleft > 0
                    else None
                )
                return {
                    "has_battery": True,
                    "percent": round(bat.percent, 1),
                    "plugged": bool(bat.power_plugged),
                    "minutes_left": mins,
                }
        except Exception:
            pass

    if _SYSTEM == "Windows":
        try:
            class SYSTEM_POWER_STATUS(ctypes.Structure):
                _fields_ = [
                    ("ACLineStatus", ctypes.c_byte),
                    ("BatteryFlag", ctypes.c_byte),
                    ("BatteryLifePercent", ctypes.c_byte),
                    ("SystemStatusFlag", ctypes.c_byte),
                    ("BatteryLifeTime", ctypes.c_ulong),
                    ("BatteryFullLifeTime", ctypes.c_ulong),
                ]
            sps = SYSTEM_POWER_STATUS()
            if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps)):
                if sps.BatteryFlag == 128 or sps.BatteryLifePercent == 255:
                    return {"has_battery": False, "plugged": True, "percent": None, "minutes_left": None}
                mins = round(sps.BatteryLifeTime / 60) if sps.BatteryLifeTime != 0xFFFFFFFF else None
                return {
                    "has_battery": True,
                    "percent": int(sps.BatteryLifePercent),
                    "plugged": sps.ACLineStatus == 1,
                    "minutes_left": mins,
                }
        except Exception:
            pass

    if _SYSTEM == "Linux":
        for bat_dir in sorted(Path("/sys/class/power_supply").glob("BAT*")) if Path("/sys/class/power_supply").is_dir() else []:
            try:
                cap = int((bat_dir / "capacity").read_text().strip())
                st = (bat_dir / "status").read_text().strip().lower()
                return {
                    "has_battery": True,
                    "percent": cap,
                    "plugged": st in ("charging", "full", "not charging"),
                    "minutes_left": None,
                }
            except Exception:
                continue

    return {"has_battery": False, "plugged": True, "percent": None, "minutes_left": None}


def get_network_summary() -> dict[str, Any]:
    """Return hostname, primary local IP, Wi-Fi SSID (when connected), and active interfaces."""
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except Exception:
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            pass

    wifi_ssid = ""
    wifi_signal = ""
    if _SYSTEM == "Windows":
        try:
            r = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, timeout=4, **_WIN_HIDE)
            for line in (r.stdout or "").splitlines():
                if re.match(r"^\s*SSID\s*:", line):
                    wifi_ssid = line.split(":", 1)[1].strip()
                elif re.match(r"^\s*Signal\s*:", line):
                    wifi_signal = line.split(":", 1)[1].strip()
        except Exception:
            pass
    elif _SYSTEM == "Linux" and shutil.which("nmcli"):
        try:
            r = subprocess.run(["nmcli", "-t", "-f", "active,ssid,signal", "dev", "wifi"], capture_output=True, text=True, timeout=3)
            for line in (r.stdout or "").splitlines():
                if line.startswith("yes:"):
                    parts = line.split(":")
                    if len(parts) >= 3:
                        wifi_ssid, wifi_signal = parts[1], f"{parts[2]}%"
                        break
        except Exception:
            pass

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "wifi_ssid": wifi_ssid or None,
        "wifi_signal": wifi_signal or None,
    }


def search_installed_apps(query: str = "") -> list[str]:
    """Search installed applications across OS app directories / Start Menu / PATH."""
    q = (query or "").strip().lower()
    found: set[str] = set()

    if _SYSTEM == "Windows":
        roots = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        ]
        for root in roots:
            if root.is_dir():
                try:
                    for lnk in root.rglob("*.lnk"):
                        if "uninstall" not in lnk.stem.lower():
                            if not q or q in lnk.stem.lower():
                                found.add(lnk.stem)
                except Exception:
                    pass
        try:
            ps_filter = f"| Where-Object {{ $_.Name.ToLower().Contains('{re.sub(r'[^a-z0-9 ._-]', '', q)}') }}" if q else ""
            r = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 f"Get-StartApps {ps_filter} | Select-Object -First 60 -ExpandProperty Name"],
                capture_output=True, text=True, timeout=4, **_WIN_HIDE,
            )
            for line in (r.stdout or "").splitlines():
                if line.strip():
                    found.add(line.strip())
        except Exception:
            pass

    elif _SYSTEM == "Darwin":
        for d in (Path("/Applications"), Path("/System/Applications"), Path.home() / "Applications"):
            if d.is_dir():
                for app in d.glob("*.app"):
                    if not q or q in app.stem.lower():
                        found.add(app.stem)

    else:
        for d in (Path("/usr/share/applications"), Path("/usr/local/share/applications"), Path.home() / ".local/share/applications"):
            if d.is_dir():
                for desk in d.glob("*.desktop"):
                    try:
                        txt = desk.read_text(encoding="utf-8", errors="ignore")
                        m = re.search(r"^Name=(.+)$", txt, re.MULTILINE)
                        nm = m.group(1).strip() if m else desk.stem
                        if not q or q in nm.lower() or q in desk.stem.lower():
                            found.add(nm)
                    except Exception:
                        continue
        if q:
            hit = shutil.which(q)
            if hit:
                found.add(f"{q} ({hit})")

    return sorted(found, key=str.lower)[:60]
