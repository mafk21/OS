"""Tests — screen memory (Phase 7): SQLite/FTS5 store, search, permissions."""
import os
import tempfile
import time
from pathlib import Path

# Point ScreenMemory at a tmp DB before importing the module
tmp_db = Path(tempfile.mkdtemp()) / "screen_memory.db"
os.environ["SCREEN_MEMORY_DB"] = str(tmp_db)

import core.screen_memory as sm


# ── Database ──────────────────────────────────────────────────────────────

def test_init_creates_db(tmp_path):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)
    assert db.exists()
    stats = store.stats()
    assert "events" in stats
    assert stats["events"] == 0


def test_store_and_search(tmp_path):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)

    event = {
        "ts": time.monotonic(),
        "iso_ts": __import__("datetime").datetime.now().isoformat(),
        "app": "Safari",
        "title": "Amazon - laptop search",
        "ocr_text": "MacBook Pro M3 $1999",
        "a11y_tree": "",
        "image_path": "",
        "duration_ms": 100,
    }
    store._store(event)

    results = store.search("MacBook", limit=5)
    assert len(results) >= 1
    assert results[0]["app"] == "Safari"
    assert "MacBook" in results[0]["ocr_text"]


def test_search_no_results(tmp_path):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)
    results = store.search("nonexistentxyz", limit=5)
    assert results == []


def test_recent_returns_empty_when_no_events(tmp_path):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)
    assert store.recent(limit=5) == []


def test_stats_shape(tmp_path):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)
    stats = store.stats()
    assert isinstance(stats["events"], int)
    assert isinstance(stats["size_mb"], float)
    assert "ocr_available" in stats
    assert "capture_available" in stats


# ── Permissions ───────────────────────────────────────────────────────────

def test_is_app_allowed_no_permissions(tmp_path, monkeypatch):
    perms_path = tmp_path / "screen_permissions.yaml"
    monkeypatch.setattr(sm, "PERMISSIONS_PATH", perms_path)
    assert sm._is_app_allowed("Safari") is True
    assert sm._is_app_allowed("Anything") is True


def test_is_app_allowed_deny_list(tmp_path, monkeypatch):
    perms_path = tmp_path / "screen_permissions.json"
    perms_path.write_text('{"allow": [], "deny": ["blocked_app"]}', encoding="utf-8")
    monkeypatch.setattr(sm, "PERMISSIONS_PATH", perms_path)
    assert sm._is_app_allowed("blocked_app") is False
    assert sm._is_app_allowed("Safari") is True


def test_is_app_allowed_allow_list(tmp_path, monkeypatch):
    perms_path = tmp_path / "screen_permissions.json"
    perms_path.write_text('{"allow": ["Safari", "Chrome"], "deny": []}',
                          encoding="utf-8")
    monkeypatch.setattr(sm, "PERMISSIONS_PATH", perms_path)
    assert sm._is_app_allowed("Safari") is True
    assert sm._is_app_allowed("Firefox") is False


# ── Tool declaration ──────────────────────────────────────────────────────

def test_tool_declaration():
    assert sm.TOOL["name"] == "screen_memory_search"
    assert sm.TOOL["handler"] is sm.screen_memory_search
    assert sm.TOOL["parameters"]["required"] == []
    assert "query" in sm.TOOL["parameters"]["properties"]
    assert "limit" in sm.TOOL["parameters"]["properties"]


# ── End-to-end via tool handler ───────────────────────────────────────────

def test_screen_memory_search_tool(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    store = sm.ScreenMemory(db_path=db, max_age_days=7, max_size_mb=500)
    monkeypatch.setattr(sm, "get_screen_memory", lambda: store)

    event = {
        "ts": time.monotonic(),
        "iso_ts": __import__("datetime").datetime.now().isoformat(),
        "app": "Notes",
        "title": "Grocery list",
        "ocr_text": "milk eggs bread",
        "a11y_tree": "",
        "image_path": "",
        "duration_ms": 50,
    }
    store._store(event)

    result = sm.screen_memory_search({"query": "milk"})
    assert "milk" in result.lower() or "Milk" in result
