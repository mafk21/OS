"""Phase 10 restart-safe initiative policy tests."""
from dataclasses import replace
import pytest
from core.soul import (
    InitiativeCandidate, InitiativePolicy, InitiativeTopicState, SoulState,
    ValidationError, record_delivery, record_outcome, select_initiative, migrate_raw,
)

NOW = "2026-10-27T12:00:00+03:00"

def candidate(topic="goal:x", confidence=.8, value=.8, urgency=.7):
    return InitiativeCandidate(topic=topic, evidence_ref=f"evidence:{topic}", confidence=confidence,
        value=value, urgency=urgency, expires_at="2026-10-28T12:00:00+03:00", suggestion="Take the next step.")

def policy(**changes):
    return replace(InitiativePolicy(enabled=True, timezone="Asia/Riyadh", quiet_start="22:00", quiet_end="08:00", daily_date="2026-10-27"), **changes)

def test_quiet_hours_cross_midnight_and_daytime_selects():
    assert select_initiative(policy(), (candidate(),), now="2026-10-27T23:00:00+03:00").reason == "quiet_hours"
    assert select_initiative(policy(), (candidate(),), now=NOW).candidate is not None

def test_disabled_snooze_and_daily_budget_suppress():
    assert select_initiative(InitiativePolicy(), (candidate(),), now=NOW).reason == "disabled"
    assert select_initiative(policy(snooze_until="2026-10-27T13:00:00+03:00"), (candidate(),), now=NOW).reason == "snoozed"
    assert select_initiative(policy(interruptions_today=3), (candidate(),), now=NOW).reason == "daily_budget"

def test_low_confidence_expired_and_cooldown_are_ineligible():
    assert select_initiative(policy(), (candidate(confidence=.4),), now=NOW).candidate is None
    expired = replace(candidate(), expires_at="2026-10-27T11:00:00+03:00")
    assert select_initiative(policy(), (expired,), now=NOW).candidate is None
    recent = InitiativeTopicState("goal:x", last_suggested_at="2026-10-27T11:30:00+03:00", ignored_count=0, last_outcome="ignored")
    assert select_initiative(policy(topics=(recent,)), (candidate(),), now=NOW).candidate is None

def test_scoring_selects_highest_value_candidate():
    low = candidate("low", confidence=.6, value=.4, urgency=.4)
    high = candidate("high", confidence=.9, value=.9, urgency=.9)
    decision = select_initiative(policy(), (low, high), now=NOW)
    assert decision.candidate.topic == "high" and decision.score > .8

def test_delivery_persists_budget_and_outcomes_backoff_across_reconstruction():
    delivered = record_delivery(policy(), candidate(), now=NOW)
    assert delivered.interruptions_today == 1
    assert delivered.topics[0].last_outcome == "delivered"
    ignored = record_outcome(delivered, "goal:x", "ignored")
    assert ignored.topics[0].ignored_count == 1
    restored = ignored
    # Persisted timestamps, counts, and outcomes drive cooldown after reconstruction.
    assert select_initiative(restored, (candidate(),), now="2026-10-27T13:30:00+03:00").candidate is None
    assert select_initiative(restored, (candidate(),), now="2026-10-27T14:01:00+03:00").candidate is not None

def test_snooze_outcome_and_new_day_reset_budget():
    snoozed = record_outcome(policy(), "goal:x", "snoozed", snooze_until="2026-10-27T15:00:00+03:00")
    assert select_initiative(snoozed, (candidate(),), now=NOW).reason == "snoozed"
    old = policy(interruptions_today=3)
    assert select_initiative(old, (replace(candidate(), expires_at="2026-10-29T12:00:00+03:00"),), now="2026-10-28T12:00:00+03:00").candidate is not None

def test_invalid_timezone_and_outcome_fail_closed():
    with pytest.raises(ValidationError, match="timezone"):
        select_initiative(policy(timezone="Mars/Olympus"), (candidate(),), now=NOW)
    with pytest.raises(ValidationError, match="outcome"):
        record_outcome(policy(), "x", "nag")

def test_v3_migration_adds_restart_safe_policy_fields():
    raw = SoulState.new(NOW).to_dict(); raw["schema_version"] = 3
    for key in ("daily_date", "interruptions_today", "snooze_until", "topics"):
        raw["initiative_policy"].pop(key)
    result = migrate_raw(raw)
    assert result.applied == ("schema-v3-to-v4",)
    assert result.state.initiative_policy.interruptions_today == 0
    assert result.state.initiative_policy.topics == ()
