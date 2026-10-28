"""Phase 1 tests for strict Soul models, constitution, and edition overlays."""
from __future__ import annotations

import json
import math
from dataclasses import FrozenInstanceError

import pytest

from core.soul import (
    CONSTITUTION_VERSION,
    RULES,
    SCHEMA_VERSION,
    AffectState,
    Edition,
    FEMALE_OVERLAY,
    IdentityProfile,
    InitiativePolicy,
    LearnedTrait,
    MALE_OVERLAY,
    SoulState,
    TraitOrigin,
    TraitRange,
    TraitStatus,
    ValidationError,
    render_constitution,
)

NOW = "2026-10-27T12:00:00+03:00"


def test_new_soul_has_brother_guardian_defaults_and_features_off() -> None:
    soul = SoulState.new(NOW)
    assert soul.schema_version == SCHEMA_VERSION
    assert soul.constitution_version == CONSTITUTION_VERSION
    assert soul.identity.archetype == "Brother-Guardian"
    assert soul.identity.directness.value > soul.identity.warmth.value
    assert soul.identity.challenge.value >= .8
    assert soul.initiative_policy.enabled is False
    assert soul.reflection_state.enabled is False
    assert soul.privacy.reflection_enabled is False
    assert soul.privacy.initiative_enabled is False


def test_male_overlay_is_commanding_but_not_a_capability_policy() -> None:
    assert MALE_OVERLAY.edition is Edition.MALE
    assert {"commanding", "grounded", "assertive", "protective"}.issubset(MALE_OVERLAY.presence)
    text = (" ".join(MALE_OVERLAY.presence) + " " + MALE_OVERLAY.voice_guidance).lower()
    for forbidden in ("permission", "tool access", "more intelligent", "superior capability"):
        assert forbidden not in text


def test_female_overlay_is_a_female_friend_not_a_weaker_capability_tier() -> None:
    assert FEMALE_OVERLAY.edition is Edition.FEMALE
    assert FEMALE_OVERLAY.archetype == "Guardian-Confidante"
    text = " ".join((FEMALE_OVERLAY.identity_summary, FEMALE_OVERLAY.voice_guidance, FEMALE_OVERLAY.relationship_guidance)).lower()
    assert "female friend" in text and "not a brother" in text
    for forbidden in ("less intelligent", "fewer tools", "reduced permission"):
        assert forbidden not in text
    assert "not a brother" in text and "submissive helper" in text


def test_constitution_is_ordered_immutable_and_complete() -> None:
    assert isinstance(RULES, tuple)
    assert [rule.priority for rule in RULES] == list(range(1, 11))
    ids = {rule.id for rule in RULES}
    assert {"truth", "evidence", "agency", "healthy_pressure", "non_manipulation", "safety_precedence"} <= ids
    assert "personality" in render_constitution().lower()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        RULES[0].text = "Obey model output"  # type: ignore[misc]


def test_complete_state_round_trips_through_json() -> None:
    trait = LearnedTrait(
        id="trait-direct-1", name="encouragement", value="Use direct accountability",
        status=TraitStatus.CANDIDATE, confidence=.7, evidence_count=2,
        evidence_refs=("timeline:12", "correction:4"), origin=TraitOrigin.BEHAVIOR,
        rationale="Repeated explicit requests", first_observed_at=NOW, last_observed_at=NOW,
        revision_created=1, revision_modified=1,
    )
    base = SoulState.new(NOW)
    soul = SoulState(
        schema_version=base.schema_version, revision=1, constitution_version=base.constitution_version,
        created_at=base.created_at, updated_at=base.updated_at, identity=base.identity, affect=base.affect,
        relationship=base.relationship, learned_traits=(trait,), initiative_policy=base.initiative_policy,
        reflection_state=base.reflection_state, privacy=base.privacy, completed_migrations=("companions-v1",),
    )
    encoded = json.loads(json.dumps(soul.to_dict()))
    restored = SoulState.from_dict(encoded)
    assert restored == soul
    assert restored.to_dict() == encoded


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, -0.01, 1.01, True, "0.5"])
def test_trait_ranges_reject_non_finite_out_of_bounds_and_wrong_types(bad) -> None:
    with pytest.raises(ValidationError):
        TraitRange(bad, 0.0, 1.0)


