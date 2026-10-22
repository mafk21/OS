"""Tests — Proactive 15-Minute Session Recycle (Phase 13)."""

from datetime import timedelta
from types import SimpleNamespace
import pytest

from core.session_recycle import (
    ABSOLUTE_CUTOFF_SEC,
    DEFAULT_GO_AWAY_SEC,
    FORCE_RECYCLE_SEC,
    HARD_LIMIT_SEC,
    SOFT_RECYCLE_SEC,
    URGENT_RECYCLE_SEC,
    SessionRecycler,
    parse_go_away_seconds,
)


class FakeClock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


# ── GoAway duration parser ────────────────────────────────────────────────

def test_parse_go_away_none():
    assert parse_go_away_seconds(None) is None


def test_parse_go_away_strings_and_types():
    assert parse_go_away_seconds(SimpleNamespace(time_left="30s")) == 30.0
    assert parse_go_away_seconds(SimpleNamespace(time_left="45.5s")) == 45.5
    assert parse_go_away_seconds(SimpleNamespace(time_left="500ms")) == 0.5
    assert parse_go_away_seconds(SimpleNamespace(time_left="2m")) == 120.0
    assert parse_go_away_seconds(SimpleNamespace(time_left=timedelta(seconds=22))) == 22.0
    assert parse_go_away_seconds(SimpleNamespace(time_left=18)) == 18.0
    assert parse_go_away_seconds(SimpleNamespace(time_left=None)) == DEFAULT_GO_AWAY_SEC
    assert parse_go_away_seconds(SimpleNamespace(time_left="unexpected")) == DEFAULT_GO_AWAY_SEC


# ── Threshold validation & initial state ──────────────────────────────────

def test_invalid_thresholds_rejected():
    with pytest.raises(ValueError):
        SessionRecycler(soft_sec=800, urgent_sec=750, force_sec=885, hard_sec=900)


def test_before_connect_never_recycles():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    assert r.session_age() == 0.0
    assert r.time_remaining() == HARD_LIMIT_SEC
    assert r.should_recycle() == (False, "")


def test_young_session_does_not_recycle():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(SOFT_RECYCLE_SEC - 1.0)
    assert r.should_recycle() == (False, "")


# ── Soft window (13m00s – 14m15s) ─────────────────────────────────────────

def test_soft_window_recycles_when_calm_and_resumable():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(SOFT_RECYCLE_SEC + 5.0)

    should, reason = r.should_recycle(
        is_speaking=False,
        audio_queued=False,
        last_user_speech_age=12.0,
        vision_busy=False,
        has_resume_handle=True,
    )
    assert should is True
    assert reason == "proactive 15m recycle"


def test_soft_window_defers_while_busy_or_recent_speech_or_no_handle():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(SOFT_RECYCLE_SEC + 10.0)

    # JARVIS speaking
    assert r.should_recycle(is_speaking=True)[0] is False
    # Audio still buffered in playback queue
    assert r.should_recycle(audio_queued=True)[0] is False
    # Vision frame injection in flight
    assert r.should_recycle(vision_busy=True)[0] is False
    # User spoke 3s ago (< 8s grace window)
    assert r.should_recycle(last_user_speech_age=3.0)[0] is False
    # Resumption handle not yet issued in soft window → wait for urgent window
    assert r.should_recycle(has_resume_handle=False)[0] is False


def test_track_tool_blocks_recycle_and_cleans_up_on_exception():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(SOFT_RECYCLE_SEC + 15.0)

    with pytest.raises(RuntimeError):
        with r.track_tool():
            assert r.active_tools == 1
            assert r.should_recycle()[0] is False
            raise RuntimeError("boom")

    assert r.active_tools == 0
    assert r.should_recycle()[0] is True


# ── Urgent window (14m15s – 14m45s) ───────────────────────────────────────

def test_urgent_window_relaxes_quiet_margin_and_handle_requirement():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(URGENT_RECYCLE_SEC + 5.0)

    # Still blocks if user literally mid-utterance (1.0s < 2.0s) or speaking
    assert r.should_recycle(last_user_speech_age=1.0, has_resume_handle=False)[0] is False
    assert r.should_recycle(is_speaking=True, last_user_speech_age=5.0)[0] is False

    # 2.5s pause without a handle is allowed in urgent window
    should, reason = r.should_recycle(
        is_speaking=False,
        last_user_speech_age=2.5,
        has_resume_handle=False,
    )
    assert should is True
    assert reason == "proactive 15m recycle (urgent)"


# ── Force & absolute cutoff windows ───────────────────────────────────────

def test_force_window_waits_only_for_in_flight_tool_until_absolute_cutoff():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(FORCE_RECYCLE_SEC + 2.0)

    # Even if speaking, force window recycles when no tool response is in flight
    should, reason = r.should_recycle(is_speaking=True, last_user_speech_age=0.5)
    assert should is True
    assert reason == "15m session limit imminent"

    # If a tool call is mid-flight at 14m47s, give it a few seconds to send response
    with r.track_tool():
        assert r.should_recycle(is_speaking=False)[0] is False

        # At 14m55s (absolute cutoff), recycle unconditionally before 15m00s drop
        clock.advance((ABSOLUTE_CUTOFF_SEC - FORCE_RECYCLE_SEC))
        should_abs, reason_abs = r.should_recycle(is_speaking=True)
        assert should_abs is True
        assert reason_abs == "15m hard limit cutoff"


# ── Server GoAway handling ────────────────────────────────────────────────

def test_server_go_away_triggers_early_recycle_on_speech_gap():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(120.0)  # only 2 minutes into session

    r.on_go_away(25.0)
    assert r.go_away_received is True
    assert r.time_remaining() == pytest.approx(25.0)

    # Waits while JARVIS finishes current sentence
    assert r.should_recycle(is_speaking=True, last_user_speech_age=10.0)[0] is False

    # Recycles immediately once sentence finishes
    should, reason = r.should_recycle(is_speaking=False, last_user_speech_age=3.0)
    assert should is True
    assert reason == "server go_away"

    # If still busy when <= 10s remain on GoAway, enters force mode
    clock.advance(16.0)  # 9s remaining on GoAway
    should_force, reason_force = r.should_recycle(is_speaking=True)
    assert should_force is True
    assert reason_force == "server go_away imminent"


# ── Multi-session lifecycle & idempotency ─────────────────────────────────

def test_mark_recycled_idempotent_and_reset_on_next_connect():
    clock = FakeClock()
    r = SessionRecycler(clock=clock)
    r.on_connect()
    clock.advance(SOFT_RECYCLE_SEC + 20.0)

    should, reason = r.should_recycle()
    assert should is True
    r.mark_recycled(reason)
    r.mark_recycled(reason)  # idempotent
    assert r.recycle_count == 1
    assert r.should_recycle() == (False, "")

    # Next WebSocket session opens fresh
    r.on_connect()
    assert r.connect_count == 2
    assert r.recycle_count == 1
    assert r.recycled is False
    assert r.go_away_received is False
    assert r.should_recycle() == (False, "")

    st = r.status()
    assert st["connected"] is True
    assert st["connect_count"] == 2
    assert st["recycle_count"] == 1
    assert st["last_recycle_reason"] == "proactive 15m recycle"
