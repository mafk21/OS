# Soul Phase 13 — Prompt reconciliation and cleanup

Date: 2026-10-28
Status: Complete

## Reconciliation result

The runtime now selects exactly one personality authority:

- with `soul_enabled=false`, legacy identity and personality wording remains intact for immediate rollback;
- with `soul_enabled=true` and a validated Soul context, the canonical Soul owns identity, relationship, affect, learned style, and edition presentation;
- operational instructions remain shared in both paths, including tools, skills, execution truthfulness, interruption behavior, language selection, confirmations, memory lookup, and capability limits.

The legacy operator persona introduction and fixed humor policy are marker-delimited in `core/prompt.txt`. `reconcile_legacy_prompt()` removes those blocks only while Soul context is active and always removes internal marker syntax before provider delivery. Malformed or nested markers fail validation rather than silently deleting unrelated instructions.

## Provider and companion behavior

Both live-provider and offline/local prompt assembly use reconciliation. Typed fallback already uses canonical Soul context directly when enabled. Telegram uses canonical Soul context and excludes migrated behavior personalization while retaining custom skills and active specialist scope. Specialist tool restrictions remain enforcement logic, not personality authority.

Name, edition, and address instructions continue to come from the legacy dynamic identity block only when Soul is disabled. When enabled, the canonical Soul edition section supplies those fields, avoiding stacked Male/Female or address instructions.

## Validation

- Focused reconciliation, provider, and companion tests: **18 passed, 1 warning**
- Complete regression suite: **731 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript and production HUD build: passed
- `git diff --check`: passed

## Gate result

**Phase 13 gate: PASSED.** No provider path stacks the reviewed legacy personality blocks with canonical Soul identity, operational rules remain available, and the feature flag restores the legacy personality path without migration or restart-sensitive state changes.

Phase 14 will perform concurrency, crash/restart, simulated-clock, portability, performance, privacy, rollback, and release hardening.
