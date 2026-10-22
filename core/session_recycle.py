"""
Proactive 15-Minute Session Recycle (Phase 13).

Gemini Multimodal Live WebSocket connections enforce a hard ~15-minute (900 s)
server-side connection lifetime ceiling. Even when `ContextWindowCompression`
and `SessionResumption` are enabled, letting the server sever the socket at
15:00 risks cutting off JARVIS mid-sentence, mid-utterance, or mid-tool-call.

`SessionRecycler` monitors connection age AND server `GoAway` notices:
  1. Soft window (13m00s – 14m15s): waits for a calm idle gap — JARVIS not
     speaking, playback queue drained, no tool call / vision injection in
     flight, user silent for >= 8s, and a resumable session handle armed.
  2. Urgent window (14m15s – 14m45s, or upon a server `GoAway` frame): relaxes
     user-silence margin to 2s and no longer requires a prior handle, while
     still waiting for active speech or tool execution to finish.
  3. Force window (>= 14m45s, or < 10s left on `GoAway`): recycles as soon as
     no tool response is mid-send (or unconditionally at 14m55s) so we beat
     an uncontrolled server disconnect.

All stdlib — zero external dependencies, deterministic via injectable clock.
"""

from __future__ import annotations

import re
import time
from contextlib import contextmanager
from datetime import timedelta
from typing import Callable, Iterator, Optional

# ── Lifecycle thresholds (seconds) ────────────────────────────────────────

HARD_LIMIT_SEC         = 900.0   # 15m 00s — Gemini Live WebSocket hard ceiling
SOFT_RECYCLE_SEC       = 780.0   # 13m 00s — begin seeking a calm speech gap
URGENT_RECYCLE_SEC     = 855.0   # 14m 15s — tighten gap requirements
FORCE_RECYCLE_SEC      = 885.0   # 14m 45s — recycle as soon as tools clear
ABSOLUTE_CUTOFF_SEC    = 895.0   # 14m 55s — unconditional recycle before server cut

USER_QUIET_SEC         = 8.0     # soft window: matches 8s wake-free grace window
URGENT_USER_QUIET_SEC  = 2.0     # urgent window: brief pause between utterances
GO_AWAY_FORCE_LEFT_SEC = 10.0    # force recycle when GoAway has <= 10s left
DEFAULT_GO_AWAY_SEC    = 30.0    # conservative default if GoAway omits time_left
CHECK_INTERVAL_SEC     = 5.0     # background poll cadence inside Live TaskGroup

_DURATION_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s|m)?\s*$", re.IGNORECASE)


def parse_go_away_seconds(go_away: object) -> Optional[float]:
    """
    Extract remaining seconds from a `google.genai.types.GoAway` object (or raw
    `time_left` value).

    Handles Protobuf duration strings ("30s", "45.5s", "500ms"), `timedelta`,
    numeric seconds, or `None`.
    """
    if go_away is None:
        return None

    raw = getattr(go_away, "time_left", go_away)
    if raw is None:
        return DEFAULT_GO_AWAY_SEC

    if isinstance(raw, timedelta):
        return max(0.0, raw.total_seconds())

    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return max(0.0, float(raw))

    if isinstance(raw, str):
        m = _DURATION_RE.match(raw)
        if m:
            val = float(m.group(1))
            unit = (m.group(2) or "s").lower()
            if unit == "ms":
                return max(0.0, val / 1000.0)
            if unit == "m":
                return max(0.0, val * 60.0)
            return max(0.0, val)

    return DEFAULT_GO_AWAY_SEC


