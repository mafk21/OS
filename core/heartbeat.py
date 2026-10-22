"""
Heartbeat engine — autonomous observe/suggest/act with HEARTBEAT_OK silence
and never-nag-twice backoff.

Phase 4 of the skills roadmap. Stacks on the existing ProactiveEngine
(actions/proactive.py) and background monitor (actions/background_monitor.py)
by adding:

  * Heartbeat levels — OBSERVE (note internally), SUGGEST (tell the user),
    ACT (act with confirmation) — the model picks the level per topic.
  * HEARTBEAT_OK silence — user says "heartbeat ok" (or the tool is called)
    and proactive suggestions pause for a configurable window.
  * Never-nag-twice — a suggested topic is never repeated within the
    backoff window; ignored suggestions back off exponentially.
  * Backoff — each ignored suggestion doubles the silence window up to a cap.

The engine itself never speaks — it only decides *if* and *at what level* a
heartbeat should fire. main.py owns the actual message sending.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class HeartbeatLevel(Enum):
    OBSERVE = "observe"      # note internally, never speak
    SUGGEST = "suggest"      # proactive message to the user
    ACT = "act"              # act (confirmation-gated by main.py)


@dataclass
class HeartbeatEntry:
    topic: str
    level: HeartbeatLevel
    suggested_at: float
    ignored_count: int = 0    # how many times this topic was suggested but not acted on


class HeartbeatEngine:
    """
    Decides heartbeat cadence and level. All state in memory — no disk,
    no network. Create one instance per JarvisLive and share it.
    """

    # ── Defaults ──────────────────────────────────────────────────────────
    # Minimum silence between any two heartbeats.
    BASE_INTERVAL_SEC = 600          # 10 min
    # After a HEARTBEAT_OK, suggestions pause this long.
    OK_SILENCE_SEC = 1800            # 30 min
    # A topic may not be re-suggested within this window.
    NAG_WINDOW_SEC = 3600            # 1 hour
    # Ignored suggestions back off: interval * 2^ignored, capped.
    BACKOFF_CAP_SEC = 21600          # 6 hours

    def __init__(
        self,
        base_interval_sec: int = BASE_INTERVAL_SEC,
        ok_silence_sec: int = OK_SILENCE_SEC,
        nag_window_sec: int = NAG_WINDOW_SEC,
        backoff_cap_sec: int = BACKOFF_CAP_SEC,
    ):
        self.base_interval_sec = base_interval_sec
        self.ok_silence_sec = ok_silence_sec
        self.nag_window_sec = nag_window_sec
        self.backoff_cap_sec = backoff_cap_sec

        self._entries: dict[str, HeartbeatEntry] = {}
        self._last_beat: float | None = None    # None = never beaten
        self._heartbeat_ok_until: float = 0.0   # silence until this timestamp

    # ── HEARTBEAT_OK silence ─────────────────────────────────────────────

    def heartbeat_ok(self, minutes: int | None = None) -> str:
        """User confirmed the heartbeat is fine — silence suggestions.

        Call this when the user says 'heartbeat ok' (or equivalent). Returns
        a human-readable confirmation line.
        """
        mins = minutes if minutes is not None else self.ok_silence_sec // 60
        self._heartbeat_ok_until = time.monotonic() + mins * 60
        self._last_beat = time.monotonic()
        return f"Heartbeat paused for {mins} minute{'s' if mins != 1 else ''}. I'll still act if something urgent comes up."

    def is_silenced(self) -> bool:
        return time.monotonic() < self._heartbeat_ok_until

    # ── Never-nag-twice ──────────────────────────────────────────────────

    def record_suggestion(self, topic: str, level: HeartbeatLevel) -> None:
        """A suggestion was made for `topic` at `level`."""
        now = time.monotonic()
        entry = self._entries.get(topic)
        if entry is None:
            entry = HeartbeatEntry(topic=topic, level=level, suggested_at=now)
            self._entries[topic] = entry
        else:
            entry.level = level
            entry.suggested_at = now
            entry.ignored_count += 1
        self._last_beat = now

    def mark_ignored(self, topic: str) -> None:
        """The user did not respond to a suggestion for `topic` — back off."""
        entry = self._entries.get(topic)
        if entry is not None:
            entry.ignored_count += 1

    def is_suggested_recently(self, topic: str) -> bool:
        """True if `topic` was suggested within the nag window."""
        entry = self._entries.get(topic)
        if entry is None:
            return False
        return (time.monotonic() - entry.suggested_at) < self.nag_window_sec

    # ── Cadence ──────────────────────────────────────────────────────────

    def interval_for(self, topic: str) -> float:
        """Current backoff interval for `topic`."""
        entry = self._entries.get(topic)
        if entry is None or entry.ignored_count == 0:
            return float(self.base_interval_sec)
        return min(
            self.base_interval_sec * (2 ** entry.ignored_count),
            float(self.backoff_cap_sec),
        )

    def should_beat(self, now: float | None = None) -> bool:
        """True if a heartbeat is due right now (respects silence + backoff)."""
        now = now or time.monotonic()
        if self.is_silenced():
            return False
        # Never beaten: nothing is due yet.
        if self._last_beat is None:
            return False
        if now - self._last_beat < self.base_interval_sec:
            return False
        # Any topic with a backlog that's past its backoff interval triggers.
        for entry in self._entries.values():
            if now - entry.suggested_at >= self.interval_for(entry.topic):
                return True
        return now - self._last_beat >= self.base_interval_sec

    # ── Snapshot ─────────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        """Debug / UI snapshot of current heartbeat state."""
        return {
            "silenced": self.is_silenced(),
            "ok_until": self._heartbeat_ok_until,
            "topics": {
                t: {
                    "level": e.level.value,
                    "ignored": e.ignored_count,
                    "interval_sec": self.interval_for(t),
                }
                for t, e in self._entries.items()
            },
        }
