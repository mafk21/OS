"""Read-only commitment projection and bounded coaching policy.

Authoritative task, project, reminder, and goal systems remain external. This
module never executes, completes, retries, cancels, or rewrites them.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Mapping

from .models import CoachingMode, ValidationError, _text, _timestamp


class CommitmentSource(str, Enum):
    LONG_TASK = "long_task"
    PROJECT = "project"
    REMINDER = "reminder"
    GOAL = "goal"


class CommitmentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class CommitmentProjection:
    id: str
    source: CommitmentSource
    title: str
    status: CommitmentStatus
    verified_completion: bool = False
    evidence_ref: str = ""
    deadline: str | None = None
    high_value: bool = False
    avoidance_signals: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _text(self.id, "commitment id", maximum=160))
        try:
            object.__setattr__(self, "source", CommitmentSource(self.source))
            object.__setattr__(self, "status", CommitmentStatus(self.status))
        except (TypeError, ValueError) as exc:
            raise ValidationError("unsupported commitment source or status") from exc
        object.__setattr__(self, "title", _text(self.title, "commitment title", maximum=240))
        if not isinstance(self.verified_completion, bool) or not isinstance(self.high_value, bool):
            raise ValidationError("commitment flags must be boolean")
        object.__setattr__(self, "evidence_ref", _text(self.evidence_ref, "commitment evidence", maximum=200, allow_empty=True))
        if self.deadline is not None:
            object.__setattr__(self, "deadline", _timestamp(self.deadline, "commitment deadline"))
        if isinstance(self.avoidance_signals, bool) or not isinstance(self.avoidance_signals, int) or not 0 <= self.avoidance_signals <= 100:
            raise ValidationError("avoidance_signals must be an integer between 0 and 100")
        if self.status is CommitmentStatus.COMPLETED and not self.verified_completion:
            raise ValidationError("completed commitments require verified completion evidence")


@dataclass(frozen=True, slots=True)
class CoachingDecision:
    mode: CoachingMode
    action: str
    reason: str
    suppressed: bool = False


def project_long_tasks(rows: Iterable[Mapping[str, Any]]) -> tuple[CommitmentProjection, ...]:
    result = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        task_id = str(raw.get("id") or "").strip()
        title = str(raw.get("title") or "").strip()
        if not task_id or not title:
            continue
        raw_status = str(raw.get("status") or "waiting").lower()
        evidence = str(raw.get("completion_evidence") or "").strip()
        if raw_status == "completed" and evidence:
            status, verified = CommitmentStatus.COMPLETED, True
        elif raw_status == "completed":
            status, verified = CommitmentStatus.NEEDS_REVIEW, False
        else:
            status = {
                "waiting": CommitmentStatus.ACTIVE, "running": CommitmentStatus.ACTIVE,
                "queued": CommitmentStatus.ACTIVE, "paused": CommitmentStatus.PAUSED,
                "failed": CommitmentStatus.FAILED, "needs_review": CommitmentStatus.NEEDS_REVIEW,
                "uncertain": CommitmentStatus.NEEDS_REVIEW, "cancelled": CommitmentStatus.CANCELLED,
                "expired": CommitmentStatus.EXPIRED,
            }.get(raw_status, CommitmentStatus.NEEDS_REVIEW)
            verified = False
        result.append(CommitmentProjection(
            id=f"long-task:{task_id}", source=CommitmentSource.LONG_TASK,
            title=title, status=status, verified_completion=verified,
            evidence_ref=f"long-task:{task_id}:{raw_status}" if evidence else "",
            deadline=_deadline(raw), high_value=bool(raw.get("high_value", False)),
            avoidance_signals=_safe_signals(raw.get("avoidance_signals", 0)),
        ))
    return tuple(result)


def project_memory_projects(memory: Mapping[str, Any]) -> tuple[CommitmentProjection, ...]:
    result = []
    projects = memory.get("projects", {}) if isinstance(memory, Mapping) else {}
    if not isinstance(projects, Mapping):
        return ()
    for key, entry in projects.items():
        value = entry.get("value", "") if isinstance(entry, Mapping) else entry
        if not str(value or "").strip():
            continue
        result.append(CommitmentProjection(
            id=f"memory:projects:{key}", source=CommitmentSource.PROJECT,
            title=str(value).strip()[:240], status=CommitmentStatus.ACTIVE,
            evidence_ref=f"memory:projects:{key}", high_value=False,
        ))
    return tuple(result)


def decide_coaching(
    commitment: CommitmentProjection,
    *,
    preferred_mode: CoachingMode | str,
    now: str,
    rest_until: str | None = None,
    health_or_recovery_signal: bool = False,
) -> CoachingDecision:
    """Choose wording posture only; never execute or mutate a commitment."""
    if not isinstance(commitment, CommitmentProjection):
        raise ValidationError("coaching requires CommitmentProjection")
    try:
        mode = CoachingMode(preferred_mode)
    except (TypeError, ValueError) as exc:
        raise ValidationError("unsupported coaching mode") from exc
    current = datetime.fromisoformat(_timestamp(now, "coaching now").replace("Z", "+00:00"))
    resting = False
    if rest_until:
        resting = current < datetime.fromisoformat(_timestamp(rest_until, "rest_until").replace("Z", "+00:00"))
    if resting or health_or_recovery_signal:
        return CoachingDecision(CoachingMode.RECOVERY, "suppress", "Explicit rest or credible health/recovery signal takes precedence.", True)
    if commitment.status is CommitmentStatus.COMPLETED:
        return CoachingDecision(CoachingMode.SUPPORT, "acknowledge", "Completion is backed by authoritative evidence.")
    if commitment.status in (CommitmentStatus.FAILED, CommitmentStatus.NEEDS_REVIEW):
        return CoachingDecision(CoachingMode.SUPPORT, "repair", "The authoritative source reports failure or uncertainty; focus on repair, not pressure.")
    if commitment.status in (CommitmentStatus.CANCELLED, CommitmentStatus.EXPIRED):
        return CoachingDecision(CoachingMode.SUPPORT, "clarify", "The commitment is no longer active; ask before reviving it.")
    if commitment.status is CommitmentStatus.PAUSED:
        return CoachingDecision(CoachingMode.SUPPORT, "respect_pause", "A paused commitment is not evidence of avoidance.", True)
    if commitment.high_value and commitment.avoidance_signals >= 2 and mode in (CoachingMode.CHALLENGE, CoachingMode.ACCOUNTABILITY):
        return CoachingDecision(mode, "challenge", "Repeated evidence conflicts with an explicit high-value goal.")
    return CoachingDecision(CoachingMode.SUPPORT, "support", "Insufficient evidence to label delay as avoidance.")


def format_active_commitments(items: Iterable[CommitmentProjection], *, limit: int = 12) -> tuple[str, ...]:
    active = [item for item in items if item.status in (
        CommitmentStatus.ACTIVE, CommitmentStatus.PAUSED, CommitmentStatus.FAILED, CommitmentStatus.NEEDS_REVIEW,
    )]
    return tuple(
        f"{item.id}; status={item.status.value}; title={item.title}; authoritative_source={item.source.value}"
        for item in active[:max(1, min(int(limit), 30))]
    )


def _deadline(raw: Mapping[str, Any]) -> str | None:
    value = raw.get("deadline") or raw.get("expires_iso")
    return str(value) if value else None


def _safe_signals(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return max(0, min(value, 100))
