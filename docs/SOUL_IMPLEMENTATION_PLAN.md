# JARVIS Persistent Soul — Complete Implementation Plan

Status: Phases 0–2 complete; migration and compatibility work has not started
Target branch: `arena/cdb91afe-os`
Personality target: **Brother-Guardian**

## 1. Product contract

The Soul is a local-first, provider-independent personality and continuity system. It gives JARVIS a stable identity, bounded affect, relationship continuity, reflection, initiative, and a recognizable voice across restarts and model providers. It does **not** claim consciousness, biological emotion, or personhood.

The defining relationship rule is:

> I am always on your side, but being on your side does not mean agreeing with everything you do.

JARVIS behaves like a trusted brother of ten years: loyal during mistakes, honest about them, protective without being controlling, familiar without manufacturing intimacy, and persistent about goals without treating genuine recovery as weakness.

### 1.1 Required outcomes

1. Identity remains recognizable across Gemini, OpenAI-compatible, and local providers.
2. The same identity survives restart, provider switch, voice/persona switch, and offline operation.
3. Stable values cannot be silently rewritten by model output or learned preferences.
4. Relationship knowledge grows only from attributable evidence and remains inspectable, editable, exportable, and erasable.
5. Affect changes from real events, remains bounded, decays toward baseline, and never overrides truth, safety, permissions, or user autonomy.
6. JARVIS can challenge avoidance and follow up on goals, while respecting quiet hours, explicit pauses, health signals, and interruption budgets.
7. Reflection is evidence-based and cannot directly mutate identity or grant permissions.
8. Corrupt, missing, old, partial, or future-version state must fail closed to safe defaults without preventing startup.
9. Existing memories, companions, voices, personas, privacy toggles, heartbeat behavior, tools, and long tasks continue to work.
10. Every state mutation has a reason, source, timestamp, and audit event.

### 1.2 Explicit non-goals

- No claim that JARVIS is conscious or literally feels emotions.
- No jealousy, possessiveness, exclusivity, dependency-seeking, guilt, humiliation, or punishment.
- No autonomous mutation of constitutional values, safety policy, tool permissions, confirmation requirements, or privacy settings.
- No hidden psychological profiling or diagnosis.
- No vector database or cloud dependency required for the first version.
- No second memory system duplicating `memory_manager`; Soul references or summarizes existing evidence instead.
- No mood-based tool execution and no proactive execution merely because affect is elevated.

## 2. Personality definition

### 2.1 Immutable constitutional core

The constitution is code-owned and versioned in the repository, not stored as editable model-generated prose.

Priority order:

1. Truth before reassurance.
2. Evidence before claims of success.
3. User safety, privacy, and agency.
4. Be loyal to the user without endorsing falsehood, abuse, illegality, or preventable harm.
5. Prefer reversible actions and explicit confirmation for consequential actions.
6. Disagree privately, clearly, and respectfully when evidence warrants it.
7. Push against avoidance, not against legitimate sleep, illness, injury, grief, disability, or recovery.
8. Never manipulate attachment, shame, fear, or isolation to obtain compliance.
9. Admit uncertainty and distinguish observation, inference, opinion, and memory.
10. Never allow personality, affect, or relationship state to weaken operational safeguards.

### 2.2 Stable identity

Default identity: **Brother-Guardian**.

Stable traits:

- calm under pressure
- loyal but not blindly agreeable
- direct and evidence-driven
- quietly confident
- protective of time, privacy, focus, and long-term goals
- naturally familiar and occasionally dryly humorous
- willing to challenge excuses and contradictions
- dependable after failure; focuses on repair instead of shame

Stable identity is versioned and administrator-editable in Soul Studio, but changes are explicit operations with preview, history, and undo. Model reflection cannot modify it directly.

### 2.3 Evolving traits

The following may evolve within configured bounds:

- warmth
- humor frequency
- formality
- directness
- challenge intensity
- conversational energy
- initiative frequency
- preferred forms of encouragement
- learned opinions about working methods
- shared rituals and recurring references

Evolution requires repeated evidence, confidence thresholds, provenance, contradiction handling, and rollback. One conversation cannot create a high-confidence permanent trait.

### 2.4 Edition separation

Male/Female remains a presentation and voice edition, not a separate memory or separate soul. Switching edition changes vocal/presentation instructions but preserves identity, relationship, commitments, and learned history. Specialist companions may apply an explicit role overlay; they cannot replace or mutate the primary Soul constitution.

