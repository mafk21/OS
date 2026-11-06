"""Safe, owner-confirmed updates for source checkouts of JARVIS.

Checking is read-only apart from Git's remote-tracking metadata. Applying an
update is always gated by the non-forgeable HUD confirmation system, requires a
clean working tree, and accepts fast-forward updates from origin/main only.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core import confirm

ROOT = Path(__file__).resolve().parent.parent
REMOTE = "origin"
BRANCH = "main"
GIT_TIMEOUT = 45


@dataclass(frozen=True)
class UpdateStatus:
    state: str
    message: str
    local_revision: str = ""
    remote_revision: str = ""
    commits_behind: int = 0

    @property
    def available(self) -> bool:
        return self.state == "available"


def _git(*args: str, timeout: int = GIT_TIMEOUT, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    # Startup checks must never open an interactive credential prompt.
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=check,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _revision(ref: str) -> str:
    return _git("rev-parse", "--verify", ref).stdout.strip()


def _is_source_checkout() -> bool:
    if getattr(sys, "frozen", False) or not (ROOT / ".git").exists():
        return False
    result = _git("rev-parse", "--show-toplevel", check=False)
    if result.returncode != 0:
        return False
    try:
        return Path(result.stdout.strip()).resolve() == ROOT.resolve()
    except OSError:
        return False


def _working_tree_clean() -> bool:
    return not _git("status", "--porcelain", "--untracked-files=normal").stdout.strip()


def check_for_updates(*, fetch: bool = True) -> UpdateStatus:
    """Check origin/main without modifying application source files."""
    if not _is_source_checkout():
        return UpdateStatus("unsupported", "Automatic updates are available only for Git source installations.")
    try:
        if fetch:
            _git("fetch", "--quiet", "--no-tags", REMOTE, BRANCH)
        local = _revision("HEAD")
        remote = _revision(f"refs/remotes/{REMOTE}/{BRANCH}")
        if local == remote:
            return UpdateStatus("current", "JARVIS is already up to date.", local, remote)
        ancestor = _git("merge-base", "--is-ancestor", "HEAD", remote, check=False)
        if ancestor.returncode != 0:
            return UpdateStatus(
                "diverged",
                "This checkout has commits that differ from origin/main. Update manually so no work is overwritten.",
                local,
                remote,
            )
        count_text = _git("rev-list", "--count", f"HEAD..{remote}").stdout.strip()
        count = int(count_text or "0")
        return UpdateStatus(
            "available",
            f"A JARVIS update is available ({count} new commit{'s' if count != 1 else ''}).",
            local,
            remote,
            count,
        )
    except FileNotFoundError:
        return UpdateStatus("error", "Git is not installed or is not available on PATH.")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return UpdateStatus("error", f"Could not check for updates ({type(exc).__name__}).")


def _launch_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [str(Path(sys.executable).resolve())]
    return [str(Path(sys.executable).resolve()), str((ROOT / "main.py").resolve()), *sys.argv[1:]]


def _schedule_restart(player=None) -> None:
    """Start a small waiter, then close this process so the waiter relaunches it."""
    helper = (ROOT / "core" / "restart_helper.py").resolve()
    command = _launch_command()
    subprocess.Popen(
        [str(Path(sys.executable).resolve()), str(helper), "--parent", str(os.getpid()),
         "--cwd", str(ROOT), "--", *command],
        cwd=str(ROOT),
        close_fds=True,
    )
    if player is not None and getattr(player, "root", None) is not None:
        player.root.after(0, player.root.destroy)
        return
    # Headless fallback. The helper waits for this process before relaunching.
    threading.Timer(0.2, lambda: os._exit(0)).start()


def apply_update_and_restart(player=None) -> str:
    """Apply one confirmed fast-forward update and schedule a clean relaunch."""
    if not _is_source_checkout():
        raise RuntimeError("This JARVIS installation is not an updateable Git checkout.")
    if not _working_tree_clean():
        raise RuntimeError("Update cancelled because the repository has local changes. Commit or remove them first.")
    status = check_for_updates(fetch=True)
    if not status.available:
        return status.message
    _git("merge", "--ff-only", status.remote_revision, timeout=120)
    _schedule_restart(player)
    return "Update installed. JARVIS is closing and will restart automatically."


def request_update(status: UpdateStatus, *, player=None) -> str:
    """Put an available update behind the HUD's human confirmation gate."""
    if not status.available:
        return status.message
    if not _working_tree_clean():
        return "An update is available, but this repository has local changes. Commit or remove them before updating."
    if confirm.pending_title():
        return "Another confirmation is already waiting on screen. Confirm or cancel it first."
    return confirm.request(
        "jarvis-self-update",
        "Update JARVIS and restart?",
        f"Install {status.commits_behind} new commit{'s' if status.commits_behind != 1 else ''} from origin/main. JARVIS will close and reopen.",
        lambda: apply_update_and_restart(player),
    )


def check_and_offer(*, player=None, log: Callable[[str], None] | None = None) -> UpdateStatus:
    status = check_for_updates(fetch=True)
    if status.available:
        response = request_update(status, player=player)
        if log:
            log(f"SYS: {status.message} {response}")
    elif status.state == "error" and log:
        log(f"NET: {status.message}")
    return status


def start_startup_check(*, player=None, log: Callable[[str], None] | None = None, delay: float = 3.0) -> None:
    """Check once in the background after startup; never delay the UI."""
    def worker() -> None:
        if delay > 0:
            time.sleep(delay)
        check_and_offer(player=player, log=log)

    threading.Thread(target=worker, daemon=True, name="jarvis-update-check").start()
