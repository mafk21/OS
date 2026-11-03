"""Publication guard: runtime identities, sessions and secrets never enter Git."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def _tracked() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [p.decode("utf-8", "surrogateescape") for p in result.stdout.split(b"\0") if p]


def test_runtime_and_identity_data_are_not_tracked() -> None:
    tracked = _tracked()
    exact = {
        "config/api_keys.json", "config/social_preferences.json", "config/.vault.key",
        "memory/long_term.json", "memory/accounts.json", "memory/companions.json",
        "memory/custom_tools.json", "memory/automations.json", "memory/routines.json",
        "memory/telegram_pairing.json", "memory/hosted_auth.json",
        "memory/screen_permissions.yaml", "memory/calendar_monitor_enabled",
    }
    forbidden_suffixes = (
        ".db", ".sqlite", ".sqlite3", ".pem", ".p12", ".pfx", ".log"
    )
    forbidden_parts = {
        "knowledge_files", "custom_skills", "learning", "generated_videos",
        "whatsapp_web", "browser-profile", "browser_profiles", "user-data", "user_data",
    }
    bad = []
    for name in tracked:
        path = PurePosixPath(name)
        low = name.lower()
        if name in exact or low.endswith(forbidden_suffixes) or forbidden_parts.intersection(path.parts):
            # Empty keep-file is the only permitted marker in a private output directory.
            if name != "memory/lecture_capture/.gitkeep":
                bad.append(name)
    assert not bad, "Private runtime files tracked by Git: " + ", ".join(bad)


def test_tracked_text_has_no_high_confidence_live_secrets() -> None:
    patterns = {
        "OpenAI-style key": re.compile(rb"\bsk-[A-Za-z0-9_-]{24,}\b"),
        "Google API key": re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
        "GitHub token": re.compile(rb"\b(?:gh[opsu]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"),
        "Slack token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
        "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    findings = []
    for name in _tracked():
        # Test credentials are assembled from fragments so provider-shaped
        # literals never trigger public-repository secret scanning.
        path = ROOT / name
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        data = path.read_bytes()
        for label, pattern in patterns.items():
            if pattern.search(data):
                findings.append(f"{name} ({label})")
    assert not findings, "Possible live secrets in tracked files: " + ", ".join(findings)


def test_production_code_avoids_insecure_temporary_names() -> None:
    """mktemp creates a race window where another process can claim the path."""
    findings = []
    for folder in ("actions", "auth", "core", "dashboard", "marketplace", "memory", "smart_home"):
        for path in (ROOT / folder).rglob("*.py"):
            if "tempfile.mktemp(" in path.read_text(encoding="utf-8", errors="replace"):
                findings.append(str(path.relative_to(ROOT)))
    assert not findings, "Insecure tempfile.mktemp usage: " + ", ".join(findings)


def test_ignore_policy_covers_all_runtime_storage() -> None:
    ignored = [
        "config/api_keys.json", "config/social_preferences.json", "config/.vault.key",
        "config/certs/jarvis.key", "config/whatsapp_web/session.json",
        "memory/long_term.json", "memory/accounts.json", "memory/routines.json",
        "memory/brain.db", "memory/security_audit.db", "memory/screen_permissions.yaml",
        "memory/lecture_capture/private-notes.txt", "memory/generated-face.png",
        ".jarvis_profiles/chrome/Cookies", "screenshots/private-screen.png",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"], cwd=ROOT,
        input="\n".join(ignored) + "\n", text=True, capture_output=True, check=False,
    )
    matched = set(result.stdout.splitlines())
    assert set(ignored) <= matched, f"Runtime paths missing from .gitignore: {set(ignored) - matched}"
