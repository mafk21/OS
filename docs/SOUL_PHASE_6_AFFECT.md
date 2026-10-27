# Soul Phase 6 — Bounded affect engine

Date: 2026-10-27
Status: Complete

## Delivered

- `core/soul/affect.py`
  - typed event vocabulary
  - deterministic event-to-delta mapping
  - persisted per-dimension baselines
  - persisted per-day accumulation accounting
  - independent daily caps
  - hard `[0,1]` state bounds
  - dimension-specific half-life decay
  - lazy wall-clock decay; no polling worker
  - transparent explanations and causes
  - strict evidence references and timestamps
  - Soul-state application helper
- `core/soul/models.py`
  - schema version 2
  - immutable `AffectDelta`
  - persisted baselines, daily deltas, daily date, causes, and update timestamp
- `core/soul/migrations.py`
  - sequential v1-to-v2 migration
  - existing values become initial baselines
  - daily accounting starts at zero
  - v0 sources pass through both v0-to-v1 and v1-to-v2
- `core/soul/service.py`
  - transactional affect event persistence
  - privacy-toggle enforcement
  - cache invalidation after mutation
  - staged runtime adapter
  - verified durable-task completion adapter
- `main.py`
  - registers the stable long-task completion adapter
- `tests/test_soul_affect.py`
  - deterministic mappings, decay, time reversal, daily caps, date reset, rest behavior, malformed inputs, explanations, context isolation, import isolation, schema migration, persistence, audit, adapter evidence checks, and privacy suppression

## Dimensions

- calm
- energy
- concern
- confidence
- curiosity
- rapport

These are bounded expressive variables. They are not assertions that JARVIS experiences human or biological emotion.

## Accepted events

- verified task success
- repeated verified failure
- explicit correction accepted
- commitment nearing deadline
- meaningful novel topic
- long inactivity
- respectful disagreement resolved
- user-requested rest

Arbitrary event names are rejected. There is no jealousy, anger, possessiveness, attachment pressure, or mood-driven punishment event.

## Update order

1. Validate typed event, timestamp, and evidence reference.
2. Reject an event older than the persisted expressive state.
3. Lazily decay values toward their own baselines.
4. Reset daily accounting if the local timestamp date changed.
5. Read the fixed event delta.
6. Apply the remaining per-dimension daily allowance.
7. Clamp every resulting value to `[0,1]`.
8. Append a bounded attributable cause.
9. Persist through one revisioned Soul transaction.
10. Emit `soul.affect_changed` and invalidate the context cache.

## Decay

Decay uses deterministic exponential half-lives. Rapport decays much more slowly than transient concern or energy. No background thread wakes merely to adjust numbers; decay is calculated when an event or explicit evaluation occurs.

If time does not advance, state is unchanged. Event timestamps older than the current state are rejected to prevent replay or clock-order corruption.

## Daily caps

Every dimension has an independent daily cap. Repeating the same event cannot push a dimension indefinitely. Numerical state is also hard-clamped, so daily accounting and absolute bounds both apply.

## Rest behavior

`user_requested_rest` raises calm and lowers concern/energy. It never treats rest as rejection or failure. Later initiative/coaching phases must continue to enforce the stronger rest/health suppression policy.

## Operational isolation

The affect module imports no:

- actions
- tool registry
- plugin registry
- confirmation layer
- OS control
- provider adapter
- Gemini/OpenAI adapter

Context comparison tests prove an affect event changes only `[CURRENT EXPRESSIVE STATE]`; constitution, identity, relationship, commitments, learned preferences, reflection, and edition remain byte-identical.

Affect cannot execute tools, change permissions, bypass confirmation, classify urgency, alter safety policy, or claim task completion.

## Verified runtime source

The first connected production event is durable long-task completion. The adapter accepts a record only when:

- status is exactly `completed`
- a stable task ID exists
- completion evidence exists
- staged Soul runtime is enabled
- affect privacy control is enabled

Failed, uncertain, cancelled, expired, missing-evidence, and missing-ID records are ignored. The evidence reference stores only the task ID and verified completion class, not arbitrary output content.

## Schema migration

Schema v1 states migrate to v2 one step at a time. Existing current affect values become baselines so an upgrade does not unexpectedly change personality. Daily accumulation begins at zero on the date of the last affect update. Exact pre-migration bytes remain archived by the existing store migration path.

## Validation

- Focused Soul, affect, migration, provider, and long-task tests: **101 passed**
- Full repository suite: **680 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 6 gate: PASSED.** Event updates and decay are deterministic, persisted values remain bounded, daily caps survive restart, v1 state migrates safely, context changes are isolated to expressive wording, and the affect module has no operational-authority dependencies.

Phase 7 will add evidence-backed relationship continuity, contradiction handling, milestones, corrections, forgetting, and bounded summaries without duplicating factual memory.
