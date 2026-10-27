# Soul Phase 5 — Provider and runtime integration

Date: 2026-10-27
Status: Complete

## Delivered

- `core/soul/service.py`
  - single runtime lifecycle facade
  - lazy initialization with no provider/network requirement
  - one-time persisted companion compatibility import
  - canonical context creation from live name/persona/voice/privacy config
  - safe legacy fallback on any Soul error
  - explicit reload/cache invalidation
- `memory/config_manager.py`
  - persisted `soul_enabled` rollout/rollback flag
  - default off during staged development
- `main.py`
  - canonical Soul in the primary Gemini Live configuration
  - same Live configuration inherited by OpenAI Live
  - canonical Soul in typed REST fallback
  - canonical Soul in local/offline system prompt
  - mutual exclusion between Soul and the legacy dynamic identity block
  - custom skills and specialist companion scope preserved in both modes
- `core/telegram_bot.py`
  - same canonical Soul identity and continuity
  - Soul passed as system instruction rather than prepended to user text
  - local fallback receives the same system instruction
- `core/companions.py`
  - behavior-preference portion can be omitted after Soul migration
  - custom skills and specialist companion overlays remain available
- `tests/test_soul_provider_integration.py`
  - flag persistence/default
  - no state creation while disabled
  - Male initialization and privacy behavior
  - one-time companion import
  - malformed companion degradation
  - rollback on context failure
  - Telegram role separation
  - OpenAI Live/REST and local adapter preservation
  - source-level primary/offline fallback wiring checks
- `readme.md`
  - honest staged Soul architecture and activation status

## Provider contract

### Gemini Live

`JarvisLive._build_config()` inserts the canonical Soul into the shared `LiveConnectConfig.system_instruction`. The old dynamic identity block is used only when Soul is disabled or unavailable.

### OpenAI Live

The existing OpenAI Live adapter extracts `system_instruction` from that same Live configuration, so it receives the exact canonical context rather than an independently maintained personality.

### OpenAI-compatible REST and Gemini REST fallback

Typed fallback calls pass canonical Soul context through `system_instruction`. Provider failover therefore preserves identity rather than rebuilding it per provider.

### Local/Ollama/LM Studio

Offline mode prepends canonical Soul context to the existing operational prompt. The provider adapter preserves `system_instruction` as the local model's system-role message.

### Telegram

Telegram uses canonical Soul context as a system instruction and keeps the inbound message as a user-role message. It no longer concatenates Soul identity and user content into one prompt when the feature is active.

### Internal specialized calls

Extraction, classification, summarization, research, and other internal one-shot calls are not globally modified. They retain narrow task prompts and do not receive private relationship context merely because they use the provider abstraction.

## Startup and failure behavior

1. If `soul_enabled` is false, return immediately without creating `memory/soul.json`.
2. If enabled, initialize validated local defaults or recover/migrate stored state.
3. Import behavior interview and adaptive rules once when available.
4. Build canonical context using current edition, voice, names, and personalization toggle.
5. If any step fails, log a bounded error and return an empty context.
6. Empty context selects the complete legacy identity path.

A malformed companion file skips only compatibility import. It cannot prevent Soul initialization or application startup, and its migration marker remains absent so a repaired source can be imported later.

## Duplicate-context prevention

When Soul is active:

- the legacy dynamic identity block is excluded
- migrated behavior interview/adaptive rule text is excluded from the companion overlay
- custom skills and active specialist scope remain included

The base operational prompt remains intact until the separate prompt-reconciliation phase. This preserves existing tool and safety behavior while rollout tests continue.

## Rollback

Setting `soul_enabled` false immediately restores legacy prompt construction. It does not delete or mutate Soul state. Re-enabling resumes the same state and relationship revision.

## Validation

- Focused provider/Soul tests: results recorded in the completion turn
- Full repository suite: results recorded in the completion turn
- Python compilation, TypeScript, and `git diff --check`: required before commit

## Gate result

Phase 5 is complete when all provider-path and full regression checks pass. Phase 6 will add the deterministic affect engine; provider wiring will consume only its bounded context output and will not grant affect any operational authority.
