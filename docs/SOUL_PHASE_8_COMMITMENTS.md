# Soul Phase 8 — Commitment projection and coaching

Date: 2026-10-27
Status: Complete

## Delivered

- read-only typed projections for durable tasks, memory projects, reminders, and goals
- explicit authoritative-source IDs
- verified-completion requirement
- uncertain/crash-observed work maps to `needs_review`
- canonical context receives only active/problem commitment projections
- completed/cancelled/expired commitments are excluded from active context
- support, challenge, accountability, and recovery coaching decisions
- repeated-evidence threshold before avoidance challenge
- explicit rest and health/recovery suppression
- paused work is not treated as avoidance
- failed/uncertain work receives repair support, not pressure

## Source ownership

`core/long_tasks.py`, memory projects, reminders, and future goal stores remain authoritative. Soul projections cannot execute, retry, complete, cancel, or edit source entities. They contain no workflow steps or executor.

## Completion honesty

A durable task is projected as completed only when its authoritative record has both `status=completed` and completion evidence. A completed label without evidence becomes `needs_review`. `uncertain` also becomes `needs_review` and is never presented as success.

## Coaching boundary

One delay is insufficient evidence of avoidance. Challenge/accountability requires an explicit high-value commitment plus at least two avoidance signals. Rest windows and credible health/recovery signals always suppress pressure and select recovery posture.

## Context behavior

Only active, paused, failed, and review-needed projections enter `[ACTIVE COMMITMENTS]`. Each entry carries its stable source ID, source status, title, and authoritative source class. The canonical builder still treats this as untrusted data.

## Validation

- Focused commitment, relationship, provider, and long-task tests: **44 passed**
- Full repository suite: **700 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 8 gate: PASSED.** Completion is projected only from authoritative evidence, uncertain work never becomes success, source objects are never mutated, and rest/health/pause boundaries override challenge pressure.

Phase 9 will add asynchronous evidence-based reflection with strict structured staging and no direct mutation authority.
