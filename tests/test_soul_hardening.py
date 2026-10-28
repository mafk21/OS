"""Phase 14 release hardening, stress, portability, and performance tests."""
from __future__ import annotations

import json
import os
import statistics
import threading
import time
from dataclasses import replace
from pathlib import Path

from core.soul import RevisionConflict, SoulContextBuilder, SoulContextInputs, SoulState, SoulStore
from core.soul.affect import decay_affect
from core.soul.service import reconcile_legacy_prompt

NOW = "2026-10-28T09:00:00+03:00"


def test_mixed_writer_stress_is_revision_safe_and_restart_clean(tmp_path: Path):
    """Conversation, reflection, Studio, and heartbeat writers cannot lose updates."""
    store = SoulStore(tmp_path / "profile with spaces-حساب" / "soul.json", clock=lambda: NOW)
    store.initialize()
    writers = ("conversation", "reflection", "soul_studio", "heartbeat")
    barrier = threading.Barrier(len(writers))
    failures: list[BaseException] = []

    def worker(source: str) -> None:
        try:
            barrier.wait(timeout=5)
            for index in range(25):
                while True:
                    current = store.load()
                    value = .80 if (current.revision + index) % 2 else .81
                    identity = replace(
                        current.identity,
                        directness=replace(current.identity.directness, value=value),
                    )
                    try:
                        store.transact(
                            lambda state, identity=identity: replace(state, identity=identity),
                            expected_revision=current.revision,
                            reason=f"stress {source}", source=source,
                        )
                        break
                    except RevisionConflict:
                        continue
        except BaseException as exc:  # surfaced in the test thread
            failures.append(exc)

    threads = [threading.Thread(target=worker, args=(source,)) for source in writers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    assert not failures and all(not thread.is_alive() for thread in threads)
    assert store.load().revision == 100
    assert len(store.read_events(limit=200)) == 101
    restarted = SoulStore(store.path, clock=lambda: NOW)
    assert restarted.load().revision == 100
    assert not list(store.path.parent.glob("*.tmp"))


def test_long_duration_decay_is_bounded_and_clock_deterministic():
    state = SoulState.new(NOW).affect
    elevated = replace(state, concern=.95, energy=.95, rapport=.95)
    after_year = decay_affect(elevated, now="2027-10-28T09:00:00+03:00").after
    for name in ("concern", "energy", "rapport"):
        assert abs(getattr(after_year, name) - getattr(after_year, f"baseline_{name}")) < 1e-9
    assert after_year.daily_date == "2027-10-28"


def test_atomic_store_supports_unicode_spaces_and_uses_replace(tmp_path: Path, monkeypatch):
    calls: list[tuple[str, str]] = []
    real_replace = os.replace

    def observed(src, dst):
        calls.append((os.fspath(src), os.fspath(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", observed)
    store = SoulStore(tmp_path / "mac linux windows contract Ω" / "memory data" / "soul.json", clock=lambda: NOW)
    store.initialize()
    assert store.load().identity.archetype == "Brother-Guardian"
    assert calls and all(Path(dst).name in {"soul.json", "soul.backup.json", "soul.events.jsonl"} for _, dst in calls)
    assert all(Path(src).parent == Path(dst).parent for src, dst in calls)


def test_context_performance_and_size_targets():
    state = SoulState.new(NOW)
    builder = SoulContextBuilder()
    inputs = SoulContextInputs()
    uncached_samples = []
    for index in range(20):
        fresh = SoulContextBuilder()
        start = time.perf_counter()
        context = fresh.build(state, inputs)
        uncached_samples.append((time.perf_counter() - start) * 1000)
    cached_samples = []
    builder.build(state, inputs)
    for _ in range(100):
        start = time.perf_counter()
        builder.build(state, inputs)
        cached_samples.append((time.perf_counter() - start) * 1000)
    assert statistics.median(uncached_samples) < 30
    assert statistics.median(cached_samples) < 5
    assert len(context.text) <= builder.total_budget
    assert len(json.dumps(state.to_dict(), ensure_ascii=False).encode()) < 256_000


def test_populated_profile_feature_flag_rollback_keeps_data_and_legacy_voice(tmp_path: Path):
    store = SoulStore(tmp_path / "soul.json", clock=lambda: NOW)
    initial = store.initialize()
    changed = store.transact(
        lambda state: replace(state, identity=replace(
            state.identity, warmth=replace(state.identity.warmth, value=.89)
        )), expected_revision=initial.revision, reason="populate", source="test",
    )
    prompt = Path("core/prompt.txt").read_text(encoding="utf-8")
    soul_path = reconcile_legacy_prompt(prompt, "[CONSTITUTION]\nactive")
    legacy_path = reconcile_legacy_prompt(prompt, "")
    assert "most experienced person in the room" not in soul_path
    assert "most experienced person in the room" in legacy_path
    assert SoulStore(store.path, clock=lambda: NOW).load().identity.warmth.value == .89
    assert SoulStore(store.path, clock=lambda: NOW).load().revision == changed.revision
