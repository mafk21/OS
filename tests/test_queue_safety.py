"""Regression tests — 2026-10-22 QueueFull flood incident.

What happened (user log): a websocket send stall left the mic->server queue
full, every mic block then raised QueueFull inside a call_soon_threadsafe
callback, asyncio's default handler printed a full traceback per block on the
event loop, the loop starved until the keepalive ping timed out (1006 close),
and the reconnect raced the dying session (1008). The user had NOT talked over
JARVIS — barge-in never fired.

These tests lock in the three defences: drop-oldest puts (never raise),
repeat-throttled loop exception handling, and the wiring in main.py.
"""
import asyncio
import pathlib

import core.loop_safety as ls
from core.loop_safety import out_put_drop_oldest, throttled_loop_exception_handler


def test_out_put_never_raises_and_drops_oldest():
    async def _run():
        q = asyncio.Queue(maxsize=3)
        for i in range(3):
            out_put_drop_oldest(q, i)
        out_put_drop_oldest(q, 99)    # naive put_nowait would raise QueueFull
        out_put_drop_oldest(q, 100)
        out = []
        while not q.empty():
            out.append(q.get_nowait())
        return out
    # oldest (0) evicted, freshest always admitted
    assert asyncio.run(_run()) == [2, 99, 100]


def test_full_queue_flood_is_silent():
    async def _run():
        q = asyncio.Queue(maxsize=1)
        out_put_drop_oldest(q, "first")
        for _ in range(500):          # one put per mic block for ~30 s
            out_put_drop_oldest(q, "fresh")
        return q.get_nowait()
    assert asyncio.run(_run()) == "fresh"


def test_handler_prints_once_then_counts_repeats(capsys):
    ls._SIG, ls._AT, ls._N = "", 0.0, 0          # module state isolation
    try:
        ctx = {"message": "Exception in callback Queue.put_nowait()",
               "exception": asyncio.QueueFull()}
        throttled_loop_exception_handler(None, ctx)
        first = capsys.readouterr().err
        assert "QueueFull" in first                # first occurrence in full

        for _ in range(100):                        # identical, inside 10 s
            throttled_loop_exception_handler(None, ctx)
        again = capsys.readouterr().err
        assert again == ""                         # nothing reprinted
        assert ls._N == 100                        # counted instead

        # a DIFFERENT error must surface immediately, with the suppression
        # count reported alongside it
        throttled_loop_exception_handler(
            None, {"message": "other", "exception": ValueError("different")}
        )
        third = capsys.readouterr().err
        assert "different" in third
        assert "100 similar error(s) suppressed" in third
    finally:
        ls._SIG, ls._AT, ls._N = "", 0.0, 0


def test_main_wires_queue_safety():
    m = pathlib.Path("main.py").read_text(encoding="utf-8")
    # mic + phone producers all go through drop-oldest
    assert "out_put_drop_oldest" in m
    assert "self.out_queue.put_nowait" not in m      # no raw producer left
    # small jitter buffer (~4 s), freshness over backlog
    assert "asyncio.Queue(maxsize=64)" in m
    # loop handler installed; stalled sends forced into a reconnect
    assert "set_exception_handler(throttled_loop_exception_handler)" in m
    assert "send_realtime_input stalled >10s" in m
    # 1008 race gets a longer backoff; TaskGroup errors classified from leaves
    assert 'elif "already connected" in err_str:' in m
    assert "_leaf_errors" in m
