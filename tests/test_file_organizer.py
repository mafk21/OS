"""Tests for Downloads/Desktop file organization, path targeting, move resolution, and undo."""

from __future__ import annotations

from pathlib import Path

import actions.desktop as desk
import actions.file_controller as fc
from core import undo as undo_stack


def _isolate_user_dirs(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    desktop = home / "Desktop"
    downloads = home / "Downloads"
    documents = home / "Documents"
    for d in (desktop, downloads, documents):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(fc, "_SAFE_ROOTS", [home])
    monkeypatch.setattr(fc, "_get_desktop", lambda: desktop)
    monkeypatch.setattr(fc, "_get_downloads", lambda: downloads)
    monkeypatch.setattr(fc, "_get_documents", lambda: documents)
    monkeypatch.setattr(fc, "_get_pictures", lambda: home / "Pictures")
    monkeypatch.setattr(fc, "_get_music", lambda: home / "Music")
    monkeypatch.setattr(fc, "_get_videos", lambda: home / "Videos")
    undo_stack.clear()
    return home, desktop, downloads, documents


def test_organize_downloads_moves_files_into_downloads_and_never_touches_desktop(monkeypatch, tmp_path):
    _, desktop, downloads, _ = _isolate_user_dirs(monkeypatch, tmp_path)

    (downloads / "syllabus.pdf").write_text("pdf", encoding="utf-8")
    (downloads / "screenshot.png").write_text("png", encoding="utf-8")
    (downloads / "setup_v2.exe").write_text("exe", encoding="utf-8")
    (downloads / "backup.zip").write_text("zip", encoding="utf-8")
    # In-progress browser download & Office lockfile must stay untouched
    (downloads / "movie.mp4.crdownload").write_text("part", encoding="utf-8")
    (downloads / "~$draft.docx").write_text("lock", encoding="utf-8")

    # Dry-run preview first: touches nothing
    preview = fc.file_controller({"action": "organize", "path": "downloads", "dry_run": True})
    assert "[DRY RUN]" in preview
    assert (downloads / "syllabus.pdf").exists()

    # Real organize on Downloads
    out = fc.file_controller({"action": "organize", "path": "downloads"})
    assert "4 file(s) moved" in out

    # Files actually moved into category folders inside Downloads
    assert (downloads / "Documents" / "syllabus.pdf").exists()
    assert (downloads / "Images" / "screenshot.png").exists()
    assert (downloads / "Installers" / "setup_v2.exe").exists()
    assert (downloads / "Archives" / "backup.zip").exists()

    # Zero empty category folders created (no Videos/ or Audio/ since none existed)
    assert not (downloads / "Videos").exists()
    assert not (downloads / "Audio").exists()

    # Active downloads & lockfiles untouched in Downloads root
    assert (downloads / "movie.mp4.crdownload").exists()
    assert (downloads / "~$draft.docx").exists()

    # Desktop was NEVER touched (0 folders created on Desktop!)
    assert list(desktop.iterdir()) == []

    # Single-step Undo puts all 4 files back and removes empty category folders
    undo_msg = undo_stack.undo_last()
    assert "4 file(s) restored" in undo_msg
    assert (downloads / "syllabus.pdf").exists()
    assert (downloads / "screenshot.png").exists()
    assert (downloads / "setup_v2.exe").exists()
    assert (downloads / "backup.zip").exists()
    assert not (downloads / "Documents").exists()
    assert not (downloads / "Images").exists()


def test_organize_handles_name_collisions_without_skipping_or_overwriting(monkeypatch, tmp_path):
    _, _, downloads, _ = _isolate_user_dirs(monkeypatch, tmp_path)

    existing_docs = downloads / "Documents"
    existing_docs.mkdir()
    (existing_docs / "invoice.pdf").write_text("old-invoice", encoding="utf-8")
    (downloads / "invoice.pdf").write_text("new-invoice", encoding="utf-8")

    out = fc.file_controller({"action": "organize", "path": "my downloads"})
    assert "1 file(s) moved" in out
    assert (existing_docs / "invoice.pdf").read_text(encoding="utf-8") == "old-invoice"
    assert (existing_docs / "invoice (2).pdf").read_text(encoding="utf-8") == "new-invoice"
    assert not (downloads / "invoice.pdf").exists()


def test_refuses_to_guess_desktop_when_path_omitted(monkeypatch, tmp_path):
    _, desktop, _, _ = _isolate_user_dirs(monkeypatch, tmp_path)

    res_org = fc.file_controller({"action": "organize"})
    assert "refusing to guess desktop" in res_org.lower()

    res_mkdir = fc.file_controller({"action": "create_folder", "name": "Images"})
    assert "refusing to guess desktop" in res_mkdir.lower()
    assert list(desktop.iterdir()) == []


def test_manual_move_resolves_bare_subfolder_inside_source_parent(monkeypatch, tmp_path):
    _, _, downloads, documents = _isolate_user_dirs(monkeypatch, tmp_path)

    (downloads / "photo.jpg").write_text("img", encoding="utf-8")
    (downloads / "notes.pdf").write_text("pdf", encoding="utf-8")
    (downloads / "Documents").mkdir()

    # Bare destination 'Images' creates Downloads/Images (NOT CWD/Images!)
    r1 = fc.file_controller({
        "action": "move",
        "path": "downloads/photo.jpg",
        "destination": "Images",
    })
    assert "Moved:" in r1
    assert (downloads / "Images" / "photo.jpg").exists()

    # Bare destination 'Documents' when Downloads/Documents exists moves into Downloads/Documents
    # instead of hijacking to ~/Documents!
    r2 = fc.file_controller({
        "action": "move",
        "path": "downloads/notes.pdf",
        "destination": "Documents",
    })
    assert "Moved:" in r2
    assert (downloads / "Documents" / "notes.pdf").exists()
    assert not (documents / "notes.pdf").exists()


def test_desktop_control_organize_or_task_routes_downloads_correctly(monkeypatch, tmp_path):
    _, desktop, downloads, _ = _isolate_user_dirs(monkeypatch, tmp_path)

    (downloads / "lecture.pptx").write_text("slides", encoding="utf-8")
    out = desk.desktop_control({"action": "task", "task": "Organize my files in Downloads"})
    assert "1 file(s) moved" in out
    assert (downloads / "Documents" / "lecture.pptx").exists()
    assert list(desktop.iterdir()) == []


def test_clean_empty_folders_removes_ghost_folders_safely(monkeypatch, tmp_path):
    _, desktop, _, _ = _isolate_user_dirs(monkeypatch, tmp_path)

    (desktop / "Images").mkdir()
    (desktop / "Videos").mkdir()
    keep = desktop / "RealProject"
    keep.mkdir()
    (keep / "main.py").write_text("print(1)", encoding="utf-8")

    out = fc.file_controller({"action": "clean_empty_folders", "path": "desktop"})
    assert "Removed 2 empty folder(s)" in out
    assert not (desktop / "Images").exists()
    assert not (desktop / "Videos").exists()
    assert (keep / "main.py").exists()
