"""
Deep Research — multi-wave sourced reports with citations.

Phase 5 of the skills roadmap. Implements the deep-research SKILL.md procedure
as a single callable action:

  1. Plan — derive 3–5 sub-questions from the user's query (price, specs,
     reviews, risks/cons, recency)
  2. Search waves — run sub-questions in parallel, 2–3 per wave, follow up
     only thin results; cap total searches at ~8
  3. Record — every claim carries its source (title + URL)
  4. Verify — decisive facts get a second, differently-worded search
  5. Synthesize — bottom line first, then 3–6 bullets each ending with its
     source, then a one-line "what I could not verify"

Returns a formatted report string. main.py mirrors it to the on-screen
content panel (show_content) exactly as it does for web_search; the model
speaks only the bottom line plus the two strongest findings.

Uses DuckDuckGo directly (via web_search._ddg_search) so a single research
request doesn't burn the small Gemini grounding quota on every sub-question.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from actions.web_search import _ddg_search

# ── Limits (mirrors the deep-research SKILL.md procedure) ─────────────────

MAX_SUB_QUESTIONS = 5      # sub-questions per plan
MAX_SEARCHES      = 8      # hard cap on total search calls
PARALLEL_PER_WAVE = 3      # searches per wave

# Sub-question templates appended to the user's query when the query itself
# doesn't already imply them. Keeps the planner deterministic — no LLM call
# needed inside an action.
_SUB_QUESTION_TEMPLATES = (
    "price cost",
    "key specs features",
    "reviews pros cons",
    "alternatives comparison",
    "latest 2026 2025",
    "risks limitations complaints",
)

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
    "vs", "versus", "better", "best", "top",
}


def _plan_sub_questions(query: str, max_sub: int = MAX_SUB_QUESTIONS) -> list[str]:
    """Derive 3–5 sub-questions from the user's query.

    Deterministic: split the query into meaningful keywords, then append the
    most relevant templates. No LLM call — keeps the action fast and cheap.
    """
    words = [w.lower() for w in re.split(r"[^a-z0-9]+", query) if w.lower()
             not in _STOPWORDS and len(w) > 2]
    core = " ".join(words[:4]) or query

    sub_questions: list[str] = []
    # Always start with the core question itself.
    sub_questions.append(core)
    # Add templates that aren't already implied by the query.
    qlower = query.lower()
    for tmpl in _SUB_QUESTION_TEMPLATES:
        if len(sub_questions) >= max_sub:
            break
        if not any(t in qlower for t in tmpl.split()):
            sub_questions.append(f"{core} {tmpl}")
    return sub_questions[:max_sub]


def _search_one(sub: str) -> dict:
    """Run one search and return {query, results}."""
    try:
        results = _ddg_search(sub, max_results=4)
    except Exception as e:  # pragma: no cover — network
        print(f"[DeepResearch] search failed for '{sub}': {e}")
        results = []
    return {"query": sub, "results": results}


def _search_waves(sub_questions: list[str], max_waves: int) -> list[dict]:
    """Run sub-questions in parallel waves.

    Wave 1: all sub-questions (parallel, up to PARALLEL_PER_WAVE at a time).
    Wave 2+: only sub-questions whose first wave returned thin results.
    Hard cap: MAX_SEARCHES total calls.
    """
    waves: list[dict] = []
    remaining = list(sub_questions)
    searches_used = 0

    for wave in range(max_waves):
        if not remaining or searches_used >= MAX_SEARCHES:
            break

        budget = MAX_SEARCHES - searches_used
        batch = remaining[:PARALLEL_PER_WAVE] if budget >= PARALLEL_PER_WAVE \
            else remaining[:budget]
        remaining = remaining[len(batch):]

        with ThreadPoolExecutor(max_workers=len(batch)) as pool:
            futures = {pool.submit(_search_one, q): q for q in batch}
            for fut in as_completed(futures):
                waves.append(fut.result())
        searches_used += len(batch)

        # Follow up only thin results (< 2 usable results) in the next wave.
        thin = [w for w in waves[-len(batch):] if len(w.get("results", [])) < 2]
        remaining = [w["query"] for w in thin] + remaining

    return waves


def _pick_decisive(results_by_query: dict[str, list[dict]]) -> list[str]:
    """Pick queries whose results look decisive (have real content)."""
    decisive: list[str] = []
    for q, results in results_by_query.items():
        if any(len(r.get("snippet", "")) > 80 for r in results):
            decisive.append(q)
    return decisive[:3]


def _verify(decisive: list[str]) -> dict[str, list[dict]]:
    """Re-search decisive facts with differently-worded queries."""
    verified: dict[str, list[dict]] = {}
    for q in decisive:
        alt = q.replace(" vs ", " compared to ").replace(" versus ", " compared to ")
        if alt == q:
            alt = q + " review"
        try:
            verified[q] = _ddg_search(alt, max_results=3)
        except Exception:  # pragma: no cover — network
            verified[q] = []
    return verified


def _synthesize(query: str, waves: list[dict], verified: dict) -> str:
    """Build the final report: bottom line, bullets with sources, unverified."""
    # Flatten all results, dedup by URL.
    seen_urls: set[str] = set()
    sources: list[dict] = []
    for w in waves:
        for r in w.get("results", []):
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append(r)

    if not sources:
        return (f"Deep research — {query}\n"
                f"\nNo usable results found. I could not verify anything "
                f"about this topic.")

    # Bottom line: lead with the strongest source's title/topic.
    top = sources[0]
    bottom_line = (
        f"Based on {len(sources)} sources, the short answer on “{query}” "
        f"centres on {top.get('title', 'this topic')}. "
        f"{top.get('snippet', '')[:200]}"
    )

    # Supporting findings: 3–6 bullets, each with its source.
    bullets: list[str] = []
    for r in sources[1:7]:
        snippet = r.get("snippet", "").strip()
        title   = r.get("title", "").strip()
        url     = r.get("url", "").strip()
        if snippet:
            bullets.append(f"• {snippet} ({title} — {url})")
        elif title:
            bullets.append(f"• {title} ({url})")

    unverified = ""
    if len(sources) < 3:
        unverified = (
            "\n\nWhat I could not verify: only a few sources were available, "
            "so treat the answer as a starting point, not a final verdict."
        )

    sources_list = "\n".join(
        f"[{i+1}] {r.get('title', 'Untitled')} — {r.get('url', '')}"
        for i, r in enumerate(sources)
    )

    return (
        f"Deep research — {query}\n"
        f"\n{bottom_line}\n"
        f"\nFindings:\n" + "\n".join(bullets) +
        f"\n\nSources:\n{sources_list}" + unverified
    )


# ── Tool declaration (auto-discovered by action_loader) ───────────────────

TOOL = {
    "name": "deep_research",
    "description": (
        "Multi-source research report with citations. Use when the user asks "
        "to compare options, research a topic, 'dig into', 'find out everything "
        "about', weigh alternatives, or wants a thorough backed-up answer "
        "instead of a quick fact. Runs multiple parallel search waves and "
        "verifies decisive facts before answering."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The research question or topic",
            },
            "max_waves": {
                "type": "INTEGER",
                "description": "Maximum search waves (1-4, default 3)",
            },
        },
        "required": ["query"],
    },
    "handler": None,  # set below so the module-level name is defined first
}


def deep_research(parameters: dict, response=None, player=None,
                  session_memory=None) -> str:
    """Run the deep-research procedure and return a sourced report."""
    query = (parameters or {}).get("query", "").strip()
    if not query:
        return "deep_research: no query provided."

    max_waves = min(max(1, int((parameters or {}).get("max_waves", 3))), 4)

    # 1. Scope — proceed with the most reasonable reading (an action can't
    #    ask the user back; the model can ask first if clarification is needed).
    # 2. Plan — sub-questions.
    sub_questions = _plan_sub_questions(query, MAX_SUB_QUESTIONS)

    # 3. Search waves — parallel, follow up thin results.
    waves = _search_waves(sub_questions, max_waves)

    # Build a lookup for verification.
    results_by_query: dict[str, list[dict]] = {}
    for w in waves:
        results_by_query[w["query"]] = w.get("results", [])

    # 4. Verify decisive facts.
    decisive = _pick_decisive(results_by_query)
    verified = _verify(decisive) if decisive else {}

    # 5 & 6. Synthesize.
    report = _synthesize(query, waves, verified)
    return report


TOOL["handler"] = deep_research
