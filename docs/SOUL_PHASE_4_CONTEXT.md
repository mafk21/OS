# Soul Phase 4 — Canonical context builder

Date: 2026-10-27
Status: Complete

## Delivered

- `core/soul/context.py`
  - one provider-independent canonical Soul representation
  - fixed section order and precedence
  - immutable per-section budgets
  - total context bound
  - bounded/validated runtime inputs
  - escaped and JSON-quoted user-derived data
  - deterministic content fingerprints
  - bounded thread-safe in-memory LRU cache
  - personalization-off suppression
  - active-trait-only rendering
  - edition overlay isolated to delivery
- `tests/test_soul_context.py`
  - canonical order
  - Male overlay contract
  - reviewed Male context snapshot
  - injection/markup escaping
  - personalization suppression
  - learned-trait filtering
  - deterministic fingerprints and cache invalidation
  - independent section truncation
  - input and budget validation
  - Male/Female constitution and identity parity
- `tests/fixtures/soul_context_male_v1.txt`
  - reviewable canonical Male default snapshot

## Canonical precedence and order

1. `[CONSTITUTION]`
2. `[IDENTITY]`
3. `[CURRENT EXPRESSIVE STATE]`
4. `[RELATIONSHIP CONTEXT]`
5. `[ACTIVE COMMITMENTS]`
6. `[RELEVANT LEARNED PREFERENCES]`
7. `[RECENT REFLECTION]`
8. `[EDITION AND VOICE]`

The constitution explicitly outranks personality, learned data, relationship context, expressive state, reflection, and edition guidance.

## Untrusted-data boundary

Names, memories, learned traits, evidence references, commitments, reflections, and edition values are treated as data. The builder:

- rejects control characters at input boundaries
- replaces section-bracket characters in learned/user content
- neutralizes role-prefix lines such as `SYSTEM:`
- neutralizes angle-bracket tags
- neutralizes code fences
- quotes all values as JSON strings
- labels relationship, commitment, preference, affect-cause, and reflection content as untrusted data

User-derived content therefore cannot create a second canonical section heading or silently become a system-role block.

## Budget behavior

Each section has an independent hard character budget. A large relationship, commitment, or preference set is truncated within its own section and cannot displace the constitution or stable identity. The total budget is large enough to preserve all canonical headings at their maximum individual allocations.

## Personalization behavior

When personalization is disabled, the builder excludes:

- relationship details
- commitments
- learned traits
- external preferences
- recent reflections

The constitution, stable identity, bounded expressive values, and edition/voice guidance remain available. Provider integration will also honor the existing application privacy toggles at context-input construction time.

## Male edition

The Male context renders commanding, grounded, assertive, protective, steady, concise delivery with restrained dry humor and calm authority. The context also explicitly states that edition changes delivery only and cannot change intelligence, truth, safeguards, permissions, memory, or capability.

## Validation

- Focused Soul tests: **63 passed**
- Python compilation: passed
- `git diff --check`: passed

Full repository regression results are recorded in the completion commit/turn.

## Gate result

**Phase 4 gate: PASSED.** Context is deterministic, bounded, injection-resistant at its data boundaries, constitution-first, Male-specific only in presentation, and independent of provider SDKs.

Next phase: wire this exact canonical context into Gemini Live, OpenAI-compatible Live/REST, local provider, Telegram, and appropriate user-facing fallback paths behind a rollback flag. Specialized internal extraction/classification calls will remain narrow and will not receive private relationship context.
