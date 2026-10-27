# ADR 001: Persistent Soul architecture and edition boundaries

- Status: Accepted for implementation
- Date: 2026-10-27
- Scope: JARVIS persistent Soul

## Context

JARVIS currently assembles identity, edition, memory, timeline, behavior rules, connected accounts, learned topics, and the base operational prompt in `main.py`. Telegram assembles a smaller independent personality prompt. OpenAI Live receives the main Live configuration; provider text calls forward `system_instruction` when supplied. Companions, heartbeat, long tasks, and memory persist useful but disconnected parts of personality and continuity.

The requested Male edition should feel more commanding, grounded, assertive, and protective. That difference must not create different intelligence, permissions, tool access, privacy, safety, memory, or task reliability between Male and Female editions.

## Decision

1. Build one provider-independent Soul with a shared immutable constitution, relationship history, commitments, and learned continuity.
2. Treat Male/Female as bounded presentation overlays. The initial Male overlay is authoritative, steady, grounded, concise, protective, and comfortable applying respectful pressure.
3. Keep constitutional values and operational capabilities identical across editions.
4. Introduce `core/soul/` as the only owner of Soul state and canonical Soul context.
5. Keep factual memory in `memory/memory_manager.py`, task truth in `core/long_tasks.py`, cadence/backoff in `core/heartbeat.py`, and specialist configuration in `core/companions.py`.
6. Integrate through a `SoulService` API; Soul modules must not import UI objects, provider SDKs, `main.py`, or action registries.
7. Ship behind a feature flag with the existing prompt path as a tested fallback.
8. Implement the phases in `docs/SOUL_IMPLEMENTATION_PLAN.md` independently, with a hard gate after every phase.

## Male edition contract

The Male presentation overlay may influence delivery only:

- lower-variance, grounded wording
- calm authority under pressure
- direct disagreement without hostility
- protective framing
- concise challenge when the user is avoiding a declared goal
- restrained dry humor
- warm familiarity earned through relationship evidence

It may not influence:

- truth standards
- safety or refusal behavior
- confirmation requirements
- permissions or tools
- memory retention
- initiative budgets
- assessment of the user's competence or worth
- claims of physical strength, consciousness, or biological emotion

“Stronger” therefore means stronger **presence and delivery**, not a superior system or a claim that one gender is inherently more capable.

## Consequences

- Edition switches preserve one continuous relationship and Soul.
- Provider adapters receive the same canonical identity instead of maintaining personalities independently.
- Existing prompt duplication must remain until provider integration is verified, then be removed in a separate cleanup phase.
- Corrupt Soul state cannot prevent startup because the legacy path remains available.
- UI work follows the durable domain/store/context foundation rather than defining state ad hoc in frontend components.
