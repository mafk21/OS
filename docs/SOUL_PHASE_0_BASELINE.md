# Soul Phase 0 — Baseline and compatibility inventory

Date: 2026-10-27  
Branch: `arena/cdb91afe-os`  
Base commit: `6b296529942d5d531b27133041e3b04dd07e0de7`  
Edition focus: Male

## Gate result

**Phase 0 gate: PASSED.** The integration map is complete enough to begin the typed domain model. The repository baseline passes once the test-only `pytest-asyncio` plugin is present.

No runtime Soul implementation was introduced in this phase.

## Baseline verification

| Check | Result |
|---|---|
| Full Python suite | 593 passed, 28 skipped, 9 warnings, 17 subtests passed |
| Python compilation | Passed for `main.py`, `core/*.py`, `memory/*.py`, `actions/*.py` |
| TypeScript | `npx tsc --noEmit` passed |
| APEX production build | Passed; 4 static pages generated and export completed |
| Plan whitespace validation | `git diff --check` passed before Phase 0 additions |

Environment note: the repository requirements do not install test runners. A local ignored `.venv` was created, `requirements.txt` installed, then `pytest` and `pytest-asyncio` installed. Running without `pytest-asyncio` produced five environment-caused async test failures; after installing it, the complete suite passed.

`npm ci` reported six dependency audit findings (five high, one critical). They are an existing dependency baseline and must be reviewed during hardening; no automatic major-version/force upgrade was applied because that could break the HUD.

## Current Male identity baseline

The main Live prompt currently injects:

- assistant name from config
- Male/Female edition from config
- user address rule from config/language
- Male line: “calm, authoritative, steady male operator presence”
- voice default: Charon for Male
- cyan/gold visual theme and Male humanoid

This is currently a thin presentation instruction, not a persistent personality. It has no constitutional core, affect, relationship state, reflection, or durable initiative policy.

The new Male Soul target is defined in ADR 001 as commanding, grounded, assertive, protective, concise, respectfully challenging, and restrained in humor. Capabilities and safeguards remain edition-neutral.

## Prompt assembly map

### Primary desktop Live session

Owner: `main.py`, `JarvisLive._build_config()`.

Current section order:

1. current date/time
2. dynamic identity/name/edition/address
3. topic-learning index
4. connected-account summary
5. formatted long-term memory
6. recent timeline
7. behavior interview, learned style rules, active companion, custom skills
8. rendered `core/prompt.txt`

The resulting string is assigned to `LiveConnectConfig.system_instruction`.

### Gemini Live

- Receives the `LiveConnectConfig` built by `main.py`.
- `core/gemini.py` also supports one-shot text generation and prepends its own one-shot operational instruction to a caller-provided system string.
- Soul integration must avoid placing conversational identity in specialized one-shot calls that are not speaking as JARVIS unless explicitly requested.

### OpenAI Live and REST compatibility

- `core/openai_live.py` extracts `system_instruction` from the same Live configuration, preserving the main prompt.
- `core/openai_compat.py` parses caller-provided `system_instruction` into OpenAI request options.
- Male voice mapping is provider-specific, but identity content should not be provider-specific.

### Local provider

- `core/provider.py::_local_call()` maps `system_instruction` to a system message before invoking `core.llm_client.call_llm()`.
- `core/llm_client.warmup_model()` optionally accepts a system prompt, but warmup should use a minimal stable context rather than private relationship history.

### Telegram

- `core/telegram_bot.py::handle_inbound()` independently assembles memory, timeline, and companion context.
- It uses a generic hardcoded “helpful assistant” identity and does not currently include edition identity or the full desktop operational prompt.
- This is a known continuity gap and a required canonical-context integration point.

### Background and specialized model calls

Specialized calls exist in actions and core modules, including flight search, YouTube, topic learning, screen analysis, and task-oriented one-shot requests. Most should retain narrow task prompts and must not automatically receive private Soul relationship context. Calls that speak directly to the user as JARVIS need the canonical Soul; calls that only extract/classify data need the constitutionally required safety/data boundary but not personality prose.

### Fallback text paths in `main.py`

`main.py` contains text-provider fallbacks with direct `system_instruction` values. Each must be classified during provider integration as either:

