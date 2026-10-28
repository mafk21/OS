"""Pure, sequential Soul schema migrations and compatibility imports."""
from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Mapping

from .models import (
    SCHEMA_VERSION,
    IdentityProfile,
    LearnedTrait,
    SoulState,
    TraitOrigin,
    TraitRange,
    TraitStatus,
    ValidationError,
    _mapping,
    _strict,
    _text,
    _timestamp,
    utc_now_iso,
)

COMPANIONS_IMPORT_ID = "compat-companions-v1"


@dataclass(frozen=True, slots=True)
class MigrationResult:
    state: SoulState
    applied: tuple[str, ...] = ()


def migrate_raw(raw: Any) -> MigrationResult:
    """Migrate a raw Soul object one schema version at a time.

    The input is deep-copied and never mutated. Future versions fail closed.
    """
    source = copy.deepcopy(_mapping(raw, "soul state"))
    version_value = source.get("schema_version", source.get("version", 0))
    if isinstance(version_value, bool) or not isinstance(version_value, int):
        raise ValidationError("schema version must be an integer")
    if version_value < 0:
        raise ValidationError("schema version cannot be negative")
    if version_value > SCHEMA_VERSION:
        raise ValidationError(f"unsupported future schema version {version_value}")

    applied: list[str] = []
    working: dict[str, Any] = dict(source)
    while version_value < SCHEMA_VERSION:
        migration = _MIGRATIONS.get(version_value)
        if migration is None:
            raise ValidationError(f"no migration path from schema version {version_value}")
        working = migration(working)
        next_version = working.get("schema_version")
        if next_version != version_value + 1:
            raise ValidationError("schema migration did not advance exactly one version")
        applied.append(f"schema-v{version_value}-to-v{next_version}")
        version_value = next_version

    return MigrationResult(SoulState.from_dict(working), tuple(applied))


