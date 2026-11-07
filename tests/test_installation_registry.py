from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from core import installation_registry as registry


def isolated(monkeypatch, tmp_path):
    state = tmp_path / "machine" / "installations.json"
    monkeypatch.setattr(registry, "registry_path", lambda: state)
    return state


def register(root: Path):
    return registry.ensure_current(
        install_type="git", revision="abc123", executable=str(root / "python"), root=root
    )


def test_first_running_installation_becomes_active(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    root = tmp_path / "one"
    root.mkdir()

    record = register(root)
    status = registry.status(record["installation_id"])

    assert record["active"] is True
    assert status["is_active"] is True
    assert status["other_count"] == 0


def test_registry_detects_side_by_side_installations_without_scanning(monkeypatch, tmp_path):
    state = isolated(monkeypatch, tmp_path)
    first_root, second_root = tmp_path / "one", tmp_path / "two"
    first_root.mkdir(); second_root.mkdir()

    first = register(first_root)
    second = register(second_root)
    snapshot = registry.status(second["installation_id"])

    assert first["installation_id"] != second["installation_id"]
    assert snapshot["is_active"] is False
    assert snapshot["other_count"] == 1
    assert json.loads(state.read_text(encoding="utf-8"))["active_id"] == first["installation_id"]


def test_moved_portable_installation_keeps_identity(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    old = tmp_path / "old"
    old.mkdir()
    first = register(old)
    marker_text = (old / "config" / "installation.json").read_text(encoding="utf-8")
    (old / "config" / "installation.json").unlink()
    (old / "config").rmdir(); old.rmdir()
    moved = tmp_path / "moved"
    (moved / "config").mkdir(parents=True)
    (moved / "config" / "installation.json").write_text(marker_text, encoding="utf-8")

    current = register(moved)

    assert current["installation_id"] == first["installation_id"]
    assert registry.status(current["installation_id"])["is_active"] is True


def test_copied_live_installation_gets_fresh_identity(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    original = tmp_path / "original"
    original.mkdir()
    first = register(original)
    copy = tmp_path / "copy"
    (copy / "config").mkdir(parents=True)
    (copy / "config" / "installation.json").write_text(
        (original / "config" / "installation.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    second = register(copy)

    assert second["installation_id"] != first["installation_id"]
    assert registry.status(second["installation_id"])["other_count"] == 1


def test_activation_rolls_registry_back_if_shortcut_verification_fails(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    first_root, second_root = tmp_path / "one", tmp_path / "two"
    first_root.mkdir(); second_root.mkdir()
    first, second = register(first_root), register(second_root)
    import core.system_repair as repair
    monkeypatch.setattr(repair, "execute_repair", lambda _name: SimpleNamespace(ok=False, verified=False))

    try:
        registry.activate_and_refresh_shortcut(second["installation_id"])
    except RuntimeError:
        pass

    assert registry.status(first["installation_id"])["is_active"] is True


def test_make_active_is_confirmation_gated(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    first_root, second_root = tmp_path / "one", tmp_path / "two"
    first_root.mkdir(); second_root.mkdir()
    register(first_root)
    second = register(second_root)
    captured = []
    from core import confirm
    monkeypatch.setattr(confirm, "request", lambda *args: captured.append(args) or "[CONFIRMATION_PENDING]")

    message = registry.request_make_active(second["installation_id"])

    assert message == "[CONFIRMATION_PENDING]"
    assert captured and captured[0][0] == "jarvis-make-installation-active"
    assert registry.status(second["installation_id"])["is_active"] is False


def test_unregister_only_removes_metadata(monkeypatch, tmp_path):
    isolated(monkeypatch, tmp_path)
    root = tmp_path / "installation"
    root.mkdir()
    record = register(root)

    assert registry.unregister(record["installation_id"]) is True
    assert root.exists()
    assert (root / "config" / "installation.json").exists()
