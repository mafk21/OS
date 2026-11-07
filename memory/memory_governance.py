"""User-controlled memory provenance, conflict, and retention operations."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from memory import memory_manager as mm


def inspect() -> list[dict[str, Any]]:
    rows = []
    for category, items in mm.load_memory().items():
        if not isinstance(items, dict): continue
        for key, entry in items.items():
            if not isinstance(entry, dict): continue
            rows.append({"category": category, "key": key, "value": entry.get("value"),
                         "source": entry.get("source", "legacy"), "confidence": entry.get("confidence"),
                         "status": entry.get("status", "active"), "pinned": bool(entry.get("pinned")),
                         "expires_at": entry.get("expires_at"), "provenance": list(entry.get("provenance") or [])})
    return rows


def edit(category: str, key: str, value: str) -> str:
    memory = mm.load_memory(); entry = (memory.get(category) or {}).get(key)
    if not isinstance(entry, dict): return "Memory not found."
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry.update(value=str(value)[:mm.MAX_VALUE_LENGTH], source="explicit_user", confidence=1.0,
                 explicit=True, status="active", updated_at=now)
    entry.setdefault("provenance", []).append({"source": "explicit_user_edit", "observed_at": now})
    mm.save_memory(memory); return f"Edited memory: {category}/{key}"


def pin(category: str, key: str, pinned: bool = True) -> str:
    memory = mm.load_memory(); entry = (memory.get(category) or {}).get(key)
    if not isinstance(entry, dict): return "Memory not found."
    entry["pinned"] = bool(pinned); mm.save_memory(memory)
    return f"{'Pinned' if pinned else 'Unpinned'} memory: {category}/{key}"


def export() -> dict[str, Any]:
    return {"version": 1, "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "memories": inspect()}


def delete(category: str, key: str) -> str:
    return mm.forget(key, category)


def conflicts() -> list[dict[str, Any]]:
    rows = []
    for category, items in mm.load_memory().items():
        if not isinstance(items, dict): continue
        for key, entry in items.items():
            if isinstance(entry, dict) and entry.get("status") == "conflicted":
                rows.append({"category": category, "key": key, "current": entry.get("value"),
                             "alternatives": list(entry.get("_prev") or []),
                             "confidence": entry.get("confidence", 0.5)})
    return rows


def resolve(category: str, key: str, value: str) -> str:
    memory = mm.load_memory()
    entry = (memory.get(category) or {}).get(key)
    if not isinstance(entry, dict) or entry.get("status") != "conflicted":
        return "No matching memory conflict was found."
    entry.update(value=str(value)[:mm.MAX_VALUE_LENGTH], status="active", confidence=1.0,
                 explicit=True, source="explicit_user", updated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    entry.pop("_prev", None)
    entry.setdefault("provenance", []).append({"source": "explicit_user_resolution", "observed_at": entry["updated_at"]})
    mm.save_memory(memory)
    return f"Resolved memory conflict: {category}/{key}"


def set_expiry(category: str, key: str, expires_at: str | None) -> str:
    memory = mm.load_memory()
    entry = (memory.get(category) or {}).get(key)
    if not isinstance(entry, dict): return "Memory not found."
    if expires_at:
        datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        entry["expires_at"] = expires_at
    else:
        entry.pop("expires_at", None)
    mm.save_memory(memory)
    return f"Updated retention for {category}/{key}."


def enforce_explicit_retention(now: datetime | None = None) -> list[str]:
    current = now or datetime.now(timezone.utc)
    memory = mm.load_memory(); removed = []
    for category, items in memory.items():
        if not isinstance(items, dict): continue
        for key, entry in list(items.items()):
            expiry = entry.get("expires_at") if isinstance(entry, dict) else None
            if not expiry: continue
            try: deadline = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
            except ValueError: continue
            if deadline.tzinfo is None: deadline = deadline.replace(tzinfo=timezone.utc)
            if deadline <= current:
                del items[key]; removed.append(f"{category}/{key}")
    if removed: mm.save_memory(memory)
    return removed