def _v0_to_v1(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Convert the unpublished prototype v0 shape into the strict v1 schema."""
    fields = {"version", "schema_version", "revision", "created_at", "updated_at", "identity"}
    _strict(raw, fields, "schema v0 state")
    stamp = _timestamp(raw.get("created_at") or utc_now_iso(), "schema v0 created_at")
    updated = _timestamp(raw.get("updated_at") or stamp, "schema v0 updated_at")
    revision = raw.get("revision", 0)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValidationError("schema v0 revision must be a non-negative integer")

    state = SoulState.new(stamp)
    old_identity = _mapping(raw.get("identity", {}), "schema v0 identity")
    identity_fields = {"archetype", "summary", "warmth", "humor", "formality", "directness", "challenge", "initiative"}
    _strict(old_identity, identity_fields, "schema v0 identity")
    defaults = state.identity

    def trait(name: str) -> TraitRange:
        current = getattr(defaults, name)
        value = old_identity.get(name, current.value)
        return TraitRange(value, current.minimum, current.maximum)

    identity = IdentityProfile(
        archetype=old_identity.get("archetype", defaults.archetype),
        summary=old_identity.get("summary", defaults.summary),
        warmth=trait("warmth"), humor=trait("humor"), formality=trait("formality"),
        directness=trait("directness"), challenge=trait("challenge"), initiative=trait("initiative"),
    )
    migrated = replace(
        state, revision=revision, created_at=stamp, updated_at=updated, identity=identity,
        completed_migrations=tuple((*state.completed_migrations, "schema-v0-to-v1")),
    ).to_dict()
    # Emit the historical v1 shape so the sequential engine must pass through
    # v1-to-v2 instead of skipping a migration.
    migrated["schema_version"] = 1
    for key in (
        "baseline_calm", "baseline_energy", "baseline_concern", "baseline_confidence",
        "baseline_curiosity", "baseline_rapport", "daily_delta", "daily_date",
    ):
        migrated["affect"].pop(key, None)
    migrated["relationship"].pop("claims", None)
    migrated["relationship"].pop("contradictions", None)
    for key in ("daily_date", "interruptions_today", "snooze_until", "topics"):
        migrated["initiative_policy"].pop(key, None)
    return migrated


def _v1_to_v2(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Add persisted affect baselines and per-day accumulation accounting."""
    working = copy.deepcopy(dict(raw))
    affect = _mapping(working.get("affect"), "schema v1 affect")
    old_fields = {"calm", "energy", "concern", "confidence", "curiosity", "rapport", "updated_at", "causes"}
    _strict(affect, old_fields, "schema v1 affect")
    missing = old_fields - set(affect)
    if missing:
        raise ValidationError(f"schema v1 affect is missing fields: {', '.join(sorted(missing))}")
    updated_at = _timestamp(affect["updated_at"], "schema v1 affect updated_at")
    updated_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date().isoformat()
    upgraded_affect = dict(affect)
    for name in ("calm", "energy", "concern", "confidence", "curiosity", "rapport"):
        upgraded_affect[f"baseline_{name}"] = affect[name]
    upgraded_affect["daily_delta"] = {
        "calm": 0.0, "energy": 0.0, "concern": 0.0,
        "confidence": 0.0, "curiosity": 0.0, "rapport": 0.0,
    }
    upgraded_affect["daily_date"] = updated_date
    working["affect"] = upgraded_affect
    working["schema_version"] = 2
    completed = working.get("completed_migrations", [])
    if not isinstance(completed, list):
        raise ValidationError("schema v1 completed_migrations must be a list")
    if "schema-v1-to-v2" not in completed:
        working["completed_migrations"] = [*completed, "schema-v1-to-v2"]
    return working


def _v2_to_v3(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Add typed evidence-backed relationship claims and contradictions."""
    working = copy.deepcopy(dict(raw))
    relationship = _mapping(working.get("relationship"), "schema v2 relationship")
    old_fields = {"stage", "rapport_evidence", "milestones", "trusted_workflows", "unresolved_commitments"}
    _strict(relationship, old_fields, "schema v2 relationship")
    missing = old_fields - set(relationship)
    if missing:
        raise ValidationError(f"schema v2 relationship is missing fields: {', '.join(sorted(missing))}")
    working["relationship"] = {**relationship, "claims": [], "contradictions": []}
    working["schema_version"] = 3
    completed = working.get("completed_migrations", [])
    if not isinstance(completed, list):
        raise ValidationError("schema v2 completed_migrations must be a list")
    if "schema-v2-to-v3" not in completed:
        working["completed_migrations"] = [*completed, "schema-v2-to-v3"]
    return working


def _v3_to_v4(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Persist restart-safe initiative budget, snooze, and topic outcomes."""
    working = copy.deepcopy(dict(raw))
    policy = _mapping(working.get("initiative_policy"), "schema v3 initiative policy")
    old_fields = {"enabled", "timezone", "quiet_start", "quiet_end", "daily_budget", "coaching_mode"}
    _strict(policy, old_fields, "schema v3 initiative policy")
    missing = old_fields - set(policy)
    if missing:
        raise ValidationError(f"schema v3 initiative policy is missing fields: {', '.join(sorted(missing))}")
    updated = _timestamp(working.get("updated_at"), "schema v3 updated_at")
    day = datetime.fromisoformat(updated.replace("Z", "+00:00")).date().isoformat()
    working["initiative_policy"] = {**policy, "daily_date": day, "interruptions_today": 0, "snooze_until": None, "topics": []}
    working["schema_version"] = 4
    completed = working.get("completed_migrations", [])
    if not isinstance(completed, list):
        raise ValidationError("schema v3 completed_migrations must be a list")
    working["completed_migrations"] = [*completed, "schema-v3-to-v4"] if "schema-v3-to-v4" not in completed else completed
    return working


_MIGRATIONS = {0: _v0_to_v1, 1: _v1_to_v2, 2: _v2_to_v3, 3: _v3_to_v4}


def import_companion_compatibility(
    state: SoulState,
    companions_raw: Any,
    *,
    now: str | None = None,
) -> MigrationResult:
    """Import existing behavior interview/rules exactly once.

    Existing companion data is not modified or deleted. Deterministic IDs and a
    completed migration marker make retries safe even if a caller reuses the
    pre-import state after an interrupted write.
    """
    if not isinstance(state, SoulState):
        raise ValidationError("companion import requires a valid SoulState")
    if COMPANIONS_IMPORT_ID in state.completed_migrations:
        return MigrationResult(state, ())

    raw = _mapping(companions_raw, "companions compatibility state")
    allowed = {"active_companion_id", "interview", "learned_rules", "companions", "theme"}
    _strict(raw, allowed, "companions compatibility state")
    interview = raw.get("interview", {})
    rules = raw.get("learned_rules", [])
    if not isinstance(interview, Mapping):
        raise ValidationError("companions interview must be an object")
    if not isinstance(rules, list):
        raise ValidationError("companions learned_rules must be a list")
    if len(interview) > 30 or len(rules) > 100:
        raise ValidationError("companions compatibility data exceeds import limits")

    stamp = _timestamp(now or utc_now_iso(), "compatibility import timestamp")
    by_id = {trait.id: trait for trait in state.learned_traits}

    for key in sorted(interview, key=str):
        clean_key = _text(str(key), "interview key", maximum=80)
        value = _text(interview[key], f"interview {clean_key}", maximum=600)
        evidence = f"companions:interview:{clean_key}"
        trait = _compat_trait(
            source_key=evidence, name=f"behavior_{clean_key}", value=value,
            evidence_ref=evidence, confidence=.98,
            rationale="Imported from an explicit behavior interview answer.", stamp=stamp,
            revision=state.revision,
        )
        by_id.setdefault(trait.id, trait)

    for index, record in enumerate(rules):
        item = _mapping(record, f"learned rule {index}")
        _strict(item, {"id", "rule", "ts"}, f"learned rule {index}")
        rule = _text(item.get("rule"), f"learned rule {index} text", maximum=600)
        source_id = _text(str(item.get("id") or f"index-{index}"), "learned rule ID", maximum=80)
        evidence = f"companions:rule:{source_id}"
        trait = _compat_trait(
            source_key=evidence, name="communication_rule", value=rule,
            evidence_ref=evidence, confidence=.92,
            rationale="Imported from an existing adaptive behavior rule.", stamp=stamp,
            revision=state.revision,
        )
        by_id.setdefault(trait.id, trait)

    completed = tuple((*state.completed_migrations, COMPANIONS_IMPORT_ID))
    imported = replace(state, learned_traits=tuple(by_id.values()), completed_migrations=completed)
    # Re-parse to enforce every size, enum, timestamp, and uniqueness invariant.
    imported = SoulState.from_dict(imported.to_dict())
    return MigrationResult(imported, (COMPANIONS_IMPORT_ID,))


def _compat_trait(
    *, source_key: str, name: str, value: str, evidence_ref: str,
    confidence: float, rationale: str, stamp: str, revision: int,
) -> LearnedTrait:
    digest = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:16]
    return LearnedTrait(
        id=f"compat-{digest}", name=name, value=value, status=TraitStatus.ACTIVE,
        confidence=confidence, evidence_count=1, evidence_refs=(evidence_ref,),
        origin=TraitOrigin.MIGRATION, rationale=rationale,
        first_observed_at=stamp, last_observed_at=stamp,
        revision_created=revision, revision_modified=revision,
    )