- user-facing JARVIS speech: canonical Soul required, or
- internal task operation: narrow task instruction only.

## Existing state ownership

| Concern | Current authority | Soul integration rule |
|---|---|---|
| Assistant/user name | `memory/config_manager.py` | Reference dynamically; do not duplicate |
| Male/Female persona and voice | `memory/config_manager.py` | Edition overlay input |
| Factual personal memory | `memory/memory_manager.py` | Evidence/source authority |
| Recent conversation history | `memory/timeline.py` | Optional evidence when enabled |
| Behavior interview/style rules | `core/companions.py` | Migration and compatibility input |
| Specialist companions/tools | `core/companions.py` | Explicit role overlay after identity |
| Long-running task truth | `core/long_tasks.py` | Read/project by stable task ID |
| Heartbeat cadence/runtime backoff | `core/heartbeat.py` | Scheduler consumes Soul candidates |
| Tool permissions/confirmations | action/plugin registries and confirmation layer | Never owned or weakened by Soul |
| Base operational behavior | `core/prompt.txt` | Reconcile only after Soul integration |

## Current persistence schemas relevant to migration

### `memory/companions.json`

- active companion ID
- behavior interview answers
- learned style rules
- specialist companion records
- theme selection

Current writes are atomic through a temporary sibling and replace. It is the import source for initial Soul style candidates; it remains untouched during migration.

### `memory/long_term.json`

- identity
- preferences
- projects
- relationships
- wishes
- notes

It has category TTL/hygiene and bounded prompt rendering. Soul must reference this data rather than copy the entire store.

### Config

Config contains names, persona, voice, and privacy toggles, along with credentials. Soul must never copy config secrets into state, audit, export, logs, or context previews.

### `memory/long_tasks.json`

Contains durable monitor/workflow state and restart recovery. Soul commitment projection must use IDs/status and must not become another executor.

## Compatibility requirements captured

1. Male/Female switching preserves the same Soul and relationship.
2. Male voice persistence and current Charon fallback remain intact.
3. Existing onboarding and skip behavior remain intact.
4. OpenAI-compatible and Gemini Live receive semantically equivalent Soul context.
5. Local mode works without a cloud provider.
6. Telegram continuity is brought into the canonical builder.
7. Typed entry, voice entry, silent HUD workflows, long tasks, and proactive checks remain functional.
8. Personalization, adaptive learning, and timeline privacy toggles take effect immediately.
9. Specialist companions remain scoped and cannot mutate the primary constitution.
10. Legacy prompt fallback starts even if Soul state is missing or corrupt.
11. macOS, Linux, and Windows path/replace behavior is retained through the existing base-directory pattern.
12. No model call is required merely to load Soul state or start the application.

## Identified risks to address in later phases

1. Prompt identity is currently duplicated between desktop, Telegram, and fallback paths.
2. Heartbeat state is in memory and uses monotonic time; restart resets its policy history.
3. Several stores recover malformed JSON by silently returning defaults; Soul requires quarantine and visible recovery.
4. Companion style rules are raw user-derived strings inserted into a system context; the Soul builder must delimit and escape them as untrusted data.
5. Relationship facts can expire under existing TTL policy; Soul milestones need explicit retention semantics without duplicating factual memory.
6. Prompt order currently puts the base operational prompt after user-derived context; the Soul builder needs explicit precedence and injection-resistant sections.
7. Specialized internal calls must not receive unnecessary personal context.
8. Frontend dependencies currently report audit findings; upgrades require isolated compatibility work rather than an unsafe forced update.
9. Requirements do not include test tooling, so reproducible contributor/CI instructions should eventually document test extras.

## Phase 1 entry criteria

Met:

- architecture ownership decision recorded
- Male presentation boundary defined
- prompt/provider integration points mapped
- persistent source schemas mapped
- compatibility requirements recorded
- baseline Python, TypeScript, production build, and compilation verified
- known baseline/tooling risks recorded

Next phase: implement typed enums/dataclasses/validators, immutable constitution constants, Brother-Guardian defaults, and Male presentation overlay—without persistence or runtime prompt wiring yet.
