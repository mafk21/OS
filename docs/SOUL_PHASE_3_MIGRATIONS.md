# Soul Phase 3 — Migration and compatibility

Date: 2026-10-27
Status: Complete

## Delivered

- `core/soul/migrations.py`
  - pure, sequential, one-version-at-a-time migration engine
  - deep-copy semantics; source objects are never mutated
  - strict future-version rejection
  - strict unknown-field rejection
  - prototype schema v0 to strict schema v1 migration
  - migration provenance in both result and state
  - deterministic, idempotent import of companion behavior interviews
  - deterministic, idempotent import of adaptive learned rules
  - bounded source size and strict source validation
  - evidence references and migration origin on every imported trait
- `core/soul/store.py`
  - automatic migration of valid older state during load
  - exact pre-migration byte archive before rewriting
  - atomic rewrite of current and backup into the new schema
  - `soul.migrated` audit event
  - no repeated migration/archive/event on later loads
- `tests/fixtures/soul_v0.json`
  - real old-schema fixture
- `tests/test_soul_migrations.py`
  - sequential migration, idempotency, source preservation, malformed/future data rejection, companion import, deterministic IDs, archival, and no-repeat coverage
- `.gitignore`
  - pre-migration archives remain private runtime data

## Compatibility import semantics

Existing `memory/companions.json` remains untouched and authoritative during the compatibility window. Its behavior interview answers and adaptive learned rules are converted into active learned traits with:

- deterministic hashed IDs
- explicit evidence references to their original companion source IDs
- `migration` origin
- confidence appropriate to explicit interview answers versus inferred adaptive rules
- a single `compat-companions-v1` completion marker

Running the import repeatedly against an already imported state is a no-op. Running it again from the same pre-import state produces identical trait IDs, allowing a transaction retry without duplicates.

The active specialist companion, theme, and custom companion definitions are intentionally not copied into Soul. They remain owned by `core/companions.py` and will be applied as role/presentation overlays later.

## Schema migration semantics

1. Parse raw JSON as untrusted data.
2. Read the current schema version.
3. Reject non-integer, negative, or future versions.
4. Apply exactly one registered migration at a time.
5. Verify that each migration advances exactly one version.
6. Validate the complete final state through `SoulState`.
7. Preserve the exact original bytes in `memory/soul.migrations/`.
8. Atomically write the migrated current state and validated backup.
9. Append a migration audit event.

No old state is overwritten before the migrated result validates and the exact source bytes are durably archived.

## Validation

- Focused Soul tests: **52 passed**
- Python compilation: passed
- `git diff --check`: passed

Full repository regression results are recorded in the completion commit/turn.

## Gate result

**Phase 3 gate: PASSED.** Applying schema migration twice produces identical state with no second migration. Companion compatibility import is deterministic and idempotent, retains provenance, and never mutates or deletes source data. Future, malformed, oversized, and instruction-like unknown fields fail closed.

Next phase: canonical provider-independent Soul context rendering, escaping, precedence, section budgets, deterministic fingerprints, and snapshot tests. Runtime provider wiring remains deferred until Phase 5.
