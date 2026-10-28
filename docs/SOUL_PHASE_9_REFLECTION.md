# Soul Phase 9 — Evidence-based reflection

Date: 2026-10-27
Status: Complete

## Delivered

- meaningful-event qualification and six-hour minimum interval
- privacy and reflection-enable gates
- bounded, non-sensitive evidence windows
- strict JSON/object candidate schema
- unknown-field and oversized-output rejection
- local confidence calculation and activation thresholds
- evidence-reference verification
- forbidden constitution/safety/permission/diagnosis/dependency mutations
- active-trait contradiction rejection
- deterministic deduplication
- candidate staging before activation
- failure accounting and exponential backoff
- asynchronous single-flight daemon runner
- revisioned persistence and audit events through `SoulService`

## Model authority boundary

The generator may propose only `name`, `value`, `evidence_refs`, and `rationale`. It cannot set confidence, status, permissions, safety, constitution, tool access, or activation. Unknown fields fail the entire reflection result.

Confidence is calculated locally from verified unique evidence. One or two evidence items remain candidates; three supported items reach the activation threshold. Unsupported evidence references are rejected.

## Privacy and reliability

Sensitive evidence never reaches the generator. Provider timeout, malformed JSON, hostile output, or exceptions increment a bounded failure counter and leave identity/constitution untouched. Backoff grows exponentially to a six-hour cap. Reflection is single-flight and runs off the user-response path.

## Contradictions

A proposed value that conflicts with an existing active trait of the same name is rejected for later clarification rather than silently replacing it.

## Persistence

Completed and failed reflection outcomes are persisted through revision-checked Soul transactions with `soul.reflection_completed` or `soul.reflection_failed` audit events. Context cache is invalidated only after durable state mutation.

## Validation

- Focused reflection, commitment, relationship, and context tests: **40 passed**
- Full repository suite: **709 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 9 gate: PASSED.** Hostile or malformed model output cannot alter constitution, safety, permissions, or active conflicting traits; sensitive evidence is withheld; failures back off; and reflection never blocks the user-response path.

Phase 10 will implement restart-safe initiative policy, quiet hours, interruption budgets, cooldowns, and heartbeat candidate scoring.
