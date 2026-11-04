# CodeQL Alert Triage

> **Status note:** Remediation decisions below are provisional until the pull request runs a fresh CodeQL analysis. “Remediated” means the source change is implemented and locally tested; it does not claim that GitHub has closed the alert. Intended dismissals likewise require owner-side Security Events permission and per-alert evidence.

Baseline: **60 findings** from the Python and JavaScript SARIF artifacts generated for `main`.

Generated output and test fixtures are excluded from CodeQL; production source remains scanned. Dismissals require repository-owner Security Events permission and must use the evidence below.

## Summary

| Rule | Count | Resolution |
|---|---:|---|
| `py/incomplete-url-substring-sanitization` | 20 | EXCLUDED — test fixture; REMEDIATED — pending fresh CodeQL confirmation |
| `py/clear-text-logging-sensitive-data` | 15 | REMEDIATED — pending fresh CodeQL confirmation |
| `py/stack-trace-exposure` | 5 | REMEDIATED — pending fresh CodeQL confirmation |
| `js/xss` | 4 | REMEDIATED — pending fresh CodeQL confirmation |
| `py/weak-sensitive-data-hashing` | 3 | DISMISS — false positive (HMAC/stream/audit integrity, not password hashing) |
| `py/path-injection` | 3 | REMEDIATED — pending fresh CodeQL confirmation |
| `js/client-side-unvalidated-url-redirection` | 3 | REMEDIATED — pending fresh CodeQL confirmation |
| `py/clear-text-storage-sensitive-data` | 2 | REMEDIATED — pending fresh CodeQL confirmation |
| `js/incomplete-html-attribute-sanitization` | 2 | REMEDIATED — pending fresh CodeQL confirmation |
| `py/reflective-xss` | 1 | REMEDIATED — pending fresh CodeQL confirmation |
| `py/insecure-protocol` | 1 | REMEDIATED — pending fresh CodeQL confirmation |
| `js/xss-through-dom` | 1 | REMEDIATED — pending fresh CodeQL confirmation |

## Alert-by-alert accounting

