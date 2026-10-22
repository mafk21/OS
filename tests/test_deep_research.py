"""Tests — deep research (Phase 5): multi-wave sourced reports."""
from unittest.mock import patch

import actions.deep_research as dr


# ── sub-question planning ──────────────────────────────────────────────────

def test_plan_sub_questions_returns_core_plus_templates():
    qs = dr._plan_sub_questions("best laptop for video editing", 5)
    assert len(qs) >= 3
    assert len(qs) <= 5
    assert any("laptop" in q and "video" in q for q in qs)


def test_plan_sub_questions_caps_at_max():
    qs = dr._plan_sub_questions("affordable noise cancelling headphones", 3)
    assert len(qs) == 3


def test_plan_sub_questions_handles_short_query():
    qs = dr._plan_sub_questions("coffee", 5)
    assert len(qs) >= 1
    assert "coffee" in qs[0]


# ── search waves ───────────────────────────────────────────────────────────

def test_search_waves_parallel_and_cap():
    fake_results = {
        "q1": [{"title": "A", "snippet": "x" * 100, "url": "https://a.com"}],
        "q2": [],
        "q3": [{"title": "B", "snippet": "y" * 50, "url": "https://b.com"}],
    }

    def fake_search(q, max_results=4):
        return fake_results.get(q, [])

    with patch.object(dr, "_ddg_search", side_effect=fake_search):
        waves = dr._search_waves(["q1", "q2", "q3"], max_waves=3)
    queries = [w["query"] for w in waves]
    assert set(queries) == {"q1", "q2", "q3"}


def test_search_waves_respects_max_searches():
    call_count = 0

    def fake_search(q, max_results=4):
        nonlocal call_count
        call_count += 1
        return [{"title": "X", "snippet": "z", "url": "https://x.com"}]

    with patch.object(dr, "_ddg_search", side_effect=fake_search):
        dr._search_waves(["a", "b", "c", "d", "e"], max_waves=4)
    assert call_count <= dr.MAX_SEARCHES


# ── synthesize ─────────────────────────────────────────────────────────────

def test_synthesize_with_sources():
    waves = [{"query": "best laptop", "results": [
        {"title": "Laptop A", "snippet": "Great for video editing, 16GB RAM.",
         "url": "https://a.com"},
        {"title": "Laptop B", "snippet": "Cheaper but slower.",
         "url": "https://b.com"},
    ]}]
    report = dr._synthesize("best laptop", waves, {})
    assert "Deep research — best laptop" in report
    assert "https://a.com" in report
    assert "https://b.com" in report


def test_synthesize_no_sources():
    report = dr._synthesize("obscure topic", [], {})
    assert "No usable results found" in report


# ── end-to-end ─────────────────────────────────────────────────────────────

def test_deep_research_end_to_end(monkeypatch):
    def fake_search(q, max_results=4):
        return [{"title": f"Result for {q}",
                 "snippet": f"Info about {q}",
                 "url": f"https://example.com/{q.replace(' ', '_')}"}]

    monkeypatch.setattr(dr, "_ddg_search", fake_search)
    result = dr.deep_research({"query": "best electric car 2026"})
    assert "Deep research — best electric car 2026" in result
    assert "https://example.com/best" in result or "example.com" in result
    assert "Sources:" in result


def test_deep_research_empty_query():
    result = dr.deep_research({"query": ""})
    assert "no query provided" in result.lower()


# ── TOOL declaration ──────────────────────────────────────────────────────

def test_tool_declaration():
    assert dr.TOOL["name"] == "deep_research"
    assert dr.TOOL["handler"] is dr.deep_research
    assert dr.TOOL["parameters"]["required"] == ["query"]
    assert "max_waves" in dr.TOOL["parameters"]["properties"]
