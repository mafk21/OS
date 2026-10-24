"""
End-to-end tests for Phase 5: Live Streaming Dev Terminal, Bidirectional Stdin,
1-Click Process Stop, Codebase File-Tree Map, and Unified Git Diffs.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

from core import dev_workspace as dw
from core.apex_bridge import ApexHudBridge


class _ReadyUI:
    def __init__(self):
        self._win = type("W", (), {"_ready": True})()
        self._integrations_ready = True
        self._persona_selected = True
        self.muted = False


def test_streaming_terminal_stdin_and_stop(tmp_path):
    mgr = dw.DevTerminalManager()
    events = []
    mgr.add_listener(events.append)

    # Interactive stdin -> stdout roundtrip
    sess = mgr.start_command(
        f'{sys.executable} -u -c "import sys; ln = sys.stdin.readline().strip(); print(\'GOT:\' + ln)"',
        cwd=str(tmp_path),
    )
    time.sleep(0.15)
    assert mgr.send_stdin(sess["id"], "HELLO_STREAM") is True

    deadline = time.monotonic() + 5.0
    final = None
    while time.monotonic() < deadline:
        cur = next(s for s in mgr.list_sessions() if s["id"] == sess["id"])
        if cur["status"] == "completed":
            final = cur
            break
        time.sleep(0.05)

    assert final is not None
    assert "GOT:HELLO_STREAM" in final["output"]
    assert len(events) >= 2

    # Long-running command stopped cleanly via stop_command
    long_sess = mgr.start_command(f'{sys.executable} -c "import time; time.sleep(30)"', cwd=str(tmp_path))
    time.sleep(0.15)
    assert mgr.stop_command(long_sess["id"]) is True
    stopped = next(s for s in mgr.list_sessions() if s["id"] == long_sess["id"])
    assert stopped["status"] == "stopped"


def test_codebase_tree_traversal_guard_and_git_diffs(tmp_path):
    # Initialize temporary git repo
    subprocess.run(["git", "init"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@jarvis.local"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.name", "JARVIS"], cwd=str(tmp_path), check=True)

    app_py = tmp_path / "src" / "app.py"
    app_py.parent.mkdir(parents=True)
    app_py.write_text("def greet():\n    return 'hi'\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(tmp_path), check=True, capture_output=True)

    # Modify tracked file + create untracked file
    app_py.write_text("def greet():\n    return 'hello world'\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("# New Feature\n", encoding="utf-8")

    tree = dw.build_codebase_tree(str(tmp_path))
    paths = {e["path"] for e in tree["entries"]}
    assert "src/app.py" in paths
    assert "notes.md" in paths

    f_read = dw.read_workspace_file(str(tmp_path), "src/app.py")
    assert "hello world" in f_read["content"]

    # Path traversal outside root must raise ValueError
    with pytest.raises(ValueError):
        dw.read_workspace_file(str(tmp_path), "../../etc/passwd")

    diffs = dw.get_workspace_diffs(str(tmp_path))
    assert diffs["is_git"] is True
    by_path = {f["path"]: f for f in diffs["files"]}
    assert "src/app.py" in by_path
    assert by_path["src/app.py"]["additions"] >= 1
    assert by_path["src/app.py"]["deletions"] >= 1
    assert "notes.md" in by_path


def test_hud_dev_http_endpoints(tmp_path):
    from fastapi.testclient import TestClient

    (tmp_path / "hello.py").write_text("print(42)\n", encoding="utf-8")
    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=8765)
    app = bridge._build_app()

    with TestClient(app) as client:
        info = client.get(f"/api/hud/dev?root_dir={tmp_path}").json()
        assert info["ok"] is True
        assert any(e["path"] == "hello.py" for e in info["tree"]["entries"])

        fread = client.post(
            "/api/hud/action",
            json={"action": "dev_read_file", "root_dir": str(tmp_path), "path": "hello.py"},
        ).json()
        assert fread["ok"] is True
        assert "print(42)" in fread["file"]["content"]
