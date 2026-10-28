"""Restart-safe initiative filtering, scoring, and outcome accounting."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import InitiativePolicy, InitiativeTopicState, ValidationError, _text, _timestamp


@dataclass(frozen=True, slots=True)
class InitiativeCandidate:
    topic: str
    evidence_ref: str
    confidence: float
    value: float
    urgency: float
    expires_at: str
    suggestion: str

    def __post_init__(self):
        for name, maximum in (("topic", 160), ("evidence_ref", 160), ("suggestion", 500)):
            object.__setattr__(self, name, _text(getattr(self, name), name, maximum=maximum))
        for name in ("confidence", "value", "urgency"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                raise ValidationError(f"initiative {name} must be between 0 and 1")
            object.__setattr__(self, name, float(value))
        object.__setattr__(self, "expires_at", _timestamp(self.expires_at, "initiative expiry"))


@dataclass(frozen=True, slots=True)
class InitiativeDecision:
    candidate: InitiativeCandidate | None
    reason: str
    score: float = 0.0


def select_initiative(policy: InitiativePolicy, candidates: tuple[InitiativeCandidate, ...], *, now: str) -> InitiativeDecision:
    if not isinstance(policy, InitiativePolicy):
        raise ValidationError("initiative selection requires InitiativePolicy")
    current = datetime.fromisoformat(_timestamp(now, "initiative now").replace("Z", "+00:00"))
    if not policy.enabled:
        return InitiativeDecision(None, "disabled")
    local = _local_time(current, policy.timezone)
    if _quiet(local, policy.quiet_start, policy.quiet_end):
        return InitiativeDecision(None, "quiet_hours")
    if policy.snooze_until and current < datetime.fromisoformat(policy.snooze_until.replace("Z", "+00:00")):
        return InitiativeDecision(None, "snoozed")
    count = policy.interruptions_today if policy.daily_date == local.date().isoformat() else 0
    if count >= policy.daily_budget:
        return InitiativeDecision(None, "daily_budget")
    topics = {item.topic: item for item in policy.topics}
    eligible = []
    for candidate in candidates:
        expiry = datetime.fromisoformat(candidate.expires_at.replace("Z", "+00:00"))
        if expiry <= current or candidate.confidence < .55:
            continue
        previous = topics.get(candidate.topic)
        if previous and previous.last_suggested_at:
            last = datetime.fromisoformat(previous.last_suggested_at.replace("Z", "+00:00"))
            cooldown = min(24 * 3600, 3600 * (2 ** previous.ignored_count))
            if (current - last).total_seconds() < cooldown:
                continue
        score = .40 * candidate.value + .35 * candidate.urgency + .25 * candidate.confidence
        eligible.append((score, candidate))
    if not eligible:
        return InitiativeDecision(None, "no_eligible_candidate")
    score, candidate = max(eligible, key=lambda item: (item[0], item[1].topic))
    return InitiativeDecision(candidate, "selected", score)


def record_delivery(policy: InitiativePolicy, candidate: InitiativeCandidate, *, now: str) -> InitiativePolicy:
    current = datetime.fromisoformat(_timestamp(now, "initiative delivery time").replace("Z", "+00:00"))
    local = _local_time(current, policy.timezone)
    count = policy.interruptions_today if policy.daily_date == local.date().isoformat() else 0
    topics = {item.topic: item for item in policy.topics}
    previous = topics.get(candidate.topic)
    topics[candidate.topic] = InitiativeTopicState(
        topic=candidate.topic, last_suggested_at=now,
        ignored_count=previous.ignored_count if previous else 0, last_outcome="delivered",
    )
    return replace(policy, daily_date=local.date().isoformat(), interruptions_today=min(20, count + 1), topics=tuple(topics.values())[-100:])


def record_outcome(policy: InitiativePolicy, topic: str, outcome: str, *, snooze_until: str | None = None) -> InitiativePolicy:
    clean_topic = _text(topic, "initiative topic", maximum=160)
    if outcome not in {"accepted", "ignored", "dismissed", "snoozed", "completed"}:
        raise ValidationError("unsupported initiative outcome")
    topics = {item.topic: item for item in policy.topics}
    previous = topics.get(clean_topic) or InitiativeTopicState(clean_topic)
    ignored = min(20, previous.ignored_count + 1) if outcome in {"ignored", "dismissed"} else 0
    topics[clean_topic] = replace(previous, ignored_count=ignored, last_outcome=outcome)
    snooze = _timestamp(snooze_until, "initiative snooze", optional=True) if outcome == "snoozed" else policy.snooze_until
    return replace(policy, topics=tuple(topics.values())[-100:], snooze_until=snooze)


def _local_time(current: datetime, timezone_name: str) -> datetime:
    if timezone_name == "local":
        return current.astimezone()
    try:
        return current.astimezone(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError as exc:
        raise ValidationError("unknown initiative timezone") from exc


def _quiet(local: datetime, start: str, end: str) -> bool:
    minute = local.hour * 60 + local.minute
    sh, sm = map(int, start.split(":")); eh, em = map(int, end.split(":"))
    a, b = sh * 60 + sm, eh * 60 + em
    if a == b:
        return False
    return minute >= a or minute < b if a > b else a <= minute < b
