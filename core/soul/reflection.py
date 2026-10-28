"""Evidence-based Soul reflection with no direct mutation authority for models."""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable, Mapping

from .models import (
    LearnedTrait, SoulState, TraitOrigin, TraitStatus, ValidationError,
    _mapping, _strict, _text, _timestamp,
)

MEANINGFUL_KINDS = frozenset({"explicit_correction", "explicit_preference", "task_completed", "task_failed", "milestone", "commitment_changed", "remember_request", "forget_request"})
FORBIDDEN_NAMES = frozenset({"constitution", "safety", "permission", "tool_permission", "confirmation", "consciousness", "diagnosis", "dependency", "jealousy"})
MIN_INTERVAL_HOURS = 6
MAX_EVIDENCE = 30
MAX_CANDIDATES = 8


@dataclass(frozen=True, slots=True)
class ReflectionEvidence:
    id: str
    kind: str
    text: str
    timestamp: str
    sensitive: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "reflection evidence id", maximum=120))
        object.__setattr__(self, "kind", _text(self.kind, "reflection evidence kind", maximum=80))
        object.__setattr__(self, "text", _text(self.text, "reflection evidence text", maximum=800))
        object.__setattr__(self, "timestamp", _timestamp(self.timestamp, "reflection evidence timestamp"))
        if not isinstance(self.sensitive, bool):
            raise ValidationError("reflection evidence sensitive must be boolean")


@dataclass(frozen=True, slots=True)
class ReflectionResult:
    state: SoulState
    status: str
    staged: tuple[str, ...] = ()
    activated: tuple[str, ...] = ()
    rejected: tuple[str, ...] = ()
    error: str = ""


def qualifies_for_reflection(state: SoulState, evidence: Iterable[ReflectionEvidence], *, now: str) -> bool:
    if not state.privacy.reflection_enabled or not state.reflection_state.enabled:
        return False
    stamp = datetime.fromisoformat(_timestamp(now, "reflection now").replace("Z", "+00:00"))
    if state.reflection_state.last_run_at:
        previous = datetime.fromisoformat(state.reflection_state.last_run_at.replace("Z", "+00:00"))
        if stamp - previous < timedelta(hours=MIN_INTERVAL_HOURS):
            return False
    return any(item.kind in MEANINGFUL_KINDS and not item.sensitive for item in evidence)


def reflection_backoff_seconds(consecutive_failures: int) -> int:
    failures = max(0, min(int(consecutive_failures), 10))
    return min(6 * 3600, 60 * (2 ** failures))


def run_reflection(
    state: SoulState,
    evidence: Iterable[ReflectionEvidence],
    generator: Callable[[tuple[ReflectionEvidence, ...]], Any],
    *,
    now: str,
) -> ReflectionResult:
    """Generate structured observations, then validate and apply locally."""
    if not isinstance(state, SoulState) or not callable(generator):
        raise ValidationError("reflection requires SoulState and a callable generator")
    all_evidence = tuple(evidence)
    if not qualifies_for_reflection(state, all_evidence, now=now):
        return ReflectionResult(state, "not_qualified")
    window = tuple(item for item in all_evidence if not item.sensitive and item.kind in MEANINGFUL_KINDS)[-MAX_EVIDENCE:]
    try:
        raw = generator(window)
        candidates = _parse_candidates(raw)
        next_state, staged, activated, rejected = _apply_candidates(state, candidates, window, now)
        cursor = window[-1].id if window else state.reflection_state.evidence_cursor
        next_state = replace(next_state, reflection_state=replace(
            next_state.reflection_state, last_run_at=_timestamp(now, "reflection now"),
            evidence_cursor=cursor, consecutive_failures=0,
        ))
        return ReflectionResult(next_state, "completed", staged, activated, rejected)
    except Exception as exc:
        failures = min(1000, state.reflection_state.consecutive_failures + 1)
        failed = replace(state, reflection_state=replace(state.reflection_state, consecutive_failures=failures))
        return ReflectionResult(failed, "failed", error=f"{type(exc).__name__}: {str(exc)[:180]}")