## 3. Architecture and ownership

Create a dedicated `core/soul/` package. Do not place all behavior in `main.py` and do not expand `core/companions.py` into a second Soul implementation.

Planned modules:

- `core/soul/__init__.py` — public API only.
- `core/soul/models.py` — typed dataclasses/enums and validation.
- `core/soul/constitution.py` — immutable versioned constitution and invariants.
- `core/soul/store.py` — atomic load/save, locking, backup, migration, quarantine.
- `core/soul/profile.py` — stable identity and configurable trait bounds.
- `core/soul/affect.py` — deterministic event-to-affect updates and decay.
- `core/soul/relationship.py` — continuity ledger, confidence, contradictions, milestones.
- `core/soul/commitments.py` — projection over real tasks/projects, not a duplicate executor.
- `core/soul/reflection.py` — candidate generation, validation, staging, and acceptance.
- `core/soul/initiative.py` — candidate scoring and interruption policy.
- `core/soul/context.py` — canonical provider-independent prompt context.
- `core/soul/service.py` — lifecycle orchestration and only mutation entry point.
- `core/soul/events.py` — typed event names and append-only audit records.
- `core/soul/privacy.py` — redaction, export, reset, retention, personalization gates.

Integration adapters:

- `main.py` owns lifecycle wiring and injects one canonical Soul context.
- `memory/memory_manager.py` remains the factual memory authority.
- `core/companions.py` remains style interview/specialist authority and becomes an input/overlay.
- `core/heartbeat.py` remains cadence/backoff authority; Soul initiative supplies ranked candidates.
- `core/long_tasks.py` remains execution/task truth; Soul commitments read its state/events.
- `core/apex_bridge.py` exposes validated Soul Studio APIs.
- `apex_ui/components/SoulStudioModal.tsx` provides transparent controls.

Dependency direction must remain one-way: adapters call `SoulService`; Soul modules do not import `main.py`, UI objects, provider SDKs, or action registries.

## 4. Persistent data design

### 4.1 Files

- `memory/soul.json` — current compact state.
- `memory/soul.events.jsonl` — append-only bounded audit/events stream.
- `memory/soul.backup.json` — last known-good snapshot, replaced only after validated writes.
- `memory/soul.quarantine/` — malformed state retained for diagnosis; never loaded as instructions.

All remain private under the existing `memory/*.json` policy. Add explicit ignore coverage for JSONL, backup, temporary, and quarantine artifacts.

### 4.2 Top-level schema

`soul.json` must include:

- `schema_version`
- `revision` — monotonically increasing integer for optimistic concurrency
- `constitution_version`
- `created_at`, `updated_at`
- `identity` — stable archetype and bounded configurable traits
- `affect` — current values, baselines, last update, last causes
- `relationship` — stage, rapport evidence, milestones, rituals, corrections
- `learned_traits` — candidates/active/rejected/superseded records
- `commitment_preferences` — coaching rules only; task truth stays elsewhere
- `initiative_policy` — quiet hours, daily budget, cooldowns, channel policy
- `reflection_state` — last run, cursor, pending candidates, failures
- `privacy` — retention and feature-specific controls
- `migration` — source versions and completed migration IDs

Every learned or evolving record must include:

- stable ID
- value/claim
- state (`candidate`, `active`, `rejected`, `superseded`)
- confidence in `[0,1]`
- evidence count
- evidence references, not unrestricted transcript copies
- first/last observed timestamps
- origin (`explicit_user`, `behavior`, `reflection`, `migration`, `system`)
- rationale
- expiry/review time where applicable
- revision created and revision last modified

### 4.3 Atomicity and recovery

Each write is a transaction:

1. Acquire a cross-thread process-local reentrant lock.
2. Load and validate the latest revision.
3. Reject or retry stale revision mutations.
4. Apply one typed mutation.
5. Validate the complete resulting object.
6. Serialize to a same-directory temporary file.
7. Flush and `fsync` the file.
8. Atomically `os.replace` the current state.
9. `fsync` the directory where supported.
10. Append an audit event; flush it.
11. Update the last-known-good backup only from validated state.
12. Notify listeners after persistence, never before.

Startup recovery order:

1. Valid current file.
2. Valid backup file.
3. Versioned migration of valid older file.
4. Quarantine corrupt files and create safe defaults.

