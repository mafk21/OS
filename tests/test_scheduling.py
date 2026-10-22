"""Tests — per-tool scheduling (Phase 6): NON_BLOCKING + WHEN_IDLE on slow tools."""
from pathlib import Path

from core.action_loader import discover_actions, _SCHEDULING, _BEHAVIORS


SLOW_TOOL_NAMES = ("web_search", "deep_research", "file_processor",
                   "browser_control", "send_message")


def test_scheduling_values_are_valid():
    assert "WHEN_IDLE" in _SCHEDULING
    assert "NON_BLOCKING" in _BEHAVIORS


def test_slow_tools_have_non_blocking_when_idle():
    """Every slow/network tool must declare NON_BLOCKING + WHEN_IDLE."""
    reg = discover_actions(Path("actions"), logger=lambda m: None)
    for name in SLOW_TOOL_NAMES:
        rec = reg._actions.get(name)
        if rec is None or not rec.valid:
            # Action couldn't be loaded (e.g. missing playwright) — skip
            continue
        assert rec.behavior == "NON_BLOCKING", \
            f"{name}: behavior={rec.behavior}, expected NON_BLOCKING"
        assert rec.scheduling == "WHEN_IDLE", \
            f"{name}: scheduling={rec.scheduling}, expected WHEN_IDLE"


def test_at_least_some_slow_tools_loaded():
    """Sanity check: at least web_search and deep_research are loadable."""
    reg = discover_actions(Path("actions"), logger=lambda m: None)
    loadable = [n for n in SLOW_TOOL_NAMES
                if reg._actions.get(n) and reg._actions[n].valid]
    assert "web_search" in loadable, "web_search must be loadable"
    assert "deep_research" in loadable, "deep_research must be loadable"


def test_scheduling_passed_through_function_response():
    """main.py attaches scheduling to the FunctionResponse extra fields."""
    m = Path("main.py").read_text(encoding="utf-8")
    assert '_sched = (self._action_registry.scheduling(name)' in m
    assert '_extra = {"scheduling": _sched} if _sched else {}' in m
    assert "response=" in m
