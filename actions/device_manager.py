"""
Device & OS Manager — verified window control, interactive terminal launcher,
process/port inspection & safe termination, battery, disks, network, and
installed-application discovery.

Auto-discovered by `core/action_loader.py` via `TOOL`.
"""

from __future__ import annotations

import ctypes
import getpass
import os
import platform
import re
import signal
import subprocess
from pathlib import Path
from typing import Any

from core import confirm
from core.os_control import (
    PROTECTED_PROCESS_STEMS,
    control_window,
    find_windows,
    get_battery_summary,
    get_disks_summary,
    get_network_summary,
    list_listening_ports,
    list_processes_snapshot,
    list_visible_windows,
    open_interactive_terminal,
    open_path_verified,
    search_installed_apps,
)

_SYSTEM = platform.system()
_WIN_HIDE: dict[str, Any] = (
    {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    if _SYSTEM == "Windows"
    else {}
)


def _protected_pid_or_name(pid: int, name: str) -> str | None:
    if pid in {os.getpid(), os.getppid(), 0, 1, 4}:
        return f"PID {pid} belongs to JARVIS or the OS kernel and cannot be terminated."
    stem = (name or "").lower()
    if stem.endswith(".exe"):
        stem = stem[:-4]
    if stem in PROTECTED_PROCESS_STEMS:
        return f"'{name}' is a critical operating-system process and cannot be terminated."
    return None


def _terminate_pids_now(targets: list[tuple[int, str]]) -> str:
    killed: list[str] = []
    errors: list[str] = []
    for pid, name in targets:
        guard = _protected_pid_or_name(pid, name)
        if guard:
            errors.append(guard)
            continue
        try:
            if _SYSTEM == "Windows":
                r = subprocess.run(
                    ["taskkill", "/PID", str(pid), "/T", "/F"],
                    capture_output=True, text=True, timeout=6, **_WIN_HIDE,
                )
                if r.returncode == 0:
                    killed.append(f"{name or 'process'} (PID {pid})")
                else:
                    errors.append(f"PID {pid}: {(r.stderr or r.stdout or '').strip()}")
            else:
                os.kill(pid, signal.SIGTERM)
                killed.append(f"{name or 'process'} (PID {pid})")
        except ProcessLookupError:
            killed.append(f"{name or 'process'} (PID {pid}, already exited)")
        except Exception as e:
            errors.append(f"PID {pid}: {e}")

    parts = []
    if killed:
        parts.append("Terminated: " + ", ".join(killed) + ".")
    if errors:
        parts.append("Errors: " + "; ".join(errors))
    return " ".join(parts) if parts else "No processes were terminated."


def _empty_trash_now() -> str:
    if _SYSTEM == "Windows":
        try:
            # SHERB_NOCONFIRMATION (1) | SHERB_NOPROGRESSUI (2) | SHERB_NOSOUND (4) = 7
            hr = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            if hr in (0, -2147418113):  # S_OK or already empty
                return "Recycle Bin emptied."
            return f"Recycle Bin empty returned code {hr}."
        except Exception as e:
            return f"Could not empty Recycle Bin: {e}"
    if _SYSTEM == "Darwin":
        r = subprocess.run(
            ["osascript", "-e", 'tell application "Finder" to empty the trash'],
            capture_output=True, text=True, timeout=10,
        )
        return "Trash emptied." if r.returncode == 0 else f"Could not empty Trash: {(r.stderr or '').strip()}"
    trash = Path.home() / ".local" / "share" / "Trash"
    removed = 0
    for sub in ("files", "info"):
        d = trash / sub
        if d.is_dir():
            for item in d.iterdir():
                try:
                    if item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    removed += 1
                except Exception:
                    continue
    return f"Trash emptied ({removed} entries removed)."


def device_manager(
    parameters: dict | None = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    action = str(params.get("action", "") or "").strip().lower().replace("-", "_").replace(" ", "_")
    target = str(params.get("target", "") or params.get("app", "") or params.get("name", "") or "").strip()
    shell_name = str(params.get("shell", "") or "powershell").strip()
    cwd = str(params.get("cwd", "") or params.get("path", "") or "").strip()
    command = str(params.get("command", "") or "").strip()
    admin = bool(params.get("admin", False))
    port_raw = params.get("port")
    pid_raw = params.get("pid")
    limit = max(1, min(50, int(params.get("limit", 15) or 15)))

    if not action:
        return (
            "Specify `action` for device_manager: list_windows | focus_window | "
            "close_window | minimize_window | maximize_window | restore_window | "
            "snap_left | snap_right | open_terminal | find_process | top_processes | "
            "list_ports | kill_process | battery | disks | network | system_info | "
            "installed_apps | open_path | empty_recycle_bin."
        )

    if player and hasattr(player, "write_log"):
        player.write_log(f"[Device] {action}" + (f" ({target})" if target else ""))

    # ── 1. Window Inspection & Control ────────────────────────────────────────
    if action in ("list_windows", "windows", "open_windows"):
        wins = list_visible_windows()
        if target:
            wins = find_windows(target, wins)
        if not wins:
            if target:
                return f"No visible window matching '{target}' is open right now."
            return "No visible desktop windows detected."
        lines = [f"Visible open windows ({len(wins)}):"]
        for w in wins[:limit]:
            flags = []
            if w.get("active"):
                flags.append("ACTIVE")
            if w.get("minimized"):
                flags.append("MIN")
            if w.get("maximized"):
                flags.append("MAX")
            badge = f"[{'|'.join(flags)}] " if flags else ""
            proc_s = f"{w['process']}, " if w.get("process") else ""
            lines.append(f"  • {badge}{w['title']} ({proc_s}PID {w.get('pid', 0)})")
        out = "\n".join(lines)
        if player and hasattr(player, "show_content"):
            player.show_content("OPEN WINDOWS", out)
        return out

    if action in (
        "focus_window", "focus",
        "close_window", "close",
        "minimize_window", "minimize",
        "maximize_window", "maximize",
        "restore_window", "restore",
        "snap_left", "snap_right",
    ):
        if not target:
            return f"`{action}` requires `target` (the window title or app name, e.g. 'PowerShell' or 'Chrome')."
        op_map = {
            "focus_window": "focus", "focus": "focus",
            "close_window": "close", "close": "close",
            "minimize_window": "minimize", "minimize": "minimize",
            "maximize_window": "maximize", "maximize": "maximize",
            "restore_window": "restore", "restore": "restore",
            "snap_left": "snap_left", "snap_right": "snap_right",
        }
        _ok, msg = control_window(target, op_map[action])
        return msg

    # ── 2. Visible Interactive Terminal / PowerShell Launcher ─────────────────
    if action in ("open_terminal", "terminal", "powershell", "cmd"):
        chosen_shell = shell_name
        if action in ("powershell", "cmd") and not params.get("shell"):
            chosen_shell = action
        elif target and target.lower() in ("powershell", "pwsh", "powershell 7", "cmd", "wt", "wsl", "git bash"):
            chosen_shell = target
        res = open_interactive_terminal(
            shell_name=chosen_shell,
            cwd=cwd,
            command=command,
            admin=admin,
        )
        return res["message"]

    # ── 3. Process Inspection & Safe Termination ──────────────────────────────
    if action in ("find_process", "check_app", "is_running"):
        if not target:
            return "Provide `target` (e.g. 'powershell', 'chrome', 'docker') to check if it is running."
        needle = target.lower()
        stem = needle[:-4] if needle.endswith(".exe") else needle
        procs = [
            p for p in list_processes_snapshot()
            if stem in p["name"].lower() or stem in p.get("cmdline", "").lower()
        ]
        wins = find_windows(target)
        if not procs and not wins:
            return f"'{target}' is NOT running (0 matching processes, 0 visible windows)."
        lines = [
            f"'{target}': {len(procs)} running process(es), {len(wins)} visible window(s)."
        ]
        for w in wins[:6]:
            lines.append(f"  [Window] '{w['title']}' (PID {w.get('pid')})")
        for p in sorted(procs, key=lambda x: x["memory_mb"], reverse=True)[:8]:
            lines.append(f"  [Process] {p['name']} (PID {p['pid']}, {p['memory_mb']} MB RAM)")
        return "\n".join(lines)

    if action in ("top_processes", "list_processes", "processes"):
        sort_by = str(params.get("sort_by", "memory") or "memory").lower()
        procs = list_processes_snapshot()
        win_pids = {int(w.get("pid") or 0) for w in list_visible_windows()}
        key_fn = (
            (lambda p: (p["cpu"], p["memory_mb"]))
            if sort_by == "cpu"
            else (lambda p: (p["memory_mb"], p["cpu"]))
        )
        procs.sort(key=key_fn, reverse=True)
        lines = [f"Top {min(limit, len(procs))} processes (sorted by {sort_by}):"]
        for p in procs[:limit]:
            w_tag = " [window]" if p["pid"] in win_pids else ""
            lines.append(
                f"  • {p['name']} (PID {p['pid']}) — {p['memory_mb']} MB RAM, "
                f"{p['cpu']:.1f}% CPU{w_tag}"
            )
        out = "\n".join(lines)
        if player and hasattr(player, "show_content"):
            player.show_content("TOP PROCESSES", out)
        return out

    if action in ("list_ports", "ports", "port_owner"):
        pf = int(port_raw) if port_raw is not None and str(port_raw).strip().isdigit() else None
        ports = list_listening_ports(port_filter=pf)
        if not ports:
            return (
                f"No process is currently listening on port {pf}."
                if pf is not None
                else "No listening TCP/UDP ports returned."
            )
        lines = [f"Listening ports ({len(ports)}):"]
        for r in ports[:limit]:
            owner = f"{r['process']} (PID {r['pid']})" if r.get("pid") else "system/unknown"
            lines.append(f"  • {r['proto'].upper()} {r['ip']}:{r['port']} → {owner}")
        out = "\n".join(lines)
        if player and hasattr(player, "show_content"):
            player.show_content("LISTENING PORTS", out)
        return out

    if action in ("kill_process", "terminate_process", "kill_port"):
        procs = list_processes_snapshot()
        by_pid = {p["pid"]: p["name"] for p in procs}
        candidates: list[tuple[int, str]] = []

        if pid_raw is not None and str(pid_raw).strip().isdigit():
            pid_i = int(pid_raw)
            candidates.append((pid_i, by_pid.get(pid_i, f"PID-{pid_i}")))
        elif port_raw is not None and str(port_raw).strip().isdigit():
            pf = int(port_raw)
            for entry in list_listening_ports(port_filter=pf):
                if entry.get("pid"):
                    candidates.append((entry["pid"], entry.get("process") or f"port-{pf}"))
            if not candidates:
                return f"Nothing is listening on port {pf}."
        elif target:
            needle = target.lower()
            stem = needle[:-4] if needle.endswith(".exe") else needle
            for p in procs:
                pname = p["name"].lower()
                pstem = pname[:-4] if pname.endswith(".exe") else pname
                if pstem == stem or pname == needle:
                    candidates.append((p["pid"], p["name"]))
            if not candidates:
                return f"No running process named '{target}' was found."
        else:
            return "Specify `pid`, `port`, or `target` process name for kill_process."

        # Deduplicate while preserving order
        seen: set[int] = set()
        uniq: list[tuple[int, str]] = []
        for pid_i, nm in candidates:
            if pid_i not in seen:
                seen.add(pid_i)
                guard = _protected_pid_or_name(pid_i, nm)
                if guard:
                    return guard
                uniq.append((pid_i, nm))

        summary = ", ".join(f"{nm} (PID {pid_i})" for pid_i, nm in uniq[:5])
        if len(uniq) > 5:
            summary += f" +{len(uniq) - 5} more"
        if confirm.pending_title():
            return "There is already a confirmation waiting on screen. Ask the user to answer it first."
        return confirm.request(
            key="kill_process",
            title=f"Terminate {len(uniq)} process(es)",
            detail=f"Force-stop: {summary}. Unsaved work in these process(es) will be lost.",
            run=lambda t=uniq: _terminate_pids_now(t),
        )

    # ── 4. Hardware, Power, Disks, Network, Installed Apps & Paths ───────────
    if action == "battery":
        b = get_battery_summary()
        if not b["has_battery"]:
            return "Power status: Desktop / AC power (no battery detected)."
        state = "Plugged in / charging" if b["plugged"] else "On battery"
        rem = f", ~{b['minutes_left']} min remaining" if b.get("minutes_left") else ""
        return f"Battery: {b['percent']}% ({state}{rem})."

    if action in ("disks", "storage"):
        disks = get_disks_summary()
        if not disks:
            return "Could not read mounted drives."
        lines = ["Mounted storage drives:"]
        for d in disks:
            lines.append(
                f"  • {d['mount']} — {d['free_gb']} GB free of {d['total_gb']} GB "
                f"({d['percent']}% used)"
            )
        return "\n".join(lines)

    if action == "network":
        net = get_network_summary()
        wifi = (
            f"{net['wifi_ssid']}" + (f" ({net['wifi_signal']})" if net.get("wifi_signal") else "")
            if net.get("wifi_ssid")
            else "Ethernet / Wi-Fi SSID unavailable"
        )
        return (
            f"Network: host={net['hostname']}, local IP={net['local_ip']}, "
            f"Wi-Fi={wifi}."
        )

    if action == "system_info":
        uname = platform.uname()
        disks = get_disks_summary()
        bat = get_battery_summary()
        net = get_network_summary()
        cores = os.cpu_count() or 1
        user = getpass.getuser()
        disk_line = (
            ", ".join(f"{d['mount']} {d['free_gb']}/{d['total_gb']} GB free" for d in disks[:3])
            if disks
            else "n/a"
        )
        bat_line = (
            f"{bat['percent']}% ({'AC' if bat['plugged'] else 'battery'})"
            if bat["has_battery"]
            else "AC desktop"
        )
        return (
            f"Device: {uname.node} ({uname.system} {uname.release}, {uname.machine})\n"
            f"User: {user} | Logical CPUs: {cores} | Local IP: {net['local_ip']}\n"
            f"Power: {bat_line} | Storage: {disk_line}"
        )

    if action == "installed_apps":
        apps = search_installed_apps(target)
        if not apps:
            return (
                f"No installed applications matched '{target}'."
                if target
                else "No installed applications enumerated."
            )
        header = f"Installed applications matching '{target}' ({len(apps)}):" if target else f"Installed applications ({len(apps)} shown):"
        return header + "\n  • " + "\n  • ".join(apps[:limit])

    if action == "open_path":
        path_arg = str(params.get("path", "") or target).strip()
        if not path_arg:
            return "Specify `path` (or `target`) to open in File Explorer / Finder."
        return open_path_verified(path_arg)["message"]

    if action == "empty_recycle_bin":
        if confirm.pending_title():
            return "There is already a confirmation waiting on screen. Ask the user to answer it first."
        return confirm.request(
            key="empty_recycle_bin",
            title="Empty Recycle Bin / Trash",
            detail="Permanently delete all items currently in the Recycle Bin / Trash.",
            run=_empty_trash_now,
        )

    return (
        f"Unknown device_manager action '{action}'. Use one of: list_windows | "
        f"focus_window | close_window | minimize_window | maximize_window | "
        f"restore_window | snap_left | snap_right | open_terminal | find_process | "
        f"top_processes | list_ports | kill_process | battery | disks | network | "
        f"system_info | installed_apps | open_path | empty_recycle_bin."
    )


TOOL = {
    "name": "device_manager",
    "description": (
        "Deep OS & device management with ground-truth verification. "
        "Manage visible windows by name (list_windows, focus_window, close_window, "
        "minimize_window, maximize_window, restore_window, snap_left, snap_right), "
        "open a real visible interactive terminal/PowerShell window (open_terminal), "
        "inspect or stop processes & ports (find_process, top_processes, list_ports, "
        "kill_process), and check hardware/OS state (battery, disks, network, "
        "system_info, installed_apps, open_path, empty_recycle_bin). "
        "Use `list_windows` or `find_process` whenever you need to verify whether "
        "an app or terminal is actually open. `kill_process` and `empty_recycle_bin` "
        "place a confirmation button on the user's screen ([CONFIRMATION_PENDING])."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "list_windows | focus_window | close_window | minimize_window | "
                    "maximize_window | restore_window | snap_left | snap_right | "
                    "open_terminal | find_process | top_processes | list_ports | "
                    "kill_process | battery | disks | network | system_info | "
                    "installed_apps | open_path | empty_recycle_bin"
                ),
            },
            "target": {
                "type": "STRING",
                "description": "Window title, application name, or process name (e.g. 'PowerShell', 'Chrome', 'Spotify')",
            },
            "shell": {
                "type": "STRING",
                "description": "For open_terminal: 'powershell' | 'pwsh' | 'cmd' | 'wt' | 'wsl' | 'git-bash'",
            },
            "cwd": {
                "type": "STRING",
                "description": "Working directory for open_terminal",
            },
            "command": {
                "type": "STRING",
                "description": "Initial command to execute inside open_terminal while keeping the window open",
            },
            "admin": {
                "type": "BOOLEAN",
                "description": "For open_terminal: True only if user explicitly asked for Administrator elevation",
            },
            "pid": {
                "type": "INTEGER",
                "description": "Process ID for kill_process",
            },
            "port": {
                "type": "INTEGER",
                "description": "TCP/UDP port number for list_ports or kill_process",
            },
            "path": {
                "type": "STRING",
                "description": "Folder or file path for open_path",
            },
            "sort_by": {
                "type": "STRING",
                "description": "'memory' or 'cpu' for top_processes",
            },
            "limit": {
                "type": "INTEGER",
                "description": "Max items to return (default 15)",
            },
        },
        "required": ["action"],
    },
    "handler": device_manager,
}