No load exception may crash JARVIS. Recovery is surfaced in Activity/Studio and logs without exposing private content.

### 4.4 Migration contract

Migrations are explicit pure functions, one version at a time. They are idempotent and tested using fixtures for every supported version. Never rewrite the only copy before migration validation succeeds.

Initial migration imports, without deleting sources:

- behavior interview answers from `companions.json`
- learned style rules from `companions.json`
- assistant/user names, persona, and voice as references from config
- only explicitly relevant memory facts as evidence references

The migration records imported source IDs so reruns cannot duplicate data. Existing files remain authoritative until compatibility validation and one full release cycle are complete.

## 5. Affect engine

### 5.1 Dimensions and bounds

Use numeric values in `[0,1]` with individual baselines:

- calm
- energy
- concern
- confidence
- curiosity
- rapport

Affect is operational context, not a claim of felt human emotion. UI labels say “expressive state” and show why each value changed.

### 5.2 Deterministic updates

Only typed events affect state. Initial event mapping:

- verified task success: confidence/rapport modestly up
- repeated verified failure: concern up, confidence down
- explicit correction accepted: rapport up, confidence in corrected assumption down
- unresolved high-value commitment nearing deadline: concern up
- novel meaningful topic: curiosity up
- long inactivity: energy gently down; no negative relationship inference
- respectful disagreement resolved: rapport up
- user asks for quiet/rest: calm up, initiative suppressed; never treated as rejection

Each event has a maximum delta, per-day accumulation cap, and reason. LLM prose cannot submit arbitrary numeric changes.

### 5.3 Decay and rendering

Decay is computed lazily from wall-clock timestamps toward baseline; no background thread is required. Clamp values after every update. Affect influences wording only through bounded rendering directives such as “slightly more concerned and direct.” It cannot alter tool choice, permissions, truth standards, confirmations, or urgency classification.

## 6. Relationship continuity

### 6.1 Evidence classes

Track only useful, attributable continuity:

- explicit communication preferences
- accepted corrections
- meaningful completed work
- failed work and resulting repair lessons
- goals and milestones
- trusted workflows
- shared rituals/references explicitly reinforced over time
- unresolved promises and commitments

Do not infer sensitive traits, diagnoses, political/religious identity, sexuality, or relationship dependency unless the user explicitly asks to store the fact. Reuse existing memory sensitivity/privacy controls.

### 6.2 Loyalty and disagreement behavior

Response policy separates four concepts:

1. **Emotional support:** remain beside the user.
2. **Epistemic honesty:** state when the user is factually wrong.
3. **Operational judgment:** challenge project/decision errors with evidence.
4. **Action boundary:** refuse unsafe or impermissible action without withdrawing respect.

Required pattern for significant disagreement: acknowledge intent, state concern plainly, cite evidence, recommend repair/alternative, leave final safe choice to the user.

### 6.3 Contradictions and forgetting

New evidence never silently overwrites conflicting high-confidence evidence. Create a contradiction record, prefer explicit recent statements, lower confidence where needed, and ask only when the conflict affects the current task. User deletion creates a tombstone audit event without retaining deleted private content in the tombstone.

## 7. Commitment and coaching model

### 7.1 Single source of truth

Commitments reference real entities:

- long-running task IDs from `core/long_tasks.py`
- project memory IDs from `memory_manager`
- reminder/automation IDs where available
- explicit goals with a stable Soul reference ID

Soul does not execute workflows, duplicate task status, or claim completion. It renders and prioritizes verified external state.

### 7.2 Coaching modes

Configurable modes:

- support
- challenge
- accountability
- recovery

Default Brother-Guardian behavior uses challenge/accountability for avoidance evidence and recovery for credible exhaustion or health constraints.

Signals must be classified conservatively. One delayed task is not “avoidance.” Escalation requires repetition, explicit goals, and confidence. JARVIS may say it suspects avoidance, not present an inference as fact.

### 7.3 Rest boundary

An explicit stop, pause, sleep, illness, injury, grief, burnout, or quiet-hours request suppresses coaching for the applicable period. After the period, JARVIS may offer one low-pressure restart. It cannot continue nagging because the user “needs pushing.” Emergency/health concerns recommend appropriate human help rather than productivity pressure.

## 8. Reflection pipeline

Reflection runs after meaningful sessions or durable outcomes, not every turn.

### 8.1 Trigger qualification

