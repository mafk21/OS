"""Tests for verified app/PowerShell launching, window/process control, and device_manager."""

from __future__ import annotations

import os
import socket
from pathlib import Path
from unittest.mock import patch

import actions.computer_control as cc
import actions.computer_settings as cs
import actions.device_manager as dm
import actions.open_app as oa
import actions.shell_agent as sa
import core.confirm as confirm_gate
import core.os_control as osc
from core.action_loader import discover_actions


# ── 1. Action Loader & main.py Popen Wrapper ─────────────────────────────────

def test_device_manager_and_open_app_auto_discover():
    reg = discover_actions(Path("actions"), reserved_names=set(), logger=lambda _: None)
    assert "device_manager" in reg.names()
    assert "open_app" in reg.names()
    assert "shell_agent" in reg.names()


def test_main_windows_popen_respects_visible_window_and_create_new_console():
    src = Path("main.py").read_text(encoding="utf-8")
    assert 'kw.pop("visible_window", False)' in src
    assert "_CREATE_NEW_CONSOLE" in src
    assert "_subprocess._OrigPopen = _OrigPopen" in src


# ── 2. open_app Normalization (No Substring Corruption!) ─────────────────────

def test_open_app_normalize_handles_terminals_and_avoids_substring_bugs(monkeypatch):
    monkeypatch.setattr(oa, "_SYSTEM", "Windows")
    assert oa._normalize("the powershell") == "powershell.exe"
    assert oa._normalize("open Windows PowerShell") == "powershell.exe"
    assert oa._normalize("PowerShell 7") == "pwsh.exe"
    assert oa._normalize("command prompt") == "cmd.exe"
    assert oa._normalize("Windows Terminal") == "wt.exe"
    assert oa._normalize("Bluetooth Settings") == "ms-settings:bluetooth"
    assert oa._normalize("Device Manager") == "devmgmt.msc"

    # Must NEVER corrupt unrelated names that happen to contain short alias words
    assert oa._normalize("GitHub Desktop") == "GitHubDesktop"
    assert oa._normalize("Password Manager") == "Password Manager"
    assert oa._normalize("Xcode") == "Xcode"
    assert oa._normalize("Knowledge Base") == "Knowledge Base"


# ── 3. Verified PowerShell Launch (Success vs Failure Ground Truth) ──────────

def test_windows_open_powershell_verifies_real_window_and_focuses_it(monkeypatch):
    monkeypatch.setattr(oa, "_SYSTEM", "Windows")
    monkeypatch.setattr(osc, "_SYSTEM", "Windows")

    shell_calls: list[tuple] = []
    focused_hwnds: list[int] = []

    monkeypatch.setattr(
        osc,
        "_resolve_windows_terminal_exe",
        lambda name: (r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "powershell"),
    )
    monkeypatch.setattr(
        osc,
        "_win32_shell_execute",
        lambda target, params="", cwd="", admin=False: (
            shell_calls.append((target, params, cwd, admin)) or (True, "ok")
        ),
    )
    # First call (before launch): no PowerShell window; second call (during verify): visible window appears!
    win_snapshots = [
        [{"id": 101, "title": "JARVIS", "pid": os.getpid(), "process": "python.exe", "active": True, "minimized": False, "maximized": False}],
        [
            {"id": 101, "title": "JARVIS", "pid": os.getpid(), "process": "python.exe", "active": False, "minimized": False, "maximized": False},
            {"id": 55501, "title": "Windows PowerShell", "pid": 42420, "process": "powershell.exe", "active": True, "minimized": False, "maximized": False},
        ],
    ]
    monkeypatch.setattr(
        osc,
        "list_visible_windows",
        lambda: win_snapshots.pop(0) if len(win_snapshots) > 1 else win_snapshots[0],
    )
    monkeypatch.setattr(osc, "list_processes_snapshot", lambda: [])
    monkeypatch.setattr(osc, "focus_win32_hwnd", lambda hwnd: focused_hwnds.append(hwnd) or True)

    msg = oa.open_app({"app_name": "the powershell"})
    assert "verified visible window 'Windows PowerShell'" in msg
    assert "42420" in msg
    assert len(shell_calls) == 1
    assert "-NoExit" in shell_calls[0][1]
    assert focused_hwnds == [55501]


def test_windows_open_powershell_never_lies_when_no_window_or_process_appears(monkeypatch):
    monkeypatch.setattr(oa, "_SYSTEM", "Windows")
    monkeypatch.setattr(osc, "_SYSTEM", "Windows")

    monkeypatch.setattr(
        osc,
        "_resolve_windows_terminal_exe",
        lambda name: (r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "powershell"),
    )
    monkeypatch.setattr(osc, "_win32_shell_execute", lambda *a, **k: (True, "ok"))
    monkeypatch.setattr(osc, "list_visible_windows", lambda: [])
    monkeypatch.setattr(osc, "list_processes_snapshot", lambda: [])

    res = osc.open_interactive_terminal("powershell", verify_timeout=0.35)
    assert res["ok"] is False
    assert "no visible window" in res["message"].lower()


