# ⚡ JARVIS OS — The AI Operating Companion

> **Not another chatbot. Not a voice skin over an API.**<br>
> **JARVIS is a local-first AI command center that can see, hear, speak, remember, research, operate your desktop, coordinate specialist agents, connect to your services, and show every moving part inside a cinematic 3D HUD.**

## Meet the monster

JARVIS turns a Windows, macOS, or Linux computer into an **AI-operated workspace**.
Talk naturally, type a command, or use the HUD. JARVIS can hold a full-duplex
conversation while it works, inspect what is on screen, use applications, search
and study, write and run code, manage files, control media, call connected
services, and delegate long jobs to visible worker agents.

This is not one giant prompt pretending to do those things. It is a real system:

- **A live voice and vision kernel** powered by OpenAI or Google Gemini, with
  interruption, continuous listening, provider failover, and optional offline
  STT/LLM/TTS components.
- **A native computer-control layer** for windows, apps, terminals, files,
  clipboard, keyboard, mouse, screenshots, audio, display settings, and verified
  process execution.
- **A durable brain** backed by SQLite timelines, searchable memories, imported
  documents, learning records, session history, and privacy controls.
- **An agent runtime** with specialist companions, parallel worker orbs,
  cancellable jobs, reusable skills, scheduled automations, and a streaming
  development workspace.
- **A connector layer** for mail, calendars, cloud drives, developer tools,
  productivity platforms, messaging, social services, webhooks, REST APIs, and
  MCP servers.
- **A security layer** with confirmation gates, reversible actions, encrypted
  credentials, tamper-evident audit history, scoped tools, and revocable portals.
- **A real interface**, not a terminal demo: Male and Female animated humanoid
  editions, live state visualization, activity queues, controls, logs, panels,
  and an optional compact background mode.

### One request can cross the whole stack

```text
You speak or type
       ↓
Live AI understands the intent and current screen/context
       ↓
JARVIS chooses a native action, connector, skill, or specialist worker
       ↓
Safety and permission policy checks the operation
       ↓
The task runs with live progress in the HUD
       ↓
Results, files, sources, traces, and durable memory are returned
```

Examples:

```text
“Watch this window, find the error, fix the project, run its tests, and show me the diff.”
“Study nuclear physics in sourced units, quiz yourself, save the gaps, and continue tomorrow.”
“Read my calendar and unread mail, prepare a briefing, then schedule the approved follow-ups.”
“Open the female edition, keep listening in the background, and interrupt immediately when I speak.”
```

## What “local-first” means

The HUD, orchestration, memory database, automation engine, tools, encrypted vault,
and action history run on **your machine**. Cloud AI and connected services are
used only when you configure and invoke them. Offline voice/model components are
optional; cloud-dependent features naturally still need their provider and an
internet connection. JARVIS does **not** secretly turn every integration into an
offline feature.

## Supported operating systems—clearly

The shared application targets **Windows, macOS, and Linux**. Native commands are
selected from the machine currently running JARVIS, not from a stale copied
profile. Launch with:

| Platform | Launcher | Important host requirements |
| :--- | :--- | :--- |
| **Windows** | `Start_JARVIS.bat` | Python 3.11+; permissions for requested desktop actions |
| **macOS** | `Start_JARVIS.command` | Python 3.11+; Accessibility, Screen Recording, Microphone, or Automation permission when the relevant feature is used |
| **Linux** | `Start_JARVIS.sh` | Python 3.11+; graphical X11/Wayland session for GUI control; `pactl` or `wpctl` for volume; desktop-specific utilities for some settings |

Unsupported permissions or missing native utilities must produce an explicit
limitation rather than a fake success. Hardware behavior—microphones, cameras,
GPU acceleration, accessibility APIs, window managers, and audio backends—still
depends on the actual computer and must be verified there.

## Privacy of a fresh clone

A published clone contains **application source and intentional visual assets—not
the previous operator's runtime state**. JARVIS creates personal state locally on
each machine, and the repository excludes it from Git:

- API keys, OAuth tokens, connector credentials, vault keys and TLS private keys
- Browser profiles, cookies, linked WhatsApp sessions and login databases
- Memories, account metadata, companions, routines, automations and pairings
- Brain, screen-memory, productivity and security-audit databases
- Imported knowledge, lecture transcripts, generated media and downloaded files
- Logs, screenshots, recordings, caches and temporary output

`tests/test_repository_privacy.py` prevents high-confidence credentials and known
runtime-storage paths from becoming tracked files. This is a publication guard,
not permission to upload arbitrary files: contributors should still inspect
`git status` and staged changes before every push. If a real secret is ever
committed, ignoring or deleting it later is insufficient—revoke it immediately
and purge it from Git history.

## Start in three steps

```bash
# 1. Clone and enter the repository
git clone https://github.com/mafk21/OS.git
cd OS

# 2. Create the environment, install OS-filtered dependencies, and launch
python3 install_jarvis.py --install --launch

# 3. Next time, use your native launcher
# Windows: Start_JARVIS.bat
# macOS:   ./Start_JARVIS.command
# Linux:   ./Start_JARVIS.sh
```

Then configure at least one supported AI provider in the guided setup. API keys,
service credentials, and optional local models are **not bundled** with the
repository. Read the platform notes and security controls before allowing desktop
or account actions.

## The system at a glance

| Metric | Verified Scale |
| :--- | :--- |
| **Codebase** | **65,000+ lines** across **159 Python & Next.js / Three.js HUD source modules** (`Windows` · `macOS` · `Linux`) |
| **Execution Surface** | **52 OS, cloud, social, media & companion action modules** (`social_hub` + `social_video` + `video_player` across **Instagram**, **Snapchat**, **TikTok**, **X**, **WhatsApp**, **YouTube**, **Reddit** & **1,800+ `yt-dlp` sites**) + **15 built-in live-session tools** + **11 core `SKILL.md` playbooks** + **Visual Custom Skills, REST/Webhook & MCP JSON-RPC 2.0 Builder** |
| **Dual-Engine Live Voice & Vision** | **OpenAI Realtime (`gpt-4o-realtime-preview` + Universal REST Live fallback) & Gemini 3.8 Live** full-duplex audio + **GPT-4o / Gemini Multimodal Vision** + **Male and Female particle-humanoid HUD Editions with distinct palettes and voices (`Charon` / `ash`, `Aoede` / `shimmer`)** + **Automatic Dual-Engine Failover** |
| **Brain & Forever Timeline** | **Zero-Reset Continuous SQLite WAL Timeline** across **Voice, Desktop Text & Telegram** + **Auto-Epoch Compression** + **Drag-and-Drop Knowledge Docs** + **Outputs Vault** + **JSON Export/Import & Privacy Toggles** |
| **Cloud, Socials & Automations** | **23 Native SaaS, Mail & Personal Social Connectors** (**Instagram**, **Snapchat Web**, **TikTok**, **X / Twitter**, **WhatsApp Web**, **Reddit**, **Email IMAP/SMTP**, **Gmail**, **Google Calendar**, **Google Classroom**, **Google Drive**, **GitHub**, **Notion**, **Slack**, **Discord**, **Telegram**, **Spotify**, **Trello**, **Linear**, **Microsoft Outlook/Graph**, **Dropbox**, **HubSpot**, **Calendly**) + **Recurring Automations Scheduler** |
| **Dev Workspace & Vault Security** | **Live Streaming Dev Terminal + Codebase Map & Colorized Git Diffs** + **Authenticated Credential Vault (`AES-256-GCM`)** + **SHA-256 Hash-Chained Audit Log** + **Revocable Guest Portals** + **1-Click Native Launchers (`install_jarvis.py`, `Start_JARVIS.bat`, `Start_JARVIS.command`, `Start_JARVIS.sh`)** |
| **Verification** | Automated `pytest` coverage for core workflows + pre-compiled zero-Node.js static HUD (`apex_ui/static_hud/`) |

---

## ⏳ Durable long-term tasks — execution and evidence, not promises

