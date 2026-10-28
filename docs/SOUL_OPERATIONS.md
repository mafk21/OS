# Soul operations, schema, troubleshooting, and rollback

## Runtime controls

Soul is local-first and disabled by default through `soul_enabled`. Enable or disable it in Soul Studio → Privacy/Control. Disabling is an immediate context rollback: it stops Soul identity injection and returns provider prompt composition to the complete legacy personality path. It does not delete `memory/soul.json`, its backup, audit history, or migration sources.

Reflection and initiative have separate controls. For diagnosis, disable initiative first, then reflection, then the Soul runtime. Existing tools, long tasks, companions, voices, and provider selection continue independently.

## Schema 4

The authoritative state is `memory/soul.json`. Schema 4 contains:

- immutable schema and constitution versions;
- revision, creation, and update timestamps;
- bounded identity ranges;
- bounded affect values, baselines, daily deltas, and evidence causes;
- evidence-backed relationship claims, contradictions, milestones, and unresolved commitment references;
- staged/active/rejected learned traits and reflection status;
- initiative policy plus persisted budget, snooze, cooldown, and topic outcomes;
- privacy controls and completed migration IDs.

`memory/soul.backup.json` is the previous validated revision. `memory/soul.events.jsonl` is a bounded append-only audit stream. Invalid state is moved to `memory/soul.quarantine/`; future schemas are never consumed by an older runtime. Writes use a same-directory temporary file, flush/fsync, and atomic replacement.

Commitments shown in Studio are read-only projections from authoritative long-task and memory stores. They are not persisted as a second executor or task authority.

## Studio diagnostics

Privacy/Control → Soul Diagnostics displays schema, revision, last successful save, last validated backup, last reflection, canonical context bytes, completed migrations, and degraded mode. Recovery and revision-conflict notices appear above the active view.

## Troubleshooting

1. **Soul unavailable:** use Retry. Check filesystem permissions for `memory/` and free disk space. The application continues through the legacy path if Soul cannot load.
2. **Recovery warning:** inspect the quarantined file and audit log; do not copy it over current state. Export the recovered state from Studio before further edits.
3. **Revision conflict:** Studio automatically reloads current state. Reapply only the intended edit after reviewing the latest values.
4. **No initiative:** verify runtime, privacy initiative, policy enabled, quiet hours, timezone, snooze, daily budget, cooldown, and explicit rest state. Restart does not reset these gates.
5. **No learning/reflection:** verify personalization, relationship learning, and reflection controls. Candidate traits require sufficient evidence and user acceptance.
6. **Provider inconsistency:** verify Soul is enabled and inspect the canonical context preview. All supported provider paths consume that same context; credentials are never included in export or diagnostics.

## Safe rollback

1. Disable Soul Runtime in Studio, or set `soul_enabled` to false through the existing local configuration control.
2. Restart only if diagnosing provider session caching; state rollback itself is immediate.
3. Confirm legacy personality wording is active and ordinary tools still work.
4. Preserve Soul files for diagnosis. Do not delete state unless the user explicitly chooses Reset.
5. To re-enable, turn Soul Runtime on. The same revision and learned state resume after validation.

If state is corrupt, allow automatic quarantine/backup recovery. Manual restoration should use a validated export and a supported migration path, never hand-edit revision or constitution fields.

## Release validation

The release gate covers concurrent mixed writers, stale revisions, fault injection around atomic persistence, restart recovery, long-duration clocks, quiet hours and backoff, Unicode/space paths, context latency and size, export redaction, secret scanning, populated-profile rollback, full Python regression, compilation, TypeScript, production HUD build, and diff checks. Native Windows/macOS filesystem behavior is additionally exercised by the cross-platform CI matrix.
