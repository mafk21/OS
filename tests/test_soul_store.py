"""Phase 2 durability, recovery, concurrency, and audit tests."""
from __future__ import annotations

import json
import threading
from dataclasses import replace
from pathlib import Path

import pytest

from core.soul import SCHEMA_VERSION, RevisionConflict, SoulState, SoulStore, SoulStoreError, ValidationError

NOW = "2026-10-27T12:00:00+03:00"
LATER = "2026-10-27T12:01:00+03:00"


class Clock:
    def __init__(self, *values: str):
        self.values = list(values) or [NOW]
        self.index = 0

    def __call__(self) -> str:
        value = self.values[min(self.index, len(self.values) - 1)]
        self.index += 1
        return value


def make_store(tmp_path: Path, **kwargs) -> SoulStore:
    return SoulStore(tmp_path / "memory" / "soul.json", clock=kwargs.pop("clock", Clock(NOW, LATER)), **kwargs)


def stronger(state: SoulState) -> SoulState:
    identity = replace(state.identity, directness=replace(state.identity.directness, value=.9))
    return replace(state, identity=identity)


def test_initialize_persists_valid_state_backup_and_audit(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    state = store.initialize()
    assert state.revision == 0
    assert store.path.exists()
    assert store.backup_path.exists()
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))) == state
    events = store.read_events()
    assert [event.event for event in events] == ["soul.initialized"]
    assert events[0].revision == 0


def test_transaction_is_atomic_revisioned_and_audited(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    initial = store.initialize()
    seen = []
    store.add_listener(seen.append)
    changed = store.transact(stronger, expected_revision=0, reason="raise directness", source="test")
    assert changed.revision == 1
    assert changed.identity.directness.value == .9
    assert changed.created_at == initial.created_at
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))) == changed
    # The backup deliberately remains the immediately preceding known-good revision.
    backup = SoulState.from_dict(json.loads(store.backup_path.read_text(encoding="utf-8")))
    assert backup.revision == 0
    assert seen == [changed]
    assert store.read_events()[-1].revision == 1


def test_stale_revision_is_rejected_without_writing(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.initialize()
    store.transact(stronger, expected_revision=0, reason="first", source="test")
    before = store.path.read_bytes()
    with pytest.raises(RevisionConflict):
        store.transact(lambda state: state, expected_revision=0, reason="stale", source="test")
    assert store.path.read_bytes() == before
    assert len(store.read_events()) == 2


def test_mutation_cannot_change_schema_constitution_or_creation_time(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    state = store.initialize()
    with pytest.raises(ValidationError, match="created_at"):
        store.transact(
            lambda current: replace(current, created_at=LATER),
            expected_revision=state.revision, reason="bad", source="test",
        )
    def corrupt_constitution(current: SoulState) -> SoulState:
        object.__setattr__(current, "constitution_version", 999)
        return current

    with pytest.raises(ValidationError, match="constitution version"):
        store.transact(
            corrupt_constitution, expected_revision=state.revision, reason="bad", source="test",
        )


def test_corrupt_current_is_quarantined_and_backup_is_restored(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.initialize()
    store.transact(stronger, expected_revision=0, reason="change", source="test")
    store.path.write_text('{"revision":', encoding="utf-8")
    recovered = store.load()
    assert recovered.revision == 0
    assert "backup" in (store.last_recovery or "").lower()
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))).revision == 0
    assert list(store.quarantine_dir.glob("soul.json.*.invalid"))
    assert store.read_events()[-1].event == "soul.recovered"


