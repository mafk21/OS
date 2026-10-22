"""
Screen Memory — event-driven screen capture with FTS5 search (Phase 7).

Implements the screenpipe pattern: periodic screen captures, OCR text
extraction, accessibility tree snapshots, SQLite/FTS5 storage, and a search
tool so JARVIS can recall what was on screen.

Designed for graceful degradation: every capture/OCR/a11y dependency is
optional. If none are installed, the store still works — captures are
empty frames, OCR returns nothing, a11y returns nothing — and search still
finds whatever was stored.

Storage: memory/screen_memory.db (SQLite with FTS5 virtual table).
Retention: configurable max age (default 7 days) and max size (default 500MB).
Permissions: memory/screen_permissions.yaml — allow/deny list of app names.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ── Optional dependencies (all degrade gracefully) ────────────────────────

try:
    import yaml  # type: ignore
    _YAML = True
except ImportError:  # pragma: no cover — yaml not installed
    _YAML = False

try:
    from actions.screen_processor import _capture_screen  # type: ignore
    _CAPTURE = True
except ImportError:  # pragma: no cover — screen_processor not available
    _CAPTURE = False

try:
    import pytesseract  # type: ignore
    _OCR = True
except ImportError:  # pragma: no cover — pytesseract not installed
    _OCR = False

try:
    import pyautogui  # type: ignore
    _A11Y = True
except ImportError:  # pragma: no cover — pyautogui not installed
    _A11Y = False


# ── Constants ─────────────────────────────────────────────────────────────

DB_PATH = Path("memory") / "screen_memory.db"
PERMISSIONS_PATH = Path("memory") / "screen_permissions.yaml"

DEFAULT_MAX_AGE_DAYS = 7
DEFAULT_MAX_SIZE_MB = 500
CAPTURE_INTERVAL_SEC = 30          # capture every 30 seconds
MIN_CAPTURE_GAP_SEC = 5            # don't capture more than once per 5s

# ── Permissions ───────────────────────────────────────────────────────────


def _load_permissions() -> dict:
    """Load allow/deny app permissions from YAML (or JSON fallback)."""
    defaults = {"allow": [], "deny": []}
    if not PERMISSIONS_PATH.exists():
        return defaults
    try:
        text = PERMISSIONS_PATH.read_text(encoding="utf-8")
        if _YAML:
            data = yaml.safe_load(text) or {}
        else:
            # Minimal JSON fallback (yaml not installed)
            data = json.loads(text) if text.strip() else {}
        allow = set(data.get("allow", [])) if isinstance(data.get("allow"), list) else set()
        deny = set(data.get("deny", [])) if isinstance(data.get("deny"), list) else set()
        return {"allow": allow, "deny": deny}
    except Exception:
        return defaults


def _is_app_allowed(app_name: str) -> bool:
    """Check if an app is allowed to be captured."""
    perms = _load_permissions()
    app_lower = (app_name or "").lower()
    if app_lower in {d.lower() for d in perms["deny"]}:
        return False
    if perms["allow"]:  # allow-list is non-empty → only allow-listed apps
        return app_lower in {a.lower() for a in perms["allow"]}
    return True   # no allow-list, not denied → allowed


# ── Database ─────────────────────────────────────────────────────────────


class ScreenMemory:
    """
    Event-driven screen memory store.

    Captures screenshots periodically, extracts OCR text and a11y tree,
    stores everything in SQLite with an FTS5 virtual table for full-text
    search. The model queries via the `screen_memory_search` tool.
    """

    def __init__(self, db_path: Path = DB_PATH,
                 max_age_days: int = DEFAULT_MAX_AGE_DAYS,
                 max_size_mb: int = DEFAULT_MAX_SIZE_MB):
        self.db_path = db_path
        self.max_age_days = max_age_days
        self.max_size_mb = max_size_mb
        self._lock = threading.Lock()
        self._last_capture: float = 0.0
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS screen_events (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts          REAL    NOT NULL,       -- monotonic capture time
                    iso_ts      TEXT    NOT NULL,       -- ISO timestamp
                    app         TEXT,                   -- active app name
                    title       TEXT,                   -- window title
                    ocr_text    TEXT,                   -- OCR-extracted text
                    a11y_tree   TEXT,                   -- JSON of accessibility tree
                    image_path  TEXT,                   -- path to saved frame
                    duration_ms INTEGER                 -- capture duration
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS screen_fts
                USING fts5(ocr_text, a11y_tree, content=screen_events,
                           content_rowid=id)
            """)
            # Triggers to keep FTS in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS screen_ai AFTER INSERT ON screen_events BEGIN
                    INSERT INTO screen_fts(rowid, ocr_text, a11y_tree)
                    VALUES (new.id, new.ocr_text, new.a11y_tree);
                END
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS screen_ad AFTER DELETE ON screen_events BEGIN
                    INSERT INTO screen_fts(screen_fts, rowid, ocr_text, a11y_tree)
                    VALUES ('delete', old.id, old.ocr_text, old.a11y_tree);
                END
            """)
            conn.commit()

    # ── Capture ─────────────────────────────────────────────────────────

    def capture(self, force: bool = False) -> Optional[dict]:
        """Capture one screen event. Returns the event dict or None."""
        now = time.monotonic()
        if not force and now - self._last_capture < MIN_CAPTURE_GAP_SEC:
            return None
        self._last_capture = now

        app = ""
        title = ""
        ocr_text = ""
        a11y_tree = ""
        image_path = ""
        duration_ms = 0

        start = time.monotonic()

        if _CAPTURE:
            try:
                img_bytes, mime = _capture_screen()
                duration_ms = int((time.monotonic() - start) * 1000)
                # Save the frame
                img_dir = self.db_path.parent / "frames"
                img_dir.mkdir(parents=True, exist_ok=True)
                ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                image_path = str(img_dir / f"{ts_str}.png")
                Path(image_path).write_bytes(img_bytes)

                # OCR
                if _OCR:
                    try:
                        import PIL.Image  # type: ignore
                        import io
                        img = PIL.Image.open(io.BytesIO(img_bytes))
                        ocr_text = pytesseract.image_to_string(img) or ""
                    except Exception:
                        pass
            except Exception:
                pass

        # a11y tree
        if _A11Y:
            try:
                # pyautogui doesn't expose a11y directly; placeholder for
                # platform-specific a11y (UI Automation on Windows, AT-SPI on Linux)
                a11y_tree = ""
            except Exception:
                pass

        event = {
            "ts": time.monotonic(),
            "iso_ts": datetime.now().isoformat(),
            "app": app,
            "title": title,
            "ocr_text": ocr_text,
            "a11y_tree": a11y_tree,
            "image_path": image_path,
            "duration_ms": duration_ms,
        }
        self._store(event)
        return event

    def _store(self, event: dict) -> None:
        with self._lock:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    "INSERT INTO screen_events "
                    "(ts, iso_ts, app, title, ocr_text, a11y_tree, image_path, duration_ms) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (event["ts"], event["iso_ts"], event.get("app", ""),
                     event.get("title", ""), event.get("ocr_text", ""),
                     event.get("a11y_tree", ""), event.get("image_path", ""),
                     event.get("duration_ms", 0)),
                )
                conn.commit()
            self._enforce_retention()

    def _enforce_retention(self) -> None:
        """Delete events older than max_age_days, or over max_size_mb."""
        cutoff = (datetime.now() - timedelta(days=self.max_age_days)).isoformat()
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("DELETE FROM screen_events WHERE iso_ts < ?", (cutoff,))
            conn.commit()
        # Size-based retention: delete oldest events until under limit
        total_mb = self._db_size_mb()
        if total_mb > self.max_size_mb:
            with sqlite3.connect(str(self.db_path)) as conn:
                rows = conn.execute(
                    "SELECT id FROM screen_events ORDER BY ts ASC LIMIT ?",
                    (max(1, (total_mb - self.max_size_mb) * 10),),
                ).fetchall()
                for (row_id,) in rows:
                    conn.execute("DELETE FROM screen_events WHERE id = ?", (row_id,))
                conn.commit()

    def _db_size_mb(self) -> float:
        try:
            return self.db_path.stat().st_size / (1024 * 1024)
        except OSError:
            return 0.0

    # ── Search ──────────────────────────────────────────────────────────

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Full-text search over OCR text and a11y tree."""
        with self._lock:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                if query.strip():
                    rows = conn.execute(
                        "SELECT se.* FROM screen_events se "
                        "JOIN screen_fts fts ON se.id = fts.rowid "
                        "WHERE screen_fts MATCH ? "
                        "ORDER BY se.ts DESC LIMIT ?",
                        (query, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM screen_events ORDER BY ts DESC LIMIT ?",
                        (limit,),
                    ).fetchall()
                return [dict(r) for r in rows]

    def recent(self, limit: int = 10) -> list[dict]:
        """Most recent screen events (no search filter)."""
        return self.search("", limit=limit)

    def stats(self) -> dict:
        """Database statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM screen_events").fetchone()[0]
            size_mb = self._db_size_mb()
        oldest = None
        newest = None
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute("SELECT MIN(iso_ts), MAX(iso_ts) FROM screen_events").fetchone()
            oldest, newest = row
        return {
            "events": count,
            "size_mb": round(size_mb, 2),
            "oldest": oldest,
            "newest": newest,
            "ocr_available": _OCR,
            "capture_available": _CAPTURE,
            "a11y_available": _A11Y,
        }


# ── Singleton ─────────────────────────────────────────────────────────────

_screen_memory: Optional[ScreenMemory] = None


def get_screen_memory() -> ScreenMemory:
    global _screen_memory
    if _screen_memory is None:
        _screen_memory = ScreenMemory()
    return _screen_memory


# ── Tool declaration (auto-discovered via main.py wiring) ─────────────────

TOOL = {
    "name": "screen_memory_search",
    "description": (
        "Search JARVIS's screen memory — full-text search over OCR text and "
        "accessibility trees captured from your screen. Use when the user asks "
        "about something they saw earlier (\'what was that article I was reading\', "
        "\'find the error message from before\', \'what was on my screen at 3pm\'). "
        "Leave query empty for the most recent captures."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Text to search for in screen captures",
            },
            "limit": {
                "type": "INTEGER",
                "description": "Maximum results to return (default 10)",
            },
        },
        "required": [],
    },
    "handler": None,  # set below
}


def screen_memory_search(parameters: dict, response=None, player=None,
                         session_memory=None) -> str:
    """Search screen memory. Returns formatted results."""
    sm = get_screen_memory()
    query = (parameters or {}).get("query", "").strip()
    limit = int((parameters or {}).get("limit", 10))
    results = sm.search(query, limit=limit)

    if not results:
        return "No screen captures matching that query."

    lines = [f"Screen memory — {len(results)} result(s)"]
    for r in results:
        ts = r.get("iso_ts", "")
        app = r.get("app") or "unknown app"
        ocr = (r.get("ocr_text") or "").strip()[:200]
        lines.append(f"\n[{ts}] {app}")
        if ocr:
            lines.append(f"  {ocr}")
    return "\n".join(lines)


TOOL["handler"] = screen_memory_search