JARVIS has a persistent engine for **actual long-running work**, not merely a
memory that says a task exists. `long_task(action="workflow")` accepts an ordered
set of real discoverable tools, executes them outside the conversation, and
atomically checkpoints each step before and after execution. A later step can
consume `${previous.output}` or `${step.N.output}`. Progress and outputs appear
in Activity; workflows can be inspected or cancelled between steps and resume
after restart.

Crash safety is deliberately conservative. If JARVIS stops while a step is
running, that step becomes `uncertain` and the workflow becomes `needs_review`.
It will **not blindly repeat a possible message, upload, deletion, purchase, or
other side effect**. The user must explicitly choose `retry` or `mark_done`.
Likewise, an action returning `[CONFIRMATION_PENDING]` pauses the workflow for the
real HUD confirmation instead of treating a model-generated “yes” as approval.
Failed steps stop later steps and preserve their real error; cancellation never
pretends an already-running Python handler was forcibly killed.

The same engine supports observable waiting conditions. For example:

> “Watch this until the end and notify me.”

When media is playing in the HUD, `long_task(action="watch_until_end")` binds to
the current video—or the complete active queue by default—and waits for the
browser's real `HTMLMediaElement.ended` event. It does **not** guess completion
from duration or immediately claim success. It retries the local completion
handoff, deduplicates repeated end events, records evidence, and uses available
in-app and native desktop notification channels.

It can also notify at a future time, wait for a file to actually appear, or wait
for an existing file to change. All task state lives privately in git-ignored
`memory/long_tasks.json`. A stopped app cannot observe media ending while it is
offline, so that monitor remains pending rather than inventing completion. Time,
file, and not-yet-started workflow steps resume after restart. OS notifications,
GUI actions, network services and hardware still depend on their real host
permissions and availability.

---

## 📚 Persistent Subject Learning — not just “I learned it”

Say **“Learn nuclear physics”**, **“Continue studying nuclear physics”**, or
**“Use what you learned about binding energy.”** The new `topic-learning` skill
calls the real `topic_learning` action, rather than answering with an unsupported
claim of learning.

One invocation studies a **bounded unit**, not an entire discipline:

1. Research three curriculum questions; deduplicate up to eight sources.
2. Read bounded public text pages where available; clearly label search excerpts
   when full-page reading fails. Keep exact excerpts, URLs, timestamps and hashes.
3. Generate structured concepts and require matching source quotations before
   accepting the notes. Unsupported drafts are retained as drafts, not success.
4. Answer practice questions using the saved notes, then separately audit the
   explanations and answers against the sources. Store answers, feedback and gaps.
5. Save `studied`, `needs_review`, or `failed` with actual check counts. Missing
   sources, model errors, malformed citations, failed checks and disk failures
   cannot silently become successful study results.

```text
memory/learning/<topic-id>/
  manifest.json                 # unit history; previous units are preserved
  runs/<timestamp-id>/
    plan.json                   # curriculum queries and previous gaps
    sources.json                # retained excerpts, provenance and content hashes
    draft.json                  # unfiltered model study draft
    lesson.json + notes.md      # evidence-linked concepts and unresolved gaps
    questions.json              # retrieval-assisted practice
    answers.json + review.json  # answers, model audit and corrective feedback
    result.json                 # actual status and check counts
```

Use `topic_learning` with `learn`, `continue`, `list`, `status`, `read`, or `search`.
`read` also accepts a historical `run_id` from status. The vault is searchable
across app restarts, **without rebuilding the generic document index**; standard
Brain/`recall_memory` searches include matching studies too. A small topic/status
index is supplied to subsequent Gemini/OpenAI sessions (unless personalization is
disabled). Both interface editions use the same provider-neutral action, backed
by the configured OpenAI, Gemini or local model. New research needs internet
search access and a working model. Explicitly requested study is retained even
if automatic style learning is paused.

**Honest boundary:** this is durable external-knowledge acquisition, retrieval
and revision—not modification of the foundation model's weights. Reviews are
**retrieval-assisted and model-scored**, not independent scientific verification,
a closed-book exam, or proof of mastery. `continue` researches recorded gaps in a
new unit; it does not run an endless background process. The vault contains private
runtime data and is excluded from Git. Public-page fetching blocks private/local
addresses, credential URLs and unsafe redirects, and pins checked DNS addresses.

Automated tests exercise persistence, cross-process recall, source/quote validation,
review failure paths, private-address blocking and action/skill discovery using
mocked network/model boundaries; they do not pretend to perform a live study.

---

## 🧠 System Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                    INPUT, 3D WORLD & MULTI-MONITOR PRESENCE                            │
│  🎙️ Full-Duplex Mic (EchoGuard + Barge-In + Wake Word + Ctrl+Space PTT + Grace Win)    │
│  👁️ Vision (Full Screen · Rubberband Region · Live Webcam · Event-Driven OCR/a11y)     │
│  🌍 Omnichannel Inbound (Webhook Gateway · Telegram Bot · TLS Phone QR Dashboard)      │
│  🪐 APEX-UI 3D World (Male/Female Core · Worker Orbs · 18-Node Graph · Pop-Out Console)│
│  🧑‍🎤 Classic PyQt6 Fallback (`JARVIS_CLASSIC_UI=1` · 3D Face Mesh · 50Hz Visemes)       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   REAL-TIME ORCHESTRATION & DUAL-ENGINE AI KERNEL                      │
│  • OpenAI Realtime + REST Live──► `gpt-4o-realtime-preview` + Whisper/GPT-4o/TTS tier  │
│  • Gemini 3.8 Live WebSocket  ──► SessionResumption + Compression + 15m Auto-Recycle   │
│  • Per-Tool Scheduling        ──► NON_BLOCKING + WHEN_IDLE speech-gap delivery         │
│  • Dual-Engine Auto-Failover  ──► Seamless OpenAI ◄──► Gemini live & multimodal switch │
│  • Offline Local Voice Loop   ──► Local LLM + Whisper STT + Local TTS (zero cloud)     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               BRAIN, COMPANIONS, SKILLS & AUTONOMOUS COGNITIVE LAYER                   │
│  • Forever Timeline & Brain   ──► Voice + Text + Telegram WAL · Epochs · Docs · Outputs│
│  • Companions & Personalize   ──► Behavior Interview · Adaptive Style · Scoped Personas│
│  • Agent Skills (SKILL.md)    ──► 3-level progressive disclosure + self-writing loop   │
│  • Scoped Subagents & Crons   ──► Parallel worker orbs + interval/daily Automations    │
│  • Heartbeat Autonomy         ──► observe / suggest / act + HEARTBEAT_OK quiet mode    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              CONNECTORS, STREAMING DEV WORKSPACE & VISUAL OS EXECUTION                 │
│  • 17 Native SaaS Connectors  ──► Mail · Google · GitHub · Linear · Outlook · HubSpot  │
│  • Custom REST & MCP Builder  ──► Point-and-click Webhooks + HTTP/stdio JSON-RPC 2.0   │
│  • Streaming Dev Workspace    ──► Live stdout/stderr + stdin · File Tree · Git Diffs   │
│  • Visual & Semantic Grounding──► Set-of-Mark boxes · Win UIA / Linux AT-SPI · FTS5    │
│  • Zero-API GWS + 49 Actions  ──► Research · Tasks/Notes · Verified Terminals · IoT    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   CRYPTOGRAPHIC VAULT, AUDIT CHAIN & SAFETY KERNEL                     │
│  • AES-256-GCM Secret Vault   ──► Authenticated `enc:v1:` at-rest secrets + key rotate │
│  • SHA-256 Action Audit Chain ──► Tamper-evident hash-linked tool & portal ledger      │
│  • Revocable Guest Portals    ──► Read-only `/portal/<token>` links + 1-click shutoff  │
│  • Unforgeable Safety Kernel  ──► UI-issued Confirm Tokens + Shared Reversible Undo    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎛️ 3D HUD Command Deck & Voice Parity

Every subsystem in the Operating Companion can be driven visually from the **APEX-UI 3D HUD** or hands-free by natural voice/text:

