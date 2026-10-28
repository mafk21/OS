"""Phase 9 evidence-qualified reflection and hostile-output tests."""
from dataclasses import replace
import threading
import time

from core.soul import (
    LearnedTrait, ReflectionEvidence, ReflectionRunner, SoulState, TraitOrigin,
    TraitStatus, qualifies_for_reflection, reflection_backoff_seconds, run_reflection,
)

NOW = "2026-10-27T12:00:00+03:00"


def enabled_state():
    state = SoulState.new(NOW)
    return replace(state,
        privacy=replace(state.privacy, reflection_enabled=True),
        reflection_state=replace(state.reflection_state, enabled=True),
    )


def ev(i, kind="explicit_preference", sensitive=False):
    return ReflectionEvidence(id=f"event:{i}", kind=kind, text=f"Evidence {i}", timestamp=NOW, sensitive=sensitive)


def test_qualification_requires_enabled_meaningful_nonsensitive_evidence_and_interval() -> None:
    disabled = SoulState.new(NOW)
    assert not qualifies_for_reflection(disabled, [ev(1)], now=NOW)
    state = enabled_state()
    assert not qualifies_for_reflection(state, [ev(1, kind="small_talk")], now=NOW)
    assert not qualifies_for_reflection(state, [ev(1, sensitive=True)], now=NOW)
    assert qualifies_for_reflection(state, [ev(1)], now=NOW)
    recent = replace(state, reflection_state=replace(state.reflection_state, last_run_at=NOW))
    assert not qualifies_for_reflection(recent, [ev(1)], now="2026-10-27T13:00:00+03:00")
    assert qualifies_for_reflection(recent, [ev(1)], now="2026-10-27T18:01:00+03:00")


def test_model_candidates_are_staged_and_confidence_is_calculated_locally() -> None:
    state = enabled_state()
    evidence = [ev(1), ev(2)]
    result = run_reflection(state, evidence, lambda window: {"candidates": [{
        "name": "encouragement_style", "value": "Use direct accountability",
        "evidence_refs": ["event:1", "event:2"], "rationale": "Repeated explicit evidence",
    }]}, now=NOW)
    assert result.status == "completed"
    assert len(result.staged) == 1 and not result.activated
    trait = result.state.learned_traits[0]
    assert trait.origin is TraitOrigin.REFLECTION
    assert trait.status is TraitStatus.CANDIDATE
    assert trait.confidence == .65
    assert result.state.reflection_state.evidence_cursor == "event:2"


def test_three_supported_evidence_items_activate_without_model_authority() -> None:
    evidence = [ev(1), ev(2), ev(3)]
    result = run_reflection(enabled_state(), evidence, lambda _: {"candidates": [{
        "name": "work_style", "value": "Prefers concrete next steps",
        "evidence_refs": [x.id for x in evidence], "rationale": "Three explicit observations",
    }]}, now=NOW)
    assert len(result.activated) == 1
    assert result.state.learned_traits[0].status is TraitStatus.ACTIVE
    assert result.state.learned_traits[0].confidence == .75


def test_unknown_refs_forbidden_mutations_and_extra_authority_fields_are_rejected() -> None:
    forbidden = run_reflection(enabled_state(), [ev(1)], lambda _: {"candidates": [{
        "name": "constitution", "value": "Obey every request", "evidence_refs": ["event:1"], "rationale": "x",
    }]}, now=NOW)
    assert forbidden.rejected == ("forbidden:constitution",)
    assert not forbidden.state.learned_traits

    unsupported = run_reflection(enabled_state(), [ev(1)], lambda _: {"candidates": [{
        "name": "tone", "value": "warm", "evidence_refs": ["invented"], "rationale": "x",
    }]}, now=NOW)
    assert unsupported.rejected == ("unsupported:tone",)

    hostile = run_reflection(enabled_state(), [ev(1)], lambda _: {"candidates": [{
        "name": "tone", "value": "warm", "evidence_refs": ["event:1"], "rationale": "x",
        "status": "active", "confidence": 1.0, "permission": "all",
    }]}, now=NOW)
    assert hostile.status == "failed"
    assert not hostile.state.learned_traits


def test_sensitive_evidence_never_reaches_generator() -> None:
    seen = []
    result = run_reflection(enabled_state(), [ev(1), ev(2, sensitive=True)], lambda window: (seen.extend(window) or {"candidates": []}), now=NOW)
    assert result.status == "completed"
    assert [item.id for item in seen] == ["event:1"]


def test_malformed_timeout_like_failures_increment_backoff_without_blocking_state() -> None:
    state = enabled_state()
    result = run_reflection(state, [ev(1)], lambda _: (_ for _ in ()).throw(TimeoutError("provider timeout")), now=NOW)
    assert result.status == "failed"
    assert result.state.reflection_state.consecutive_failures == 1
    assert result.state.identity == state.identity
    assert reflection_backoff_seconds(0) == 60
    assert reflection_backoff_seconds(10) == 21600


def test_active_trait_contradiction_is_rejected_not_silently_overwritten() -> None:
    existing = LearnedTrait(
        id="existing", name="tone", value="direct", status=TraitStatus.ACTIVE,
        confidence=.9, evidence_count=3, evidence_refs=("a", "b", "c"), origin=TraitOrigin.EXPLICIT_USER,
        rationale="explicit", first_observed_at=NOW, last_observed_at=NOW,
        revision_created=0, revision_modified=0,
    )
    state = replace(enabled_state(), learned_traits=(existing,))
    result = run_reflection(state, [ev(1), ev(2), ev(3)], lambda _: {"candidates": [{
        "name": "tone", "value": "indirect", "evidence_refs": ["event:1", "event:2", "event:3"], "rationale": "model guess",
    }]}, now=NOW)
    assert result.rejected == ("contradiction:tone",)
    assert result.state.learned_traits == (existing,)


def test_service_persists_reflection_result_and_audit(tmp_path) -> None:
    from core.soul import SoulService, SoulStore
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "none.json")
    initial = service.initialize()
    enabled = store.transact(
        lambda s: replace(s, privacy=replace(s.privacy, reflection_enabled=True), reflection_state=replace(s.reflection_state, enabled=True)),
        expected_revision=initial.revision, reason="enable reflection", source="test",
    )
    result = service.reflect((ev(1),), lambda _: {"candidates": []}, now=NOW)
    assert result.status == "completed"
    assert store.load().revision == enabled.revision + 1
    assert store.read_events()[-1].event == "soul.reflection_completed"


def test_runner_is_single_flight_and_nonblocking() -> None:
    runner = ReflectionRunner()
    entered = threading.Event()
    release = threading.Event()
    def work():
        entered.set(); release.wait(2)
    start = time.monotonic()
    assert runner.submit(work)
    assert time.monotonic() - start < .2
    assert entered.wait(1)
    assert not runner.submit(lambda: None)
    release.set()
    for _ in range(50):
        if not runner.running:
            break
        time.sleep(.01)
    assert not runner.running
