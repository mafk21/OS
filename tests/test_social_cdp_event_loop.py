"""CDP sync boundaries must also work while Playwright owns the caller's loop.

The actual Playwright driver runs, but no browser or Instagram network traffic
is used. Mocking Playwright.start() alone misses its greenlet/event-loop state.
"""
from __future__ import annotations

import asyncio
import threading

import pytest
from playwright.sync_api import sync_playwright

from core import social_hub as hub


@pytest.mark.parametrize("caller", ["plain", "asyncio", "playwright"])
def test_cdp_sync_boundary_preserves_result_without_nesting_loops(monkeypatch, caller):
    browser = hub._NativeCdpSocialBrowser()
    caller_thread = threading.get_ident()
    executions = []

    async def call_many(connection, fn, *, timeout):
        executions.append(threading.get_ident())
        assert asyncio.get_running_loop().is_running()
        return await fn(connection, None)

    async def operation(_conn, _ws):
        await asyncio.sleep(0)
        return {"provider_ack": "simulated-id"}

    monkeypatch.setattr(hub._CdpConnection, "call_many", call_many)

    def invoke():
        return browser.run_on_tab("ws://unused", operation, timeout=2)

    if caller == "plain":
        result = invoke()
    elif caller == "asyncio":
        async def running_loop():
            return invoke()
        result = asyncio.run(running_loop())
    else:
        # Real driver, no Chromium launch. Sync Playwright leaves a running
        # loop on this OS thread even between synchronous API calls.
        with sync_playwright():
            assert asyncio.get_running_loop().is_running()
            result = invoke()
    assert result == {"provider_ack": "simulated-id"}
    assert len(executions) == 1
    assert (executions[0] == caller_thread) is (caller == "plain")


def test_cdp_worker_propagates_original_failure_once(monkeypatch):
    browser = hub._NativeCdpSocialBrowser()
    attempts = []
    failure = TimeoutError("write receipt lost")

    async def call_many(_connection, _fn, *, timeout):
        attempts.append(threading.get_ident())
        raise failure

    monkeypatch.setattr(hub._CdpConnection, "call_many", call_many)
    with sync_playwright():
        with pytest.raises(TimeoutError) as raised:
            browser.run_on_tab("ws://unused", lambda *_: None)
    assert raised.value is failure
    assert len(attempts) == 1  # no retry on a different loop/transport


def test_concurrent_loop_callers_still_serialize_cdp_io(monkeypatch):
    browser = hub._NativeCdpSocialBrowser()
    start = threading.Barrier(2)
    state_lock = threading.Lock()
    active = 0
    maximum = 0
    results, failures = [], []

    async def call_many(_connection, _fn, *, timeout):
        nonlocal active, maximum
        with state_lock:
            active += 1
            maximum = max(maximum, active)
        try:
            await asyncio.sleep(0.02)
            return "completed once"
        finally:
            with state_lock:
                active -= 1

    monkeypatch.setattr(hub._CdpConnection, "call_many", call_many)
    def caller():
        async def running_loop():
            start.wait(timeout=3)
            return browser.run_on_tab("ws://unused", lambda *_: None)
        try:
            results.append(asyncio.run(running_loop()))
        except Exception as exc:
            failures.append(exc)
    callers = [threading.Thread(target=caller, daemon=True) for _ in range(2)]
    for thread in callers:
        thread.start()
    for thread in callers:
        thread.join(timeout=5)
    assert not any(thread.is_alive() for thread in callers), "CDP worker lock deadlock"
    assert not failures
    assert results == ["completed once", "completed once"]
    assert maximum == 1 and active == 0


def test_browser_shutdown_uses_loop_safe_cdp_boundary(monkeypatch):
    from types import SimpleNamespace
    browser = hub._NativeCdpSocialBrowser()
    browser._port = 1234
    monkeypatch.delenv("JARVIS_SOCIALS_CDP_PORT", raising=False)
    monkeypatch.setattr(hub.httpx, "get", lambda *_a, **_kw: SimpleNamespace(json=lambda: {"webSocketDebuggerUrl": "ws://unused"}))
    closed_on = []
    async def send(_connection, _ws, method, *, timeout):
        assert method == "Browser.close"
        closed_on.append(threading.get_ident())
        return {}
    async def call_many(connection, fn, *, timeout):
        return await fn(connection, None)
    monkeypatch.setattr(hub._CdpConnection, "send_cmd", send)
    monkeypatch.setattr(hub._CdpConnection, "call_many", call_many)
    caller = threading.get_ident()
    with sync_playwright():
        browser.shutdown()
    assert len(closed_on) == 1 and closed_on[0] != caller
    assert browser._port == 0
