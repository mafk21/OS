"""Tests — heartbeat engine (Phase 4): levels, HEARTBEAT_OK, never-nag-twice, backoff."""
import time

from core.heartbeat import HeartbeatEngine, HeartbeatLevel


# ── levels ──────────────────────────────────────────────────────────────────

def test_observe_level_never_speaks():
    h = HeartbeatEngine()
    h.record_suggestion("project_x", HeartbeatLevel.OBSERVE)
    assert h._entries["project_x"].level == HeartbeatLevel.OBSERVE


# ── HEARTBEAT_OK silence ────────────────────────────────────────────────────

def test_heartbeat_ok_silences():
    h = HeartbeatEngine()
    msg = h.heartbeat_ok(30)
    assert "30 minute" in msg
    assert h.is_silenced()
    assert not h.should_beat()   # silenced → never beats


def test_heartbeat_ok_expires():
    h = HeartbeatEngine(ok_silence_sec=1)
    h.heartbeat_ok(minutes=0)     # 0 minutes → silence until now (basically instant)
    # Advance time past the silence window
    time.sleep(1.1)
    assert not h.is_silenced()


def test_heartbeat_ok_default_minutes():
    h = HeartbeatEngine(ok_silence_sec=1800)
    h.heartbeat_ok()              # default = ok_silence_sec // 60 = 30
    assert h.is_silenced()


# ── never-nag-twice ─────────────────────────────────────────────────────────

def test_never_nag_twice_within_window():
    h = HeartbeatEngine(nag_window_sec=3600)
    h.record_suggestion("wish_x", HeartbeatLevel.SUGGEST)
    assert h.is_suggested_recently("wish_x")
    assert h.is_suggested_recently("wish_x")   # still within window


def test_nag_window_expires():
    h = HeartbeatEngine(nag_window_sec=1)
    h.record_suggestion("wish_x", HeartbeatLevel.SUGGEST)
    assert h.is_suggested_recently("wish_x")
    time.sleep(1.1)
    assert not h.is_suggested_recently("wish_x")


def test_unknown_topic_not_suggested():
    h = HeartbeatEngine()
    assert not h.is_suggested_recently("nothing")


# ── backoff ─────────────────────────────────────────────────────────────────

def test_backoff_doubles_on_ignore():
    h = HeartbeatEngine(base_interval_sec=100, backoff_cap_sec=10000)
    h.record_suggestion("topic_a", HeartbeatLevel.SUGGEST)
    assert h.interval_for("topic_a") == 100
    h.mark_ignored("topic_a")
    assert h.interval_for("topic_a") == 200
    h.mark_ignored("topic_a")
    assert h.interval_for("topic_a") == 400


def test_backoff_capped():
    h = HeartbeatEngine(base_interval_sec=100, backoff_cap_sec=300)
    h.record_suggestion("topic_a", HeartbeatLevel.SUGGEST)
    for _ in range(10):
        h.mark_ignored("topic_a")
    assert h.interval_for("topic_a") == 300  # capped


def test_unknown_topic_base_interval():
    h = HeartbeatEngine(base_interval_sec=999)
    assert h.interval_for("unknown") == 999


# ── should_beat ─────────────────────────────────────────────────────────────

def test_should_beat_respects_base_interval():
    h = HeartbeatEngine(base_interval_sec=600)
    assert not h.should_beat()      # nothing ever beat
    h._last_beat = time.monotonic() - 601
    assert h.should_beat()          # past interval


def test_should_beat_respects_silence():
    h = HeartbeatEngine(base_interval_sec=1, ok_silence_sec=3600)
    h.heartbeat_ok(minutes=60)
    h._last_beat = 0                # long past interval
    assert not h.should_beat()      # silenced


# ── snapshot ────────────────────────────────────────────────────────────────

def test_snapshot_shape():
    h = HeartbeatEngine()
    h.record_suggestion("topic_a", HeartbeatLevel.SUGGEST)
    snap = h.snapshot()
    assert "silenced" in snap
    assert "topics" in snap
    assert snap["topics"]["topic_a"]["level"] == "suggest"
    assert snap["topics"]["topic_a"]["ignored"] == 0
