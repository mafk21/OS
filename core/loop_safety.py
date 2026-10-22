"""Loop-safety helpers — keep asyncio's callback machinery quiet and alive.

Incident 2026-10-22 (user log): a network stall left the mic -> server queue
full, so every ~64 ms mic block raised QueueFull inside a call_soon_threadsafe
callback. asyncio's default exception handler printed a full traceback per
block straight to the console; that console I/O runs ON the event loop, so the
spam starved the loop until the websocket keepalive ping timed out (server
closed 1006), and the reconnect then raced the dying session (1008). Nothing
to do with barge-in or the user talking over JARVIS — a full queue with no
error path. This module is stdlib-only so it can be unit-tested directly.
"""

from __future__ import annotations

import asyncio
import sys
import time
import traceback

__all__ = ["out_put_drop_oldest", "throttled_loop_exception_handler"]


def out_put_drop_oldest(q: asyncio.Queue, msg) -> None:
    """Put `msg` into `q`, dropping the OLDEST item rather than raising.

    Used by the microphone callback (via call_soon_threadsafe) and the phone
    relay. QueueFull inside a callback is not something to log block by block —
    it means the websocket send stalled, and the stale item that falls out is
    exactly what must NOT be replayed when the send recovers. Freshness is the
    only property a mic queue has; keep it.
    """
    try:
        q.put_nowait(msg)
        return
    except asyncio.QueueFull:
        pass
    try:
        q.get_nowait()
    except asyncio.QueueEmpty:
        return                      # consumer drained it between our two calls
    try:
        q.put_nowait(msg)
    except asyncio.QueueFull:
        pass                        # raced another producer — drop ours


# Repeat-suppression state for the handler below. One loop per process, so
# module level is the right scope.
_SIG: str = ""
_AT: float = 0.0
_N: int = 0


def throttled_loop_exception_handler(loop, context) -> None:
    """Loop exception handler that counts repeats instead of reprinting them.

    asyncio's default handler prints every occurrence in full. When a callback
    error repeats at microphone rate, that printing becomes the outage: the
    loop cannot answer keepalive pings and the server drops the session. Print
    each distinct error once (message + traceback), then only a one-line
    suppressed-count for the next 10 s of identical failures.
    """
    global _SIG, _AT, _N
    exc = context.get("exception")
    # Key on type name + message: str(exc) alone can be "" (QueueFull), which
    # would never match and defeat the dedup.
    msg = (f"{type(exc).__name__}: {exc}" if exc is not None
           else str(context.get("message", "")))
    now = time.monotonic()
    if msg and msg == _SIG and (now - _AT) < 10.0:
        _N += 1
        _AT = now
        return
    if _N:
        print(f"[asyncio] (+{_N} similar error(s) suppressed)", file=sys.stderr)
        _N = 0
    _SIG, _AT = msg, now
    print(
        f"[asyncio] {context.get('message', 'unhandled exception in callback')}",
        file=sys.stderr,
    )
    if exc is not None:
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
