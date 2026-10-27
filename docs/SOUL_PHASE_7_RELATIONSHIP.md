# Soul Phase 7 — Relationship continuity

Date: 2026-10-27
Status: Complete

## Delivered

- typed relationship claims, kinds, statuses, sensitivity, and contradictions
- deterministic evidence-derived claim and contradiction IDs
- explicit versus inferred evidence separation
- confidence reinforcement without duplicate claims
- explicit recent-statement precedence
- disputed inference handling
- sensitive-data explicit-consent requirement
- bounded active-only summaries
- relationship stages derived only from active evidence
- selective forgetting that removes claims, contradictions, and private values
- privacy-toggle enforcement
- schema v2-to-v3 migration
- canonical-context integration with untrusted-data escaping
- explicit correction integration from adaptive style learning
- verified durable-task milestone integration

## Claim types

- preference
- correction
- milestone
- trusted workflow
- shared reference

Every claim contains a stable ID, subject, value, active/disputed/superseded status, sensitivity, explicitness, confidence, evidence count and references, and first/last observation timestamps.

## Contradictions

A repeated identical claim reinforces confidence and evidence without duplication. A conflicting inferred claim marks both alternatives disputed and excludes both from prompt summaries until clarified. A conflicting explicit recent statement supersedes the older claim while preserving an attributable contradiction record.

## Sensitive information

Sensitive claims cannot be inferred. They require explicit user evidence. Relationship continuity does not diagnose or silently infer health, religion, politics, sexuality, or dependency.

## Memory ownership

`memory/memory_manager.py` remains authoritative for factual personal memory. Soul relationship records store continuity evidence and interaction meaning; they do not replace the factual memory store or task executor.

## Forgetting

Selective forgetting removes every matching claim and related contradiction. The audit event records only that user-requested relationship forgetting occurred; it does not retain the forgotten subject or private value.

## Relationship stages

- `new`: fewer than three active claims
- `familiar`: at least three active claims
- `trusted`: at least eight active claims including at least two milestone/trusted-workflow markers

Disputed and superseded claims do not advance the relationship stage.

## Runtime evidence

- Newly detected explicit communication corrections create a correction claim and an explicit-correction affect event.
- Verified durable task completions create a milestone claim using only stable task ID and completion class.
- Failed, uncertain, cancelled, expired, or evidence-free tasks do not create milestones.

All runtime learning also requires the staged Soul flag, adaptive learning, and relationship privacy control.

## Operational boundaries

Relationship state cannot alter tools, permissions, confirmations, safety rules, or claim task completion. Canonical context labels summaries as evidence-backed untrusted data and excludes disputed/superseded claims.

## Validation

- Focused Soul, relationship, affect, provider, companion, and long-task tests: **117 passed, 1 warning**
- Full repository suite: **692 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 7 gate: PASSED.** Unsupported inference cannot become active relationship context, explicit contradictions resolve predictably, disputed/superseded claims stay out of prompts, sensitive inference fails closed, and forgetting immediately removes private content from state and context.

Phase 8 will project real commitments and coaching state without duplicating long-task execution.
