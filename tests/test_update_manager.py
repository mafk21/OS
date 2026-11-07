from __future__ import annotations

import subprocess

import pytest

from actions.jarvis_update import jarvis_update
from core import confirm
from core import restart_helper
from core import update_manager as updates


def _run(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture()
def git_checkout(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    local = tmp_path / "local"
    _run(tmp_path, "git", "init", "--bare", str(remote))
    _run(tmp_path, "git", "init", "-b", "main", str(seed))
    _run(seed, "git", "config", "user.email", "test@example.invalid")
    _run(seed, "git", "config", "user.name", "Test")
    (seed / "main.py").write_text("print('one')\n", encoding="utf-8")
    _run(seed, "git", "add", "main.py")
    _run(seed, "git", "commit", "-m", "initial")
    _run(seed, "git", "remote", "add", "origin", str(remote))
    _run(seed, "git", "push", "-u", "origin", "main")
    _run(tmp_path, "git", "clone", "-b", "main", str(remote), str(local))
    monkeypatch.setattr(updates, "ROOT", local)
    monkeypatch.setattr(updates.sys, "frozen", False, raising=False)
    return seed, local


def _push_update(seed, text="print('two')\n"):
    (seed / "main.py").write_text(text, encoding="utf-8")
    _run(seed, "git", "add", "main.py")
    _run(seed, "git", "commit", "-m", "update")
    _run(seed, "git", "push", "origin", "main")


def test_check_reports_current_then_available(git_checkout):
    seed, _local = git_checkout
    assert updates.check_for_updates().state == "current"
    _push_update(seed)
    status = updates.check_for_updates()
    assert status.available
    assert status.commits_behind == 1
    assert status.local_revision != status.remote_revision


def test_update_refuses_dirty_checkout(git_checkout):
    seed, local = git_checkout
    _push_update(seed)
    (local / "notes.txt").write_text("do not overwrite", encoding="utf-8")
    status = updates.check_for_updates()
    assert "local changes" in updates.request_update(status).lower()
    with pytest.raises(RuntimeError, match="local changes"):
        updates.apply_update_and_restart()
    assert (local / "notes.txt").read_text(encoding="utf-8") == "do not overwrite"


def test_confirmed_update_fast_forwards_and_schedules_restart(git_checkout, monkeypatch):
    seed, local = git_checkout
    _push_update(seed)
    restarted = []
    monkeypatch.setattr(updates, "_schedule_restart", lambda player=None: restarted.append(player))

    result = updates.apply_update_and_restart(player="ui")

    assert "restart" in result.lower()
    assert restarted == ["ui"]
    assert "two" in (local / "main.py").read_text(encoding="utf-8")
    assert _run(local, "git", "status", "--porcelain").stdout == ""


def test_action_uses_non_forgeable_confirmation(git_checkout, monkeypatch):
    seed, _local = git_checkout
    _push_update(seed)
    shown = []
    monkeypatch.setattr(confirm, "_pending", None)
    confirm.bind(lambda title, detail: shown.append((title, detail)), lambda: None)

    response = jarvis_update({"action": "update"}, player="ui")

    assert response.startswith("[CONFIRMATION_PENDING]")
    assert shown and "Update JARVIS" in shown[0][0]
    # Do not leave a live confirmation in the global test process.
    confirm.resolve(False)


def test_restart_helper_waits_then_launches(monkeypatch, tmp_path):
    alive = iter([True, False, False])
    launched = []
    monkeypatch.setattr(restart_helper, "_parent_alive", lambda _pid: next(alive))
    monkeypatch.setattr(restart_helper.time, "sleep", lambda _delay: None)
    monkeypatch.setattr(restart_helper.subprocess, "Popen", lambda command, **kwargs: launched.append((command, kwargs)))

    result = restart_helper.main([
        "--parent", "123", "--cwd", str(tmp_path), "--", "python", "main.py"
    ])

    assert result == 0
    assert launched[0][0] == ["python", "main.py"]
    assert launched[0][1]["cwd"] == str(tmp_path.resolve())


def test_restart_helper_rejects_different_installation_identity(tmp_path):
    config = tmp_path / "config"
    config.mkdir()
    (config / "installation.json").write_text('{"installation_id":"expected"}', encoding="utf-8")

    result = restart_helper.main([
        "--parent", "123", "--cwd", str(tmp_path),
        "--installation-id", "different", "--", "python", "main.py"
    ])

    assert result == 4
