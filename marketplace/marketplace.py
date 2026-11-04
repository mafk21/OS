"""Plugin marketplace — one-click install with bounded, traversal-safe extraction."""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import tempfile
import time
from urllib.parse import urlparse

import requests

from core.archive_safety import extract_archive

REGISTRY_URL = "https://raw.githubusercontent.com/mafk21/OS-marketplace/main/registry.json"
INSTALL_DIR = pathlib.Path("plugins")
CACHE = pathlib.Path("memory/marketplace_cache.json")
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024


def _fetch_registry():
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < 3600:
        return json.loads(CACHE.read_text())
    try:
        response = requests.get(REGISTRY_URL, timeout=10)
        response.raise_for_status()
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(response.text)
        return response.json()
    except (requests.RequestException, ValueError, OSError):
        return {"plugins": []}


def list_marketplace():
    return _fetch_registry().get("plugins", [])


def _plugin_dir(name: str) -> pathlib.Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", name or ""):
        raise ValueError("Invalid plugin name")
    root = INSTALL_DIR.resolve()
    target = (root / name).resolve()
    if target.parent != root:
        raise ValueError("Plugin path escapes install directory")
    return target


def install_plugin(name: str, version: str = "latest"):
    reg = _fetch_registry()
    for plugin in reg.get("plugins", []):
        if plugin.get("name") != name:
            continue
        url = str(plugin.get("zip_url", "") or plugin.get("url", "")).strip()
        parts = urlparse(url)
        if parts.scheme != "https" or not parts.hostname:
            return f"Install failed: plugin URL must use HTTPS"
        try:
            target = _plugin_dir(name)
            with requests.get(url, timeout=30, stream=True) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    zpath = pathlib.Path(tmp.name)
                    downloaded = 0
                    for chunk in response.iter_content(64 * 1024):
                        if not chunk:
                            continue
                        downloaded += len(chunk)
                        if downloaded > MAX_DOWNLOAD_BYTES:
                            raise ValueError("Plugin archive exceeds 100 MB limit")
                        tmp.write(chunk)
            try:
                extract_archive(zpath, target)
            finally:
                zpath.unlink(missing_ok=True)
            return f"Installed {name}@{version} to plugins/{name} — restart to load"
        except Exception as exc:
            return f"Install failed: {type(exc).__name__}"
    return f"Plugin {name} not found in marketplace"


def remove_plugin(name: str):
    try:
        target = _plugin_dir(name)
    except ValueError as exc:
        return f"Remove failed: {exc}"
    if not target.exists():
        return f"Plugin {name} not installed"
    shutil.rmtree(target)
    return f"Removed {name}"