def test_open_app_nonexistent_app_reports_honest_failure():
    out = oa.open_app({"app_name": "TotallyFakeNonExistentApp_998877"})
    assert "Opened TotallyFakeNonExistentApp_998877" not in out
    assert "could not open" in out.lower() or "not found" in out.lower() or "no graphical display" in out.lower()


# ── 4. device_manager Window, Process, Port & Hardware Operations ────────────

def test_device_manager_list_and_control_windows_protects_jarvis_pid(monkeypatch):
    fake_wins = [
        {"id": 11, "title": "JARVIS HUD", "pid": os.getpid(), "process": "python", "active": True, "minimized": False, "maximized": False},
        {"id": 22, "title": "Windows PowerShell", "pid": 99991, "process": "powershell.exe", "active": False, "minimized": False, "maximized": False},
    ]
    monkeypatch.setattr(dm, "list_visible_windows", lambda: fake_wins)
    monkeypatch.setattr(osc, "list_visible_windows", lambda: fake_wins)

    listed = dm.device_manager({"action": "list_windows"})
    assert "[ACTIVE] JARVIS HUD" in listed
    assert "Windows PowerShell" in listed

    # Closing JARVIS's own window via close_window must be blocked
    refused = dm.device_manager({"action": "close_window", "target": "JARVIS HUD"})
    assert "Refusing to close JARVIS" in refused


def test_device_manager_top_processes_find_process_and_live_port():
    top = dm.device_manager({"action": "top_processes", "limit": 5})
    assert "Top " in top and "PID" in top

    # Spin up an ephemeral localhost TCP listener and verify list_ports finds it
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    try:
        ports_out = dm.device_manager({"action": "list_ports", "port": port})
        assert str(port) in ports_out
    finally:
        srv.close()

    assert "Storage:" in dm.device_manager({"action": "system_info"})
    assert "GB free" in dm.device_manager({"action": "disks"})
    assert "local IP=" in dm.device_manager({"action": "network"})
    bat_out = dm.device_manager({"action": "battery"})
    assert "Battery:" in bat_out or "Power status:" in bat_out


def test_device_manager_kill_process_blocks_protected_and_gates_user_apps(monkeypatch):
    # Cannot kill JARVIS itself
    self_kill = dm.device_manager({"action": "kill_process", "pid": os.getpid()})
    assert "cannot be terminated" in self_kill.lower()

    # Cannot kill critical OS process
    monkeypatch.setattr(
        dm,
        "list_processes_snapshot",
        lambda: [
            {"pid": 600, "name": "csrss.exe", "exe": "csrss.exe", "cpu": 0.0, "memory_mb": 12.0, "cmdline": ""},
            {"pid": 54321, "name": "notepad.exe", "exe": "notepad.exe", "cpu": 0.0, "memory_mb": 24.0, "cmdline": ""},
        ],
    )
    sys_kill = dm.device_manager({"action": "kill_process", "target": "csrss.exe"})
    assert "critical operating-system process" in sys_kill.lower()

    # Killing a normal user process triggers unforgeable HUD confirmation gate
    confirm_gate._clear_for_tests() if hasattr(confirm_gate, "_clear_for_tests") else None
    with patch.object(confirm_gate, "pending_title", return_value=None), patch.object(
        confirm_gate, "request", return_value="[CONFIRMATION_PENDING] Terminate 1 process(es)"
    ) as req_mock:
        user_kill = dm.device_manager({"action": "kill_process", "target": "notepad"})
        assert "[CONFIRMATION_PENDING]" in user_kill
        assert req_mock.called


# ── 5. shell_agent, computer_settings & computer_control Upgrades ────────────

def test_shell_agent_detects_powershell_cmdlets_and_supports_open_terminal(monkeypatch):
    monkeypatch.setattr(sa, "_SYSTEM", "Windows")
    assert sa._should_use_powershell("Get-Process | Select-Object -First 5") is True
    assert sa._should_use_powershell("$PSVersionTable.PSVersion") is True
    assert sa._should_use_powershell("dir /b") is False
    assert sa._should_use_powershell("dir", shell_pref="powershell") is True

    monkeypatch.setattr(
        sa,
        "open_interactive_terminal",
        lambda **kw: {"ok": True, "message": "Opened powershell — verified visible window 'Windows PowerShell' (PID 777)."},
    )
    out = sa.shell_agent({"action": "open_terminal", "shell": "powershell"})
    assert "verified visible window 'Windows PowerShell'" in out


def test_computer_settings_targeted_close_and_computer_control_honest_focus(monkeypatch):
    monkeypatch.setattr(
        osc,
        "control_window",
        lambda target, op: (True, f"Closed window '{target}'.") if target == "Notepad" else (False, f"No visible window matching '{target}' is currently open."),
    )
    # Targeted close works even without pyautogui and never sends blind Alt+F4
    res = cs.computer_settings({"action": "close_app", "value": "Notepad"})
    assert res == "Closed window 'Notepad'."

    # focus_window reports honestly when window doesn't exist
    miss = cc.computer_control({"action": "focus_window", "title": "NonExistentWindow_404"})
    assert "No visible window" in miss
