"""Tests for end-to-end latency optimizations without regressions."""

from __future__ import annotations

import asyncio
import os
import re
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import core.gemini as gem
import core.os_control as osc


def test_gemini_rest_leads_ladders_with_live_fallback_preserved():
    assert gem._LADDERS[gem.FAST][0] != gem.LIVE
    assert gem._LADDERS[gem.SMART][0] != gem.LIVE
    assert gem.LIVE in gem._LADDERS[gem.FAST]
    assert gem.LIVE in gem._LADDERS[gem.SMART]


def test_gemini_client_pool_reuses_warm_connections():
    gem._client_pool.clear()
    fake_clients: list[object] = []

    def _fake_ctor(**kwargs):
        obj = SimpleNamespace(**kwargs)
        fake_clients.append(obj)
        return obj

    with patch("google.genai.Client", side_effect=_fake_ctor):
        c1 = gem.client(timeout_ms=10_000, key="test-key-abc")
        c2 = gem.client(timeout_ms=10_000, key="test-key-abc")
        c3 = gem.client(timeout_ms=25_000, key="test-key-abc")

    assert c1 is c2
    assert c3 is not c1
    assert len(fake_clients) == 2
    gem._client_pool.clear()


def test_os_control_fast_pid_and_window_pid_lookup_speed_and_monkeypatch(monkeypatch):
    t0 = time.perf_counter()
    pids = osc._fast_pid_set()
    dt_ms = (time.perf_counter() - t0) * 1000.0
    assert os.getpid() in pids
    assert dt_ms < 50.0

    names = osc._pid_names_for({os.getpid()})
    assert os.getpid() in names and len(names[os.getpid()]) > 0

    # Verify monkeypatching list_processes_snapshot is still honored by _fast_pid_set
    monkeypatch.setattr(
        osc,
        "list_processes_snapshot",
        lambda: [{"pid": 987654, "name": "mock.exe", "cmdline": ""}],
    )
    assert osc._fast_pid_set() == {987654}


def test_windows_uwp_cache_avoids_repeated_powershell_spawns(monkeypatch):
    monkeypatch.setattr(osc, "_SYSTEM", "Windows")
    osc._UWP_CACHE = None
    osc._UWP_CACHED_AT = 0.0

    calls = 0

    def _fake_run(*args, **kwargs):
        nonlocal calls
        calls += 1
        return SimpleNamespace(
            returncode=0,
            stdout="WhatsApp\t5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App\nCalculator\tMicrosoft.WindowsCalculator_8wekyb3d8bbwe!App\n",
        )

    monkeypatch.setattr(osc.subprocess, "run", _fake_run)
    try:
        r1 = osc._find_windows_uwp_appid("WhatsApp")
        r2 = osc._find_windows_uwp_appid("Calculator")
        r3 = osc._find_windows_uwp_appid("Spotify")
        assert r1 == "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
        assert r2 == "shell:AppsFolder\\Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
        assert r3 is None
        # Only ONE PowerShell spawn across all three lookups!
        assert calls == 1
    finally:
        osc._UWP_CACHE = None
        osc._UWP_CACHED_AT = 0.0


def test_dispatch_tool_call_executes_multi_tool_batches_in_parallel():
    import main as m

    jl = m.JarvisLive.__new__(m.JarvisLive)
    jl._session_recycler = m.SessionRecycler()
    sent_batches: list[list[object]] = []

    async def _fake_exec(fc):
        await asyncio.sleep(0.16)
        return f"res:{fc.name}"

    async def _fake_send(function_responses):
        sent_batches.append(list(function_responses))

    async def _fake_flush():
        return None

    jl._execute_tool = _fake_exec
    jl._flush_pending_vision = _fake_flush
    jl.session = SimpleNamespace(send_tool_response=_fake_send)

    tool_call = SimpleNamespace(
        function_calls=[
            SimpleNamespace(name="weather_report"),
            SimpleNamespace(name="calendar_monitor"),
            SimpleNamespace(name="web_search"),
        ]
    )

    t0 = time.perf_counter()
    asyncio.run(jl._dispatch_tool_call(tool_call))
    elapsed = time.perf_counter() - t0

    # 3 x 0.16s sequentially = >=0.48s; in parallel with asyncio.gather < 0.34s
    assert elapsed < 0.34, f"Expected parallel tool execution (<0.34s), took {elapsed:.3f}s"
    assert sent_batches == [["res:weather_report", "res:calendar_monitor", "res:web_search"]]


def test_powershell_invocations_use_noprofile_and_ui_stops_hidden_timers():
    root = Path(__file__).resolve().parent.parent
    cs_src = (root / "actions" / "computer_settings.py").read_text(encoding="utf-8")
    # Every ["powershell", ...] call in computer_settings.py must include -NoProfile
    ps_calls = re.findall(r'\[\s*"powershell"[^\]]+\]', cs_src)
    assert len(ps_calls) >= 5
    for snippet in ps_calls:
        assert "-NoProfile" in snippet, f"Missing -NoProfile in {snippet}"

    ui_src = (root / "ui.py").read_text(encoding="utf-8")
    assert "findChildren(QTimer)" in ui_src

    main_src = (root / "main.py").read_text(encoding="utf-8")
    assert "_dispatch_tool_call" in main_src
    assert "run_in_executor(None, self._screen_memory.capture)" in main_src