| # | Rule | Location | Decision |
|---:|---|---|---|
| 1 | `py/clear-text-storage-sensitive-data` | `core/apex_bridge.py:906` | REMEDIATED — pending fresh CodeQL confirmation |
| 2 | `py/clear-text-storage-sensitive-data` | `memory/config_manager.py:58` | REMEDIATED — pending fresh CodeQL confirmation |
| 3 | `py/clear-text-logging-sensitive-data` | `core/audio_devices.py:416` | REMEDIATED — pending fresh CodeQL confirmation |
| 4 | `py/clear-text-logging-sensitive-data` | `core/gemini.py:284` | REMEDIATED — pending fresh CodeQL confirmation |
| 5 | `py/clear-text-logging-sensitive-data` | `core/gemini.py:289` | REMEDIATED — pending fresh CodeQL confirmation |
| 6 | `py/clear-text-logging-sensitive-data` | `main.py:2722` | REMEDIATED — pending fresh CodeQL confirmation |
| 7 | `py/clear-text-logging-sensitive-data` | `main.py:2712` | REMEDIATED — pending fresh CodeQL confirmation |
| 8 | `py/clear-text-logging-sensitive-data` | `main.py:3016` | REMEDIATED — pending fresh CodeQL confirmation |
| 9 | `py/clear-text-logging-sensitive-data` | `main.py:3037` | REMEDIATED — pending fresh CodeQL confirmation |
| 10 | `py/clear-text-logging-sensitive-data` | `main.py:3738` | REMEDIATED — pending fresh CodeQL confirmation |
| 11 | `py/clear-text-logging-sensitive-data` | `main.py:3746` | REMEDIATED — pending fresh CodeQL confirmation |
| 12 | `py/clear-text-logging-sensitive-data` | `core/openai_compat.py:424` | REMEDIATED — pending fresh CodeQL confirmation |
| 13 | `py/clear-text-logging-sensitive-data` | `core/openai_compat.py:428` | REMEDIATED — pending fresh CodeQL confirmation |
| 14 | `py/clear-text-logging-sensitive-data` | `core/openai_compat.py:437` | REMEDIATED — pending fresh CodeQL confirmation |
| 15 | `py/clear-text-logging-sensitive-data` | `core/openai_live.py:900` | REMEDIATED — pending fresh CodeQL confirmation |
| 16 | `py/clear-text-logging-sensitive-data` | `core/openai_live.py:907` | REMEDIATED — pending fresh CodeQL confirmation |
| 17 | `py/clear-text-logging-sensitive-data` | `core/openai_live.py:928` | REMEDIATED — pending fresh CodeQL confirmation |
| 18 | `py/reflective-xss` | `dashboard/server.py:622` | REMEDIATED — pending fresh CodeQL confirmation |
| 19 | `py/insecure-protocol` | `core/topic_learning.py:116` | REMEDIATED — pending fresh CodeQL confirmation |
| 20 | `py/weak-sensitive-data-hashing` | `core/security_vault.py:149` | DISMISS — false positive (HMAC/stream/audit integrity, not password hashing) |
| 21 | `py/weak-sensitive-data-hashing` | `core/security_vault.py:152` | DISMISS — false positive (HMAC/stream/audit integrity, not password hashing) |
| 22 | `py/weak-sensitive-data-hashing` | `core/security_vault.py:342` | DISMISS — false positive (HMAC/stream/audit integrity, not password hashing) |
| 23 | `py/incomplete-url-substring-sanitization` | `core/media_engine.py:178` | REMEDIATED — pending fresh CodeQL confirmation |
| 24 | `py/incomplete-url-substring-sanitization` | `core/media_engine.py:190` | REMEDIATED — pending fresh CodeQL confirmation |
| 25 | `py/incomplete-url-substring-sanitization` | `core/media_engine.py:230` | REMEDIATED — pending fresh CodeQL confirmation |
| 26 | `py/incomplete-url-substring-sanitization` | `core/media_engine.py:239` | REMEDIATED — pending fresh CodeQL confirmation |
| 27 | `py/incomplete-url-substring-sanitization` | `core/media_engine.py:240` | REMEDIATED — pending fresh CodeQL confirmation |
| 28 | `py/incomplete-url-substring-sanitization` | `core/openai_compat.py:349` | REMEDIATED — pending fresh CodeQL confirmation |
| 29 | `py/incomplete-url-substring-sanitization` | `core/openai_live.py:848` | REMEDIATED — pending fresh CodeQL confirmation |
| 30 | `py/incomplete-url-substring-sanitization` | `tests/test_deep_research.py:69` | EXCLUDED — test fixture |
| 31 | `py/incomplete-url-substring-sanitization` | `tests/test_deep_research.py:70` | EXCLUDED — test fixture |
| 32 | `py/incomplete-url-substring-sanitization` | `tests/test_deep_research.py:89` | EXCLUDED — test fixture |
| 33 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:12` | EXCLUDED — test fixture |
| 34 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:16` | EXCLUDED — test fixture |
| 35 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:17` | EXCLUDED — test fixture |
| 36 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:18` | EXCLUDED — test fixture |
| 37 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:19` | EXCLUDED — test fixture |
| 38 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:21` | EXCLUDED — test fixture |
| 39 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:47` | EXCLUDED — test fixture |
| 40 | `py/incomplete-url-substring-sanitization` | `tests/test_gws_pack.py:52` | EXCLUDED — test fixture |
| 41 | `py/incomplete-url-substring-sanitization` | `tests/test_topic_learning.py:64` | EXCLUDED — test fixture |
| 42 | `py/incomplete-url-substring-sanitization` | `tests/test_topic_learning.py:291` | EXCLUDED — test fixture |
| 43 | `py/path-injection` | `dashboard/server.py:809` | REMEDIATED — pending fresh CodeQL confirmation |
| 44 | `py/path-injection` | `dashboard/server.py:809` | REMEDIATED — pending fresh CodeQL confirmation |
| 45 | `py/path-injection` | `dashboard/server.py:811` | REMEDIATED — pending fresh CodeQL confirmation |
| 46 | `py/stack-trace-exposure` | `core/apex_bridge.py:1885` | REMEDIATED — pending fresh CodeQL confirmation |
| 47 | `py/stack-trace-exposure` | `core/apex_bridge.py:1893` | REMEDIATED — pending fresh CodeQL confirmation |
| 48 | `py/stack-trace-exposure` | `core/apex_bridge.py:2033` | REMEDIATED — pending fresh CodeQL confirmation |
| 49 | `py/stack-trace-exposure` | `core/apex_bridge.py:2092` | REMEDIATED — pending fresh CodeQL confirmation |
| 50 | `py/stack-trace-exposure` | `dashboard/server.py:768` | REMEDIATED — pending fresh CodeQL confirmation |
| 51 | `js/xss` | `apex_ui/components/HudVideoModal.tsx:306` | REMEDIATED — pending fresh CodeQL confirmation |
| 52 | `js/xss` | `apex_ui/components/HudVideoModal.tsx:368` | REMEDIATED — pending fresh CodeQL confirmation |
| 53 | `js/xss` | `apex_ui/components/HudVideoModal.tsx:390` | REMEDIATED — pending fresh CodeQL confirmation |
| 54 | `js/xss` | `dashboard/static/app.html:353` | REMEDIATED — pending fresh CodeQL confirmation |
| 55 | `js/xss-through-dom` | `dashboard/static/app.html:286` | REMEDIATED — pending fresh CodeQL confirmation |
| 56 | `js/client-side-unvalidated-url-redirection` | `apex_ui/components/HudVideoModal.tsx:306` | REMEDIATED — pending fresh CodeQL confirmation |
| 57 | `js/client-side-unvalidated-url-redirection` | `apex_ui/components/HudVideoModal.tsx:368` | REMEDIATED — pending fresh CodeQL confirmation |
| 58 | `js/client-side-unvalidated-url-redirection` | `apex_ui/components/HudVideoModal.tsx:390` | REMEDIATED — pending fresh CodeQL confirmation |
| 59 | `js/incomplete-html-attribute-sanitization` | `dashboard/static/app.html:325` | REMEDIATED — pending fresh CodeQL confirmation |
| 60 | `js/incomplete-html-attribute-sanitization` | `dashboard/static/app.html:359` | REMEDIATED — pending fresh CodeQL confirmation |

## Additional manually identified hardening

- Archive extraction now rejects traversal, absolute paths, links/devices, oversized archives, and excessive member counts.
- Model-generated desktop code is AST-gated before execution; imports, reflection/dunder access, unsafe builtins, and unapproved call roots are rejected.
- Linux XRandR brightness fallback no longer invokes a shell.
- Marketplace downloads require HTTPS, successful bounded responses, valid archives, safe plugin names, and per-plugin containment.

## Verification

- Archive traversal/link and desktop sandbox regression tests were added.
- Full Python suite, TypeScript, npm audit, pip-audit, Bandit high/high, compileall, and git diff checks are required before merge.
- A fresh CodeQL run must establish the post-fix alert count; any residual by-design/false-positive alert must be dismissed individually with evidence, never hidden from production scanning.
