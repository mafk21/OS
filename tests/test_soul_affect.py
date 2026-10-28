"""Phase 6 deterministic bounded affect and operational-isolation tests."""
from __future__ import annotations

import ast
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

from core.soul import (
    DAILY_CAPS,
    AffectDelta,
    AffectEvent,
    AffectState,
    SoulContextBuilder,
    SoulService,
    SoulState,
    SoulStore,
    ValidationError,
    apply_affect_event,
    apply_event_to_soul,
    decay_affect,
    explain_affect,
    migrate_raw,
)

NOW = "2026-10-27T12:00:00+03:00"


def test_verified_events_have_small_deterministic_explainable_effects() -> None:
    state = AffectState(updated_at=NOW, daily_date="2026-10-27")
    first = apply_affect_event(
        state, AffectEvent.VERIFIED_TASK_SUCCESS,
        occurred_at=NOW, evidence_ref="long-task:abc:completed",
    )
    second = apply_affect_event(
        state, "verified_task_success",
        occurred_at=NOW, evidence_ref="long-task:abc:completed",
    )
    assert first == second
    assert first.after.confidence == pytest.approx(state.confidence + .04)
    assert first.after.rapport == pytest.approx(state.rapport + .025)
    assert first.after.concern == pytest.approx(state.concern - .02)
    assert first.after.causes[-1] == "verified_task_success:long-task:abc:completed"
    assert "Applied verified_task_success" in first.explanation


def test_decay_moves_each_dimension_toward_baseline_by_half_life() -> None:
    state = AffectState(
        calm=.98, baseline_calm=.78,
        energy=.78, baseline_energy=.58,
        concern=.38, baseline_concern=.18,
        confidence=.92, baseline_confidence=.72,
        curiosity=.82, baseline_curiosity=.62,
        rapport=.65, baseline_rapport=.45,
        updated_at="2026-10-27T00:00:00+00:00", daily_date="2026-10-27",
    )
    # Energy has a four-hour half-life.
    update = decay_affect(state, now="2026-10-27T04:00:00+00:00")
    assert update.after.energy == pytest.approx(.68)
    for name in ("calm", "energy", "concern", "confidence", "curiosity", "rapport"):
        before_distance = abs(getattr(state, name) - getattr(state, f"baseline_{name}"))
        after_distance = abs(getattr(update.after, name) - getattr(state, f"baseline_{name}"))
        assert after_distance <= before_distance
    assert update.after.updated_at == "2026-10-27T04:00:00+00:00"


def test_time_not_advancing_never_inverts_or_amplifies_state() -> None:
    state = AffectState(energy=.8, updated_at=NOW, daily_date="2026-10-27")
    same = decay_affect(state, now=NOW)
    backwards = decay_affect(state, now="2026-10-27T11:00:00+03:00")
    assert same.after.energy == state.energy
    assert backwards.after.energy == state.energy
    assert "did not advance" in backwards.explanation


def test_repeated_events_cannot_exceed_daily_caps_or_numeric_bounds() -> None:
    state = AffectState(updated_at=NOW, daily_date="2026-10-27")
    for index in range(20):
        state = apply_affect_event(
            state, AffectEvent.REPEATED_VERIFIED_FAILURE,
            occurred_at=NOW, evidence_ref=f"failure:{index}",
        ).after
    assert abs(state.daily_delta.concern) <= DAILY_CAPS["concern"] + 1e-12
    assert abs(state.daily_delta.confidence) <= DAILY_CAPS["confidence"] + 1e-12
    assert abs(state.daily_delta.calm) <= DAILY_CAPS["calm"] + 1e-12
    for name in ("calm", "energy", "concern", "confidence", "curiosity", "rapport"):
        assert 0.0 <= getattr(state, name) <= 1.0
    assert len(state.causes) == 12


def test_new_local_date_resets_daily_accumulator_before_event() -> None:
    state = AffectState(
        daily_delta=AffectDelta(confidence=.20),
        daily_date="2026-10-27", updated_at="2026-10-27T23:50:00+03:00",
    )
    update = apply_affect_event(
        state, AffectEvent.VERIFIED_TASK_SUCCESS,
        occurred_at="2026-10-28T00:10:00+03:00", evidence_ref="task:new-day",
    )
    assert update.after.daily_date == "2026-10-28"
    assert update.after.daily_delta.confidence == pytest.approx(.04)


def test_rest_event_reduces_pressure_instead_of_punishing_user() -> None:
    state = AffectState(concern=.5, energy=.7, calm=.5, updated_at=NOW, daily_date="2026-10-27")
    update = apply_affect_event(
        state, AffectEvent.USER_REQUESTED_REST, occurred_at=NOW, evidence_ref="user:explicit-rest",
    )
    assert update.after.calm > state.calm
    assert update.after.concern < state.concern
    assert update.after.energy < state.energy


def test_invalid_events_evidence_dates_and_delta_values_fail_closed() -> None:
    state = AffectState(updated_at=NOW, daily_date="2026-10-27")
    with pytest.raises(ValidationError, match="unsupported"):
        apply_affect_event(state, "jealousy", occurred_at=NOW, evidence_ref="x")
    with pytest.raises(ValidationError, match="cannot be empty"):
        apply_affect_event(state, AffectEvent.LONG_INACTIVITY, occurred_at=NOW, evidence_ref="")
    with pytest.raises(ValidationError, match="timezone"):
        decay_affect(state, now="2026-10-27T12:00:00")
    with pytest.raises(ValidationError, match="finite"):
        AffectDelta(calm=math.nan)
    with pytest.raises(ValidationError, match="YYYY-MM-DD"):
        AffectState(updated_at=NOW, daily_date="27/10/2026")


