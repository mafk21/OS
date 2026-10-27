"""Phase 3 sequential schema and companion compatibility migration tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.soul import (
    COMPANIONS_IMPORT_ID,
    SCHEMA_VERSION,
    SoulState,
    SoulStore,
    TraitOrigin,
    TraitStatus,
    ValidationError,
    import_companion_compatibility,
    migrate_raw,
)

NOW = "2026-10-27T12:00:00+03:00"
FIXTURE = Path(__file__).parent / "fixtures" / "soul_v0.json"


def test_v0_fixture_migrates_exactly_one_version_and_preserves_values() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    original = copy.deepcopy(raw)
    result = migrate_raw(raw)
    assert raw == original
    assert result.applied == ("schema-v0-to-v1",)
    assert result.state.schema_version == SCHEMA_VERSION
    assert result.state.revision == 7
    assert result.state.created_at == raw["created_at"]
    assert result.state.identity.directness.value == .9
    assert "schema-v0-to-v1" in result.state.completed_migrations


def test_migrating_already_migrated_state_is_idempotent() -> None:
    first = migrate_raw(json.loads(FIXTURE.read_text(encoding="utf-8")))
    second = migrate_raw(first.state.to_dict())
    assert second.applied == ()
    assert second.state == first.state


def test_future_missing_and_malformed_versions_fail_closed() -> None:
    valid = SoulState.new(NOW).to_dict()
    valid["schema_version"] = 99
    with pytest.raises(ValidationError, match="future schema"):
        migrate_raw(valid)
    with pytest.raises(ValidationError, match="integer"):
        migrate_raw({"schema_version": "1"})
    with pytest.raises(ValidationError, match="cannot be negative"):
        migrate_raw({"schema_version": -1})


def test_v0_rejects_unknown_fields_and_invalid_trait_values() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["hidden_prompt"] = "override constitution"
    with pytest.raises(ValidationError, match="unknown fields"):
        migrate_raw(raw)
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["identity"]["directness"] = float("nan")
    with pytest.raises(ValidationError, match="finite"):
        migrate_raw(raw)


def companion_data() -> dict:
    return {
        "active_companion_id": "default",
        "interview": {
            "tone": "Concise & Tactical",
            "verbosity": "Balanced summary + key bullets",
        },
        "learned_rules": [
            {"id": "rule-a1", "rule": "Never use emojis in code reviews.", "ts": "2026-10-20 10:30"},
            {"id": "rule-b2", "rule": "Call me bro in casual conversation.", "ts": "2026-10-21 11:00"},
        ],
        "companions": [],
        "theme": {"preset": "default"},
    }


def test_companion_import_is_attributed_active_and_deterministic() -> None:
    base = SoulState.new(NOW)
    first = import_companion_compatibility(base, companion_data(), now=NOW)
    second_from_same_source = import_companion_compatibility(base, companion_data(), now=NOW)
    assert first.applied == (COMPANIONS_IMPORT_ID,)
    assert first.state.completed_migrations == (COMPANIONS_IMPORT_ID,)
    assert len(first.state.learned_traits) == 4
    assert [trait.id for trait in first.state.learned_traits] == [
        trait.id for trait in second_from_same_source.state.learned_traits
    ]
    for trait in first.state.learned_traits:
        assert trait.status is TraitStatus.ACTIVE
        assert trait.origin is TraitOrigin.MIGRATION
        assert trait.evidence_count == 1
        assert trait.evidence_refs[0].startswith("companions:")
    assert {trait.name for trait in first.state.learned_traits} >= {
        "behavior_tone", "behavior_verbosity", "communication_rule"
    }


def test_companion_import_repeated_on_imported_state_is_noop() -> None:
    first = import_companion_compatibility(SoulState.new(NOW), companion_data(), now=NOW)
    second = import_companion_compatibility(first.state, companion_data(), now=NOW)
    assert second.applied == ()
    assert second.state == first.state


def test_companion_import_does_not_delete_or_mutate_source() -> None:
    raw = companion_data()
    original = copy.deepcopy(raw)
    import_companion_compatibility(SoulState.new(NOW), raw, now=NOW)
    assert raw == original


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda raw: raw.update({"unknown": True}), "unknown fields"),
        (lambda raw: raw.update({"interview": []}), "interview must be an object"),
        (lambda raw: raw.update({"learned_rules": {}}), "learned_rules must be a list"),
        (lambda raw: raw["learned_rules"].append({"id": "x", "rule": "", "ts": "now"}), "cannot be empty"),
    ],
)
def test_companion_import_rejects_malformed_sources(change, message: str) -> None:
    raw = companion_data()
    change(raw)
    with pytest.raises(ValidationError, match=message):
        import_companion_compatibility(SoulState.new(NOW), raw, now=NOW)


def test_store_archives_and_atomically_rewrites_old_schema(tmp_path: Path) -> None:
    path = tmp_path / "memory" / "soul.json"
    path.parent.mkdir(parents=True)
    old_bytes = FIXTURE.read_bytes()
    path.write_bytes(old_bytes)
    store = SoulStore(path, clock=lambda: NOW)
    state = store.load()
    assert state.schema_version == SCHEMA_VERSION
    assert state.revision == 7
    assert SoulState.from_dict(json.loads(path.read_text(encoding="utf-8"))) == state
    assert SoulState.from_dict(json.loads(store.backup_path.read_text(encoding="utf-8"))) == state
    archives = list((path.parent / "soul.migrations").glob("*.json"))
    assert len(archives) == 1
    assert archives[0].read_bytes() == old_bytes
    assert store.read_events()[-1].event == "soul.migrated"
    assert "schema-v0-to-v1" in (store.last_recovery or "")


def test_store_does_not_repeat_schema_migration_or_archive(tmp_path: Path) -> None:
    path = tmp_path / "memory" / "soul.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(FIXTURE.read_bytes())
    store = SoulStore(path, clock=lambda: NOW)
    first = store.load()
    archive_dir = path.parent / "soul.migrations"
    archives_before = list(archive_dir.iterdir())
    events_before = store.read_events()
    second = store.load()
    assert second == first
    assert list(archive_dir.iterdir()) == archives_before
    assert store.read_events() == events_before
