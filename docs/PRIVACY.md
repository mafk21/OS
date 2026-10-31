# Privacy and Data-Flow Disclosure

JARVIS is local-first, but it is not automatically zero-network. This document describes what stays on the device and what can leave it when the owner enables a cloud feature.

## No project telemetry

The JARVIS application does not include analytics, advertising SDKs, crash-reporting beacons, or a project-operated telemetry service. Runtime files are excluded from Git and publication by `.gitignore` and `tests/test_repository_privacy.py`.

## Data stored locally

Depending on enabled features, JARVIS can store the following on the owner's computer:

- API keys, connector credentials, and encrypted account metadata;
- conversation timeline, memories, Soul state, tasks, notes, routines, and audit records;
- screen-memory OCR, accessibility text, and optional captured frames;
- browser profiles, cookies, social sessions, generated media, uploaded knowledge files, and outputs.

These paths are runtime-only and must not be committed. Use the Brain and privacy controls to disable timeline persistence, personalization, adaptive learning, or screen memory and to remove saved data.

## Data that can leave the device

Data leaves the computer only when the owner configures or invokes a network-backed capability. Relevant data is then sent directly to that third-party service under its own terms and privacy policy:

| Capability | Possible recipient | Data involved |
|---|---|---|
| Cloud voice/chat/vision | Configured OpenAI-compatible provider or Google Gemini | microphone audio, prompts, conversation context, selected memory context, and images/screens explicitly supplied to the model |
| Web search/research/media | Requested websites and configured search/model providers | search queries, URLs, fetched public content, and analysis prompts |
| Connected accounts | The selected mail, calendar, drive, social, messaging, productivity, or developer service | the minimum request content needed for the owner-approved action; attachments only when selected |
| Image/TTS/STT services | Configured generation or speech provider | requested prompt, text, image, or audio |
| Optional hosted relay/custom tools | Endpoint configured by the owner | content explicitly routed to that endpoint |

JARVIS cannot guarantee that third-party providers retain nothing. Users requiring zero external disclosure must select a local provider such as Ollama or LM Studio, use local STT/TTS, leave cloud connectors and hosted relays disabled, and avoid network tools.

## Network exposure

- The multi-channel webhook binds to `127.0.0.1` by default.
- The optional phone/dashboard interface does not start at application launch. It starts only after the owner explicitly presses **Remote Control**, then uses authenticated, short-lived pairing and encrypted sessions. It is a LAN feature and should be used only on a trusted network.
- Custom HTTP/MCP endpoints and reverse proxies are owner-configured and inherit the security properties of that configuration.

## Publication checklist

Before publishing a fork or release:

1. Run `python -m pytest tests/test_repository_privacy.py -q`.
2. Run the complete test suite.
3. Run `pip-audit -r requirements.txt` and `npm audit` in `apex_ui/`.
4. Inspect `git status`, staged changes, and release artifacts.
5. Confirm no runtime files, screenshots, logs, databases, browser profiles, certificates, keys, or generated outputs are included.
6. If a real credential was ever committed, revoke it and rewrite Git history; deleting it only from the latest commit is insufficient.

## Security reports

Do not include live credentials or unrelated personal data in a report. Provide minimal reproduction details privately to the repository owner through GitHub's security-reporting facilities when available.
