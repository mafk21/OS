"""Tests — memory hygiene (Phase 3): TTL forgetting, dedup, conflict history.

Runs against a tmp long_term.json by monkeypatching memory_manager.MEMORY_PATH,
so the real memory file is never touched.
"""
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor

import memory.memory_manager as mm


def _empty_store():
    return {c: {} for c in ("identity", "preferences", "projects",
                            "relationships", "wishes", "notes")}


def _write(path, **cats):
    store = _empty_store()
    store.update(cats)
    path.write_text(__import__("json").dumps(store, ensure_ascii=False),
                    encoding="utf-8")


# ── TTL / forgetting ────────────────────────────────────────────────────────

def test_load_never_silently_expires_personal_memories(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    old = date.today() - timedelta(days=1000)
    _write(tmp_path / "long_term.json",
           wishes={"dream_car": {"value": "Tesla", "updated": old.isoformat()}},
           projects={"website": {"value": "portfolio", "updated": old.isoformat()}},
           identity={"name": {"value": "Ayse", "updated": old.isoformat()}})
    data = mm.load_memory()
    assert data["wishes"]["dream_car"]["value"] == "Tesla"
    assert data["projects"]["website"]["value"] == "portfolio"
    assert data["identity"]["name"]["value"] == "Ayse"


def test_ttl_keeps_recent_within_limit(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    recent = date.today() - timedelta(days=10)
    _write(tmp_path / "long_term.json",
           wishes={"dream_car": {"value": "Tesla", "updated": recent.isoformat()}})
    assert mm.load_memory()["wishes"]["dream_car"]["value"] == "Tesla"


def test_ttl_unparseable_date_kept(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    _write(tmp_path / "long_term.json",
           notes={"weird": {"value": "x", "updated": "not-a-date"}})
    assert "weird" in mm.load_memory()["notes"]


# ── dedup (called on a plain dict, bypassing load_memory's auto-hygiene) ───

def test_dedup_does_not_destroy_same_value_with_different_meaning(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    old = date.today() - timedelta(days=50)
    recent = date.today() - timedelta(days=5)
    store = _empty_store()
    store["relationships"]["brother"] = {"value": "Ali", "updated": old.isoformat()}
    store["notes"]["coworker"] = {"value": "Ali", "updated": recent.isoformat()}
    assert mm.dedup_memory(store) == []
    assert store["relationships"]["brother"]["value"] == "Ali"
    assert store["notes"]["coworker"]["value"] == "Ali"


def test_dedup_different_values_not_merged(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    store = _empty_store()
    store["preferences"]["color"] = {"value": "blue"}
    store["notes"]["fav_color"]   = {"value": "red"}
    assert mm.dedup_memory(store) == []
    assert store["preferences"]["color"]["value"] == "blue"
    assert store["notes"]["fav_color"]["value"] == "red"


# ── conflict resolution ─────────────────────────────────────────────────────

def test_conflict_keeps_previous_in_history(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    today = date.today().isoformat()
    mm.update_memory({"identity": {"city": {"value": "London"}}})
    mm.update_memory({"identity": {"city": {"value": "Paris"}}})
    data = mm.load_memory()
    entry = data["identity"]["city"]
    assert entry["value"] == "Paris"
    assert entry["_prev"] == [{"value": "London", "updated": today}]


def test_entry_value_still_current_after_conflict(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    mm.update_memory({"identity": {"city": {"value": "London"}}})
    mm.update_memory({"identity": {"city": {"value": "Paris"}}})
    assert mm._entry_value(mm.load_memory()["identity"]["city"]) == "Paris"


# ── user profile ────────────────────────────────────────────────────────────

def test_user_profile_shape(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    mm.update_memory({"identity": {"name": {"value": "Ayse"}}})
    mm.update_memory({"identity": {"city": {"value": "Istanbul"}}})
    mm.update_memory({"preferences": {"favorite_food": {"value": "lahmacun"}}})
    prof = mm.user_profile()
    assert "identity" in prof and prof["identity"]["name"] == "Ayse"
    assert prof["identity"]["city"] == "Istanbul"
    assert "about" in prof
    assert any("lahmacun" in str(v) for v in prof["about"].values())


def test_session_summary_is_briefed_without_being_deleted(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    mm.save_session_summary("We fixed the phone call and planned a memory upgrade.", "English")
    first = mm.pop_last_session()
    assert first and "phone call" in first["summary"]
    assert mm.pop_last_session() is None
    stored = mm.load_memory()["sessions"]
    assert len(stored) == 1 and stored[0]["briefed"] is True
    assert "phone call" in mm.search_memory("phone call")


def test_manual_memory_preserves_language_and_provenance(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    mm.remember("sister name", "نورة", "relationships", manual=True)
    entry = mm.load_memory()["relationships"]["sister_name"]
    assert entry["value"] == "نورة"
    assert entry["source"] == "explicit_user"
    assert entry["confidence"] == 1.0
    assert entry["explicit"] is True


def test_forget_normalizes_key_and_finds_correct_category(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    mm.remember("Favorite Food", "kabsa", "preferences", manual=True)
    assert "preferences/favorite_food" in mm.forget("Favorite Food")
    assert "favorite_food" not in mm.load_memory()["preferences"]


def test_concurrent_updates_do_not_lose_memories(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda i: mm.remember(f"fact_{i}", f"value {i}", manual=True), range(20)))
    notes = mm.load_memory()["notes"]
    assert len(notes) == 20
    assert all(notes[f"fact_{i}"]["value"] == f"value {i}" for i in range(20))