def test_corrupt_state_without_backup_uses_safe_unsaved_defaults(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_bytes(b"\xffnot-json")
    recovered = store.load()
    assert recovered.identity.archetype == "Brother-Guardian"
    assert recovered.revision == 0
    assert not store.path.exists()
    assert list(store.quarantine_dir.glob("*.invalid"))
    assert "safe defaults" in (store.last_recovery or "").lower()


def test_future_version_is_never_consumed(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    raw = SoulState.new(NOW).to_dict()
    raw["schema_version"] = 999
    store.path.parent.mkdir(parents=True)
    store.path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = store.load()
    assert loaded.schema_version == SCHEMA_VERSION
    assert not store.path.exists()
    assert list(store.quarantine_dir.glob("*.invalid"))


@pytest.mark.parametrize(
    "stage",
    ["validated", "backup_before_temp", "backup_temp_fsynced", "backup_replaced", "state_before_temp", "state_temp_fsynced"],
)
def test_fault_before_state_replace_keeps_old_current_and_cleans_temp(tmp_path: Path, stage: str) -> None:
    armed = False

    def fail(point: str) -> None:
        if armed and point == stage:
            raise OSError(f"fault at {stage}")

    store = make_store(tmp_path, fault_hook=fail)
    initial = store.initialize()
    armed = True
    with pytest.raises(SoulStoreError) as caught:
        store.transact(stronger, expected_revision=0, reason="fault", source="test")
    assert caught.value.committed is False
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))) == initial
    assert not list(store.path.parent.glob("*.tmp"))
    assert not list(store.path.parent.glob(".*.tmp"))


def test_fault_after_state_replace_reports_commit_and_load_repairs_audit(tmp_path: Path) -> None:
    armed = False

    def fail(point: str) -> None:
        if armed and point == "state_replaced":
            raise OSError("simulated process death after replace")

    store = make_store(tmp_path, fault_hook=fail)
    store.initialize()
    armed = True
    with pytest.raises(SoulStoreError) as caught:
        store.transact(stronger, expected_revision=0, reason="fault", source="test")
    assert caught.value.committed is True
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))).revision == 1

    clean_store = SoulStore(store.path, clock=Clock(LATER))
    loaded = clean_store.load()
    assert loaded.revision == 1
    assert clean_store.read_events()[-1].event == "soul.audit_recovered"


def test_audit_write_failure_after_commit_is_repaired_on_next_load(tmp_path: Path, monkeypatch) -> None:
    store = make_store(tmp_path)
    store.initialize()
    original = store._append_event
    monkeypatch.setattr(store, "_append_event", lambda _event: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(SoulStoreError) as caught:
        store.transact(stronger, expected_revision=0, reason="audit fault", source="test")
    assert caught.value.committed is True
    assert SoulState.from_dict(json.loads(store.path.read_text(encoding="utf-8"))).revision == 1
    monkeypatch.setattr(store, "_append_event", original)
    assert store.load().revision == 1
    assert store.read_events()[-1].event == "soul.audit_recovered"


def test_invalid_audit_lines_are_skipped_without_losing_valid_events(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.initialize()
    with store.audit_path.open("a", encoding="utf-8") as handle:
        handle.write("not-json\n")
        handle.write('{"event":"incomplete"}\n')
    events = store.read_events()
    assert len(events) == 1
    assert events[0].event == "soul.initialized"


def test_concurrent_same_revision_allows_exactly_one_commit(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.initialize()
    barrier = threading.Barrier(2)
    results: list[str] = []

    def worker() -> None:
        barrier.wait()
        try:
            store.transact(stronger, expected_revision=0, reason="race", source="thread")
            results.append("committed")
        except RevisionConflict:
            results.append("conflict")

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert sorted(results) == ["committed", "conflict"]
    assert store.load().revision == 1


def test_listener_failure_cannot_roll_back_or_break_commit(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.initialize()
    store.add_listener(lambda _state: (_ for _ in ()).throw(RuntimeError("UI gone")))
    changed = store.transact(stronger, expected_revision=0, reason="listener", source="test")
    assert changed.revision == 1
    assert store.load().revision == 1


def test_labels_and_mutation_results_are_validated_before_disk_changes(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    initial = store.initialize()
    with pytest.raises(ValidationError):
        store.transact(lambda state: state, expected_revision=0, reason="", source="test")
    with pytest.raises(ValidationError, match="return SoulState"):
        store.transact(lambda _state: {}, expected_revision=0, reason="bad return", source="test")  # type: ignore[arg-type]
    assert store.load() == initial