class SessionRecycler:
    """
    Tracks a single Gemini Live WebSocket's age, in-flight activity, and server
    `GoAway` warnings to decide the safest moment to proactively recycle.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        soft_sec: float = SOFT_RECYCLE_SEC,
        urgent_sec: float = URGENT_RECYCLE_SEC,
        force_sec: float = FORCE_RECYCLE_SEC,
        hard_sec: float = HARD_LIMIT_SEC,
    ) -> None:
        if not (0 < soft_sec < urgent_sec < force_sec < hard_sec):
            raise ValueError(
                "Thresholds must satisfy 0 < soft_sec < urgent_sec < force_sec < hard_sec"
            )
        self._clock = clock
        self.soft_sec = float(soft_sec)
        self.urgent_sec = float(urgent_sec)
        self.force_sec = float(force_sec)
        self.hard_sec = float(hard_sec)
        self.absolute_sec = min(ABSOLUTE_CUTOFF_SEC, self.hard_sec - 2.0)

        self.connected_at: Optional[float] = None
        self.go_away_received: bool = False
        self.go_away_deadline: Optional[float] = None
        self.active_tools: int = 0
        self.recycled: bool = False

        self.connect_count: int = 0
        self.recycle_count: int = 0
        self.last_recycle_reason: str = ""

    # ── Lifecycle hooks ───────────────────────────────────────────────────

    def on_connect(self) -> None:
        """Call each time a fresh `client.aio.live.connect` session opens."""
        self.connected_at = self._clock()
        self.go_away_received = False
        self.go_away_deadline = None
        self.active_tools = 0
        self.recycled = False
        self.connect_count += 1

    def on_go_away(self, time_left_sec: Optional[float] = None) -> None:
        """Record a server `GoAway` frame so we recycle before forced close."""
        now = self._clock()
        left = DEFAULT_GO_AWAY_SEC if time_left_sec is None else max(0.0, float(time_left_sec))
        deadline = now + left
        self.go_away_received = True
        if self.go_away_deadline is None or deadline < self.go_away_deadline:
            self.go_away_deadline = deadline

    def tool_started(self) -> None:
        """Mark a tool call (and its `send_tool_response`) as in flight."""
        self.active_tools += 1

    def tool_finished(self) -> None:
        """Mark an in-flight tool call complete."""
        self.active_tools = max(0, self.active_tools - 1)

    @contextmanager
    def track_tool(self) -> Iterator[None]:
        """Context manager guarding tool execution + `send_tool_response`."""
        self.tool_started()
        try:
            yield
        finally:
            self.tool_finished()

    # ── Timing queries ────────────────────────────────────────────────────

    def session_age(self) -> float:
        """Seconds elapsed since `on_connect()` (0.0 if not yet connected)."""
        if self.connected_at is None:
            return 0.0
        return max(0.0, self._clock() - self.connected_at)

    def time_remaining(self) -> float:
        """Estimated seconds before server-side WebSocket termination."""
        if self.connected_at is None:
            return self.hard_sec
        now = self._clock()
        by_age = max(0.0, (self.connected_at + self.hard_sec) - now)
        if self.go_away_deadline is not None:
            by_go_away = max(0.0, self.go_away_deadline - now)
            return min(by_age, by_go_away)
        return by_age

    # ── Core decision logic ───────────────────────────────────────────────

    def should_recycle(
        self,
        *,
        is_speaking: bool = False,
        audio_queued: bool = False,
        last_user_speech_age: float = 999.0,
        vision_busy: bool = False,
        has_resume_handle: bool = True,
    ) -> tuple[bool, str]:
        """
        Decide whether the active WebSocket should recycle right now.

        Returns `(should_recycle, reason)`.
        """
        if self.connected_at is None or self.recycled:
            return False, ""

        now = self._clock()
        age = max(0.0, now - self.connected_at)
        go_away_left = (
            max(0.0, self.go_away_deadline - now)
            if self.go_away_deadline is not None
            else None
        )

        # 0. Not yet in any recycle window
        if age < self.soft_sec and not self.go_away_received:
            return False, ""

        # 1. Absolute last-second safety net right before hard server cut
        if age >= self.absolute_sec or (go_away_left is not None and go_away_left <= 2.0):
            reason = "server go_away cutoff" if self.go_away_received else "15m hard limit cutoff"
            return True, reason

        # 2. Force window: beat the cliff as soon as no tool response is mid-send
        in_force = (
            age >= self.force_sec
            or (go_away_left is not None and go_away_left <= GO_AWAY_FORCE_LEFT_SEC)
        )
        if in_force:
            if self.active_tools == 0:
                reason = (
                    "server go_away imminent"
                    if self.go_away_received
                    else "15m session limit imminent"
                )
                return True, reason
            return False, ""

        # Common idle checks for soft & urgent windows: never clip active audio,
        # buffered audio chunks, in-flight tools, or pending vision frames.
        output_busy = is_speaking or audio_queued or (self.active_tools > 0) or vision_busy
        if output_busy:
            return False, ""

        # 3. Urgent window (or explicit server GoAway): short user pause suffices
        if age >= self.urgent_sec or self.go_away_received:
            if last_user_speech_age >= URGENT_USER_QUIET_SEC:
                reason = (
                    "server go_away"
                    if self.go_away_received
                    else "proactive 15m recycle (urgent)"
                )
                return True, reason
            return False, ""

        # 4. Soft window (13m00s – 14m15s): wait for full quiet grace period AND
        #    a valid session resumption handle so the handoff is 100% lossless.
        if has_resume_handle and last_user_speech_age >= USER_QUIET_SEC:
            return True, "proactive 15m recycle"

        return False, ""

    def mark_recycled(self, reason: str = "proactive 15m recycle") -> None:
        """Record that a recycle reconnect has been triggered for this session."""
        if not self.recycled:
            self.recycled = True
            self.recycle_count += 1
            self.last_recycle_reason = reason

    def status(self) -> dict:
        """Diagnostic snapshot of session recycle health."""
        return {
            "connected": self.connected_at is not None,
            "session_age_sec": round(self.session_age(), 1),
            "time_remaining_sec": round(self.time_remaining(), 1),
            "connect_count": self.connect_count,
            "recycle_count": self.recycle_count,
            "active_tools": self.active_tools,
            "go_away_received": self.go_away_received,
            "last_recycle_reason": self.last_recycle_reason,
        }
