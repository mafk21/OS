"""Strict typed domain model for the persistent JARVIS Soul.

This module performs no file I/O and makes no provider calls. It is the schema
boundary used later by persistence, reflection, context, and Studio layers.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from .constitution import CONSTITUTION_VERSION

SCHEMA_VERSION = 3
MAX_SHORT_TEXT = 160
MAX_TEXT = 600
MAX_LIST_ITEMS = 100


class ValidationError(ValueError):
    """Raised when untrusted Soul data violates the domain schema."""


class Edition(str, Enum):
    MALE = "male"
    FEMALE = "female"


class TraitStatus(str, Enum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class TraitOrigin(str, Enum):
    EXPLICIT_USER = "explicit_user"
    BEHAVIOR = "behavior"
    REFLECTION = "reflection"
    MIGRATION = "migration"
    SYSTEM = "system"


class CoachingMode(str, Enum):
    SUPPORT = "support"
    CHALLENGE = "challenge"
    ACCOUNTABILITY = "accountability"
    RECOVERY = "recovery"


class RelationshipKind(str, Enum):
    PREFERENCE = "preference"
    CORRECTION = "correction"
    MILESTONE = "milestone"
    TRUSTED_WORKFLOW = "trusted_workflow"
    SHARED_REFERENCE = "shared_reference"


class RelationshipClaimStatus(str, Enum):
    ACTIVE = "active"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"


class Sensitivity(str, Enum):
    NORMAL = "normal"
    SENSITIVE = "sensitive"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{label} must be an object")
    return value


def _strict(data: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValidationError(f"{label} contains unknown fields: {', '.join(sorted(map(str, unknown)))}")


def _text(value: Any, label: str, *, maximum: int = MAX_TEXT, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{label} must be text")
    clean = value.strip()
    if not clean and not allow_empty:
        raise ValidationError(f"{label} cannot be empty")
    if len(clean) > maximum:
        raise ValidationError(f"{label} exceeds {maximum} characters")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in clean):
        raise ValidationError(f"{label} contains control characters")
    return clean


def _number(value: Any, label: str, *, minimum: float = 0.0, maximum: float = 1.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValidationError(f"{label} must be finite and between {minimum} and {maximum}")
    return result


def _integer(value: Any, label: str, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValidationError(f"{label} must be an integer between {minimum} and {maximum}")
    return value


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"{label} must be true or false")
    return value


def _timestamp(value: Any, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    text = _text(value, label, maximum=40)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{label} must include a timezone")
    return text


def _enum(cls: type[Enum], value: Any, label: str):
    try:
        return cls(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label} is not a supported value") from exc


def _text_list(value: Any, label: str, *, maximum: int = MAX_LIST_ITEMS) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{label} must be a list")
    if len(value) > maximum:
        raise ValidationError(f"{label} exceeds {maximum} entries")
    return tuple(_text(item, f"{label} item", maximum=MAX_SHORT_TEXT) for item in value)


@dataclass(frozen=True, slots=True)
class TraitRange:
    value: float
    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        for name in ("value", "minimum", "maximum"):
            object.__setattr__(self, name, _number(getattr(self, name), name))
        if self.minimum > self.maximum or not self.minimum <= self.value <= self.maximum:
            raise ValidationError("trait value must remain inside its configured range")

    @classmethod
    def from_dict(cls, raw: Any) -> "TraitRange":
        data = _mapping(raw, "trait range")
        _strict(data, {"value", "minimum", "maximum"}, "trait range")
        return cls(data.get("value"), data.get("minimum"), data.get("maximum"))


@dataclass(frozen=True, slots=True)
class IdentityProfile:
    archetype: str = "Brother-Guardian"
    summary: str = "A loyal, grounded brother who tells the truth, stays through mistakes, and pushes the user toward declared goals."
    warmth: TraitRange = field(default_factory=lambda: TraitRange(.68, .35, .90))
    humor: TraitRange = field(default_factory=lambda: TraitRange(.28, .05, .60))
    formality: TraitRange = field(default_factory=lambda: TraitRange(.32, .10, .70))
    directness: TraitRange = field(default_factory=lambda: TraitRange(.82, .55, .98))
    challenge: TraitRange = field(default_factory=lambda: TraitRange(.84, .50, .98))
    initiative: TraitRange = field(default_factory=lambda: TraitRange(.70, .30, .90))

    def __post_init__(self) -> None:
        object.__setattr__(self, "archetype", _text(self.archetype, "archetype", maximum=80))
        object.__setattr__(self, "summary", _text(self.summary, "identity summary", maximum=MAX_TEXT))
        for name in ("warmth", "humor", "formality", "directness", "challenge", "initiative"):
            if not isinstance(getattr(self, name), TraitRange):
                raise ValidationError(f"identity {name} must be a trait range")

    @classmethod
    def from_dict(cls, raw: Any) -> "IdentityProfile":
        data = _mapping(raw, "identity")
        fields = {"archetype", "summary", "warmth", "humor", "formality", "directness", "challenge", "initiative"}
        _strict(data, fields, "identity")
        required = fields - {"archetype", "summary"}
        missing = required - set(data)
        if missing:
            raise ValidationError(f"identity is missing fields: {', '.join(sorted(missing))}")
        return cls(
            archetype=data.get("archetype", "Brother-Guardian"), summary=data.get("summary", cls().summary),
            warmth=TraitRange.from_dict(data["warmth"]), humor=TraitRange.from_dict(data["humor"]),
            formality=TraitRange.from_dict(data["formality"]), directness=TraitRange.from_dict(data["directness"]),
            challenge=TraitRange.from_dict(data["challenge"]), initiative=TraitRange.from_dict(data["initiative"]),
        )


@dataclass(frozen=True, slots=True)
class EditionOverlay:
    edition: Edition
    label: str
    presence: tuple[str, ...]
    voice_guidance: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "edition", _enum(Edition, self.edition, "edition"))
        object.__setattr__(self, "label", _text(self.label, "edition label", maximum=80))
        object.__setattr__(self, "presence", _text_list(self.presence, "edition presence", maximum=12))
        object.__setattr__(self, "voice_guidance", _text(self.voice_guidance, "voice guidance", maximum=MAX_TEXT))


MALE_OVERLAY = EditionOverlay(
    edition=Edition.MALE,
    label="Male — Commanding Brother-Guardian",
    presence=("commanding", "grounded", "assertive", "protective", "steady", "concise", "restrained dry humor"),
    voice_guidance=(
        "Use calm authority and grounded, decisive language. Challenge excuses directly without hostility, "
        "remain beside the user after mistakes, and show warmth through dependable action rather than excessive reassurance."
    ),
)

FEMALE_OVERLAY = EditionOverlay(
    edition=Edition.FEMALE,
    label="Female — Composed Brother-Guardian",
    presence=("composed", "articulate", "steady", "protective", "direct"),
    voice_guidance="Use composed, articulate, steady language while preserving the same constitution, continuity, and capability.",
)

EDITION_OVERLAYS = {Edition.MALE: MALE_OVERLAY, Edition.FEMALE: FEMALE_OVERLAY}


@dataclass(frozen=True, slots=True)
class AffectDelta:
    calm: float = 0.0
    energy: float = 0.0
    concern: float = 0.0
    confidence: float = 0.0
    curiosity: float = 0.0
    rapport: float = 0.0

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValidationError(f"affect delta {name} must be a number")
            value = float(value)
            if not math.isfinite(value) or not -1.0 <= value <= 1.0:
                raise ValidationError(f"affect delta {name} must be finite and between -1.0 and 1.0")
            object.__setattr__(self, name, value)

    @classmethod
    def from_dict(cls, raw: Any) -> "AffectDelta":
        data = _mapping(raw, "affect daily delta")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "affect daily delta")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"affect daily delta is missing fields: {', '.join(sorted(missing))}")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class AffectState:
    calm: float = .78
    energy: float = .58
    concern: float = .18
    confidence: float = .72
    curiosity: float = .62
    rapport: float = .45
    baseline_calm: float = .78
    baseline_energy: float = .58
    baseline_concern: float = .18
    baseline_confidence: float = .72
    baseline_curiosity: float = .62
    baseline_rapport: float = .45
    daily_delta: AffectDelta = field(default_factory=AffectDelta)
    daily_date: str = field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
    updated_at: str = field(default_factory=utc_now_iso)
    causes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        dimensions = ("calm", "energy", "concern", "confidence", "curiosity", "rapport")
        for name in dimensions:
            object.__setattr__(self, name, _number(getattr(self, name), f"affect {name}"))
            baseline_name = f"baseline_{name}"
            object.__setattr__(self, baseline_name, _number(getattr(self, baseline_name), f"affect {baseline_name}"))
        if not isinstance(self.daily_delta, AffectDelta):
            raise ValidationError("affect daily_delta has the wrong type")
        daily_date = _text(self.daily_date, "affect daily_date", maximum=10)
        try:
            datetime.strptime(daily_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValidationError("affect daily_date must use YYYY-MM-DD") from exc
        object.__setattr__(self, "daily_date", daily_date)
        object.__setattr__(self, "updated_at", _timestamp(self.updated_at, "affect updated_at"))
        object.__setattr__(self, "causes", _text_list(self.causes, "affect causes", maximum=12))

    @classmethod
    def from_dict(cls, raw: Any) -> "AffectState":
        data = _mapping(raw, "affect")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "affect")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"affect is missing fields: {', '.join(sorted(missing))}")
        return cls(**{
            **data,
            "daily_delta": AffectDelta.from_dict(data["daily_delta"]),
            "causes": tuple(data["causes"]),
        })


@dataclass(frozen=True, slots=True)
class LearnedTrait:
    id: str
    name: str
    value: str
    status: TraitStatus
    confidence: float
    evidence_count: int
    evidence_refs: tuple[str, ...]
    origin: TraitOrigin
    rationale: str
    first_observed_at: str
    last_observed_at: str
    revision_created: int
    revision_modified: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "trait id", maximum=80))
        object.__setattr__(self, "name", _text(self.name, "trait name", maximum=80))
        object.__setattr__(self, "value", _text(self.value, "trait value", maximum=MAX_TEXT))
        object.__setattr__(self, "status", _enum(TraitStatus, self.status, "trait status"))
        object.__setattr__(self, "confidence", _number(self.confidence, "trait confidence"))
        object.__setattr__(self, "evidence_count", _integer(self.evidence_count, "evidence count", maximum=1_000_000))
        object.__setattr__(self, "evidence_refs", _text_list(self.evidence_refs, "evidence refs"))
        object.__setattr__(self, "origin", _enum(TraitOrigin, self.origin, "trait origin"))
        object.__setattr__(self, "rationale", _text(self.rationale, "trait rationale", maximum=MAX_TEXT))
        object.__setattr__(self, "first_observed_at", _timestamp(self.first_observed_at, "first observed"))
        object.__setattr__(self, "last_observed_at", _timestamp(self.last_observed_at, "last observed"))
        object.__setattr__(self, "revision_created", _integer(self.revision_created, "revision created"))
        object.__setattr__(self, "revision_modified", _integer(self.revision_modified, "revision modified"))
        if self.evidence_count < len(self.evidence_refs):
            raise ValidationError("evidence count cannot be smaller than evidence references")
        if self.revision_modified < self.revision_created:
            raise ValidationError("modified revision cannot precede created revision")

    @classmethod
    def from_dict(cls, raw: Any) -> "LearnedTrait":
        data = _mapping(raw, "learned trait")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "learned trait")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"learned trait is missing fields: {', '.join(sorted(missing))}")
        return cls(**{**data, "evidence_refs": tuple(data["evidence_refs"])})


@dataclass(frozen=True, slots=True)
class RelationshipClaim:
    id: str
    kind: RelationshipKind
    subject: str
    value: str
    status: RelationshipClaimStatus
    sensitivity: Sensitivity
    explicit: bool
    confidence: float
    evidence_count: int
    evidence_refs: tuple[str, ...]
    first_observed_at: str
    last_observed_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "relationship claim id", maximum=80))
        object.__setattr__(self, "kind", _enum(RelationshipKind, self.kind, "relationship kind"))
        object.__setattr__(self, "subject", _text(self.subject, "relationship subject", maximum=120))
        object.__setattr__(self, "value", _text(self.value, "relationship value", maximum=600))
        object.__setattr__(self, "status", _enum(RelationshipClaimStatus, self.status, "relationship claim status"))
        object.__setattr__(self, "sensitivity", _enum(Sensitivity, self.sensitivity, "relationship sensitivity"))
        object.__setattr__(self, "explicit", _boolean(self.explicit, "relationship explicit"))
        object.__setattr__(self, "confidence", _number(self.confidence, "relationship confidence"))
        object.__setattr__(self, "evidence_count", _integer(self.evidence_count, "relationship evidence count", maximum=1_000_000))
        object.__setattr__(self, "evidence_refs", _text_list(self.evidence_refs, "relationship evidence refs", maximum=20))
        object.__setattr__(self, "first_observed_at", _timestamp(self.first_observed_at, "relationship first observed"))
        object.__setattr__(self, "last_observed_at", _timestamp(self.last_observed_at, "relationship last observed"))
        if self.sensitivity is Sensitivity.SENSITIVE and not self.explicit:
            raise ValidationError("sensitive relationship claims require explicit user evidence")
        if self.evidence_count < len(self.evidence_refs):
            raise ValidationError("relationship evidence count cannot be smaller than evidence references")

    @classmethod
    def from_dict(cls, raw: Any) -> "RelationshipClaim":
        data = _mapping(raw, "relationship claim")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "relationship claim")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"relationship claim is missing fields: {', '.join(sorted(missing))}")
        return cls(**{**data, "evidence_refs": tuple(data["evidence_refs"])})


@dataclass(frozen=True, slots=True)
class RelationshipContradiction:
    id: str
    subject: str
    claim_ids: tuple[str, ...]
    created_at: str
    resolution: str = "unresolved"

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "contradiction id", maximum=80))
        object.__setattr__(self, "subject", _text(self.subject, "contradiction subject", maximum=120))
        object.__setattr__(self, "claim_ids", _text_list(self.claim_ids, "contradiction claim ids", maximum=10))
        if len(self.claim_ids) < 2:
            raise ValidationError("relationship contradiction requires at least two claims")
        object.__setattr__(self, "created_at", _timestamp(self.created_at, "contradiction created_at"))
        object.__setattr__(self, "resolution", _text(self.resolution, "contradiction resolution", maximum=80))

    @classmethod
    def from_dict(cls, raw: Any) -> "RelationshipContradiction":
        data = _mapping(raw, "relationship contradiction")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "relationship contradiction")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"relationship contradiction is missing fields: {', '.join(sorted(missing))}")
        return cls(**{**data, "claim_ids": tuple(data["claim_ids"])})


@dataclass(frozen=True, slots=True)
class RelationshipState:
    stage: str = "new"
    rapport_evidence: tuple[str, ...] = ()
    milestones: tuple[str, ...] = ()
    trusted_workflows: tuple[str, ...] = ()
    unresolved_commitments: tuple[str, ...] = ()
    claims: tuple[RelationshipClaim, ...] = ()
    contradictions: tuple[RelationshipContradiction, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage", _text(self.stage, "relationship stage", maximum=40))
        for name in ("rapport_evidence", "milestones", "trusted_workflows", "unresolved_commitments"):
            object.__setattr__(self, name, _text_list(getattr(self, name), name))
        if not isinstance(self.claims, tuple) or len(self.claims) > 200 or any(not isinstance(x, RelationshipClaim) for x in self.claims):
            raise ValidationError("relationship claims must be a bounded typed tuple")
        if not isinstance(self.contradictions, tuple) or len(self.contradictions) > 100 or any(not isinstance(x, RelationshipContradiction) for x in self.contradictions):
            raise ValidationError("relationship contradictions must be a bounded typed tuple")
        claim_ids = [claim.id for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValidationError("relationship claim IDs must be unique")
        contradiction_ids = [item.id for item in self.contradictions]
        if len(contradiction_ids) != len(set(contradiction_ids)):
            raise ValidationError("relationship contradiction IDs must be unique")

    @classmethod
    def from_dict(cls, raw: Any) -> "RelationshipState":
        data = _mapping(raw, "relationship")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "relationship")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"relationship is missing fields: {', '.join(sorted(missing))}")
        return cls(
            stage=data["stage"],
            rapport_evidence=tuple(data["rapport_evidence"]),
            milestones=tuple(data["milestones"]),
            trusted_workflows=tuple(data["trusted_workflows"]),
            unresolved_commitments=tuple(data["unresolved_commitments"]),
            claims=tuple(RelationshipClaim.from_dict(x) for x in data["claims"]),
            contradictions=tuple(RelationshipContradiction.from_dict(x) for x in data["contradictions"]),
        )


@dataclass(frozen=True, slots=True)
class InitiativePolicy:
    enabled: bool = False
    timezone: str = "local"
    quiet_start: str = "22:00"
    quiet_end: str = "08:00"
    daily_budget: int = 3
    coaching_mode: CoachingMode = CoachingMode.ACCOUNTABILITY

    def __post_init__(self) -> None:
        object.__setattr__(self, "enabled", _boolean(self.enabled, "initiative enabled"))
        object.__setattr__(self, "timezone", _text(self.timezone, "timezone", maximum=80))
        for name in ("quiet_start", "quiet_end"):
            val = _text(getattr(self, name), name, maximum=5)
            try:
                datetime.strptime(val, "%H:%M")
            except ValueError as exc:
                raise ValidationError(f"{name} must use 24-hour HH:MM") from exc
            object.__setattr__(self, name, val)
        object.__setattr__(self, "daily_budget", _integer(self.daily_budget, "daily budget", maximum=20))
        object.__setattr__(self, "coaching_mode", _enum(CoachingMode, self.coaching_mode, "coaching mode"))

    @classmethod
    def from_dict(cls, raw: Any) -> "InitiativePolicy":
        data = _mapping(raw, "initiative policy")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "initiative policy")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class ReflectionState:
    enabled: bool = False
    last_run_at: str | None = None
    evidence_cursor: str = ""
    consecutive_failures: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "enabled", _boolean(self.enabled, "reflection enabled"))
        object.__setattr__(self, "last_run_at", _timestamp(self.last_run_at, "reflection last run", optional=True))
        object.__setattr__(self, "evidence_cursor", _text(self.evidence_cursor, "evidence cursor", maximum=120, allow_empty=True))
        object.__setattr__(self, "consecutive_failures", _integer(self.consecutive_failures, "reflection failures", maximum=1000))

    @classmethod
    def from_dict(cls, raw: Any) -> "ReflectionState":
        data = _mapping(raw, "reflection state")
        _strict(data, set(cls.__dataclass_fields__), "reflection state")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    relationship_learning: bool = True
    affect_enabled: bool = True
    reflection_enabled: bool = False
    initiative_enabled: bool = False

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, _boolean(getattr(self, name), f"privacy {name}"))

    @classmethod
    def from_dict(cls, raw: Any) -> "PrivacyPolicy":
        data = _mapping(raw, "privacy policy")
        _strict(data, set(cls.__dataclass_fields__), "privacy policy")
        return cls(**data)


@dataclass(frozen=True, slots=True)
class SoulState:
    schema_version: int
    revision: int
    constitution_version: int
    created_at: str
    updated_at: str
    identity: IdentityProfile
    affect: AffectState
    relationship: RelationshipState
    learned_traits: tuple[LearnedTrait, ...]
    initiative_policy: InitiativePolicy
    reflection_state: ReflectionState
    privacy: PrivacyPolicy
    completed_migrations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _integer(self.schema_version, "schema version", minimum=1, maximum=SCHEMA_VERSION))
        if self.schema_version != SCHEMA_VERSION:
            raise ValidationError(f"unsupported schema version {self.schema_version}")
        object.__setattr__(self, "revision", _integer(self.revision, "revision"))
        object.__setattr__(self, "constitution_version", _integer(self.constitution_version, "constitution version", minimum=1))
        if self.constitution_version != CONSTITUTION_VERSION:
            raise ValidationError(f"unsupported constitution version {self.constitution_version}")
        object.__setattr__(self, "created_at", _timestamp(self.created_at, "created_at"))
        object.__setattr__(self, "updated_at", _timestamp(self.updated_at, "updated_at"))
        for name, cls in (("identity", IdentityProfile), ("affect", AffectState), ("relationship", RelationshipState),
                          ("initiative_policy", InitiativePolicy), ("reflection_state", ReflectionState), ("privacy", PrivacyPolicy)):
            if not isinstance(getattr(self, name), cls):
                raise ValidationError(f"{name} has the wrong type")
        if not isinstance(self.learned_traits, tuple) or len(self.learned_traits) > MAX_LIST_ITEMS:
            raise ValidationError("learned traits must be a bounded tuple")
        if any(not isinstance(item, LearnedTrait) for item in self.learned_traits):
            raise ValidationError("learned traits contains an invalid item")
        ids = [item.id for item in self.learned_traits]
        if len(ids) != len(set(ids)):
            raise ValidationError("learned trait IDs must be unique")
        object.__setattr__(self, "completed_migrations", _text_list(self.completed_migrations, "completed migrations"))

    @classmethod
    def new(cls, now: str | None = None) -> "SoulState":
        stamp = _timestamp(now or utc_now_iso(), "initial timestamp")
        return cls(
            schema_version=SCHEMA_VERSION, revision=0, constitution_version=CONSTITUTION_VERSION,
            created_at=stamp, updated_at=stamp, identity=IdentityProfile(),
            affect=AffectState(updated_at=stamp, daily_date=datetime.fromisoformat(stamp.replace("Z", "+00:00")).date().isoformat()),
            relationship=RelationshipState(), learned_traits=(), initiative_policy=InitiativePolicy(),
            reflection_state=ReflectionState(), privacy=PrivacyPolicy(), completed_migrations=(),
        )

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))

    @classmethod
    def from_dict(cls, raw: Any) -> "SoulState":
        data = _mapping(raw, "soul state")
        fields = set(cls.__dataclass_fields__)
        _strict(data, fields, "soul state")
        missing = fields - set(data)
        if missing:
            raise ValidationError(f"soul state is missing fields: {', '.join(sorted(missing))}")
        traits_raw = data["learned_traits"]
        if not isinstance(traits_raw, list):
            raise ValidationError("learned_traits must be a list")
        return cls(
            schema_version=data["schema_version"], revision=data["revision"],
            constitution_version=data["constitution_version"], created_at=data["created_at"], updated_at=data["updated_at"],
            identity=IdentityProfile.from_dict(data["identity"]), affect=AffectState.from_dict(data["affect"]),
            relationship=RelationshipState.from_dict(data["relationship"]),
            learned_traits=tuple(LearnedTrait.from_dict(item) for item in traits_raw),
            initiative_policy=InitiativePolicy.from_dict(data["initiative_policy"]),
            reflection_state=ReflectionState.from_dict(data["reflection_state"]),
            privacy=PrivacyPolicy.from_dict(data["privacy"]),
            completed_migrations=_text_list(data["completed_migrations"], "completed migrations"),
        )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value
