"""Tests — memory hygiene (Phase 3): TTL forgetting, dedup, conflict history.

Runs against a tmp long_term.json by monkeypatching memory_manager.MEMORY_PATH,
so the real memory file is never touched.
"""
from datetime import date, timedelta

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

def test_ttl_expires_wishes(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    old = date.today() - timedelta(days=100)
    _write(tmp_path / "long_term.json",
           wishes={"dream_car": {"value": "Tesla", "updated": old.isoformat()}},
           identity={"name": {"value": "Ayse", "updated": old.isoformat()}})
    data = mm.load_memory()
    assert "dream_car" not in data["wishes"]
    assert data["identity"]["name"]["value"] == "Ayse"   # identity never expires


def test_ttl_expires_projects_but_not_relationships(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    old = date.today() - timedelta(days=200)
    recent = date.today() - timedelta(days=100)
    _write(tmp_path / "long_term.json",
           projects={"website": {"value": "portfolio", "updated": old.isoformat()}},
           relationships={"sister": {"value": "Ayse", "updated": recent.isoformat()}})
    data = mm.load_memory()
    assert "website" not in data["projects"]
    assert data["relationships"]["sister"]["value"] == "Ayse"


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

def test_dedup_cross_category_keeps_newer(tmp_path):
    mm.MEMORY_PATH = tmp_path / "long_term.json"
    old = date.today() - timedelta(days=50)
    recent = date.today() - timedelta(days=5)
    store = _empty_store()
    store["preferences"]["color"] = {"value": "blue", "updated": old.isoformat()}
    store["notes"]["fav_color"]   = {"value": "blue", "updated": recent.isoformat()}
    removed = mm.dedup_memory(store)
    assert removed == [("preferences", "color", "notes", "fav_color")]
    assert store["notes"]["fav_color"]["value"] == "blue"
    assert "color" not in store["preferences"]


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
