# Soul Phase 1 — Typed domain model

Date: 2026-10-27  
Edition focus: Male  
Status: Complete

## Delivered

- `core/soul/constitution.py`
  - immutable, ordered constitutional rules
  - independent constitution version
  - deterministic renderer
- `core/soul/models.py`
  - strict typed schema with no I/O or provider dependency
  - Brother-Guardian identity defaults
  - bounded identity traits
  - bounded expressive-state dimensions
  - relationship, learned-trait, initiative, reflection, and privacy records
  - schema and constitution version rejection
  - ISO-8601 timezone validation
  - finite numeric bounds and list/text limits
  - recursive unknown-field rejection
  - JSON-safe serialization and strict round trip
- `core/soul/__init__.py`
  - narrow public API
- `tests/test_soul_models.py`
  - 20 focused Phase 1 tests

## Male overlay

The initial Male overlay is commanding, grounded, assertive, protective, steady, concise, and restrained in humor. It changes delivery only. It cannot change permissions, tools, memory, confirmation behavior, safety, truth standards, or technical capability.

## Safe defaults

- reflection disabled
- initiative disabled
- privacy controls explicit
- affect bounded to `[0,1]`
- learned traits bounded and provenance-bearing
- no persistence or provider calls

## Validation

- Phase 1 tests: **20 passed**
- Full suite: **613 passed, 28 skipped, 9 warnings, 17 subtests passed**
- Python compilation: passed
- TypeScript: passed
- `git diff --check`: passed

## Gate result

**Phase 1 gate: PASSED.** Invalid values, unknown fields, NaN/infinity, oversized content, malformed timestamps, future schema versions, duplicate trait IDs, and invalid revision ordering are rejected.

Next phase: durable store and recovery. This phase will add atomic persistence, optimistic revisions, backup, quarantine, audit events, and fault-injection tests without wiring Soul into runtime prompts.
