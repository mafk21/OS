#!/usr/bin/env python3
"""Build clean, reproducible JARVIS source bundles from Git-tracked files only."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release"
EXCLUDED_PREFIXES = (".github/", "tests/", "tools/", "docs/assets/")
EXCLUDED_EXACT = {".gitignore", "RELEASING.md"}


def tracked_files() -> list[str]:
    raw = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    names = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    return [
        n for n in names
        if n not in EXCLUDED_EXACT
        and not n.startswith(EXCLUDED_PREFIXES)
        and (ROOT / n).is_file()
    ]


def files_for(platform: str) -> list[str]:
    names = tracked_files()
    platform_launchers = {
        "windows": {"Start_JARVIS.command", "Start_JARVIS.sh"},
        "macos": {"Start_JARVIS.bat", "Start_JARVIS.sh"},
        "linux": {"Start_JARVIS.bat", "Start_JARVIS.command"},
    }
    return [n for n in names if n not in platform_launchers[platform]]


def zip_bundle(path: Path, prefix: str, names: list[str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in names:
            data = (ROOT / name).read_bytes()
            info = zipfile.ZipInfo(f"{prefix}/{PurePosixPath(name)}", (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.endswith((".sh", ".command")) else 0o644) << 16
            zf.writestr(info, data)


def tar_bundle(path: Path, prefix: str, names: list[str]) -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name in names:
            data = (ROOT / name).read_bytes()
            info = tarfile.TarInfo(f"{prefix}/{PurePosixPath(name)}")
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if name.endswith((".sh", ".command")) else 0o644
            tf.addfile(info, io.BytesIO(data))
    with path.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0, compresslevel=9) as gz:
            gz.write(raw.getvalue())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    version = args.version.removeprefix("v")
    prefix = f"JARVIS-{version}"
    OUT.mkdir(exist_ok=True)
    for old in OUT.iterdir():
        if old.is_file():
            old.unlink()

    windows = OUT / f"{prefix}-windows.zip"
    macos = OUT / f"{prefix}-macos.tar.gz"
    linux = OUT / f"{prefix}-linux.tar.gz"
    zip_bundle(windows, prefix, files_for("windows"))
    tar_bundle(macos, prefix, files_for("macos"))
    tar_bundle(linux, prefix, files_for("linux"))

    archives = (windows, macos, linux)
    checksums = "".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in archives
    )
    (OUT / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
    print(checksums, end="")


if __name__ == "__main__":
    main()
