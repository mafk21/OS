---
name: deep-research
description: Multi-source research report with citations — use when the user asks to compare options, research a topic, "dig into", "find out everything about", weigh alternatives, or wants a thorough backed-up answer instead of a quick fact.
---

# Deep research

Turn a vague question into a short, sourced report. This is a PROCEDURE, not
a search — a single `web_search` call is never enough for this skill.

## When to use

Comparison questions ("which laptop…", "X vs Y"), purchase/advice decisions,
"research …", "find out everything about …", anything where the user expects
evidence rather than a one-liner. For a quick fact, just answer normally.

## Procedure

1. **Scope** (one round max): if the request is missing budget, purpose, or
   constraints that would change the recommendation, ask ONE compact question.
   Otherwise proceed with the most reasonable reading.
2. **Plan**: silently pick 3–5 sub-questions that must be answered (price,
   key specs/reviews, risks/cons, recency). Do not read the plan aloud.
3. **Search, in waves**: run `web_search` with one sub-question per call,
   batching 2–3 calls in parallel when they are independent. Follow up only
   the sub-questions whose first wave was thin — cap total searches at ~8.
4. **Record as you go**: keep a running list of (claim → source). Never carry
   a number or quote forward without the source that produced it.
5. **Verify the decisive facts**: anything the recommendation hinges on gets a
   second, differently-worded search. If two sources disagree, say so rather
   than picking the convenient one.
6. **Synthesize**: write the answer as — one-paragraph bottom line first
   (the actual recommendation), then 3–6 bullets of supporting findings, each
   ending with its source in parentheses, then a one-line "what I could not
   verify".
7. **Deliver**: `show_content` with the full report so the user can read it,
   and speak only the bottom line plus the two strongest findings. Long
   reports read aloud are worse than useless.

## Pitfalls

- Do not stream findings as they arrive — the user gets one report, not a
  running commentary of half-facts.
- A search result is not a fact. If you cannot name the source, do not state
  the claim.
- If every wave fails (network/search errors), say that plainly and answer
  from what you know, labelled as unverified. Never invent citations.

## Verification

Before answering: 3+ distinct sources? Bottom line present? Every number
traceable? Anything unverifiable named as such?