| HUD Control / Shortcut | What It Opens or Controls | Matching Voice / Live Tool |
| :--- | :--- | :--- |
| **`BRAIN`** | Continuous Forever Timeline (Voice + Text + Telegram), Memories CRUD + JSON Export/Import, Drag-and-Drop Knowledge Docs, Outputs Vault, and Privacy Governance toggles | `brain_control` (`recall_memory`, `save_memory`, `forget_memory`) |
| **`STUDIO`** | 5-Step Guided Behavior Interview, Specialist Companions (scoped tool whitelists + voices), Visual `SKILL.md` Playbook Builder, 6 Theme Presets + Custom Primary/Secondary Hex Color Pickers | `companion_os`, `skill_manage`, `skill_read` |
| **`LINKS`** | **23 Native SaaS, Mail & Personal Social Connectors** (**Instagram**, **Snapchat Web**, **TikTok**, **X**, **WhatsApp Web**, **Reddit**, **Gmail**, **GitHub**, **Notion**, **Slack**, **Discord**, **Telegram**, **Spotify**, etc. with `Ask` / `Full` / `ReadOnly` / `Paused` policies), Custom REST/Webhook Builder, and MCP Server Registry (`HTTP` & `stdio`) | `manage_accounts`, `cloud_integrations`, `social_hub`, `custom_connector` |
| **Personal Socials Hub** | Persistent `AES-256-GCM` encrypted sessions + 1-click browser cookie import for **Instagram**, **Snapchat Web (`web.snapchat.com`)**, **TikTok**, **X / Twitter**, **WhatsApp Web** & **Reddit**: check unread DMs/Snaps/notifications (`check_inbox`), read threads (`read_messages`), send replies (Instagram extra prompt disabled by preference) and confirmation-gated posts (`send_message`, `post` via `core.confirm`), and control Reels/feeds hands-free (`feed`: `open_reels`, `next`, `previous`, `like`, `save`, `look`) | `social_hub` (`check_inbox`, `read_messages`, `send_message`, `post`, `feed`, `connect`, `status`) |
| **`AUTOMATE`** | Recurring Interval & Daily Automations Scheduler with 1-click Run Now, Pause/Resume, and execution history | `companion_os` (`automation_save`, `automation_run`, `automation_list`) |
| **Long-term tasks** | Durable multi-tool workflows with per-step checkpoints, output chaining, restart recovery and crash review, plus real media/time/file completion monitors | `long_task` (`workflow`, `watch_until_end`, `at_time`, `file_exists`, `file_changed`, `status`, `resume`, `cancel`) |
| **`CODE`** | Live Streaming Dev Terminal (`stdout`/`stderr` + interactive `stdin` + Stop), Codebase File-Tree Explorer, and Colorized Unified Git Diffs | `dev_agent`, `shell_agent`, `code_helper`, `github_automation` |
| **`SHIELD`** | `AES-256-GCM` Vault status & 256-bit key rotation, `SHA-256` Hash-Chained Action Audit Log verifier, and Revocable Read-Only Guest Portals (`/portal/<token>`) | `companion_os` (`portal_create`, `portal_revoke_all`, `audit_verify`) |
| **Universal Social, Web Video & YouTube Mixes** | Visually watch timestamped keyframes (`watch`), download MP4 video / MP3 audio (or entire numbered **YouTube Mix `list=RD...` & Playlist** folders), play inline inside the 3D HUD theater player (with **Mix Queue**, **Prev/Next**, **Tracklist Drawer** & **Auto-Advance**), or transcribe & summarize across **Instagram**, **YouTube (Videos, Shorts, Radio Mixes & Playlists)**, **Snapchat**, **TikTok**, **X**, **Reddit**, **Facebook**, **Twitch**, **Vimeo**, **SoundCloud** & **1,800+ sites** | `social_video` (`watch`, `download`, `play`, `summarize`, `info`, `next`, `previous`, `jump`), `video_player`, `youtube_video` |
| **`BG` (Background Mode)** | Minimizes/hides the full HUD window and docks a glowing always-on-top orb button in the **bottom-right corner of the screen**; clicking it expands a sleek quick-type & live-transcript drawer while JARVIS continuously listens and talks back | Live mic + TTS stay 100% active (`FULL ⤢` restores full 3D HUD) |
| **`ACTIVITY` / `POP OUT`** | Live `Running · Queued · Done` worker drawer with 1-click Cancel, drag-resizable bottom console, and Dual-Monitor Pop-Out Console (`/?view=console`) | `subagent` (`spawn`, `list`, `status`, `cancel`) |
| **`WASD` / `Arrows` · `Ctrl+Space` · `Ctrl×2`** | Smooth 3D World camera orbit/zoom (`WASD`/Arrows, `0` reset), global Push-to-Talk (`Ctrl+Space`), and direct cursor Flow/Dictation (`Ctrl×2`) | Always active (`"Hey Jarvis"` wake word optional) |

---

### Efficiency improvements to existing workflows

No new features or appearance changes in this maintenance pass:

- **Shared settings reads:** reuse the unchanged on-disk configuration instead of
  reopening/parsing it for every getter. Each access checks file identity, size,
  modification and change timestamps. Managed writes/key rotation invalidate
  immediately; a 250ms maximum age also covers external same-stamp edits on
  coarse-timestamp filesystems. Replacement and deletion invalidate on access. Decryption still runs afresh (no decrypted-secret cache), and
  callers receive independent dictionaries. Detected malformed writes return empty settings rather than stale
  credentials. This benefits startup, provider routing, settings and HUD snapshots.
- **Skill loading:** index only the existing 40-resource display limit, skip
  dependency/generated environments and directory symlinks, and read references
  only up to the existing 100,000-character cap. Discovery summaries log once.
  Explicit safe reference reads and existing path protections remain unchanged.
- **HUD transport:** send to windows concurrently with per-window ordering and
  bounded socket-write waits. A stalled window cannot block healthy ones; stale
  sockets close so the existing reconnect path can recover. Construct background
  broadcast coroutines on their owning loop to avoid shutdown-race leaks.

A local synthetic benchmark of 5,000 representative settings reads (median of
five runs) measured **0.1288s before → 0.0581s after (~2.22× for this operation)**.
This is not a whole-app, network/model-generation, GPU or Windows speed guarantee.
Headless regression: **546 passed, 28 skipped**; optional browser/hardware paths
still require live-device verification. Voice settings, Male/Female visuals,
Instagram send policy, Ollama behavior and paused learning were not changed.

### Automatic Ollama setup — no extra approval

Say **“Set up Ollama and download the best model for this PC.”** The discoverable
`ollama_setup` action starts a background job without another JARVIS approval.
It detects RAM/available memory and NVIDIA free VRAM, chooses a conservative
Qwen3 size (0.6B / 1.7B / 4B / 8B / 14B / 30B-A3B), checks disk space, installs
an official portable Ollama release if missing, starts its loopback HTTP server,
pulls the model and tests **actual local inference before saving settings**.
“Best” here means a documented hardware-fit heuristic, not a benchmark win.
Unknown/Apple/AMD GPU capacity is treated conservatively, not invented.

- **No admin installer or terminal approval:** official GitHub release metadata
  provides a version/size/SHA-256 digest. Only the matching official portable
  asset is accepted. No `curl | sh`, arbitrary command strings, sudo, PATH edits,
  system services, or UAC/Gatekeeper bypass. Windows x64/ARM64, Linux x64/ARM64
  and macOS x64/ARM64 have fixed asset mappings. Linux extraction uses the
  declared `zstandard` dependency. OS/security/network failures are reported.
- **Local HTTP:** managed server binds `127.0.0.1:11434`; local requests bypass
  proxy variables. Never exposes an unauthenticated Ollama server to the LAN.
  An already running server is reused, not reconfigured or killed; its existing
  bind policy remains the user's responsibility. Logs: `~/.jarvis/ollama/server.log`.
- **Honest lifecycle:** `setup`, `status`, `cancel`, `doctor`; queued is not ready.
  Completion/failure reaches the HUD/transcript. Duplicate setup requests reuse
  the active job. Interrupted work is not marked complete. Cancellation can wait
  for an HTTP read timeout; partial model blobs may remain resumable. Installer
  staging is cleaned on ordinary failures. A hard app/process crash can leave
  temporary downloads. Model downloads can be multi-GB and take considerable time.
