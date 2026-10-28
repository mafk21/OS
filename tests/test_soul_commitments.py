"""Phase 8 authoritative commitment projection and coaching boundaries."""
from core.soul import (
    CoachingMode, CommitmentProjection, CommitmentSource, CommitmentStatus,
    ValidationError, decide_coaching, format_active_commitments,
    project_long_tasks, project_memory_projects,
)
import pytest

NOW = "2026-10-27T12:00:00+03:00"


def test_long_task_projection_never_claims_unverified_completion() -> None:
    rows = [
        {"id": "ok", "title": "Ship release", "status": "completed", "completion_evidence": "checkpoint"},
        {"id": "bad", "title": "Send report", "status": "completed", "completion_evidence": ""},
        {"id": "uncertain", "title": "External send", "status": "uncertain"},
    ]
    items = {x.id: x for x in project_long_tasks(rows)}
    assert items["long-task:ok"].status is CommitmentStatus.COMPLETED
    assert items["long-task:ok"].verified_completion is True
    assert items["long-task:bad"].status is CommitmentStatus.NEEDS_REVIEW
    assert items["long-task:bad"].verified_completion is False
    assert items["long-task:uncertain"].status is CommitmentStatus.NEEDS_REVIEW


def test_completed_projection_constructor_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="verified"):
        CommitmentProjection(
            id="x", source=CommitmentSource.GOAL, title="Goal",
            status=CommitmentStatus.COMPLETED,
        )


def test_memory_projects_are_references_not_duplicate_executors() -> None:
    memory = {"projects": {"launch": {"value": "Launch the product", "updated": "2026-10-20"}}}
    item = project_memory_projects(memory)[0]
    assert item.id == "memory:projects:launch"
    assert item.source is CommitmentSource.PROJECT
    assert item.status is CommitmentStatus.ACTIVE
    assert not hasattr(item, "execute")
    assert not hasattr(item, "steps")


def test_rest_and_health_always_suppress_pressure() -> None:
    item = CommitmentProjection(
        id="goal:x", source=CommitmentSource.GOAL, title="Train",
        status=CommitmentStatus.ACTIVE, high_value=True, avoidance_signals=10,
    )
    resting = decide_coaching(
        item, preferred_mode=CoachingMode.ACCOUNTABILITY, now=NOW,
        rest_until="2026-10-27T18:00:00+03:00",
    )
    assert resting.suppressed and resting.mode is CoachingMode.RECOVERY
    health = decide_coaching(
        item, preferred_mode=CoachingMode.CHALLENGE, now=NOW,
        health_or_recovery_signal=True,
    )
    assert health.suppressed and health.action == "suppress"


def test_one_delay_is_not_avoidance_and_repeated_high_value_evidence_can_challenge() -> None:
    base = dict(id="goal:x", source=CommitmentSource.GOAL, title="Build company", status=CommitmentStatus.ACTIVE, high_value=True)
    one = CommitmentProjection(**base, avoidance_signals=1)
    assert decide_coaching(one, preferred_mode=CoachingMode.ACCOUNTABILITY, now=NOW).action == "support"
    repeated = CommitmentProjection(**base, avoidance_signals=2)
    decision = decide_coaching(repeated, preferred_mode=CoachingMode.ACCOUNTABILITY, now=NOW)
    assert decision.action == "challenge"
    assert decision.mode is CoachingMode.ACCOUNTABILITY


def test_failure_uncertainty_pause_and_cancellation_never_trigger_pressure() -> None:
    expected = {
        CommitmentStatus.FAILED: "repair",
        CommitmentStatus.NEEDS_REVIEW: "repair",
        CommitmentStatus.PAUSED: "respect_pause",
        CommitmentStatus.CANCELLED: "clarify",
        CommitmentStatus.EXPIRED: "clarify",
    }
    for status, action in expected.items():
        item = CommitmentProjection(id=f"x:{status.value}", source=CommitmentSource.LONG_TASK, title="Task", status=status, high_value=True, avoidance_signals=9)
        decision = decide_coaching(item, preferred_mode=CoachingMode.CHALLENGE, now=NOW)
        assert decision.action == action
        assert decision.mode is CoachingMode.SUPPORT


def test_active_context_excludes_completed_cancelled_and_expired() -> None:
    items = [
        CommitmentProjection(id="a", source=CommitmentSource.GOAL, title="Active", status=CommitmentStatus.ACTIVE),
        CommitmentProjection(id="c", source=CommitmentSource.GOAL, title="Complete", status=CommitmentStatus.COMPLETED, verified_completion=True, evidence_ref="goal:c:done"),
        CommitmentProjection(id="x", source=CommitmentSource.GOAL, title="Cancelled", status=CommitmentStatus.CANCELLED),
    ]
    rendered = format_active_commitments(items)
    assert len(rendered) == 1 and "id" not in rendered[0]
    assert "a; status=active" in rendered[0]


def test_projection_does_not_mutate_authoritative_rows() -> None:
    row = {"id": "1", "title": "Task", "status": "running", "target": {"steps": [1]}}
    before = repr(row)
    project_long_tasks([row])
    assert repr(row) == before
