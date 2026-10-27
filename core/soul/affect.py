"""Deterministic bounded expressive-state engine.

Affect changes wording context only. This module has no imports from tools,
actions, permissions, confirmation, providers, UI, or safety policy.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .models import AffectDelta, AffectState, SoulState, ValidationError, _text, _timestamp

DIMENSIONS = ("calm", "energy", "concern", "confidence", "curiosity", "rapport")
DAILY_CAPS: Mapping[str, float] = MappingProxyType({
    "calm": .20,
    "energy": .20,
    "concern": .25,
    "confidence": .20,
    "curiosity": .20,
    "rapport": .15,
})
HALF_LIFE_HOURS: Mapping[str, float] = MappingProxyType({
    "calm": 6.0,
    "energy": 4.0,
    "concern": 3.0,
    "confidence": 8.0,
    "curiosity": 5.0,
    "rapport": 48.0,
})


class AffectEvent(str, Enum):
    VERIFIED_TASK_SUCCESS = "verified_task_success"
    REPEATED_VERIFIED_FAILURE = "repeated_verified_failure"
    EXPLICIT_CORRECTION_ACCEPTED = "explicit_correction_accepted"
    COMMITMENT_NEARING_DEADLINE = "commitment_nearing_deadline"
    MEANINGFUL_NOVEL_TOPIC = "meaningful_novel_topic"
    LONG_INACTIVITY = "long_inactivity"
    RESPECTFUL_DISAGREEMENT_RESOLVED = "respectful_disagreement_resolved"
    USER_REQUESTED_REST = "user_requested_rest"


EVENT_DELTAS: Mapping[AffectEvent, AffectDelta] = MappingProxyType({
    AffectEvent.VERIFIED_TASK_SUCCESS: AffectDelta(concern=-.02, confidence=.04, rapport=.025),
    AffectEvent.REPEATED_VERIFIED_FAILURE: AffectDelta(calm=-.03, concern=.08, confidence=-.05),
    AffectEvent.EXPLICIT_CORRECTION_ACCEPTED: AffectDelta(confidence=-.03, curiosity=.02, rapport=.03),
    AffectEvent.COMMITMENT_NEARING_DEADLINE: AffectDelta(energy=.02, concern=.05),
    AffectEvent.MEANINGFUL_NOVEL_TOPIC: AffectDelta(energy=.02, curiosity=.06),
    AffectEvent.LONG_INACTIVITY: AffectDelta(energy=-.04),
    AffectEvent.RESPECTFUL_DISAGREEMENT_RESOLVED: AffectDelta(calm=.02, rapport=.04),
    AffectEvent.USER_REQUESTED_REST: AffectDelta(calm=.05, energy=-.02, concern=-.03),
})


@dataclass(frozen=True, slots=True)
class AffectUpdate:
    before: AffectState
    after: AffectState
    event: AffectEvent | None
    requested_delta: AffectDelta
    applied_delta: AffectDelta
    explanation: str


def decay_affect(state: AffectState, *, now: str) -> AffectUpdate:
    """Lazily decay current values toward persisted baselines."""
    if not isinstance(state, AffectState):
        raise ValidationError("affect decay requires AffectState")
    now_text = _timestamp(now, "affect decay timestamp")
    previous = _parse_timestamp(state.updated_at)
    current = _parse_timestamp(now_text)
    elapsed_hours = (current - previous).total_seconds() / 3600.0
    if elapsed_hours <= 0:
        return AffectUpdate(
            before=state, after=state, event=None, requested_delta=AffectDelta(), applied_delta=AffectDelta(),
            explanation="No decay applied because time did not advance.",
        )
    values: dict[str, float] = {}
    for name in DIMENSIONS:
        value = getattr(state, name)
        baseline = getattr(state, f"baseline_{name}")
        if elapsed_hours <= 0:
            values[name] = value
        else:
            remaining = math.pow(.5, elapsed_hours / HALF_LIFE_HOURS[name])
            values[name] = _clamp(baseline + (value - baseline) * remaining)
    date = current.date().isoformat()
    daily_delta = state.daily_delta if date == state.daily_date else AffectDelta()
    after = replace(state, **values, daily_delta=daily_delta, daily_date=date, updated_at=now_text)
    applied = AffectDelta(**{name: getattr(after, name) - getattr(state, name) for name in DIMENSIONS})
    return AffectUpdate(
        before=state, after=after, event=None, requested_delta=AffectDelta(), applied_delta=applied,
        explanation=(
            f"Expressive state decayed toward baseline over {elapsed_hours:.2f} hours."
            if elapsed_hours > 0 else "No decay applied because time did not advance."
        ),
    )


def apply_affect_event(
    state: AffectState,
    event: AffectEvent | str,
    *,
    occurred_at: str,
    evidence_ref: str,
) -> AffectUpdate:
    """Decay, then apply one typed event under per-dimension daily caps."""
    if not isinstance(state, AffectState):
        raise ValidationError("affect event requires AffectState")
    try:
        typed_event = AffectEvent(event)
    except (TypeError, ValueError) as exc:
        raise ValidationError("unsupported affect event") from exc
    evidence = _text(evidence_ref, "affect evidence reference", maximum=160)
    occurred_text = _timestamp(occurred_at, "affect event timestamp")
    if _parse_timestamp(occurred_text) < _parse_timestamp(state.updated_at):
        raise ValidationError("affect event timestamp cannot precede the current affect state")
    decayed = decay_affect(state, now=occurred_text).after
    requested = EVENT_DELTAS[typed_event]
    current_daily = decayed.daily_delta
    applied_values: dict[str, float] = {}
    daily_values: dict[str, float] = {}
    state_values: dict[str, float] = {}
    for name in DIMENSIONS:
        wanted = getattr(requested, name)
        accumulated = getattr(current_daily, name)
        cap = DAILY_CAPS[name]
        if wanted > 0:
            allowed = max(0.0, cap - max(0.0, accumulated))
            applied = min(wanted, allowed)
        elif wanted < 0:
            allowed = max(0.0, cap - max(0.0, -accumulated))
            applied = -min(-wanted, allowed)
        else:
            applied = 0.0
        old_value = getattr(decayed, name)
        new_value = _clamp(old_value + applied)
        actual = new_value - old_value
        applied_values[name] = actual
        daily_values[name] = _signed_clamp(accumulated + actual)
        state_values[name] = new_value

    cause = f"{typed_event.value}:{evidence}"
    causes = tuple((*decayed.causes, cause)[-12:])
    after = replace(
        decayed,
        **state_values,
        daily_delta=AffectDelta(**daily_values),
        causes=causes,
        updated_at=_timestamp(occurred_at, "affect event timestamp"),
    )
    applied_delta = AffectDelta(**applied_values)
    clipped = any(
        not math.isclose(getattr(requested, name), getattr(applied_delta, name), abs_tol=1e-12)
        for name in DIMENSIONS
    )
    explanation = (
        f"Applied {typed_event.value} from {evidence}."
        + (" One or more changes were bounded by state or daily caps." if clipped else "")
    )
    return AffectUpdate(
        before=state, after=after, event=typed_event,
        requested_delta=requested, applied_delta=applied_delta, explanation=explanation,
    )


def apply_event_to_soul(
    state: SoulState,
    event: AffectEvent | str,
    *,
    occurred_at: str,
    evidence_ref: str,
) -> tuple[SoulState, AffectUpdate]:
    if not isinstance(state, SoulState):
        raise ValidationError("affect event requires SoulState")
    update = apply_affect_event(state.affect, event, occurred_at=occurred_at, evidence_ref=evidence_ref)
    return replace(state, affect=update.after), update


def explain_affect(state: AffectState) -> dict[str, object]:
    """Return transparent bounded diagnostics without claiming human feelings."""
    if not isinstance(state, AffectState):
        raise ValidationError("affect explanation requires AffectState")
    return {
        "framing": "Bounded expressive state derived from verified events; not biological emotion.",
        "updated_at": state.updated_at,
        "daily_date": state.daily_date,
        "dimensions": {
            name: {
                "value": getattr(state, name),
                "baseline": getattr(state, f"baseline_{name}"),
                "daily_delta": getattr(state.daily_delta, name),
                "daily_cap": DAILY_CAPS[name],
                "half_life_hours": HALF_LIFE_HOURS[name],
            }
            for name in DIMENSIONS
        },
        "causes": list(state.causes),
    }


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _signed_clamp(value: float) -> float:
    return min(1.0, max(-1.0, float(value)))
