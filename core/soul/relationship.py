"""Evidence-backed relationship continuity without duplicating factual memory."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from typing import Iterable

from .models import (
    RelationshipClaim,
    RelationshipClaimStatus,
    RelationshipContradiction,
    RelationshipKind,
    RelationshipState,
    Sensitivity,
    SoulState,
    ValidationError,
    _text,
    _timestamp,
)


@dataclass(frozen=True, slots=True)
class RelationshipUpdate:
    before: RelationshipState
    after: RelationshipState
    claim: RelationshipClaim | None
    contradiction: RelationshipContradiction | None
    explanation: str


@dataclass(frozen=True, slots=True)
class ForgetResult:
    state: RelationshipState
    removed_claims: int
    removed_contradictions: int


def observe_relationship(
    state: RelationshipState,
    *,
    kind: RelationshipKind | str,
    subject: str,
    value: str,
    evidence_ref: str,
    observed_at: str,
    explicit: bool,
    sensitivity: Sensitivity | str = Sensitivity.NORMAL,
) -> RelationshipUpdate:
    """Add/reinforce a claim or stage a contradiction from attributable evidence."""
    if not isinstance(state, RelationshipState):
        raise ValidationError("relationship observation requires RelationshipState")
    try:
        typed_kind = RelationshipKind(kind)
        typed_sensitivity = Sensitivity(sensitivity)
    except (TypeError, ValueError) as exc:
        raise ValidationError("unsupported relationship kind or sensitivity") from exc
    clean_subject = _text(subject, "relationship subject", maximum=120)
    clean_value = _text(value, "relationship value", maximum=600)
    evidence = _text(evidence_ref, "relationship evidence reference", maximum=160)
    stamp = _timestamp(observed_at, "relationship observed_at")
    if not isinstance(explicit, bool):
        raise ValidationError("relationship explicit must be true or false")
    if typed_sensitivity is Sensitivity.SENSITIVE and not explicit:
        raise ValidationError("sensitive relationship observations require explicit user evidence")

    claim_id = _claim_id(typed_kind, clean_subject, clean_value)
    claims = list(state.claims)
    existing_index = next((i for i, item in enumerate(claims) if item.id == claim_id), None)
    if existing_index is not None:
        old = claims[existing_index]
        refs = tuple(dict.fromkeys((*old.evidence_refs, evidence)))[-20:]
        reinforced = replace(
            old,
            status=RelationshipClaimStatus.ACTIVE if explicit else old.status,
            explicit=old.explicit or explicit,
            confidence=min(1.0, old.confidence + (.10 if explicit else .06)),
            evidence_count=old.evidence_count + 1,
            evidence_refs=refs,
            last_observed_at=stamp,
        )
        claims[existing_index] = reinforced
        after = replace(state, claims=tuple(claims), stage=_derive_stage(tuple(claims)))
        return RelationshipUpdate(state, after, reinforced, None, "Reinforced an existing relationship claim with new evidence.")

    same_subject = [
        item for item in claims
        if item.kind is typed_kind and item.subject.casefold() == clean_subject.casefold()
        and item.status is not RelationshipClaimStatus.SUPERSEDED
    ]
    new_claim = RelationshipClaim(
        id=claim_id, kind=typed_kind, subject=clean_subject, value=clean_value,
        status=RelationshipClaimStatus.ACTIVE if not same_subject or explicit else RelationshipClaimStatus.DISPUTED,
        sensitivity=typed_sensitivity, explicit=explicit,
        confidence=.95 if explicit else .60,
        evidence_count=1, evidence_refs=(evidence,),
        first_observed_at=stamp, last_observed_at=stamp,
    )
    contradiction = None
    if same_subject:
        old_ids = tuple(item.id for item in same_subject)
        if explicit:
            claims = [
                replace(item, status=RelationshipClaimStatus.SUPERSEDED)
                if item.id in old_ids else item
                for item in claims
            ]
            resolution = "explicit_recent_statement"
        else:
            claims = [
                replace(item, status=RelationshipClaimStatus.DISPUTED)
                if item.id in old_ids else item
                for item in claims
            ]
            resolution = "unresolved"
        contradiction = RelationshipContradiction(
            id=_contradiction_id(typed_kind, clean_subject, (*old_ids, claim_id)),
            subject=clean_subject, claim_ids=(*old_ids, claim_id), created_at=stamp,
            resolution=resolution,
        )
    claims.append(new_claim)
    contradictions = tuple((*state.contradictions, *((contradiction,) if contradiction else ())))[-100:]
    after = replace(
        state, claims=tuple(claims[-200:]), contradictions=contradictions,
        stage=_derive_stage(tuple(claims)),
    )
    explanation = (
        "Explicit recent evidence superseded a conflicting relationship claim."
        if contradiction and explicit else
        "Conflicting inferred claims were marked disputed pending clarification."
        if contradiction else
        "Recorded a new evidence-backed relationship claim."
    )
    return RelationshipUpdate(state, after, new_claim, contradiction, explanation)


def forget_relationship_subject(state: RelationshipState, subject: str) -> ForgetResult:
    """Remove matching content without retaining its private value in a tombstone."""
    if not isinstance(state, RelationshipState):
        raise ValidationError("relationship forgetting requires RelationshipState")
    clean = _text(subject, "relationship subject", maximum=120)
    removed_ids = {claim.id for claim in state.claims if claim.subject.casefold() == clean.casefold()}
    claims = tuple(claim for claim in state.claims if claim.id not in removed_ids)
    contradictions = tuple(
        item for item in state.contradictions
        if item.subject.casefold() != clean.casefold() and not removed_ids.intersection(item.claim_ids)
    )
    return ForgetResult(
        state=replace(state, claims=claims, contradictions=contradictions, stage=_derive_stage(claims)),
        removed_claims=len(state.claims) - len(claims),
        removed_contradictions=len(state.contradictions) - len(contradictions),
    )


def summarize_relationship(state: RelationshipState, *, limit: int = 12) -> tuple[str, ...]:
    """Return bounded active continuity data; disputed/superseded claims stay out."""
    if not isinstance(state, RelationshipState):
        raise ValidationError("relationship summary requires RelationshipState")
    limit = max(1, min(int(limit), 30))
    active = [claim for claim in state.claims if claim.status is RelationshipClaimStatus.ACTIVE]
    active.sort(key=lambda claim: (claim.explicit, claim.confidence, claim.last_observed_at), reverse=True)
    return tuple(
        f"{claim.kind.value}:{claim.subject}={claim.value} (confidence {claim.confidence:.2f}; evidence {claim.evidence_count})"
        for claim in active[:limit]
    )


def apply_relationship_to_soul(state: SoulState, **observation) -> tuple[SoulState, RelationshipUpdate]:
    if not isinstance(state, SoulState):
        raise ValidationError("relationship observation requires SoulState")
    update = observe_relationship(state.relationship, **observation)
    return replace(state, relationship=update.after), update


def _derive_stage(claims: Iterable[RelationshipClaim]) -> str:
    active = [claim for claim in claims if claim.status is RelationshipClaimStatus.ACTIVE]
    trust_markers = sum(claim.kind in (RelationshipKind.MILESTONE, RelationshipKind.TRUSTED_WORKFLOW) for claim in active)
    if len(active) >= 8 and trust_markers >= 2:
        return "trusted"
    if len(active) >= 3:
        return "familiar"
    return "new"


def _claim_id(kind: RelationshipKind, subject: str, value: str) -> str:
    raw = f"{kind.value}\0{subject.casefold()}\0{value.casefold()}"
    return "relationship-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _contradiction_id(kind: RelationshipKind, subject: str, claim_ids: tuple[str, ...]) -> str:
    raw = f"{kind.value}\0{subject.casefold()}\0{'|'.join(sorted(claim_ids))}"
    return "contradiction-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
