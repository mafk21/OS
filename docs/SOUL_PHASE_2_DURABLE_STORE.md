# Soul Phase 2 — Durable store and recovery

Date: 2026-10-27
Status: Complete

## Delivered

- `core/soul/events.py`
  - immutable validated audit event records
  - strict fields, bounds, timestamps, and JSON representation
- `core/soul/store.py`
  - atomic same-directory temporary writes and `os.replace`
  - file and best-effort directory `fsync`
  - process-local reentrant locking
  - optimistic revision checks
  - full-state validation before persistence
  - last-known-good previous-revision backup
  - corruption/future-schema quarantine
  - validated backup restoration
  - safe unsaved defaults when no valid state exists
  - append-only bounded JSONL audit stream
  - interrupted-commit audit repair
  - post-durability listeners
  - deterministic fault-injection checkpoints
- `.gitignore`
  - Soul audit, temporary, invalid, and quarantine runtime artifacts remain private
- `tests/test_soul_store.py`
  - initialization, transactions, stale revisions, immutability boundaries, recovery, quarantine, future versions, interruption stages, audit repair, malformed audit records, concurrency, listeners, and input validation

## Transaction order

1. Lock and load validated current state.
2. Check the caller's expected revision.
3. Apply one typed mutation.
4. Re-parse the complete serialized candidate.
5. Prevent runtime changes to creation time, schema version, or constitution version.
6. Assign the next revision and trusted store timestamp.
7. Atomically persist the current revision as backup.
8. Atomically persist the new current revision.
9. Append and flush its audit event.
10. Release the lock.
11. Notify listeners without allowing listener failure to roll back state.

## Recovery behavior

- Valid current state wins.
- Invalid current state is quarantined and never consumed as instructions.
- A valid backup is atomically restored and a recovery event is recorded.
- Invalid backups are also quarantined.
- If neither is valid, safe Brother-Guardian defaults are returned without pretending they were durably saved.
- If a process stops after state replacement but before audit append, the next load detects the revision gap and writes `soul.audit_recovered`.
- Temporary files are cleaned on handled write failures.

## Important semantics

A `SoulStoreError` exposes `committed=True` when the new state was already atomically replaced but a later audit/checkpoint failed. Callers must reload instead of blindly retrying. This prevents accidental duplicate mutations.

The backup intentionally contains the immediately preceding validated revision after a mutation. It is therefore useful if the current file is later corrupted. First-run initialization writes both current and backup defaults.

## Validation

- Phase 1 + Phase 2 focused tests: **39 passed**
- Python compilation: passed
- `git diff --check`: passed

Full repository regression results are recorded in the completion commit/turn.

## Gate result

**Phase 2 gate: PASSED.** The current or immediately preceding validated state remains recoverable across simulated failures before replacement, during temporary-file persistence, after state replacement, and during audit persistence. Partial or future-version content is never loaded as Soul state.

Next phase: explicit, sequential, idempotent migrations and compatibility import from existing companion preferences. Runtime prompt wiring remains deferred.