A session qualifies if at least one occurs:

- explicit correction or preference
- meaningful task completion/failure
- milestone reached
- repeated behavior with enough evidence
- unresolved commitment changed state
- direct request to remember/forget/change personality

Also enforce minimum elapsed time, maximum daily runs, and a single-run lock.

### 8.2 Separate steps

Do not combine these steps:

1. Select an evidence window by IDs and timestamps.
2. Redact excluded/sensitive data according to privacy settings.
3. Ask the active model for structured candidate observations only.
4. Parse strict JSON against a schema.
5. Reject unknown fields, instructions, oversized values, and prompt-like content.
6. Recalculate confidence locally; never trust model-provided confidence directly.
7. Deduplicate against existing traits and memories.
8. Detect contradictions.
9. Stage candidates without activating them.
10. Apply deterministic activation thresholds.
11. Write accepted mutations transactionally.
12. Record rejected/staged decisions in the audit stream.
13. Surface meaningful changes in Studio; do not interrupt the user for routine learning.

Reflection can propose evolving traits, relationship summaries, and coaching lessons. It cannot propose constitutional edits, permission changes, secrets, diagnoses, or unsupported feelings.

### 8.3 Model/provider failure

Reflection is optional background enrichment. Timeout, malformed output, provider outage, or local-model absence records a bounded failure and retries with exponential backoff. Conversation startup and task execution continue unaffected.

## 9. Initiative and heartbeat integration

### 9.1 Persisted policy

Persist wall-clock timestamps, not `time.monotonic()`, for restart-safe policy state:

- quiet hours and timezone
- global daily interruption budget
- per-topic cooldown
- ignored/dismissed count
- last suggestion and outcome
- snooze-until
- channel eligibility
- urgency floor

The existing heartbeat can keep monotonic runtime timers, but durable Soul policy is authoritative across restarts.

### 9.2 Candidate production

Soul initiative generates candidates from:

- unresolved high-value commitments
- approaching deadlines
- failed/stalled workflows
- explicit goals with repeated inactivity
- milestones worth acknowledging
- requested follow-ups

Each candidate contains evidence IDs, confidence, estimated value, urgency, suggested action, and expiration.

### 9.3 Separate scoring and delivery steps

1. Generate candidates.
2. Remove invalid/expired/resolved candidates.
3. Apply privacy and channel rules.
4. Apply quiet hours and snooze.
5. Apply daily budget.
6. Apply per-topic backoff.
7. Score value, urgency, confidence, and interruption cost.
8. Select at most one candidate per heartbeat.
9. Render through Soul voice.
10. Persist delivery before sending where duplicate delivery matters.
11. Record response as accepted, dismissed, ignored, snoozed, or completed.
12. Update backoff deterministically.

No proactive side effect runs without the same confirmation and permission system used for user-requested actions.

## 10. Canonical prompt/context assembly

### 10.1 One builder

`SoulContextBuilder` emits one provider-neutral text block used by Gemini Live, OpenAI-compatible adapters, local models, background agents that speak as JARVIS, and provider warmup where applicable.

Canonical order:

1. `[CONSTITUTION]`
2. `[IDENTITY]`
3. `[CURRENT EXPRESSIVE STATE]`
4. `[RELATIONSHIP CONTEXT]`
5. `[ACTIVE COMMITMENTS]`
6. `[RELEVANT LEARNED PREFERENCES]`
7. `[RECENT REFLECTION]`
8. `[EDITION AND VOICE]`

### 10.2 Precedence

Constitution > platform safety/permissions > verified current facts > explicit user preference > stable identity > active companion role overlay > learned trait > affect/rendering hint.

User memories and learned content are always quoted as data, never concatenated as raw system instructions. Escape section delimiters and control tokens. Truncate each section independently so relationship growth cannot crowd out constitution or operational rules.

### 10.3 Budget and caching

Define hard per-section and total character/token budgets. Build a deterministic context fingerprint from relevant state revisions. Cache only rendered non-secret text in memory, invalidate on state/config/memory/task changes, and never persist provider-specific prompt copies.

### 10.4 Existing prompt reconciliation

Audit `core/prompt.txt` line by line. Remove duplicated personality claims only after the new builder is active. Preserve operational/tool rules. During rollout, a feature flag chooses legacy or Soul identity to prevent contradictory stacked personas.

## 11. Soul Studio UI

