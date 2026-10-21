"""
Productivity Core — Phase 3
SQLite store at memory/productivity.db

Tables:
  tasks      (id, title, due, priority, status, created, updated, archived)
  notes      (id, title, content, created, updated, archived, tags)
  routines   (name PK, trigger, steps_json, created)
  checkpoints(id, name, paths_json, created)

Lecture notes uses notes table with tag=lecture + transient file at memory/lecture_capture/*.txt
"""

from __future__ import annotations
import json, time, sqlite3
from pathlib import Path
import sys

def _base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

DB_PATH = _base() / "memory" / "productivity.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    due TEXT DEFAULT '',
    priority TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'open',
    created TEXT NOT NULL,
    updated TEXT NOT NULL,
    archived INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '',
    created TEXT NOT NULL,
    updated TEXT NOT NULL,
    archived INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS routines (
    name TEXT PRIMARY KEY,
    trigger TEXT NOT NULL,
    steps_json TEXT NOT NULL,
    description TEXT DEFAULT '',
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    paths_json TEXT NOT NULL,
    note TEXT DEFAULT '',
    created TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_archived ON tasks(archived);
CREATE INDEX IF NOT EXISTS idx_notes_archived ON notes(archived);
"""

def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    return con

def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")

# ── Tasks ────────────────────────────────────────────────────────────────

def add_task(title: str, due: str = "", priority: str = "normal", description: str = "") -> dict:
    title = (title or "").strip()
    if not title:
        raise ValueError("task title required")
    priority = priority.lower() if priority.lower() in ("low","normal","high","urgent") else "normal"
    now = _now_iso()
    con = _connect()
    cur = con.execute("INSERT INTO tasks(title,description,due,priority,status,created,updated) VALUES(?,?,?,?,?,?,?)",
                      (title, description, due, priority, "open", now, now))
    con.commit()
    tid = cur.lastrowid
    con.close()
    return {"id": tid, "title": title, "due": due, "priority": priority, "status": "open"}

def list_tasks(status: str = "open", include_archived: bool = False, page: int = 1, page_size: int = 20) -> dict:
    page = max(1, int(page)); page_size = max(1, min(50, int(page_size)))
    con = _connect()
    where = []
    params: list = []
    if status and status.lower() != "all":
        where.append("status=?"); params.append(status.lower())
    if not include_archived:
        where.append("archived=0")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    total = con.execute(f"SELECT COUNT(*) FROM tasks {where_sql}", params).fetchone()[0]
    rows = con.execute(f"SELECT * FROM tasks {where_sql} ORDER BY updated DESC LIMIT ? OFFSET ?", (*params, page_size, (page-1)*page_size)).fetchall()
    con.close()
    pages = max(1, (total + page_size - 1)//page_size)
    return {"total": total, "page": page, "pages": pages, "tasks": [dict(r) for r in rows]}

def search_tasks(query: str, page: int = 1) -> dict:
    q = f"%{(query or '').strip()}%"
    con = _connect()
    rows = con.execute("SELECT * FROM tasks WHERE (title LIKE ? OR description LIKE ?) AND archived=0 ORDER BY updated DESC LIMIT 20 OFFSET ?", (q,q,(max(1,page)-1)*20)).fetchall()
    con.close()
    return {"query": query, "tasks": [dict(r) for r in rows]}

def complete_task(task_id: int) -> str:
    con = _connect()
    con.execute("UPDATE tasks SET status='done', updated=? WHERE id=?", (_now_iso(), int(task_id)))
    con.commit(); con.close()
    return f"Task {task_id} marked done."

def reopen_task(task_id: int) -> str:
    con = _connect()
    con.execute("UPDATE tasks SET status='open', updated=? WHERE id=?", (_now_iso(), int(task_id)))
    con.commit(); con.close()
    return f"Task {task_id} reopened."

def archive_task(task_id: int, archived: bool = True) -> str:
    con = _connect()
    con.execute("UPDATE tasks SET archived=?, updated=? WHERE id=?", (1 if archived else 0, _now_iso(), int(task_id)))
    con.commit(); con.close()
    return f"Task {task_id} {'archived' if archived else 'restored'}."

def delete_task(task_id: int) -> str:
    con = _connect()
    con.execute("DELETE FROM tasks WHERE id=?", (int(task_id),))
    con.commit(); con.close()
    return f"Task {task_id} deleted."

# ── Notes ────────────────────────────────────────────────────────────────

def add_note(title: str, content: str, tags: str = "") -> dict:
    title = (title or "").strip() or "Untitled"
    content = (content or "").strip()
    if not content:
        raise ValueError("note content required")
    now = _now_iso()
    con = _connect()
    cur = con.execute("INSERT INTO notes(title,content,tags,created,updated) VALUES(?,?,?,?,?)", (title, content, tags, now, now))
    con.commit(); nid = cur.lastrowid; con.close()
    return {"id": nid, "title": title}

def list_notes(include_archived: bool = False, page: int = 1, page_size: int = 20) -> dict:
    page = max(1, int(page))
    con = _connect()
    where = "WHERE archived=0" if not include_archived else ""
    total = con.execute(f"SELECT COUNT(*) FROM notes {where}").fetchone()[0]
    rows = con.execute(f"SELECT * FROM notes {where} ORDER BY updated DESC LIMIT ? OFFSET ?", (page_size, (page-1)*page_size)).fetchall()
    con.close()
    pages = max(1, (total + page_size - 1)//page_size)
    return {"total": total, "page": page, "pages": pages, "notes": [dict(r) for r in rows]}

def search_notes(query: str, page: int = 1) -> dict:
    q = f"%{(query or '').strip()}%"
    con = _connect()
    rows = con.execute("SELECT * FROM notes WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?) AND archived=0 ORDER BY updated DESC LIMIT 20", (q,q,q)).fetchall()
    con.close()
    return {"query": query, "notes": [dict(r) for r in rows]}

def get_note(note_id: int) -> dict | None:
    con = _connect()
    row = con.execute("SELECT * FROM notes WHERE id=?", (int(note_id),)).fetchone()
    con.close()
    return dict(row) if row else None

def archive_note(note_id: int, archived: bool = True) -> str:
    con = _connect()
    con.execute("UPDATE notes SET archived=?, updated=? WHERE id=?", (1 if archived else 0, _now_iso(), int(note_id)))
    con.commit(); con.close()
    return f"Note {note_id} {'archived' if archived else 'restored'}."

def delete_note(note_id: int) -> str:
    con = _connect()
    con.execute("DELETE FROM notes WHERE id=?", (int(note_id),))
    con.commit(); con.close()
    return f"Note {note_id} deleted."

# ── Routines ─────────────────────────────────────────────────────────────

def add_routine(name: str, trigger: str, steps: list, description: str = "") -> dict:
    name = (name or "").strip()
    trigger = (trigger or "").strip().lower()
    if not name or not trigger or not steps:
        raise ValueError("routine name, trigger, and steps required")
    now = _now_iso()
    con = _connect()
    con.execute("INSERT OR REPLACE INTO routines(name,trigger,steps_json,description,created) VALUES(?,?,?,?,?)",
                (name, trigger, json.dumps(steps), description, now))
    con.commit(); con.close()
    # also persist to JSON for human edit
    _sync_routines_json()
    return {"name": name, "trigger": trigger, "steps": steps}

def list_routines() -> list[dict]:
    con = _connect()
    rows = con.execute("SELECT * FROM routines ORDER BY name").fetchall()
    con.close()
    return [{"name": r["name"], "trigger": r["trigger"], "steps": json.loads(r["steps_json"]), "description": r["description"]} for r in rows]

def get_routine_by_trigger(trigger: str) -> dict | None:
    con = _connect()
    row = con.execute("SELECT * FROM routines WHERE trigger=?", (trigger.strip().lower(),)).fetchone()
    con.close()
    if not row:
        return None
    return {"name": row["name"], "trigger": row["trigger"], "steps": json.loads(row["steps_json"]), "description": row["description"]}

def delete_routine(name: str) -> str:
    con = _connect()
    con.execute("DELETE FROM routines WHERE name=?", (name,))
    con.commit(); con.close()
    _sync_routines_json()
    return f"Routine '{name}' deleted."

def _sync_routines_json():
    try:
        p = _base() / "memory" / "routines.json"
        data = list_routines()
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

# ── Checkpoints ──────────────────────────────────────────────────────────

def create_checkpoint(name: str, paths: list[str], note: str = "") -> dict:
    name = (name or "").strip()
    if not name or not paths:
        raise ValueError("checkpoint name and paths required")
    now = _now_iso()
    con = _connect()
    cur = con.execute("INSERT INTO checkpoints(name,paths_json,note,created) VALUES(?,?,?,?)", (name, json.dumps(paths), note, now))
    con.commit(); cid = cur.lastrowid; con.close()
    return {"id": cid, "name": name, "paths": paths}

def list_checkpoints() -> list[dict]:
    con = _connect()
    rows = con.execute("SELECT * FROM checkpoints ORDER BY created DESC").fetchall()
    con.close()
    return [{"id": r["id"], "name": r["name"], "paths": json.loads(r["paths_json"]), "note": r["note"], "created": r["created"]} for r in rows]

def get_checkpoint(cid: int) -> dict | None:
    con = _connect()
    row = con.execute("SELECT * FROM checkpoints WHERE id=?", (int(cid),)).fetchone()
    con.close()
    if not row:
        return None
    return {"id": row["id"], "name": row["name"], "paths": json.loads(row["paths_json"]), "note": row["note"], "created": row["created"]}

def delete_checkpoint(cid: int) -> str:
    con = _connect()
    con.execute("DELETE FROM checkpoints WHERE id=?", (int(cid),))
    con.commit(); con.close()
    return f"Checkpoint {cid} deleted."

def restore_checkpoint(cid: int, dry_run: bool = True) -> dict:
    """Return the actions that would be taken; actual open delegated to caller (needs UI thread)."""
    cp = get_checkpoint(cid)
    if not cp:
        raise ValueError(f"Checkpoint {cid} not found")
    # Validate paths exist
    existing = []
    missing = []
    for pth in cp["paths"]:
        if Path(pth).exists():
            existing.append(pth)
        else:
            missing.append(pth)
    return {"checkpoint": cp, "existing": existing, "missing": missing, "dry_run": dry_run}

# ── Lecture capture ──────────────────────────────────────────────────────

def lecture_start(title: str = "") -> dict:
    """Begin a lecture capture session — creates a file to append transcripts to."""
    cap_dir = _base() / "memory" / "lecture_capture"
    cap_dir.mkdir(parents=True, exist_ok=True)
    sess_id = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{sess_id}_{(title or 'lecture').replace(' ','_')[:20]}.txt"
    fpath = cap_dir / fname
    fpath.write_text(f"# {title or 'Lecture'} — {sess_id}\n\n", encoding="utf-8")
    # marker for current session
    (cap_dir / "_current.txt").write_text(str(fpath), encoding="utf-8")
    return {"session_id": sess_id, "file": str(fpath), "title": title or "Lecture"}

def lecture_append(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    cap_dir = _base() / "memory" / "lecture_capture"
    marker = cap_dir / "_current.txt"
    if not marker.exists():
        lecture_start("Auto")
    fpath = Path(marker.read_text(encoding="utf-8").strip())
    if not fpath.exists():
        lecture_start("Auto")
        fpath = Path(marker.read_text(encoding="utf-8").strip())
    with fpath.open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    return True

def lecture_stop(summarize: bool = True) -> dict:
    cap_dir = _base() / "memory" / "lecture_capture"
    marker = cap_dir / "_current.txt"
    if not marker.exists():
        return {"error": "No active lecture session"}
    fpath = Path(marker.read_text(encoding="utf-8").strip())
    if not fpath.exists():
        marker.unlink(missing_ok=True)
        return {"error": "Lecture file missing"}
    transcript = fpath.read_text(encoding="utf-8")
    marker.unlink(missing_ok=True)
    result: dict = {"file": str(fpath), "transcript_chars": len(transcript)}
    if summarize and transcript.strip():
        # Try to summarize via provider (offline-capable), else stub
        try:
            from core.provider import text as prov_text
            summary = prov_text(
                f"Summarize these lecture notes concisely with key points and any homework/action items:\n\n{transcript[:8000]}",
                tier="smart", timeout_ms=20000, default=""
            )
            if summary:
                result["summary"] = summary
                # Save as a note for persistence
                try:
                    n = add_note(title=f"Lecture {time.strftime('%Y-%m-%d')}", content=f"{summary}\n\n---\n{transcript[:6000]}", tags="lecture")
                    result["note_id"] = n["id"]
                except Exception:
                    pass
                # Append summary to file
                fpath.write_text(transcript + f"\n\n## Summary\n{summary}\n", encoding="utf-8")
        except Exception as e:
            result["summary_error"] = str(e)
    return result

def lecture_status() -> dict:
    cap_dir = _base() / "memory" / "lecture_capture"
    marker = cap_dir / "_current.txt"
    if not marker.exists():
        return {"active": False}
    fpath = Path(marker.read_text(encoding="utf-8").strip())
    if not fpath.exists():
        return {"active": False, "error": "file missing"}
    try:
        chars = fpath.stat().st_size
    except Exception:
        chars = 0
    return {"active": True, "file": str(fpath), "chars": chars}