- **Connect without breaking cloud voice:** saves `llm_provider=ollama`, local URL,
  selected model and offline fallback only after a successful response. Existing
  cloud keys (including encrypted values), persona, voice and provider are kept.
  `activate=true` explicitly selects the **local text provider** for callers of
  the provider abstraction; it does not turn Ollama into Gemini/OpenAI Realtime,
  change STT/TTS, or reroute every cloud-specific feature. Other safety gates and
  the paused-learning preference are unchanged. No automatic app launch at login.
- **Recovery:** per-user runtimes live under `~/.jarvis/ollama/runtime/`; the normal
  local client can restart this binary without a PATH change. Runtime/models are
  outside the repository. No working configuration is replaced on install,
  download, cancellation or inference failure. Fresh installs require internet
  access to official GitHub release assets and Ollama's registry/CDN.

Example: `ollama_setup(action="setup", model="auto")`. Use its returned job_id
with `status`/`cancel`. Tests simulate downloads/inference; do not mistake them
for a live hardware benchmark or a certified real-model installation.

### Instagram / Socials reliability

- **Exact handle input:** accepts `@username`, bare usernames, and exact Instagram profile links (including copied RTL formatting), with one shared normalizer across send/API/native paths. Never guesses display names or lookalike accounts. Missing SPA profile metadata can recover through an exact read-only profile lookup, then the independently checked native picker/chat. Search ignores hidden stale inputs and supports selectable checkbox/radio rows. A timeout or missing existing chat is not reported as proof the account does not exist.
- **No repeated Instagram send approval:** an explicit recipient/message request executes without an extra confirmation by default, including when the preference file is missing. Only an explicit opt-in setting/environment override restores the prompt. ReadOnly/Paused, sender changes, draft protection, exact recipient proof and single-submission/receipt rules remain enforced. No global destructive-action gates were removed.

- **Chats really open in the HUD:** “open my Instagram chats” uses `social_hub(action="open_inbox", platform="instagram")`. `check_inbox` remains a background digest. Background operations have separate browser tabs so they cannot navigate the visible HUD away from your chats.
- **One session, honest status:** current browser cookies take precedence over stale encrypted cookies. Saved credentials are shown as *not live-verified* until Instagram API/DOM evidence verifies the login. Expired logins and security challenges update LINKS/Settings and can be completed inside the HUD. Recovery preserves Ask / Full / ReadOnly / Paused and Ignore choices.
- **More than one transport:** Instagram reuses the signed-in browser through same-origin requests (fresh cookies/CSRF), or uses encrypted-cookie HTTP without starting a browser. If API lookup fails **before any send attempt**, a native headless Instagram web-composer fallback verifies the exact profile, preserves existing drafts, and uses Instagram's own Message/Send controls. Routine use never opens an external browser/app.
- **Confirmed-send event-loop safety:** browser-control calls made while Playwright owns the confirmation worker’s event loop run on an isolated CDP worker instead of nesting `asyncio.run()`. Results and failures are propagated once, without retrying a send. Regression tests use the real Playwright driver/event loop (with simulated pages and no real DMs), not only mocked Playwright startup.
- **Native Instagram sending first:** an existing authenticated browser session uses Instagram’s own composer before undocumented API writes. Exact profile verification supports canonical metadata or an exact profile-header username, Message links/buttons, verified chat dialogs, labelled editable composers, and Enter-to-send. Existing drafts remain protected, the approved text is checked before submission, and one server receipt—not a click—determines success. Failures include an `[IG:step]` recovery code, and a broken HUD display no longer suppresses the spoken result.
- **Rewritten Instagram message engine (v2):** one operation object owns explicit attach → GET-only existing-thread lookup → native conversation resolution → draft/account/permission validation → one submission → provider-receipt states. Existing exact one-to-one threads can open directly without the profile Message button or picker. UI fallback collapses only nested matching rows (not unrelated child buttons), accepts independent exact profile links, and rejects conflicting identity evidence. No recovery branch is reachable after submission starts. Audit/display failures cannot overwrite a known send result.
- **No hidden-log debugging:** the exact execution result is written to the visible SYS transcript as well as the result card. Failure states report specific observed reasons, not blanket login advice. A privacy-allowlisted `instagram_last_failure.json` in the social-session directory records engine version, state history, attempted status and structural counts only—never cookies, handles, message text, raw DOM, URLs or screenshots. Spoken reporting is instructed not to invent a cause or honorific.
- **Blocked-page detection and exact-page review:** a missing recipient search is no longer assumed to be a loaded inbox. Known login/security, encrypted-storage unlock, restriction, cookie-consent and app-interstitial screens are classified locally; one detected load error may be safely reloaded, and a uniquely labelled Not now may dismiss an optional notifications/save-login dialog. Security, PIN and consent are never clicked through. Pre-submission failures expose the same failed target in the wide HUD without navigating it; its automation mapping is relinquished so another send cannot navigate the inspection tab. Diagnostic v3 adds only an allowlisted page-state enum. An unclassified sparse page stays unclassified rather than inventing a cause.
- **Browser startup and reconnect:** restarting JARVIS can reconnect to the existing dedicated browser via Chromium’s validated `DevToolsActivePort` target or the exact legacy profile process. Startup no longer deletes profile locks or races a second browser against a live profile. New browsers bind their own debugging port; local CDP HTTP calls bypass proxy environment variables. Errors distinguish busy profiles, early browser exits, invalid configured ports, endpoint timeouts, background-tab preparation, and Playwright-driver startup instead of recommending Instagram login for browser failures. Lifecycle tests include an actual managed Chromium startup/reconnect without any Instagram navigation.
- **Conversation-opening recovery:** both standard `/direct/t/…` and encrypted `/direct/e2ee/t/…` chats are recognized. Hidden duplicate profile controls are ignored. A pre-submission navigation timeout can recover through Instagram’s own New Message recipient picker, requiring a unique exact primary username and no other selected recipient. Recovery never retries a submitted message or bypasses login/security checks. The picker accepts checkbox and ARIA-option layouts, and can launch New Message if `/direct/new/` redirects to the inbox. Step codes distinguish profile controls, chat transitions, compose search, exact-recipient lookup, selection, and opening the chat.
- **Actual-browser regressions:** `JARVIS_TEST_CHROMIUM=/path/to/chromium python -m pytest tests/test_instagram_real_browser.py` tests the confirmation worker through real CDP and Chromium DOM interactions. All requests are intercepted; no Instagram connection or real DM is made. Without an external Chromium binary these twenty-six opt-in tests skip.
- **Instagram no-extra-confirmation preference:** `config/social_preferences.json` now sets `instagram_confirm_send` to `false` at the user’s request. Instagram DMs execute without a second Confirm click, but read-only/paused permissions, exact recipient, current account, draft and receipt checks still apply. Set it to `true` (or `JARVIS_INSTAGRAM_CONFIRM_SEND=1`) to restore Ask-mode previews; other platforms and publishing are unchanged.
- **Exact recipient and real approval:** personal DMs use exact @usernames, never name fragments or group membership. When confirmation is enabled, Ask mode previews the message, waits for the real HUD Confirm click, rechecks permissions and sending-account identity, then displays the result. A second action cannot silently replace a pending confirmation.
- **No fake “sent”:** a provider-issued message acknowledgment is required. A click, HTTP 200 alone, optimistic text, or timeout is not proof. Ambiguous sends are reported as **delivery unknown** and are **not automatically retried**, avoiding duplicates. An acknowledgment is not a recipient read receipt. Like/Save controls also require an observable state change before claiming success.
- **Visible HUD failures:** interaction errors remain visible even with a stale screenshot; input is serialized, stale-session interactions are rejected, and quick text is retained when forwarding fails.
- **Limits:** Instagram's personal web endpoints and markup are undocumented and can change; login/2FA, rate limits, recipient restrictions, some encrypted-chat receipts, and unsupported UI layouts can still require manual review in the HUD. Text-only Instagram publishing is explicitly unsupported; use Instagram's own media creation UI. Tests simulate HTTP/CDP/browser flows and never send real DMs; an actual signed-in account still needs a local smoke test.

