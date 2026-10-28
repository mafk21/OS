# Soul Phase 10 — Restart-safe initiative policy

Date: 2026-10-27
Status: Complete

## Delivered

- schema v4 persisted initiative policy
- timezone-aware quiet hours, including overnight ranges
- persisted local daily date and interruption count
- persisted snooze deadline
- persisted per-topic last delivery, ignored count, and outcome
- exponential per-topic cooldown capped at 24 hours
- confidence, value, and urgency candidate scoring
- expiration and confidence filtering
- reservation persisted before heartbeat delivery
- fail-closed heartbeat integration when Soul is enabled
- unchanged legacy heartbeat behavior when Soul is disabled

## Selection order

1. Feature enabled
2. Quiet hours
3. Snooze
4. Daily interruption budget
5. Candidate expiration
6. Confidence floor
7. Per-topic cooldown/backoff
8. Value/urgency/confidence scoring
9. Persist delivery reservation
10. Send at most one heartbeat suggestion

## Restart behavior

All policy times use timezone-aware wall-clock timestamps. Restart cannot reset daily budgets, snooze, ignored counts, or topic cooldowns. Schema v3 state migrates with zero interruptions and empty topic history without inventing prior deliveries.

## Safety and autonomy

Initiative only permits a suggestion to be delivered. It cannot execute a tool or bypass confirmation. Disabled policy, quiet hours, snooze, exhausted budget, invalid timezone, or persistence failure suppresses delivery. Existing explicit rest/health coaching suppression remains authoritative.

## Validation

- Focused initiative, schema, affect, relationship, and heartbeat tests: **80 passed**
- Full repository suite: **717 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 10 gate: PASSED.** Restart cannot reset budgets, snooze, outcomes, or cooldowns; quiet hours and exhausted budgets suppress delivery; and persistence is reserved before heartbeat speech.

Phase 11 will expose validated backend APIs for Soul Studio.
