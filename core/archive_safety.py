"""Bounded archive extraction with traversal and link defenses."""
from __future__ import annotations

import os
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILES = 10_000
MAX_TOTAL_BYTES = 1_000_000_000


def _target(root: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or pure.drive or ".." in pure.parts or not pure.parts:
        raise ValueError(f"Unsafe archive member: {member_name!r}")
    target = (root / Path(*pure.parts)).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Archive member escapes destination: {member_name!r}")
    return target


def extract_archive(source: Path, destination: Path) -> None:
    """Extract ZIP/TAR archives without traversal, links, or decompression bombs."""
    source = Path(source)
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    total = 0

    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            members = archive.infolist()
            if len(members) > MAX_FILES:
                raise ValueError("Archive contains too many files")
            for member in members:
                target = _target(root, member.filename)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"Archive links are not allowed: {member.filename!r}")
                total += member.file_size
                if total > MAX_TOTAL_BYTES:
                    raise ValueError("Archive expands beyond the safety limit")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
        return

    if tarfile.is_tarfile(source):
        with tarfile.open(source) as archive:
            members = archive.getmembers()
            if len(members) > MAX_FILES:
                raise ValueError("Archive contains too many files")
            for member in members:
                target = _target(root, member.name)
                if member.issym() or member.islnk() or member.isdev():
                    raise ValueError(f"Archive links/devices are not allowed: {member.name!r}")
                total += max(0, member.size)
                if total > MAX_TOTAL_BYTES:
                    raise ValueError("Archive expands beyond the safety limit")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    src = archive.extractfile(member)
                    if src is None:
                        raise ValueError(f"Unreadable archive member: {member.name!r}")
                    with src, target.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
        return

    raise ValueError("Unsupported or invalid archive format")