## 🔥 The 9 Architectural Pillars

### 1. Real-Time Voice, Male/Female Editions & 3D World Presence
Built around an ultra-low-latency full-duplex audio pipeline (`main.py`, `ui.py`, `core/apex_bridge.py`) that feels alive rather than turn-locked:

| Capability | Engineering |
| :--- | :--- |
| 🌐 **APEX-UI 3D Desktop HUD (Male ~300K-Particle Humanoid & Female Editions)** | Primary desktop interface (`apex_ui/`, `core/apex_bridge.py`, built on MIT-licensed `RubenM1990/APEX-UI` by Ruben Mouradian / `@reznikov_engineering`) served locally with **zero Node.js required at runtime**. On launch (`python main.py`), choose between the **Male Edition** (**~300,000-dot GPU Figure-of-Light 3D Humanoid** `ApexMaleHumanoid.tsx` with dark-to-figure birth assembly, radial shockwave + Web Audio birth synthesis, 3D depth-shaded head turn, organic breathing, living particle horizon backdrop, 4 radial facial mood blooms, and real-time voice resonance · `Charon` / `ash` voice) and **Female Edition** (Luminous Rose-Magenta & Orchid-Amethyst 3D core `ApexHeroOrb.tsx` · `Aoede` / `shimmer` voice), with live hover-preview and 1-click hot-swapping anytime (`--male` / `--female` CLI flags also supported). |
| 🪐 **Orbiting 3D Worker Orbs & Dual-Monitor Console** | Parallel subagents and `NON_BLOCKING` tools spawn orbiting 3D satellite worker orbs around the core (`WorkerOrbsLayer.tsx`) connected by energy tethers, paired with a live **Activity Drawer** (`Running · Queued · Done` + 1-click Cancel), **WASD/Arrow 3D Camera Navigation**, drag-resizable console, and a synced **Dual-Monitor Pop-Out Console** (`DualMonitorConsole.tsx`). |
| 🧑‍🎤 **Classic Software 3D Avatar (`JARVIS_CLASSIC_UI=1`)** | Optional classic PyQt6 HUD rendering the 468-vertex MediaPipe canonical face mesh (`core/face_model.obj`) with procedural skull/neck/eye rigs, 50 Hz formant + Unicode transcript lip-sync (`core/viseme.py`), phrase-tracking eyebrows, saccadic eye fixations, and live hex theming purely in `QPainter` (no GPU required). |
| 🔇 **Calibrated Barge-In & EchoGuard** | `core/echo.py` separates speaker bleed and non-speech mic noise (breathing/sighs) from real user speech so you can **interrupt JARVIS mid-sentence** at normal speaking volume (50 ms playback slicing + instant queue drain) without false self-triggers. |
| 🎙️ **Wake Word, Grace Window & PTT** | Local offline `"Hey Jarvis"` wake word (`core/wake_word.py`), **8-second wake-free follow-up grace window**, **Pause vs. Stop** controls, and global **Ctrl+Space** Push-to-Talk (`core/hotkey.py`). |
| ⚡ **Non-Blocking `WHEN_IDLE` Tool Router** | Long-running network, research, Companion OS, and UI tools execute `NON_BLOCKING` and inject results during natural speech gaps — never freezing live conversation. |
| 🌐 **97-Language Live Switching & 15-Min Auto-Recycle** | Native mid-turn response across **97 languages** (`set_language` + `WhisperSTT.set_language()`), drop-oldest mic ring buffer (`core/loop_safety.py`), and proactive **15-minute idle-gap WebSocket recycling** (`core/session_recycle.py`) so multi-hour sessions never cut out mid-sentence. |

---

### 2. The Brain & Zero-Reset Forever Timeline
JARVIS never starts from amnesia on reboot (`memory/timeline.py`, `actions/brain_control.py`, `apex_ui/components/BrainModal.tsx`):

- **Unified Cross-Channel Stream**: Every spoken voice turn, desktop text message, and inbound/outbound Telegram message writes to a single local SQLite WAL timeline (`memory/brain.db`) that reloads automatically on startup.
- **Automatic Epoch Compression**: As history grows, older stretches compress into searchable executive epoch summaries while preserving full raw transcripts for instant keyword/date search.
- **Plain-Language Memories & Portability**: Inspect, edit, or **1-click Forget** any learned fact from the `BRAIN` panel (or by voice), plus full **1-click JSON Export & Import**.
- **Drag-and-Drop Knowledge Docs & Outputs Vault**: Drop `.pdf`, `.md`, `.txt`, `.csv`, `.json`, or `.py` files into the Brain for chunked lexical/semantic retrieval during live voice & chat, and pin/search/copy every generated research brief, code artifact, or plan in the **Outputs Vault**.
- **Granular Privacy Governance**: Independent live toggles for **Timeline Persistence**, **Personalization**, and **Adaptive Style Learning** (`memory/config_manager.py`).

---

### 3. Behavior Interviews, Specialist Companions & Studio
Shape how JARVIS thinks, speaks, and delegates (`core/companions.py`, `apex_ui/components/StudioModal.tsx`):

- **5-Step Guided Behavior Interview**: Interactive Q&A capturing your role, verbosity preference, tone, autonomy comfort, and focus priorities — compiled directly into live system instructions.
- **Automatic Adaptive Style Learning**: Passively learns explicit conversational preferences (*"keep answers concise"*, *"always show commands first"*) without manual prompt engineering when Adaptive Learning is enabled.
- **Persistent Specialist Companions**: Switch between built-in specialists (**Chief of Staff**, **Senior Code Architect**, **Deep Research Analyst**, **Executive Comms**) or create custom companions with dedicated **Male/Female personas, voices (`Charon`, `Aoede`, `Puck`, `Fenrir`, `Kore`), instructions, and scoped tool whitelists**.
- **Visual Abilities (`SKILL.md`) & Custom Hex Theme Studio**: Create/edit custom Markdown skills visually and switch between **6 signature HUD theme presets** or pick **any custom Primary & Secondary hex colors** live.

---

### 4. 17 SaaS Connectors, Custom REST/MCP Builder & Recurring Automations
Connect external tools cleanly on first boot or anytime later (`memory/accounts.py`, `core/mcp_adapter.py`, `core/automations.py`):

- **Optional First-Run Integrations Onboarding**: Right after entering your Gemini API key on first launch, configure any of **17 native connectors** (**Email IMAP/SMTP App Password**, **Gmail**, **Google Calendar**, **Google Classroom**, **Google Drive**, **GitHub**, **Notion**, **Slack**, **Discord**, **Telegram**, **Spotify**, **Trello**, **Linear**, **Microsoft Outlook/Graph**, **Dropbox**, **HubSpot**, **Calendly**) — with per-service **`IGNORE`** toggles and **`IGNORE ALL / SKIP FOR NOW`** across both Male and Female editions.
- **Visual Custom REST/Webhook & MCP JSON-RPC 2.0 Builder**: Turn any HTTP endpoint + Bearer/Header secret into a live LLM tool with zero code, or register **Model Context Protocol (`MCP`)** servers over **HTTP (`POST` JSON-RPC 2.0)** or **local `stdio` subprocesses** with 1-click `tools/list` discovery and live `tools/call` invocation (`actions/custom_tools_runner.py`).
- **Recurring Automations Center**: Schedule interval (`every N minutes`) or daily (`HH:MM`) background workflows targeting any built-in, cloud, or custom tool — active in **both** the 3D APEX HUD and Classic PyQt6 mode (`main.py`), with 1-click **Run Now**, **Pause/Resume**, and run logs.

---

### 5. Live Streaming Dev Workspace & Autonomous Engineering
A real-time engineering cockpit built directly into the HUD (`core/dev_workspace.py`, `apex_ui/components/DevWorkspaceModal.tsx`):