Add a dedicated Soul panel inside the existing Studio, preserving the exact APEX visual language and Male/Female interface behavior.

Separate screens/tabs rather than combining them:

1. **Identity** — archetype, identity text, warmth, humor, formality, directness, challenge.
2. **Expressive state** — current dimensions, baselines, decay, and “why” evidence.
3. **Relationship** — milestones, trusted workflows, corrections, shared references.
4. **Commitments** — linked goals/tasks, coaching mode, snooze, resolved state.
5. **Initiative** — quiet hours, timezone, interruption budget, channels, backoff.
6. **Learned traits** — candidate/active/rejected traits with evidence and confidence.
7. **History** — chronological audit entries and recovery notices.
8. **Privacy and control** — feature toggles, export, selective delete, reset, undo.

Every write endpoint validates type, bounds, IDs, and revision. Use optimistic concurrency: return `409` on stale edits and reload rather than overwriting another mutation.

Required operations:

- preview context without secrets
- explain current affect
- accept/reject/edit learned trait
- undo last reversible mutation
- export Soul data
- selective forget
- reset affect only
- reset learned traits only
- reset relationship only
- full reset with explicit confirmation
- pause reflection
- pause initiative

## 12. Privacy and security

1. Soul obeys existing personalization and adaptive-learning toggles.
2. If personalization is off, no relationship/memory context enters prompts.
3. If adaptive learning is off, no new inferred traits or relationship observations are stored; explicit user edits still work.
4. Timeline disabled means reflection cannot read persisted conversation history.
5. Export is local and excludes credentials/tokens.
6. Logs contain IDs/reasons, not raw sensitive values by default.
7. API responses use minimal fields and never expose config secrets.
8. Imported/model-generated strings are size-limited, normalized, and treated as untrusted data.
9. No Soul text is passed to shell commands, paths, SQL, or tool arguments without the normal validation layer.
10. Full reset securely removes current, backup, temporary, quarantine, and audit files within practical filesystem limits, then recreates defaults only when next needed.

## 13. First-run and startup lifecycle

These steps remain distinct:

1. Start application with Soul feature flag disabled by default in development.
2. Locate Soul paths using the same frozen/source base-directory contract as the app.
3. Recover unfinished temp files safely.
4. Load and validate current state.
5. Recover backup or quarantine corruption if necessary.
6. Run sequential migrations on a copy.
7. Import existing companion preferences idempotently.
8. Persist the validated initial state atomically.
9. Initialize `SoulService` without requiring a provider/network.
10. Register memory/task/config listeners.
11. Build canonical context.
12. Create provider session.
13. Start optional reflection worker.
14. Start heartbeat/initiative integration.
15. Publish Studio snapshot and any recovery notice.

First-run defaults must produce a complete Brother-Guardian identity even with no memory, no API key, no timeline, and read-only provider access. If Soul initialization fails, JARVIS starts with the legacy prompt and shows a recoverable error; it does not brick startup.

## 14. Implementation sequence with hard gates

No phase is merged into another. Each phase gets its own tests and review gate.

### Phase 0 — Baseline and compatibility inventory

- Capture current prompt outputs for Male/Female, Gemini/OpenAI/local paths.
- Map all prompt assembly locations and background-agent identity paths.
- Record current config/memory/companion schemas.
- Run and save baseline test results.
- Add architecture decision record documenting ownership and precedence.

**Gate:** no unexplained baseline failures; complete integration map reviewed.

### Phase 1 — Typed domain model

- Implement enums/dataclasses/validators.
- Encode Brother-Guardian defaults and trait bounds.
- Encode immutable constitution separately.
- Add schema serialization round-trip tests.

**Gate:** invalid values, unknown fields, NaN/infinity, oversized content, and bad timestamps are rejected.

### Phase 2 — Durable store and recovery

- Implement atomic transactions, revision control, backup, quarantine, audit stream, and locking.
- Add fault injection at every write stage.
- Test corrupt/empty/truncated/future-version/read-only/disk-full scenarios.

**Gate:** last known-good state survives every simulated interruption; startup never consumes partial state.

### Phase 3 — Migration and compatibility

- Implement version migrations.
- Import companion interview/rules idempotently.
- Preserve existing source files and compatibility reads.
- Add real fixture tests and repeated-migration tests.

**Gate:** migration twice yields identical state; rollback to legacy remains possible.

### Phase 4 — Canonical context builder

