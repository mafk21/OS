# Soul Female Edition — Guardian-Confidante

Date: 2026-10-28
Status: Complete

## Gap review

The completed Phase 0–14 implementation was re-audited before extending it. Persistence, constitution, affect, relationship evidence, commitments, reflection, initiative, provider integration, Studio controls, rollback, and hardening were complete. The material edition gap was identity presentation: Female still inherited the literal `Brother-Guardian` archetype and only received a short “composed” delivery overlay. That could make her sound like a softened Male rather than a female friend.

## Female identity

Female now presents as **Guardian-Confidante**: a trusted female friend of many years who is warm, perceptive, composed, protective, candid, opinionated, and firm about declared goals. She explicitly presents herself as a woman and female friend when relevant—not as a brother, man, mother, romantic partner, or submissive helper. The contract forbids manufactured stereotypes, flirtation, jealousy, exclusivity, and dependency.

Her delivery is naturally feminine, mature, and emotionally perceptive without coddling or becoming weak. Male remains the more commanding, grounded, assertive presentation as requested.

## Equality and continuity

Edition selection changes identity presentation and delivery only. Both editions use the same:

- constitution and immutable safety boundaries;
- intelligence, providers, tools, permissions, and confirmations;
- persisted Soul revision and relationship evidence;
- factual memory, commitments, reflection validation, and initiative gates;
- reliability, recovery, privacy, export, and audit behavior.

Switching editions does not fork, reset, rewrite, or duplicate Soul state. The Female identity is derived from the active edition at canonical-context build time. Existing Male state remains backward compatible.

## Studio and provider behavior

Soul Studio now displays the active edition’s label, archetype, summary, presence, and relationship guidance. The canonical context and snapshot API expose the same active presentation. Gemini, OpenAI-compatible, local/offline, typed fallback, and Telegram continue consuming the shared canonical context path.

## Validation

- Female context semantics and anti-stereotype boundaries
- Male identity and commanding presentation regression
- identical constitution and authority across editions
- edition switch without state fork or revision mutation
- snapshot and Studio presentation contracts
- focused edition/provider/Studio tests: **53 passed, 1 warning**
- full regression: **738 passed, 28 skipped, 9 warnings, 18 subtests passed**
- Python compilation, TypeScript, production build, and diff checks: passed
- npm audit: **0 vulnerabilities**