- **Streaming Dev Terminal**: Spawns background shell, Python, npm, pytest, or git processes with real-time WebSocket `stdout`/`stderr` streaming, interactive **`stdin` input**, exit-code badges, and **1-click process tree termination**.
- **Codebase File-Tree Explorer & Colorized Git Diffs**: Browse repository files safely (path-traversal jailed with secret-file redaction) and inspect live `git status` + colorized unified diffs (`+` / `-` / `@@` hunks) side-by-side.
- **Full Developer Action Suite**: Backed by `actions/dev_agent.py`, `actions/code_helper.py`, `actions/shell_agent.py`, `core/background_agent.py`, `actions/github_automation.py`, and `actions/web_studio.py` (local dev server, live preview, SEO auditor, and 9 theme presets).

---

### 6. Multi-Provider Ladder & 100% Offline Local Mode
JARVIS never bricks when an API key hits quota or Wi-Fi drops:

- **9-Rung Gemini Model Ladder (`core/gemini.py`)**: Every Live and one-shot call walks a measured fallback ladder with automatic per-model cooldowns on quota (`429`), timeout, or preview deprecation.
- **Universal Provider Abstraction (`core/provider.py`)**: Unified failover across **Gemini**, **Anthropic**, **OpenAI**, **xAI (Grok)**, **DeepSeek**, **Groq**, **Together**, and local **Ollama / LM Studio** (`core/llm_client.py`).
- **Offline Voice Pipeline (`core/local_voice.py`, `core/stt.py`, `core/tts.py`)**: Automatically drops to local LLM inference + local **Whisper STT** + **Piper / Kokoro / Edge / pyttsx3 TTS** when cloud connectivity is unreachable, complete with Flow/Dictate hotkeys (`Ctrl×2`) for direct cursor dictation.

---

