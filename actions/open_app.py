"""
Verified Application, Terminal, Folder & System-Utility Launcher.

Uses `core.os_control` so console apps (`PowerShell`, `CMD`, `Windows Terminal`,
`WSL`, `Git Bash`) always spawn in a real visible foreground window (never
swallowed by `CREATE_NO_WINDOW`) and every launch is checked against live OS
windows and PIDs before claiming success.
"""

from __future__ import annotations

import platform
import re

from core.os_control import launch_application

_SYSTEM = platform.system()

_APP_ALIASES: dict[str, dict[str, str]] = {
    # ── Shells & Terminals ────────────────────────────────────────────────────
    "powershell":          {"Windows": "powershell.exe",          "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "windows powershell":  {"Windows": "powershell.exe",          "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "powershell 7":        {"Windows": "pwsh.exe",                "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "pwsh":                {"Windows": "pwsh.exe",                "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "cmd":                 {"Windows": "cmd.exe",                 "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "command prompt":      {"Windows": "cmd.exe",                 "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "terminal":            {"Windows": "wt.exe",                  "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "windows terminal":    {"Windows": "wt.exe",                  "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "wt":                  {"Windows": "wt.exe",                  "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "wsl":                 {"Windows": "wsl.exe",                 "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "ubuntu":              {"Windows": "wsl.exe",                 "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "git bash":            {"Windows": "git-bash.exe",            "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},
    "git-bash":            {"Windows": "git-bash.exe",            "Darwin": "Terminal",             "Linux": "x-terminal-emulator"},

    # ── Browsers ──────────────────────────────────────────────────────────────
    "chrome":              {"Windows": "chrome",                  "Darwin": "Google Chrome",        "Linux": "google-chrome"},
    "google chrome":       {"Windows": "chrome",                  "Darwin": "Google Chrome",        "Linux": "google-chrome"},
    "firefox":             {"Windows": "firefox",                 "Darwin": "Firefox",              "Linux": "firefox"},
    "edge":                {"Windows": "msedge",                  "Darwin": "Microsoft Edge",       "Linux": "microsoft-edge"},
    "microsoft edge":      {"Windows": "msedge",                  "Darwin": "Microsoft Edge",       "Linux": "microsoft-edge"},
    "brave":               {"Windows": "brave",                   "Darwin": "Brave Browser",        "Linux": "brave-browser"},
    "safari":              {"Windows": "msedge",                  "Darwin": "Safari",               "Linux": "firefox"},
    "opera":               {"Windows": "opera",                   "Darwin": "Opera",                "Linux": "opera"},

    # ── Communication ─────────────────────────────────────────────────────────
    "whatsapp":            {"Windows": "WhatsApp",                "Darwin": "WhatsApp",             "Linux": "whatsapp"},
    "telegram":            {"Windows": "Telegram",                "Darwin": "Telegram",             "Linux": "telegram-desktop"},
    "discord":             {"Windows": "Discord",                 "Darwin": "Discord",              "Linux": "discord"},
    "slack":               {"Windows": "Slack",                   "Darwin": "Slack",                "Linux": "slack"},
    "zoom":                {"Windows": "Zoom",                    "Darwin": "zoom.us",              "Linux": "zoom"},
    "teams":               {"Windows": "ms-teams:",               "Darwin": "Microsoft Teams",      "Linux": "teams"},
    "microsoft teams":     {"Windows": "ms-teams:",               "Darwin": "Microsoft Teams",      "Linux": "teams"},
    "skype":               {"Windows": "skype",                   "Darwin": "Skype",                "Linux": "skype"},
    "signal":              {"Windows": "Signal",                  "Darwin": "Signal",               "Linux": "signal-desktop"},

    # ── Developer Tools ───────────────────────────────────────────────────────
    "vscode":              {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "vs code":             {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "visual studio code":  {"Windows": "code",                    "Darwin": "Visual Studio Code",   "Linux": "code"},
    "github desktop":      {"Windows": "GitHubDesktop",           "Darwin": "GitHub Desktop",       "Linux": "github-desktop"},
    "postman":             {"Windows": "Postman",                 "Darwin": "Postman",              "Linux": "postman"},
    "docker":              {"Windows": "Docker Desktop",          "Darwin": "Docker",               "Linux": "docker-desktop"},
    "docker desktop":      {"Windows": "Docker Desktop",          "Darwin": "Docker",               "Linux": "docker-desktop"},

    # ── System Utilities & Deep OS Settings ───────────────────────────────────
    "explorer":            {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "file explorer":       {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "finder":              {"Windows": "explorer.exe",            "Darwin": "Finder",               "Linux": "nautilus"},
    "task manager":        {"Windows": "taskmgr.exe",             "Darwin": "Activity Monitor",     "Linux": "gnome-system-monitor"},
    "device manager":      {"Windows": "devmgmt.msc",             "Darwin": "System Information",   "Linux": "gnome-control-center"},
    "disk management":     {"Windows": "diskmgmt.msc",            "Darwin": "Disk Utility",         "Linux": "gnome-disks"},
    "services":            {"Windows": "services.msc",            "Darwin": "Activity Monitor",     "Linux": "gnome-system-monitor"},
    "event viewer":        {"Windows": "eventvwr.msc",            "Darwin": "Console",              "Linux": "gnome-logs"},
    "registry editor":     {"Windows": "regedit.exe",             "Darwin": "Terminal",             "Linux": "dconf-editor"},
    "regedit":             {"Windows": "regedit.exe",             "Darwin": "Terminal",             "Linux": "dconf-editor"},
    "control panel":       {"Windows": "control.exe",             "Darwin": "System Settings",      "Linux": "gnome-control-center"},
    "resource monitor":    {"Windows": "resmon.exe",              "Darwin": "Activity Monitor",     "Linux": "gnome-system-monitor"},
    "system information":  {"Windows": "msinfo32.exe",            "Darwin": "System Information",   "Linux": "gnome-control-center"},
    "task scheduler":      {"Windows": "taskschd.msc",            "Darwin": "Automator",            "Linux": "gnome-system-monitor"},
    "snipping tool":       {"Windows": "snippingtool.exe",        "Darwin": "Screenshot",           "Linux": "gnome-screenshot"},
    "on-screen keyboard":  {"Windows": "osk.exe",                 "Darwin": "KeyboardViewer",       "Linux": "onboard"},
    "settings":            {"Windows": "ms-settings:",            "Darwin": "System Settings",      "Linux": "gnome-control-center"},
    "bluetooth settings":  {"Windows": "ms-settings:bluetooth",   "Darwin": "System Settings",      "Linux": "gnome-control-center bluetooth"},
    "wifi settings":       {"Windows": "ms-settings:network-wifi","Darwin": "System Settings",      "Linux": "gnome-control-center wifi"},
    "network settings":    {"Windows": "ms-settings:network",     "Darwin": "System Settings",      "Linux": "gnome-control-center network"},
    "sound settings":      {"Windows": "ms-settings:sound",       "Darwin": "System Settings",      "Linux": "gnome-control-center sound"},
    "audio settings":      {"Windows": "ms-settings:sound",       "Darwin": "System Settings",      "Linux": "gnome-control-center sound"},
    "display settings":    {"Windows": "ms-settings:display",     "Darwin": "System Settings",      "Linux": "gnome-control-center display"},
    "windows update":      {"Windows": "ms-settings:windowsupdate","Darwin": "System Settings",     "Linux": "software-properties-gtk"},
    "power settings":      {"Windows": "ms-settings:powersleep",  "Darwin": "System Settings",      "Linux": "gnome-control-center power"},
    "battery settings":    {"Windows": "ms-settings:batterysaver","Darwin": "System Settings",      "Linux": "gnome-control-center power"},
    "storage settings":    {"Windows": "ms-settings:storagesense","Darwin": "System Settings",      "Linux": "gnome-control-center"},
    "installed apps":      {"Windows": "ms-settings:appsfeatures","Darwin": "Finder",               "Linux": "gnome-software"},
    "apps settings":       {"Windows": "ms-settings:appsfeatures","Darwin": "System Settings",      "Linux": "gnome-control-center applications"},
    "startup apps":        {"Windows": "ms-settings:startupapps", "Darwin": "System Settings",      "Linux": "gnome-session-properties"},
    "default apps":        {"Windows": "ms-settings:defaultapps", "Darwin": "System Settings",      "Linux": "gnome-control-center default-apps"},
    "microsoft store":     {"Windows": "ms-windows-store:",       "Darwin": "App Store",            "Linux": "gnome-software"},
    "store":               {"Windows": "ms-windows-store:",       "Darwin": "App Store",            "Linux": "gnome-software"},
    "calculator":          {"Windows": "calc.exe",                "Darwin": "Calculator",           "Linux": "gnome-calculator"},
    "notepad":             {"Windows": "notepad.exe",             "Darwin": "TextEdit",             "Linux": "gedit"},
    "textedit":            {"Windows": "notepad.exe",             "Darwin": "TextEdit",             "Linux": "gedit"},
    "paint":               {"Windows": "mspaint.exe",             "Darwin": "Preview",              "Linux": "gimp"},

    # ── Media, Office, Productivity & Gaming ──────────────────────────────────
    "spotify":             {"Windows": "Spotify",                 "Darwin": "Spotify",              "Linux": "spotify"},
    "vlc":                 {"Windows": "vlc",                     "Darwin": "VLC",                  "Linux": "vlc"},
    "netflix":             {"Windows": "Netflix",                 "Darwin": "Netflix",              "Linux": "firefox"},
    "figma":               {"Windows": "Figma",                   "Darwin": "Figma",                "Linux": "figma"},
    "blender":             {"Windows": "blender",                 "Darwin": "Blender",              "Linux": "blender"},
    "word":                {"Windows": "winword",                 "Darwin": "Microsoft Word",       "Linux": "libreoffice --writer"},
    "microsoft word":      {"Windows": "winword",                 "Darwin": "Microsoft Word",       "Linux": "libreoffice --writer"},
    "excel":               {"Windows": "excel",                   "Darwin": "Microsoft Excel",      "Linux": "libreoffice --calc"},
    "microsoft excel":     {"Windows": "excel",                   "Darwin": "Microsoft Excel",      "Linux": "libreoffice --calc"},
    "powerpoint":          {"Windows": "powerpnt",                "Darwin": "Microsoft PowerPoint", "Linux": "libreoffice --impress"},
    "libreoffice":         {"Windows": "soffice",                 "Darwin": "LibreOffice",          "Linux": "libreoffice"},
    "notion":              {"Windows": "Notion",                  "Darwin": "Notion",               "Linux": "notion"},
    "obsidian":            {"Windows": "Obsidian",                "Darwin": "Obsidian",             "Linux": "obsidian"},
    "capcut":              {"Windows": "CapCut",                  "Darwin": "CapCut",               "Linux": "capcut"},
    "steam":               {"Windows": "steam",                   "Darwin": "Steam",                "Linux": "steam"},
    "epic":                {"Windows": "EpicGamesLauncher",       "Darwin": "Epic Games Launcher",  "Linux": "legendary"},
    "epic games":          {"Windows": "EpicGamesLauncher",       "Darwin": "Epic Games Launcher",  "Linux": "legendary"},
    "obs":                 {"Windows": "obs64",                   "Darwin": "OBS",                  "Linux": "obs"},
    "obs studio":          {"Windows": "obs64",                   "Darwin": "OBS",                  "Linux": "obs"},
}


def _clean_app_phrase(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"^(please\s+)?(open|launch|start|run)\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^(the|a|an|my)\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+(app|application|program|window)$", "", s, flags=re.IGNORECASE)
    return s.strip()


def _normalize(raw: str) -> str:
    cleaned = _clean_app_phrase(raw)
    key = cleaned.lower()

    if key in _APP_ALIASES:
        return _APP_ALIASES[key].get(_SYSTEM, cleaned)

    # Whole-word phrase match only (longest alias first) — never match substrings
    # like 'git' inside 'GitHub Desktop' or 'word' inside 'Password Manager'.
    for alias_key in sorted(_APP_ALIASES, key=len, reverse=True):
        if len(alias_key) < 3:
            continue
        if re.search(rf"\b{re.escape(alias_key)}\b", key):
            return _APP_ALIASES[alias_key].get(_SYSTEM, cleaned)

    return cleaned or raw.strip()


def open_app(
    parameters=None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    raw_name = str(params.get("app_name", "") or "").strip()
    if not raw_name:
        return "No application name provided."

    cleaned = _clean_app_phrase(raw_name) or raw_name
    normalized = _normalize(raw_name)
    args = str(params.get("args", "") or "").strip()
    cwd = str(params.get("cwd", "") or "").strip()
    command = str(params.get("command", "") or "").strip()
    admin = bool(params.get("admin", False))

    print(f"[open_app] Launching: '{raw_name}' -> '{normalized}' ({_SYSTEM}, admin={admin})")
    if player and hasattr(player, "write_log"):
        player.write_log(f"[open_app] {cleaned}")

    try:
        res = launch_application(
            app_name=cleaned,
            normalized=normalized,
            args=args,
            cwd=cwd,
            command=command,
            admin=admin,
        )
        return res["message"]
    except Exception as e:
        print(f"[open_app] Error: {e}")
        return f"Failed to open {cleaned}: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "open_app",
    "description": (
        "Opens any desktop application, interactive terminal (PowerShell, CMD, "
        "Windows Terminal, WSL, Git Bash, macOS/Linux Terminal), system utility "
        "(Task Manager, Device Manager, Services, Registry Editor, Control Panel), "
        "deep OS settings page (Bluetooth, Wi-Fi, Sound, Display, Windows Update, "
        "Startup Apps), or folder (Downloads, Documents, path) — and VERIFIES "
        "that a real visible window or process actually opened before reporting "
        "success. Never claim an app opened if this tool reports failure."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app_name": {
                "type": "STRING",
                "description": (
                    "Name of the app, shell, system tool, settings page, or folder "
                    "(e.g. 'PowerShell', 'Windows Terminal', 'CMD', 'Chrome', "
                    "'VS Code', 'Device Manager', 'Bluetooth Settings', 'Downloads')"
                ),
            },
            "cwd": {
                "type": "STRING",
                "description": "Optional working directory to open the app/terminal in",
            },
            "command": {
                "type": "STRING",
                "description": "Optional startup command for terminals (runs visibly and keeps terminal open)",
            },
            "args": {
                "type": "STRING",
                "description": "Optional arguments or URL to pass to the application",
            },
            "admin": {
                "type": "BOOLEAN",
                "description": "True only if user explicitly asked to run as Administrator (triggers UAC prompt)",
            },
        },
        "required": ["app_name"],
    },
    "handler": open_app,
}