def test_explanation_is_transparent_and_non_anthropomorphic() -> None:
    state = apply_affect_event(
        AffectState(updated_at=NOW, daily_date="2026-10-27"),
        AffectEvent.MEANINGFUL_NOVEL_TOPIC,
        occurred_at=NOW, evidence_ref="topic:physics",
    ).after
    explanation = explain_affect(state)
    assert "not biological emotion" in explanation["framing"]
    assert explanation["dimensions"]["curiosity"]["baseline"] == state.baseline_curiosity
    assert explanation["dimensions"]["curiosity"]["daily_cap"] == DAILY_CAPS["curiosity"]
    assert explanation["causes"] == list(state.causes)


def test_affect_changes_only_expressive_context_section() -> None:
    base = SoulState.new(NOW)
    changed, _update = apply_event_to_soul(
        base, AffectEvent.REPEATED_VERIFIED_FAILURE,
        occurred_at=NOW, evidence_ref="workflow:verified-failure",
    )
    builder = SoulContextBuilder()
    before = builder.build(base).text
    after = builder.build(changed).text
    assert before != after
    before_sections = _sections(before)
    after_sections = _sections(after)
    for name in before_sections:
        if name == "CURRENT EXPRESSIVE STATE":
            assert before_sections[name] != after_sections[name]
        else:
            assert before_sections[name] == after_sections[name]


def test_affect_module_has_no_operational_authority_imports() -> None:
    source = Path("core/soul/affect.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = {
        "actions", "core.confirm", "core.action_loader", "core.plugin_loader",
        "core.os_control", "core.provider", "core.openai_live", "core.gemini",
    }
    assert not any(name in forbidden or name.startswith("actions.") for name in imported)
    for forbidden_word in ("execute_tool", "allowed_tools", "confirmation_required"):
        assert forbidden_word not in source


def test_v1_state_migrates_affect_baselines_and_daily_accounting() -> None:
    raw = SoulState.new(NOW).to_dict()
    raw["schema_version"] = 1
    raw["relationship"].pop("claims")
    raw["relationship"].pop("contradictions")
    for key in ("daily_date", "interruptions_today", "snooze_until", "topics"):
        raw["initiative_policy"].pop(key)
    for key in (
        "baseline_calm", "baseline_energy", "baseline_concern", "baseline_confidence",
        "baseline_curiosity", "baseline_rapport", "daily_delta", "daily_date",
    ):
        raw["affect"].pop(key)
    result = migrate_raw(raw)
    assert result.applied == ("schema-v1-to-v2", "schema-v2-to-v3", "schema-v3-to-v4")
    assert result.state.schema_version == 4
    assert result.state.affect.baseline_calm == result.state.affect.calm
    assert result.state.affect.daily_delta == AffectDelta()
    assert "schema-v1-to-v2" in result.state.completed_migrations


def test_service_persists_verified_event_and_audits_it(tmp_path) -> None:
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "memory" / "companions.json")
    update = service.record_affect_event(
        AffectEvent.VERIFIED_TASK_SUCCESS,
        evidence_ref="long-task:done",
        occurred_at=NOW,
    )
    assert update is not None
    persisted = store.load()
    assert persisted.revision == 1
    assert persisted.affect.confidence > persisted.affect.baseline_confidence
    assert store.read_events()[-1].event == "soul.affect_changed"
    assert "long-task:done" in persisted.affect.causes[-1]


def test_long_task_adapter_requires_completed_status_id_and_evidence(monkeypatch) -> None:
    from core.soul import service as service_module

    captured = []
    monkeypatch.setattr(
        service_module, "record_runtime_affect_event",
        lambda event, **kwargs: captured.append((event, kwargs)),
    )
    service_module.record_long_task_completion({"id": "x", "status": "failed", "completion_evidence": "error"})
    service_module.record_long_task_completion({"id": "x", "status": "completed", "completion_evidence": ""})
    service_module.record_long_task_completion({"id": "", "status": "completed", "completion_evidence": "done"})
    assert captured == []
    service_module.record_long_task_completion({
        "id": "long-123", "status": "completed", "completion_evidence": "workflow checkpoint",
    })
    assert captured == [(
        AffectEvent.VERIFIED_TASK_SUCCESS,
        {"evidence_ref": "long-task:long-123:completed"},
    )]


def test_service_does_not_mutate_when_affect_privacy_control_is_off(tmp_path) -> None:
    store = SoulStore(tmp_path / "memory" / "soul.json", clock=lambda: NOW)
    service = SoulService(store, companions_path=tmp_path / "memory" / "companions.json")
    initial = service.initialize()
    disabled = store.transact(
        lambda state: replace(state, privacy=replace(state.privacy, affect_enabled=False)),
        expected_revision=initial.revision, reason="disable affect", source="test",
    )
    result = service.record_affect_event(
        AffectEvent.VERIFIED_TASK_SUCCESS, evidence_ref="task:x", occurred_at=NOW,
    )
    assert result is None
    assert store.load() == disabled


def _sections(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("[") and line.endswith("]"):
            if current is not None:
                result[current] = "\n".join(lines)
            current = line[1:-1]
            lines = []
        else:
            lines.append(line)
    if current is not None:
        result[current] = "\n".join(lines)
    return result