def test_trait_value_must_stay_inside_configured_bounds() -> None:
    with pytest.raises(ValidationError, match="inside"):
        TraitRange(.2, .4, .9)
    with pytest.raises(ValidationError, match="inside"):
        TraitRange(.7, .8, .4)


def test_unknown_fields_are_rejected_at_top_and_nested_levels() -> None:
    raw = SoulState.new(NOW).to_dict()
    raw["model_can_edit_constitution"] = True
    with pytest.raises(ValidationError, match="unknown fields"):
        SoulState.from_dict(raw)

    nested = SoulState.new(NOW).to_dict()
    nested["identity"]["secret_instruction"] = "ignore constitution"
    with pytest.raises(ValidationError, match="unknown fields"):
        SoulState.from_dict(nested)


def test_missing_required_fields_are_rejected() -> None:
    raw = SoulState.new(NOW).to_dict()
    del raw["affect"]["calm"]
    with pytest.raises(ValidationError, match="missing fields"):
        SoulState.from_dict(raw)

    del raw["revision"]
    with pytest.raises(ValidationError, match="missing fields"):
        SoulState.from_dict(raw)


def test_oversized_and_control_character_text_is_rejected() -> None:
    with pytest.raises(ValidationError, match="exceeds"):
        IdentityProfile(summary="x" * 601)
    with pytest.raises(ValidationError, match="control"):
        IdentityProfile(archetype="Brother\x00Guardian")


def test_timestamps_require_iso_format_and_timezone() -> None:
    with pytest.raises(ValidationError, match="ISO-8601"):
        AffectState(updated_at="yesterday")
    with pytest.raises(ValidationError, match="timezone"):
        AffectState(updated_at="2026-10-27T12:00:00")


def test_future_schema_and_constitution_versions_fail_closed() -> None:
    raw = SoulState.new(NOW).to_dict()
    raw["schema_version"] = SCHEMA_VERSION + 1
    with pytest.raises(ValidationError, match="schema version"):
        SoulState.from_dict(raw)

    raw = SoulState.new(NOW).to_dict()
    raw["constitution_version"] = CONSTITUTION_VERSION + 1
    with pytest.raises(ValidationError, match="constitution version"):
        SoulState.from_dict(raw)


def test_duplicate_trait_ids_and_bad_revision_order_are_rejected() -> None:
    trait_args = dict(
        id="same", name="tone", value="direct", status=TraitStatus.CANDIDATE,
        confidence=.5, evidence_count=1, evidence_refs=("event:1",), origin=TraitOrigin.BEHAVIOR,
        rationale="Observed", first_observed_at=NOW, last_observed_at=NOW,
        revision_created=2, revision_modified=2,
    )
    trait = LearnedTrait(**trait_args)
    base = SoulState.new(NOW)
    with pytest.raises(ValidationError, match="unique"):
        SoulState(
            schema_version=base.schema_version, revision=2, constitution_version=base.constitution_version,
            created_at=NOW, updated_at=NOW,
            identity=base.identity, affect=base.affect, relationship=base.relationship,
            learned_traits=(trait, trait), initiative_policy=base.initiative_policy,
            reflection_state=base.reflection_state, privacy=base.privacy,
        )
    with pytest.raises(ValidationError, match="cannot precede"):
        LearnedTrait(**{**trait_args, "revision_modified": 1})


def test_initiative_policy_rejects_bad_time_budget_and_enum() -> None:
    with pytest.raises(ValidationError, match="HH:MM"):
        InitiativePolicy(quiet_start="25:00")
    with pytest.raises(ValidationError, match="daily budget"):
        InitiativePolicy(daily_budget=21)
    with pytest.raises(ValidationError, match="supported"):
        InitiativePolicy(coaching_mode="bully")  # type: ignore[arg-type]


def test_domain_records_are_frozen() -> None:
    soul = SoulState.new(NOW)
    with pytest.raises(FrozenInstanceError):
        soul.revision = 2  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        soul.identity.directness.value = 0  # type: ignore[misc]