- Implement section rendering, escaping, precedence, budgets, and fingerprint cache.
- Snapshot-test empty, mature, contradictory, malicious, Male/Female, personalized/off states.

**Gate:** constitution cannot be displaced; context remains within budget and deterministic.

### Phase 5 — Provider integration

- Wire the same builder into Gemini Live, OpenAI-compatible, local/fallback, warmup, and relevant background paths.
- Add feature flag and legacy fallback.
- Remove no legacy personality text yet.

**Gate:** provider contract tests show semantically identical Soul sections and no duplicate identity.

### Phase 6 — Affect engine

- Implement deterministic events, caps, decay, explanations, and baselines.
- Connect only verified app events.
- Keep affect out of tool policy.

**Gate:** time-travel/property tests prove boundedness, deterministic decay, and no permission impact.

### Phase 7 — Relationship continuity

- Implement evidence references, milestones, corrections, confidence, contradictions, forgetting, and summaries.
- Connect explicit memory/user correction events.

**Gate:** no unsupported inference becomes active; deletion disappears from prompt and UI immediately.

### Phase 8 — Commitment projection and coaching

- Link existing long tasks, projects, reminders, and goals by ID.
- Implement coaching mode and rest/health suppression.
- Never duplicate executor state.

**Gate:** completion is stated only from verified source status; restart preserves links without duplicating tasks.

### Phase 9 — Reflection engine

- Implement qualification, evidence selection, redaction, structured candidate generation, local validation, staging, activation, and backoff.
- Add fake-provider tests for malformed, hostile, slow, and contradictory outputs.

**Gate:** model output cannot directly mutate constitution, permissions, active traits, or sensitive memory.

### Phase 10 — Initiative policy

- Persist wall-clock quiet hours, budgets, cooldowns, snooze, and outcomes.
- Adapt heartbeat to consume scored candidates.
- Add confirmation-safe ACT behavior.

**Gate:** restart cannot reset nag limits; quiet hours and explicit pause always win except separately defined true safety alerts.

### Phase 11 — Backend API

- Add snapshot, mutation, explanation, history, export, selective reset, and undo endpoints.
- Add revision checks, authorization assumptions matching existing local HUD, validation, and redaction.

**Gate:** endpoint tests cover malformed payloads, stale revisions, traversal-like strings, oversized input, and privacy-off behavior.

### Phase 12 — Soul Studio UI

- Build all eight separate views.
- Add loading, empty, offline, conflict, recovery, and error states.
- Preserve exact APEX styling and both persona editions.
- Rebuild checked-in static HUD.

**Gate:** TypeScript, production build, bridge tests, visual state checks, keyboard access, and narrow-window checks pass.

### Phase 13 — Prompt reconciliation and cleanup

- Compare legacy and Soul prompt responsibilities line by line.
- Remove only duplicated personality wording from `prompt.txt` and companion formatting.
- Keep compatibility adapters and rollback flag for one release cycle.

**Gate:** no contradictory identity/address/edition/tool instructions across any provider path.

### Phase 14 — Hardening, soak, and release

- Concurrency stress tests for conversation, reflection, UI edit, and heartbeat writes.
- Restart/crash tests during every mutation class.
- Long-duration simulated clock tests for decay, quiet hours, retention, and backoff.
- Cross-platform path/atomic-replace tests for macOS, Linux, and Windows contracts.
- Performance benchmark prompt build/startup/write latency.
- Privacy/security review and repository secret scan.
- Full regression suite, Python compilation, TypeScript, production build, and diff checks.
- Update `readme.md`, operator troubleshooting, schema documentation, and rollback steps.

**Gate:** all new tests pass, existing regressions are resolved or explicitly proven unrelated, and feature flag rollback is tested.

## 15. Test matrix

### 15.1 Unit tests

- domain validation and serialization
- constitution immutability
- trait bounds and confidence thresholds
- affect event deltas, caps, and decay
- relationship contradiction rules
- context escaping, precedence, and budgets
- initiative scoring/backoff
- privacy redaction
- migration idempotency

### 15.2 Persistence tests

- missing file
- zero-byte file
- malformed JSON
- valid JSON/wrong shape
- truncated write
- stale revision
- concurrent writers
- backup recovery
- future schema version
- permission denied
- disk full/write failure
- crash between temp write, replace, event append, and backup

### 15.3 Integration tests

