from __future__ import annotations

import io
import stat
import tarfile
import zipfile
from pathlib import Path

import pytest

from core.archive_safety import extract_archive


def test_zip_traversal_is_rejected_without_outside_write(tmp_path: Path) -> None:
    archive = tmp_path / "attack.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../../evil.py", "owned")
    dest = tmp_path / "plugins" / "demo"
    with pytest.raises(ValueError, match="Unsafe|escapes"):
        extract_archive(archive, dest)
    assert not (tmp_path / "evil.py").exists()


def test_zip_symlink_is_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "link.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, "../../outside")
    with pytest.raises(ValueError, match="links"):
        extract_archive(archive, tmp_path / "out")


def test_tar_links_are_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "attack.tar"
    with tarfile.open(archive, "w") as tf:
        member = tarfile.TarInfo("safe-link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        tf.addfile(member)
    with pytest.raises(ValueError, match="links"):
        extract_archive(archive, tmp_path / "out")


def test_normal_zip_extracts(tmp_path: Path) -> None:
    archive = tmp_path / "normal.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("folder/plugin.py", "VALUE = 1\n")
    dest = tmp_path / "out"
    extract_archive(archive, dest)
    assert (dest / "folder" / "plugin.py").read_text() == "VALUE = 1\n"