### 7. Autonomous Cognition: Open Agent Skills, Subagents & Heartbeat
- **Open Agent Skills Standard (`skills/*/SKILL.md`, `core/skill_loader.py`)**: Full [agentskills.io](https://agentskills.io) progressive-disclosure implementation (*Level 1* frontmatter at boot → *Level 2* SOP via `skill_read` → *Level 3* `references/` & `scripts/`) — compatible out of the box with skills written for **Claude Code, Codex, Cursor, GitHub Copilot, and Gemini CLI**.
- **Self-Writing Learning Loop (`skill_manage`)**: Creates, patches, and refines reusable `SKILL.md` playbooks from experience — hardened against path traversal and prompt injection.
- **Scoped Subagents (`core/subagents.py`)**: Spawns isolated multi-step workers (`spawn | list | status | result | cancel | remove`) with explicit goals, tool whitelists, `max_steps` caps, and live 3D Worker Orb telemetry.
- **Heartbeat Autonomy (`core/heartbeat.py`, `actions/proactive.py`, `actions/background_monitor.py`)**: Configurable `observe` / `suggest` / `act` autonomy levels, `HEARTBEAT_OK` quiet suppression, never-nag-twice deduplication, Morning Briefings, and daily topic watchers.

---

### 8. Visual Grounding, Screen Memory & 49-Module OS Execution Core
JARVIS sees and operates any application on screen — even apps with no API:

| Subsystem | What It Does |
| :--- | :--- |
| 🖱️ **Set-of-Mark Computer Use** (`actions/computer_use.py`) | UI-TARS / Agent-S visual grounding: `som_capture` snapshots the screen, numbers interactive elements with red bounding boxes mirrored to the HUD, and executes `click_by_id`, `type_by_id`, and `hover_by_id`. |
| 🌲 **Accessibility Tree Engine** (`actions/accessibility.py`) | Queries native OS accessibility APIs (**Windows UI Automation** / **Linux AT-SPI**) to inspect windows and press buttons by semantic name inside Discord, VS Code, Electron, and native apps. |
| 🧠 **Event-Driven Screen Memory** (`core/screen_memory.py`) | Local Rewind-style recall: change-detected screen capture, OCR + accessibility extraction, **SQLite FTS5** search (`screen_memory_search`), and per-app privacy blocklists. |
| 📦 **Zero-API GWS Pack** (`core/gws_pack.py`) | Zero-OAuth browser automation for Gmail, Docs, Drive, and Calendar via `computer_use` on your signed-in browser (`send_meeting_notes`, `schedule_meeting`, etc.). |
| 🖥️ **Verified Device, Window & Terminal Control** (`core/os_control.py`, `actions/device_manager.py`, `actions/open_app.py`) | Launches interactive PowerShell/CMD/Windows Terminal/macOS/Linux terminals in real visible foreground windows, verifies launched PIDs/window handles before reporting success, snaps/focuses/closes windows, inspects CPU/RAM/ports, and manages volume, brightness, Wi-Fi, battery, and power. |
| 🔬 **Deep Research, SQLite Productivity & Media** (`actions/deep_research.py`, `memory/productivity.py`, `actions/rag_docs.py`) | Multi-wave cited synthesis, SQLite Tasks & isolated Notes DBs, continuous Lecture Notes + homework extraction, undo-backed Safe File Organizer, Obsidian/RAG indexing, HUD YouTube/video playback, image generation, Spotify control, and flight/weather tracking. |

---

### 9. Encrypted Vault, Audit Chain, Guest Portals, Omnichannel & Safety
- **Authenticated Credential Vault (`core/security_vault.py`)**: Encrypts all connector tokens and secrets in `memory/accounts.json` at rest using **`AES-256-GCM`** (`cryptography`, PBKDF2-HMAC-SHA256 fallback) with `0600` local key permissions (`config/.vault.key`), live **256-bit key rotation**, and opt-in Strict API-Key Encryption (`config/api_keys.json`).
- **Tamper-Evident `SHA-256` Action Audit Chain**: Every tool execution, vault rotation, and portal access appends to a local SQLite ledger where each row hashes `prev_hash + timestamp + actor + action + redacted_params + status`, verifiable anytime in 1 click or via `companion_os(action="audit_verify")`.
- **Revocable Guest Portals (`/portal/<token>`)**: Share any generated brief, code output, or custom report externally via a standalone read-only link with configurable expiration, max-view limits, visitor IP/User-Agent logs, and **1-click Shut Off All Portals**.
- **Omnichannel Gateway, QR Mobile Dashboard & Smart Home**: Zero-dependency inbound/outbound webhook router (`core/multi_channel.py`), self-signed HTTPS QR phone mic/control dashboard (`dashboard/server.py`), paired Telegram bot with `/stop` (`core/telegram_bot.py`), and local **Tuya + MQTT** smart-home control (`smart_home/`).
- **Unforgeable Confirmation Gate & Shared Undo (`core/confirm.py`, `core/undo.py`)**: Destructive OS actions require a UI-minted cryptographic confirmation token that the LLM cannot forge, and file/setting mutations push inverse operations onto a unified `"undo that"` stack.

---

## ⚡ Quick Start (1-Click Native Launcher or CLI)

```bash
git clone https://github.com/mafk21/OS.git
cd OS

# Option A — 1-Click Isolated .venv + Native Desktop Launchers (Windows .bat / macOS .command)
python install_jarvis.py --install --launch

# Option B — OS-aware installer + direct launch
python setup.py        # installs deps for YOUR OS + Playwright browser engine
python main.py         # launches 3D APEX-UI HUD -> OpenAI / Gemini API key -> optional Integrations -> Male/Female chooser
```

After first install, double-click **`Start_JARVIS.bat`** (Windows) or **`Start_JARVIS.command`** (macOS) anytime — **zero Node.js required** (`apex_ui/static_hud/` ships pre-compiled).

### Useful Launch Flags & Environment Modes

```bash
python main.py --male                # Boot directly into Male Edition (Electric Cyan/Gold · Charon / ash)
python main.py --female              # Boot directly into Female Edition (Rose-Magenta/Amethyst · Aoede / shimmer)
JARVIS_CLASSIC_UI=1 python main.py   # Launch Classic PyQt6 3D face-mesh HUD instead of APEX 3D Orb HUD
python -m pytest -q                  # Run all 275 automated unit & integration tests
```

> 💡 **Optional Add-ons:**
> - **Wake Word (`"Hey Jarvis"`)**: One-click install inside the HUD under **⚙ → WAKE WORD** (`openwakeword`, runs 100% locally).
> - **Offline Mode**: Install [Ollama](https://ollama.com) or LM Studio locally — JARVIS detects and falls back to it automatically if cloud Live connectivity is unavailable.

---

## 📋 Requirements

| Requirement | Details |
| :--- | :--- |
| **OS** | Windows 10/11, macOS, or Linux |
| **Python** | **3.11 – 3.15** (uses `asyncio.TaskGroup` & `BaseExceptionGroup`) |
| **Audio** | Microphone + speakers/headphones (enumerated, measured & selectable live in HUD) |
| **API Key** | **OpenAI API key (`sk-...`)**, **Google Gemini API key (`AIza...`)**, or **both** (automatic dual-engine failover) — prompted on first launch & hot-swappable anytime under **⚙ → AI ENGINES** |
| **Node.js / GPU** | **Neither required at runtime** — `apex_ui/static_hud/` is pre-exported and Classic 3D avatar renders in software |

---

## 🗂️ Repository Architecture

```text
OS/
├── main.py                        # Core runtime — Dual-Engine OpenAI Realtime & Gemini 3.8 Live loop, duplex audio & 60 tools
├── ui.py                          # Desktop bridge + Classic PyQt6 3D Avatar HUD fallback (`JARVIS_CLASSIC_UI=1`)
├── install_jarvis.py              # 1-click isolated `.venv` installer & native launcher generator
├── Start_JARVIS.bat               # Double-click native Windows launcher
├── Start_JARVIS.command           # Double-click native macOS launcher
├── setup.py                       # Cross-platform OS-aware dependency & Playwright installer
├── requirements.txt               # Core Python runtime & cryptography/HUD dependencies
├── ROADMAP.md                     # Architectural phase roadmap & design milestones
│
├── apex_ui/                       # 3D Particle Orb & Operating Companion HUD (Next.js + Three.js)
│   ├── static_hud/                # Pre-compiled zero-Node.js production HUD served by `core/apex_bridge.py`
│   └── components/                # 13 modular 3D & HUD interfaces:
│       ├── ApexWorld.tsx          # Interactive 3D scene + WASD/Arrow camera navigation
│       ├── ApexHeroOrb.tsx        # Audio-reactive Male/Female 3D particle core & 18-node reasoning web
│       ├── WorkerOrbsLayer.tsx    # Orbiting 3D worker satellites for active subagents & background tools
│       ├── JarvisHudOverlays.tsx  # Onboarding wizard, Male/Female chooser, Command Dock & resizable console
│       ├── DualMonitorConsole.tsx # Synced standalone secondary-display console (`/?view=console`)
│       ├── BrainModal.tsx         # Forever Timeline, Memories CRUD/Export, Knowledge Docs, Outputs & Privacy
│       ├── StudioModal.tsx        # Behavior Interview, Specialist Companions, SKILL.md Studio & Hex Themes
│       ├── IntegrationsModal.tsx  # 17 SaaS Connectors, Custom REST/Webhook Builder & MCP Server Registry
│       ├── AutomationsModal.tsx   # Recurring interval & daily Automations scheduler + run logs
│       ├── DevWorkspaceModal.tsx  # Live streaming Dev Terminal, Codebase File-Tree & Colorized Git Diffs
│       └── SecurityModal.tsx      # AES-256-GCM Vault, SHA-256 Audit Chain verifier & Guest Portals
│
├── core/                          # Engine, cognition, vault security & gateway internals (37 modules)
│   ├── apex_bridge.py             # FastAPI + `/ws/hud` real-time bridge, `/portal/<token>` & HUD action router
│   ├── openai_live.py             # Full-duplex OpenAI Realtime WebSocket + Universal REST Live (Whisper+GPT-4o+TTS)
│   ├── openai_compat.py           # Universal OpenAI Multimodal Vision, JSON, Search, DALL-E 3, STT & TTS adapter
│   ├── companions.py              # Behavior Interviews, Adaptive Style Learning, Specialist Companions & Themes
│   ├── automations.py             # Recurring interval & daily Automations scheduler + run history
│   ├── mcp_adapter.py             # Custom REST/Webhook Builder + MCP JSON-RPC 2.0 (`HTTP` & `stdio`) client
│   ├── dev_workspace.py           # Live streaming Dev Terminal, Codebase File-Tree Map & Git Diffs
│   ├── security_vault.py          # AES-256-GCM Credential Vault, SHA-256 Audit Chain & Revocable Guest Portals
│   ├── gemini.py                  # 9-rung Gemini model ladder, cooldowns, transparent vault decrypt & timeouts
│   ├── provider.py                # Universal multi-provider ladder (Anthropic/OpenAI/xAI/DeepSeek/Groq/Ollama)
│   ├── llm_client.py              # Local LLM client (Ollama / LM Studio)
│   ├── local_voice.py             # Offline voice loop + Flow/Dictate hotkey pipeline
│   ├── stt.py                     # Local Whisper STT with 97-language switching hints
│   ├── tts.py                     # Multi-backend TTS (Piper, Kokoro, Edge, pyttsx3)
│   ├── avatar.py                  # Software 3D head renderer — lighting, pose, gaze, expressions (QPainter)
│   ├── avatar_mesh.py             # 3D mesh loader + procedural skull, neck & eye rigs (`face_model.obj`)
│   ├── viseme.py                  # ~50 Hz audio formant + Unicode transcript mouth-shape fusion
│   ├── echo.py                    # Self-calibrating EchoGuard for mid-speech voice barge-in
│   ├── wake_word.py               # Offline "Hey Jarvis" wake-word detector thread
│   ├── hotkey.py                  # Global/windowed Push-to-Talk chord handler
│   ├── audio_devices.py           # Filtered, measured microphone & speaker enumeration
│   ├── loop_safety.py             # Drop-oldest bounded audio queues & throttled asyncio loop guards
│   ├── session_recycle.py         # Proactive 15-min WebSocket recycler + GoAway speech-gap handoff
│   ├── skill_loader.py            # Open Agent Skills (`SKILL.md`) loader + self-writing `skill_manage`
│   ├── subagents.py               # Scoped subagent manager (spawn/list/status/result/cancel/remove)
│   ├── heartbeat.py               # Observe/suggest/act autonomy, HEARTBEAT_OK & never-nag-twice
│   ├── screen_memory.py           # Event-driven screen capture, OCR/a11y & SQLite FTS5 search
│   ├── multi_channel.py           # Omnichannel HTTP webhook server & outbound channel router
│   ├── gws_pack.py                # Zero-API Google Workspace automation via `computer_use`
│   ├── background_agent.py        # Asynchronous background job runner
│   ├── telegram_bot.py            # Paired Telegram remote control bot with `/stop` + Forever Timeline sync
│   ├── os_control.py              # Verified app/terminal launcher + live window/PID/port/hardware engine
│   ├── action_loader.py           # Auto-discovery, schema validation & crash isolation for `actions/`
│   ├── plugin_loader.py           # Hot-discovery & collision protection for drop-in `plugins/`
│   ├── confirm.py                 # Unforgeable UI-issued confirmation gate for destructive actions
│   ├── undo.py                    # Shared reversible undo stack across file & system operations
│   ├── installer.py               # On-demand optional package installer
│   └── prompt.txt                 # Dynamic system prompt template hydrated from live runtime state
│
├── actions/                       # 49 self-describing OS, cloud, companion, research & creative modules
│   ├── brain_control.py           # Voice/text Brain & Forever Timeline tool (search, remember, forget, docs, outputs)
│   ├── companion_os.py            # Voice/text Automations, Specialist Companions, Guest Portals & Audit verifier
│   ├── custom_tools_runner.py     # Runtime dispatcher for user-created Custom REST/Webhooks & MCP tools
│   ├── cloud_integrations.py      # Direct APIs across 17 SaaS & Mail services (IMAP/SMTP, Google, Linear, Outlook, etc.)
│   ├── accounts_center.py         # Per-account Ask / Full / ReadOnly / Paused permission control (17 services)
│   ├── device_manager.py          # Verified window, terminal, process, port, disk, battery & network manager
│   ├── computer_use.py            # Set-of-Mark visual grounding (`som_capture`, `click/type/hover_by_id`)
│   ├── accessibility.py           # Native UI Automation (Win) / AT-SPI (Linux) semantic element control
│   ├── computer_control.py        # Mouse, keyboard, `smart_type`, `screen_find` & window control
│   ├── computer_settings.py       # Cross-platform volume, brightness, Wi-Fi & power management
│   ├── desktop.py                 # Taskbar, virtual desktop & window orchestration
│   ├── open_app.py                # Verified app, PowerShell/terminal, folder & deep settings launcher
│   ├── screen_processor.py        # Full-screen, rubberband region & webcam vision capture
│   ├── deep_research.py           # Multi-wave cited research synthesis (`NON_BLOCKING` / `WHEN_IDLE`)
│   ├── web_search.py              # Grounded Gemini + DuckDuckGo search (news/research/price/compare)
│   ├── browser_control.py         # Voice-driven Playwright browser automation
│   ├── browser_agent.py           # Risk-tiered goal-driven browser agent
│   ├── productivity_tasks.py      # SQLite Tasks manager (due dates, priorities, pagination)
│   ├── productivity_notes.py      # Isolated searchable Notes manager
│   ├── productivity_routines.py   # Single-trigger multi-step voice routines
│   ├── productivity_checkpoints.py# Encrypted workspace checkpoints & restore
│   ├── lecture_notes.py           # Continuous lecture recorder, transcriber & homework extractor
│   ├── file_processor.py          # Universal document/PDF/code reader & Q&A
│   ├── file_controller.py         # Undo-backed safe file & directory organizer
│   ├── rag_docs.py                # Obsidian vault sync, RAG indexing & document generator
│   ├── dev_agent.py               # Autonomous multi-step software engineering helper
│   ├── code_helper.py             # Code review, refactoring & explanation tool
│   ├── shell_agent.py             # Background shell / PowerShell execution agent
│   ├── github_automation.py       # GitHub repository, commit & pull request automation
│   ├── web_studio.py              # Local web server, preview, SEO auditor & 9 theme presets
│   ├── image_generation.py        # AI image generation (OpenAI DALL-E 3 / Gemini Imagen / local SD)
│   ├── video_player.py            # Renders local/streamed video directly in the HUD avatar slot
│   ├── youtube_video.py           # YouTube search, playback & summary integration
│   ├── music_selection.py         # Spotify playback control + selection summarize/translate
│   ├── send_message.py            # Cross-app desktop messaging automation
│   ├── reminder.py                # OS-native scheduled notifications (Task Scheduler/LaunchAgent/systemd)
│   ├── calendar_monitor.py        # Proactive Calendar & Classroom deadline heads-ups
│   ├── remote_relay.py            # Opt-in remote relay connector
│   ├── proactive.py               # Time- and project-aware Proactive 2.0 check-in engine
│   ├── background_monitor.py      # Daily topic headline watcher
│   ├── system_monitor.py          # Real-time CPU, RAM, GPU & thermal telemetry alerts
│   ├── diagnostics.py             # Interactive audio, key, dependency & network health checker
│   ├── smart_home_control.py      # Voice interface for Tuya & MQTT smart-home devices
│   ├── weather_report.py          # City-aware live weather reporting
│   ├── flight_finder.py           # Live flight search & fare comparison
│   ├── game_updater.py            # Launcher/game update automation
│   ├── career_helpers.py          # LinkedIn, sysadmin diagnostic & voice KB helpers
│   ├── marketplace_action.py      # Voice/tool interface to the plugin marketplace
│   └── hosted_auth_action.py      # Opt-in email OTP hosted auth management
│
├── skills/                        # 11 default Open Agent Skills (`SKILL.md` progressive-disclosure SOPs)
│   ├── code-ship/                 # Bugfix, feature build, test verification & Git/PR shipping
│   ├── daily-briefing/            # Executive briefing (calendar, tasks, live weather, news & memory)
│   ├── deep-research/             # Multi-wave cited synthesis (+ source reliability rubric)
│   ├── focus-mode/                # Deep-work orchestrator (checkpoints, heartbeat quiet, routines & timer)
│   ├── gui-autopilot/             # Tiered GUI automation (accessibility tree → SoM `computer_use` → coords)
│   ├── meeting-copilot/           # Live lecture/meeting capture → summary, tasks & deadline reminders
│   ├── safe-file-organizer/       # Dry-run folder triage, quarantine & undo-backed cleanup
│   ├── second-brain/              # Unified recall across Brain timeline, notes, RAG vault & screen FTS5
│   ├── system-doctor/             # Hardware, audio, network, storage & subsystem diagnostics
│   └── workspace-comms/           # Gmail, Docs, Drive, Calendar & omnichannel messaging SOP
│
├── memory/                        # Persistent local state, SQLite WAL stores & encrypted vault files
│   ├── timeline.py                # Zero-Reset Forever Timeline, epoch compression, Knowledge Docs & Outputs Vault
│   ├── memory_manager.py          # Two-tier long-term memory, search, hygiene, JSON export/import & summaries
│   ├── config_manager.py          # Thread-safe preferences, Male/Female persona & Privacy Governance toggles
│   ├── productivity.py            # SQLite backend for tasks, notes & productivity state
│   ├── accounts.py                # 17-service connector registry (`AES-256-GCM` encrypted at rest) & API clients
│   └── routines.json              # Saved multi-step voice routines
│
├── dashboard/                     # Local HTTPS mobile companion server (QR pairing + phone mic relay)
├── smart_home/                    # Tuya & MQTT IoT protocol adapters
├── marketplace/                   # Versioned, isolated plugin marketplace installer
├── auth/                          # Opt-in email OTP + quota hosted authentication client
├── plugins/                       # Drop-in user plugins (`_template.py` starter included)
├── config/                        # Local runtime keys, `.vault.key` & self-signed TLS certs (git-ignored)
├── LICENSE                        # MIT License
└── tests/                         # 275 automated `pytest` unit & integration tests across 32 test suites
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).

### Female humanoid: existing edition, same scene as Male

The approved female contour portrait is placed in the actual **Female edition** of
`apex_ui/components/ApexWorld.tsx`, selected by the existing `activePersona` flow.
It uses the same full-viewport dark humanoid scene and animation engine as Male,
with the existing rose/orchid theme. The app root, overview, system dialogs,
background mode and console route stay connected to the original HUD/provider.
The incorrect standalone blue reference-screen placement and local figure switch
were removed. Choose Female through the existing edition selector; there is no
second visual preference or new setup flow. Voice/approval/backend behavior is
unchanged. See `apex_ui/README.md` for routing and asset details.

### Windows, macOS, and Linux support

The desktop runtime detects the **current host OS** for native actions; it does
not trust an `os_system` value copied from another computer. Native launchers are
included for Windows (`Start_JARVIS.bat`), macOS (`Start_JARVIS.command`), and
Linux (`Start_JARVIS.sh`). Python 3.11+ is required, and `requirements.txt` uses
platform markers so Windows-only packages are skipped elsewhere.

Cross-platform behavior includes verified app/terminal launching, Command-key
clipboard shortcuts on macOS, shell-specific command routing (`bash`, `zsh`,
`sh`, and `pwsh` where installed), PulseAudio or PipeWire volume controls on
Linux, safe process-tree cancellation, headless import degradation, and paths
containing spaces or Unicode. Some operating-system actions still require host
permissions or installed native tools: macOS Accessibility/Automation approval;
a graphical X11/Wayland session for Linux GUI automation; `pactl` or `wpctl` for
Linux volume; and `brightnessctl` or desktop display utilities for brightness.
The app returns an explicit limitation instead of reporting false success.

`.github/workflows/cross-platform.yml` installs the real OS-filtered dependencies
and runs startup/platform regressions on Windows, macOS, and Ubuntu with Python
3.11 and 3.12. The HUD is separately type-checked and production-built. Local
Linux validation currently covers the complete Python test suite; CI is the
source of native Windows/macOS results.