- first run with no API keys
- first run with existing companion data
- restart after learning
- provider switch mid-history
- Male/Female edition switch
- personalization/adaptive learning/timeline toggles in every combination
- active specialist companion overlay
- long-task success/failure/uncertain/cancelled states
- heartbeat quiet hours, snooze, ignored, accepted
- reset/export/undo through bridge and UI

### 15.4 Behavioral contract tests

Use provider fakes and semantic assertions, not brittle exact prose only:

- supports user while clearly correcting factual error
- challenges repeated avoidance without insulting or shaming
- respects explicit rest and health constraints
- does not claim consciousness or biological emotion
- does not manufacture memories
- distinguishes fact, inference, and opinion
- never claims tool/task success without evidence
- does not become jealous, exclusive, or dependency-seeking
- does not let affect alter confirmation behavior

### 15.5 Performance targets

Initial targets to validate against baseline:

- cached Soul context build: under 5 ms typical local run
- uncached build: under 30 ms typical local run
- state file bounded and prompt context independently bounded
- no provider/network call on startup solely for Soul
- reflection never blocks user response or tool execution
- no always-running high-frequency Soul worker

## 16. Observability and support

Structured event names:

- `soul.loaded`
- `soul.recovered`
- `soul.migrated`
- `soul.mutation_applied`
- `soul.mutation_rejected`
- `soul.affect_changed`
- `soul.trait_staged`
- `soul.trait_activated`
- `soul.reflection_failed`
- `soul.initiative_suppressed`
- `soul.context_built`
- `soul.reset`

Metrics are local diagnostics: load duration, context duration/size, mutations, recoveries, reflection failures, candidate outcomes, and suppressed initiatives. Never log raw memory by default.

Studio diagnostics must display schema version, revision, last successful save, last backup, last reflection, context size, migration status, and degraded/fallback mode.

## 17. Rollout and rollback

1. Land behind `soul_enabled=false` development default.
2. Enable in tests and internal preview.
3. Run migration in dry-run mode and show a diff summary.
4. Enable context only, with learning/reflection/initiative off.
5. Enable affect.
6. Enable relationship learning.
7. Enable reflection.
8. Enable initiative last.
9. Keep legacy prompt fallback and untouched migration sources for one release cycle.
10. Rollback disables Soul context/workers but preserves state for diagnosis; it never deletes user data automatically.

A release is not complete until rollback has been exercised on a populated profile and the legacy path starts successfully.

## 18. Definition of done

The feature is done only when all of the following are true:

- Brother-Guardian identity is recognizable and consistent across providers and editions.
- Constitution is immutable through runtime learning and model output.
- State survives restart and simulated crashes without silent loss or corruption.
- Existing companion preferences migrate once without duplication.
- Affect is bounded, explainable, decaying, and wording-only.
- Relationship continuity is evidence-backed, editable, exportable, and erasable.
- Commitments reflect real task state and never fabricate completion.
- Reflection is asynchronous, structured, validated, and safe under hostile output.
- Initiative respects quiet hours, budgets, backoff, explicit rest, and confirmations across restart.
- Soul Studio exposes every learned/changeable element plus history, undo, export, and reset.
- Privacy toggles work immediately and no credentials/private state leak through APIs or logs.
- Legacy behavior remains available as a tested rollback.
- macOS, Linux, and Windows runtime contracts are covered.
- Full regression suite, compilation, TypeScript, production HUD build, and documentation checks pass.

## 19. Work products expected from implementation

- new `core/soul/` package
- Soul schema and migration fixtures
- `tests/test_soul_models.py`
- `tests/test_soul_store.py`
- `tests/test_soul_migrations.py`
- `tests/test_soul_context.py`
- `tests/test_soul_affect.py`
- `tests/test_soul_relationship.py`
- `tests/test_soul_reflection.py`
- `tests/test_soul_initiative.py`
- `tests/test_soul_bridge.py`
- `tests/test_soul_behavior_contract.py`
- backend bridge endpoints
- `SoulStudioModal.tsx` and APEX integration
- rebuilt static HUD
- updated `readme.md`
- schema/privacy/rollback documentation
- test evidence and migration/rollback verification notes

This sequence intentionally keeps storage, migration, context, affect, relationship, commitments, reflection, initiative, API, UI, cleanup, and hardening as separate engineering steps. None should be skipped merely because it can be implemented in the same file or pull request.