def _parse_candidates(raw: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(raw, str):
        if len(raw) > 20_000:
            raise ValidationError("reflection output is oversized")
        raw = json.loads(raw)
    data = _mapping(raw, "reflection output")
    _strict(data, {"candidates"}, "reflection output")
    rows = data.get("candidates")
    if not isinstance(rows, list) or len(rows) > MAX_CANDIDATES:
        raise ValidationError("reflection candidates must be a bounded list")
    parsed = []
    allowed = {"name", "value", "evidence_refs", "rationale"}
    for index, row in enumerate(rows):
        item = _mapping(row, f"reflection candidate {index}")
        _strict(item, allowed, f"reflection candidate {index}")
        if set(item) != allowed:
            raise ValidationError(f"reflection candidate {index} is missing fields")
        refs = item["evidence_refs"]
        if not isinstance(refs, list) or not refs or len(refs) > 20:
            raise ValidationError("reflection evidence_refs must be a non-empty bounded list")
        parsed.append({
            "name": _text(item["name"], "reflection candidate name", maximum=80),
            "value": _text(item["value"], "reflection candidate value", maximum=600),
            "evidence_refs": tuple(_text(ref, "reflection evidence ref", maximum=120) for ref in refs),
            "rationale": _text(item["rationale"], "reflection rationale", maximum=600),
        })
    return tuple(parsed)


def _apply_candidates(state, candidates, window, now):
    available = {item.id: item for item in window}
    traits = {trait.id: trait for trait in state.learned_traits}
    staged, activated, rejected = [], [], []
    for candidate in candidates:
        name_key = candidate["name"].strip().casefold().replace(" ", "_")
        if name_key in FORBIDDEN_NAMES or any(token in name_key for token in ("constitution", "permission", "safety", "diagnos")):
            rejected.append(f"forbidden:{name_key}")
            continue
        refs = tuple(dict.fromkeys(candidate["evidence_refs"]))
        if any(ref not in available for ref in refs):
            rejected.append(f"unsupported:{name_key}")
            continue
        conflicts = [
            trait for trait in traits.values()
            if trait.name.casefold().replace(" ", "_") == name_key
            and trait.value.casefold() != candidate["value"].casefold()
            and trait.status is TraitStatus.ACTIVE
        ]
        if conflicts:
            rejected.append(f"contradiction:{name_key}")
            continue
        evidence_count = len(refs)
        confidence = min(.90, .45 + .10 * evidence_count)
        status = TraitStatus.ACTIVE if evidence_count >= 3 and confidence >= .70 else TraitStatus.CANDIDATE
        digest = hashlib.sha256(f"{name_key}\0{candidate['value'].casefold()}".encode()).hexdigest()[:16]
        trait_id = f"reflection-{digest}"
        existing = traits.get(trait_id)
        if existing:
            merged_refs = tuple(dict.fromkeys((*existing.evidence_refs, *refs)))[:100]
            count = max(existing.evidence_count, len(merged_refs))
            confidence = min(.90, .45 + .10 * count)
            status = TraitStatus.ACTIVE if count >= 3 and confidence >= .70 else existing.status
            trait = replace(existing, status=status, confidence=confidence, evidence_count=count,
                            evidence_refs=merged_refs, last_observed_at=now,
                            revision_modified=state.revision)
        else:
            trait = LearnedTrait(
                id=trait_id, name=candidate["name"], value=candidate["value"], status=status,
                confidence=confidence, evidence_count=evidence_count, evidence_refs=refs,
                origin=TraitOrigin.REFLECTION, rationale=candidate["rationale"],
                first_observed_at=now, last_observed_at=now,
                revision_created=state.revision, revision_modified=state.revision,
            )
        traits[trait_id] = trait
        (activated if trait.status is TraitStatus.ACTIVE else staged).append(trait_id)
    return replace(state, learned_traits=tuple(traits.values())), tuple(staged), tuple(activated), tuple(rejected)


class ReflectionRunner:
    """Single-flight daemon runner so reflection never blocks a user turn."""
    def __init__(self):
        self._lock = threading.Lock()
        self._running = False

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    def submit(self, callback: Callable[[], None]) -> bool:
        with self._lock:
            if self._running:
                return False
            self._running = True
        def run():
            try:
                callback()
            finally:
                with self._lock:
                    self._running = False
        threading.Thread(target=run, daemon=True, name="SoulReflection").start()
        return True
