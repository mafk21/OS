# ⚡ OS

**A full-duplex desktop AI operating layer with real-time voice, a 3D software-rendered holographic avatar, Set-of-Mark visual computer use, FTS5 screen memory, self-writing procedural skills, scoped subagents, an omnichannel messaging gateway, and seamless offline fallback.**

| Metric | Scale |
| :--- | :--- |
| **Codebase** | **34,000+ lines** across **85+ Python modules** (`Windows` · `macOS` · `Linux`) |
| **Execution Surface** | **46 self-describing OS actions** + **15 live-session tools** + **10 default `SKILL.md` playbooks** + **drop-in plugins & MCP** |
| **Live Voice Engine** | **Gemini 3.8 Live** bidirectional audio + **9-rung model ladder** + **97-language** mid-turn switching |
| **Provider & Offline Stack** | **8 cloud/local LLM providers** (Gemini, Anthropic, OpenAI, xAI, DeepSeek, Groq, Together, Ollama) + local **Whisper STT / Piper-Kokoro TTS** |
| **Rendering** | **Zero GPU required** — 3D MediaPipe canonical head mesh, lighting, rig & ~50 Hz formant/transcript lip-sync rendered pure in software (`QPainter`) |
| **Verification** | **179+ automated `pytest` tests** covering voice, session recycling, scheduling, memory, default skills, subagents, computer use, screen memory, gateway & GWS automation |

---

## 🧠 System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                        INPUT & PRESENCE SURFACES                                     │
│  🎙️ Full-Duplex Mic (EchoGuard + Barge-In + Wake Word + Ctrl+Space PTT + Grace Win)  │
│  👁️ Vision (Full Screen · Rubberband Region · Live Webcam · Event-Driven OCR/a11y)   │
│  🌍 Omnichannel Inbound (Webhook Gateway · Telegram Bot · TLS Phone QR Dashboard)    │
│  🌐 APEX-UI Desktop HUD (3D Cyan Particle Orb · 18-Node Reasoning Web · Live WS)    │
│  🧑‍🎤 Classic PyQt6 Fallback (`JARVIS_CLASSIC_UI=1` · 3D Avatar · 50Hz Visemes)       │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME ORCHESTRATION & PROVIDER KERNEL                        │
│  • Gemini 3.8 Live WebSocket  ──► SessionResumption + Compression + 15m Auto-Recycle │
│  • Per-Tool Scheduling        ──► NON_BLOCKING + WHEN_IDLE speech-gap delivery       │
│  • 9-Rung Gemini Ladder       ──► Auto-failover on quota / timeout / deprecation     │
│  • Universal Provider Ladder  ──► Anthropic · OpenAI · xAI · DeepSeek · Groq · Ollama│
│  • Offline Local Voice Loop   ──► Local LLM + Whisper STT + Local TTS (zero cloud)   │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                       AUTONOMOUS COGNITIVE LAYER                                     │
│  • Agent Skills (SKILL.md)    ──► 3-level progressive disclosure (agentskills.io)    │
│  • Self-Writing Learning Loop ──► skill_manage creates/patches skills from experience│
│  • Scoped Subagents           ──► Goal tracking, tool whitelists & result isolation  │
│  • Heartbeat Autonomy         ──► observe / suggest / act + HEARTBEAT_OK quiet mode  │
│  • Two-Tier Memory + Hygiene  ──► Core prompt identity + unlimited local search      │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                  VISUAL GROUNDING, OS CONTROL & SAFETY KERNEL                        │
│  • Set-of-Mark Computer Use   ──► Numbered UI bounding boxes → click/type by ID      │
│  • Native Accessibility Tree  ──► Windows UI Automation / Linux AT-SPI element press │
│  • Screen Memory (SQLite FTS5)──► Searchable OCR + window/a11y timeline              │
│  • GWS Pack (Zero-API/OAuth)  ──► Gmail · Docs · Drive · Calendar via computer_use   │
│  • 46 Bundled Actions         ──► Deep Research · Tasks/Notes · Dev/Shell · IoT      │
│  • Unforgeable Safety Kernel  ──► UI-issued Confirm Tokens + Shared Reversible Undo  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔥 The 7 Pillars

### 1. Real-Time Voice, Barge-In & 3D Holographic Presence
Built around an ultra-low-latency full-duplex audio pipeline (`main.py`, `ui.py`) that feels alive rather than turn-locked:

| Capability | Engineering |
| :--- | :--- |
| 🌐 **APEX-UI 3D Desktop HUD (Male & Female Editions)** | Primary desktop interface (`apex_ui/`, `core/apex_bridge.py`, based on MIT-licensed `RubenM1990/APEX-UI` by Ruben Mouradian / `@reznikov_engineering`) served locally with **zero Node.js required at runtime**. On launch (`python main.py`), choose between the **Male Edition** (Electric Cyan & Stark Gold 3D core · `Charon` deep baritone voice) and **Female Edition** (Luminous Rose-Magenta & Orchid-Amethyst 3D core · `Aoede` natural female voice), with live hover-preview and 1-click hot-swapping anytime from the HUD. Set `JARVIS_CLASSIC_UI=1` to use the classic PyQt6 avatar window instead. |
| 🧑‍🎤 **Classic Software 3D Avatar** | Optional classic PyQt6 HUD (`JARVIS_CLASSIC_UI=1`) rendering the 468-vertex MediaPipe canonical face mesh (`core/face_model.obj`) with procedural skull/neck/eye rigs, dynamic lighting, and live hue/hex theming purely in `QPainter`. |
| 👄 **50 Hz Formant + Transcript Lip-Sync** | `core/viseme.py` fuses real-time audio formants with incoming transcript phonemes for accurate bilabial closures, spreads, and rounded vowels across Latin, Cyrillic, and Greek scripts via Unicode reduction. |
| 🙂 **State-Driven Facial Acting** | Phrase-tracking eyebrows, saccadic eye fixations, stressed-syllable nods, thinking gaze-away, eye contact while listening, closed lids while sleeping, and downward glances when HUD content updates. |
| 🔇 **Calibrated Barge-In & EchoGuard** | `core/echo.py` separates speaker bleed from real user speech so you can **interrupt JARVIS mid-sentence** (50 ms playback slicing + instant queue drain) without triggering on its own voice. |
| 🎙️ **Wake Word, Grace Window & PTT** | Local offline `"Hey Jarvis"` wake word (`core/wake_word.py`), **8-second wake-free follow-up grace window**, **Pause vs. Stop** controls, and global **Ctrl+Space** Push-to-Talk (`core/hotkey.py`). |
| ⚡ **Non-Blocking `WHEN_IDLE` Tools** | Slow network/UI tools (`web_search`, `deep_research`, `file_processor`, `browser_control`, `send_message`, `computer_use`, `multi_channel`, `gws_pack`) execute `NON_BLOCKING` and inject results during natural speech gaps — never freezing conversation. |
| 🌐 **97-Language Live Switching** | Native mid-turn detection and response across **97 languages** on `gemini-3.8-live`, backed by `set_language` persistent preference storage and `WhisperSTT.set_language()` hints. |
| 🔗 **Resilient Bounded Streaming** | Drop-oldest mic ring buffer (`out_put_drop_oldest`, 64-block / ~4s ceiling) prevents WebSocket ping-timeouts under backpressure; `SessionResumptionConfig` + `ContextWindowCompressionConfig` preserve context across reconnects and multi-hour sessions. |
| ♻️ **Proactive 15-Min Session Recycle** | `core/session_recycle.py` beats Gemini Live's ~15-minute WebSocket hard cutoff (and server `GoAway` notices) by waiting for an idle speech gap with zero active audio, tools, or vision frames and silently rebuilding a resumed connection before Google severs the socket mid-sentence. |

---

### 2. Multi-Provider Ladder & 100% Offline Local Mode
  never bricks when an API key hits quota or Wi-Fi drops:

- **9-Rung Gemini Model Ladder (`core/gemini.py`)**: Every Live and one-shot call walks a measured fallback ladder with automatic per-model cooldowns on quota (`429`), timeout, or preview deprecation.
- **Universal Provider Abstraction (`core/provider.py`)**: Unified failover across **Gemini**, **Anthropic**, **OpenAI**, **xAI (Grok)**, **DeepSeek**, **Groq**, **Together**, and local **Ollama / LM Studio** (`core/llm_client.py`).
- **Offline Voice Pipeline (`core/local_voice.py`, `core/stt.py`, `core/tts.py`)**: Automatically drops to local LLM inference + local **Whisper STT** + **Piper / Kokoro / Edge / pyttsx3 TTS** when cloud connectivity is unreachable, complete with Flow/Dictate hotkeys (`Ctrl×2`) for direct cursor dictation.

---

### 3. Autonomous Cognition: Self-Writing Skills, Subagents, Heartbeat & Memory
Instead of a static system prompt, JARVIS learns procedures, delegates work, and manages its own attention:

- **Open Agent Skills Standard (`skills/*/SKILL.md`, `core/skill_loader.py`)**: Full implementation of the [agentskills.io](https://agentskills.io) specification — compatible out of the box with skills written for **Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, skills.sh, and ClawHub**:
  - *Level 1*: Only `name` + `description` frontmatter enter `[SKILLS]` at startup (tiny token footprint).
  - *Level 2*: Full `SKILL.md` SOP body loads on demand via `skill_read`.
  - *Level 3*: Bundled `references/` and `scripts/` load only when referenced.
- **Self-Writing Learning Loop (`skill_manage`)**: When JARVIS solves a non-trivial workflow, hits a platform quirk, or gets corrected by the user, it calls `skill_manage` (`create | edit | patch | delete`) to write or refine reusable `SKILL.md` skills — hardened against path traversal and prompt-injection payloads.
- **Subagent Task Decomposition (`core/subagents.py`)**: Complex 5+ step missions can spawn isolated subagents (`spawn | list | status | result | cancel | remove`) with explicit goals, **scoped tool whitelists**, step-by-step audit logs, `max_steps` runaway caps, and isolated result handoff.
- **Heartbeat Autonomy (`core/heartbeat.py`, `actions/proactive.py`, `actions/background_monitor.py`)**: Configurable `observe` / `suggest` / `act` autonomy levels, `heartbeat_ok` quiet-mode suppression, **never-nag-twice** topic deduplication, Morning Briefings, context-aware Proactive 2.0 check-ins, and daily background topic monitors.
- **Two-Tier Recallable Memory & Hygiene (`memory/memory_manager.py`)**: Keeps core identity lean inside the system prompt while storing unlimited personal facts, project context, and next-morning session summaries locally — searchable on demand via `recall_memory`, automatically deduplicated/cleaned, and editable in one click from the HUD **Memory Panel**.

---

### 4. Visual Grounding, Screen Memory & Zero-API Workspace Automation
JARVIS sees and operates any application on screen — even apps with no API:

| Subsystem | What It Does |
| :--- | :--- |
| 🖱️ **Set-of-Mark Computer Use** (`actions/computer_use.py`) | UI-TARS / Agent-S visual grounding: `som_capture` snapshots the screen, detects interactive elements, draws numbered red bounding boxes mirrored live to the HUD, and executes `click_by_id`, `type_by_id`, and `hover_by_id` with coordinate fallback. |
| 🌲 **Accessibility Tree Engine** (`actions/accessibility.py`) | Queries native OS accessibility APIs (**Windows UI Automation** / **Linux AT-SPI**) to inspect windows and press buttons by semantic name inside Discord, VS Code, Electron, and native apps. |
| 🧠 **Event-Driven Screen Memory** (`core/screen_memory.py`) | Local Rewind-style recall: background screen capture with change detection, OCR + accessibility text extraction, **SQLite FTS5** full-text indexing (`screen_memory_search`), per-app blocklists, and local privacy permissions. |
| 📦 **GWS Pack** (`core/gws_pack.py`) | **Zero-API, zero-OAuth Google Workspace automation** (`gmail_send`, `gmail_search`, `docs_create`, `docs_write`, `drive_upload`, `calendar_add`, `gws_open`, plus multi-step `workflow`s like `send_meeting_notes` and `schedule_meeting`) driven via `computer_use` on your already signed-in browser, with human-readable SOP fallbacks. |
| 📷 **Multi-Angle Live Vision** (`actions/screen_processor.py`) | Pipes full-screen captures, interactive rubberband **region captures**, or live webcam frames directly into the active Gemini Live conversation. |

---

### 5. Deep Research, Productivity Core, Developer & Creative Studio
46 self-describing action modules in `actions/` give JARVIS deep domain execution out of the box:

- **Deep Research & Multi-Mode Search (`actions/deep_research.py`, `actions/web_search.py`)**: Multi-wave parallel research that decomposes questions into sub-queries, cross-verifies sources via Gemini Grounding + DuckDuckGo, and delivers bottom-line-first reports with inline citations — alongside specialized `news`, `price`, `compare`, and `search` modes rendered in the HUD Content Panel.
- **SQLite Productivity Suite (`memory/productivity.py`, `actions/productivity_*.py`, `actions/lecture_notes.py`)**:
  - **Tasks DB**: Priorities, due dates, search, complete/reopen, archive, 20/page pagination.
  - **Notes DB**: Dedicated searchable notes isolated from conversational auto-memory.
  - **Live Lecture Notes**: Continuous mic capture + live transcription → structured summary, key takeaways, and homework extraction on `"stop the notes"`.
  - **Voice Routines & Checkpoints**: Single-phrase multi-action routines (`memory/routines.json`, e.g. *"study mode"*) and encrypted workspace state checkpoints with reviewable restore.
- **Developer, Shell & Web Studio (`actions/dev_agent.py`, `actions/code_helper.py`, `actions/shell_agent.py`, `core/background_agent.py`, `actions/github_automation.py`, `actions/web_studio.py`)**: Code generation/analysis, background shell & long-running job execution while you keep chatting, GitHub PR/commit/issue automation, and a local Web Studio with live dev server, Chrome preview, SEO auditor, and 9 theme presets.
- **Browser, RAG, Media & Desktop Control**:
  - **Goal-Driven Browser (`actions/browser_control.py`, `actions/browser_agent.py`)**: Playwright automation with low/medium/high risk permission gating and safe messaging review.
  - **RAG & Universal File Processor (`actions/rag_docs.py`, `actions/file_processor.py`, `actions/file_controller.py`)**: Obsidian vault sync, local RAG indexing, document generation, PDF/Doc/code reading, and undo-backed file management.
  - **Verified Device, Window, Process & Terminal Control (`actions/device_manager.py`, `actions/open_app.py`, `core/os_control.py`, `actions/computer_settings.py`, `actions/computer_control.py`, `actions/desktop.py`)**: Opens interactive PowerShell/CMD/Windows Terminal/macOS/Linux terminals in real visible foreground windows (bypassing background `CREATE_NO_WINDOW`), verifies launched apps against live OS window handles and PIDs before reporting success, manages windows by name (`list_windows`, `focus_window`, `close_window`, `snap_left`/`snap_right`), inspects/stops top CPU/RAM processes and TCP/UDP port owners with HUD confirmation gates, and controls volume, brightness, deep `ms-settings:` pages, Wi-Fi, battery, storage, and power.
  - **HUD Video, Music, Creative & Utilities**: Plays YouTube/local video directly in the HUD avatar slot (`actions/video_player.py`, `actions/youtube_video.py`), generates images (`actions/image_generation.py`), controls Spotify & translates/summarizes text selections (`actions/music_selection.py`), tracks flights (`actions/flight_finder.py`), updates games (`actions/game_updater.py`), assists with LinkedIn/sysadmin workflows (`actions/career_helpers.py`), schedules OS-native reminders (`actions/reminder.py`), and monitors CPU/RAM/GPU/temps (`actions/system_monitor.py`).

---

### 6. Omnichannel Gateway, Mobile Remote & Smart Home
Talk to and control the same live JARVIS instance from your desk, phone, or chat apps:

- **Multi-Channel Gateway (`core/multi_channel.py`)**: Zero-dependency inbound HTTP webhook server (`127.0.0.1:8766/webhook`) + outbound channel registry (`desktop`, `telegram`, `whatsapp`, `discord`, `slack`, `imessage`). Inbound messages inject directly into the active Gemini Live session via `run_coroutine_threadsafe`; outbound replies dispatch or broadcast non-blockingly (`send | channels | webhook | broadcast`).
- **QR-Paired HTTPS Mobile Dashboard (`dashboard/server.py`)**: Generates a local self-signed TLS certificate (`config/certs/`) and one-tap QR code so your phone can stream mic audio, send commands, and monitor live status over LAN.
- **Telegram Remote & Relay (`core/telegram_bot.py`, `actions/remote_relay.py`)**: Pairing-code authenticated Telegram bot with `/stop` instant task cancellation, plus optional opt-in internet relay.
- **Account Center & Calendar Heads-Ups (`memory/accounts.py`, `actions/accounts_center.py`, `actions/calendar_monitor.py`)**: Per-service permission policies (`Ask` / `Full` / `ReadOnly` / `Paused`) and proactive heads-ups 10 minutes before Calendar events or 24h/2h before Classroom deadlines.
- **Smart Home IoT (`smart_home/mqtt.py`, `smart_home/tuya.py`, `actions/smart_home_control.py`)**: Local Tuya and MQTT device control by voice.

---

### 7. Defense-in-Depth Safety & 3-Layer Extensibility
- **Unforgeable Confirmation Gate (`core/confirm.py`)**: Destructive or irreversible operations (shutdown, restart, Wi-Fi toggles, high-risk actions) require a cryptographic/UI token minted **only** when you click Confirm on the HUD — the LLM cannot synthesize or bypass confirmation on its own.
- **Shared Reversible Undo Stack (`core/undo.py`)**: File moves, renames, writes, creations, and system setting changes register inverse operations on one unified stack — say *"undo that"* to roll back.
- **Diagnostics Health Center (`actions/diagnostics.py`)**: Built-in hardware, audio device, API key, and connectivity self-test with actionable fix instructions.
- **Three Clean Ways to Extend JARVIS**:
  1. **`skills/<name>/SKILL.md`** — Drop in any Markdown skill (or let JARVIS write its own via `skill_manage`).
  2. **`plugins/<name>.py`** — Drop a single Python file into `plugins/` (isolated validation & crash containment via `core/plugin_loader.py`) or install versioned plugins via `marketplace/marketplace.py`.
  3. **MCP Servers (`core/mcp_adapter.py`)** — Expose any Model Context Protocol server as native JARVIS tools.

---

## ⚡ Quick Start

```bash
git clone https://github.com/mafk21/OS.git
cd OS
python setup.py        # OS-aware installer: installs deps for YOUR OS + Playwright browser engine
python main.py         # launches APEX-UI HUD -> pick Male or Female edition -> starts Gemini Live
# Optional direct CLI preset: python main.py --female   or   python main.py --male
```

`setup.py` validates your Python version up front and automatically skips packages meant for other operating systems (Windows-only COM/UIA libraries are skipped on macOS/Linux and vice versa). Manual install works too:

```bash
pip install -r requirements.txt
```

### Running the Test Suite

```bash
pytest tests/ -q
```

> 💡 **Optional Add-ons:**
> - **Wake Word (`"Hey Jarvis"`)**: One-click install inside the HUD under **⚙ → WAKE WORD** (`openwakeword`, runs 100% locally).
> - **Offline Mode**: Install [Ollama](https://ollama.com) or LM Studio locally —   detects and falls back to it automatically if cloud Live is unavailable.

---

## 📋 Requirements

| Requirement | Details |
| :--- | :--- |
| **OS** | Windows 10/11, macOS, or Linux |
| **Python** | **3.11 – 3.15** (uses `asyncio.TaskGroup` & `BaseExceptionGroup`) |
| **Audio** | Microphone + speakers/headphones (enumerated, measured & selectable live in HUD) |
| **API Key** | Free Gemini API key (prompted on first launch → saved locally to git-ignored `config/api_keys.json`; optional multi-provider keys or Hosted Auth OTP supported) |
| **GPU** | **Not required** — 3D avatar, visemes, and HUD video all render in software |

---

## 🗂️ Repository Architecture

```text
OS/
├── main.py                        # Core runtime — Gemini 3.8 Live loop, duplex audio, visemes, tool router
├── ui.py                          # PyQt6 HUD — 3D avatar canvas, waveform, content panel, memory & settings
├── setup.py                       # Cross-platform OS-aware dependency & browser installer
├── ROADMAP.md                     # Architectural phase roadmap & design milestones
│
├── core/                          # Engine, cognition, safety & gateway internals
│   ├── gemini.py                  # 9-rung Gemini model ladder, cooldowns & timeout management
│   ├── provider.py                # Universal multi-provider ladder (Anthropic/OpenAI/xAI/DeepSeek/Groq/Ollama)
│   ├── llm_client.py              # Local LLM client (Ollama / LM Studio)
│   ├── local_voice.py             # Offline voice loop + Flow/Dictate hotkey pipeline
│   ├── stt.py                     # Local Whisper STT with 97-language switching hints
│   ├── tts.py                     # Multi-backend TTS (Piper, Kokoro, Edge, pyttsx3)
│   ├── avatar.py                  # Software 3D head renderer — lighting, pose, gaze, expressions (QPainter)
│   ├── avatar_mesh.py             # 3D mesh loader + procedural skull, neck & eye rigs
│   ├── face_model.obj             # MediaPipe canonical 468-vertex face mesh (Apache-2.0)
│   ├── viseme.py                  # ~50 Hz audio formant + Unicode transcript mouth-shape fusion
│   ├── echo.py                    # Self-calibrating EchoGuard for mid-speech voice barge-in
│   ├── wake_word.py               # Offline "Hey Jarvis" wake-word detector thread
│   ├── hotkey.py                  # Global/windowed Push-to-Talk chord handler
│   ├── audio_devices.py           # Filtered, measured microphone & speaker enumeration
│   ├── loop_safety.py             # Drop-oldest bounded audio queues & throttled asyncio loop guards
│   ├── session_recycle.py         # Proactive 15-min WebSocket recycler + GoAway speech-gap handoff
│   ├── skill_loader.py            # Open Agent Skills (SKILL.md) loader + self-writing skill_manage
│   ├── subagents.py               # Scoped subagent manager (spawn/list/status/result/cancel/remove)
│   ├── heartbeat.py               # Observe/suggest/act autonomy, HEARTBEAT_OK & never-nag-twice
│   ├── screen_memory.py           # Event-driven screen capture, OCR/a11y & SQLite FTS5 search
│   ├── multi_channel.py           # Omnichannel HTTP webhook server & outbound channel router
│   ├── gws_pack.py                # Zero-API Google Workspace automation via computer_use
│   ├── background_agent.py        # Asynchronous background job runner
│   ├── telegram_bot.py            # Paired Telegram remote control bot with /stop support
│   ├── os_control.py              # Verified app/terminal launcher + live window/PID/port/hardware engine
│   ├── action_loader.py           # Auto-discovery, schema validation & crash isolation for actions/
│   ├── plugin_loader.py           # Hot-discovery & collision protection for drop-in plugins/
│   ├── mcp_adapter.py             # Model Context Protocol (MCP) server-to-tool bridge
│   ├── confirm.py                 # Unforgeable UI-issued confirmation gate for destructive actions
│   ├── undo.py                    # Shared reversible undo stack across file & system operations
│   ├── installer.py               # On-demand optional package installer
│   └── prompt.txt                 # Dynamic system prompt template hydrated from live runtime state
│
├── actions/                       # 47 self-describing OS, research, productivity & creative actions
│   ├── device_manager.py          # Verified window, terminal, process, port, disk, battery & network manager
│   ├── computer_use.py            # Set-of-Mark visual grounding (som_capture, click/type/hover_by_id)
│   ├── accessibility.py           # Native UI Automation (Win) / AT-SPI (Linux) semantic element control
│   ├── computer_control.py        # Mouse, keyboard, smart_type, screen_find & window control
│   ├── computer_settings.py       # Cross-platform volume, brightness, Wi-Fi & power management
│   ├── desktop.py                 # Taskbar, virtual desktop & window orchestration
│   ├── open_app.py                # Verified app, PowerShell/terminal, folder & deep settings launcher
│   ├── screen_processor.py        # Full-screen, rubberband region & webcam vision capture
│   ├── deep_research.py           # Multi-wave cited research synthesis (NON_BLOCKING / WHEN_IDLE)
│   ├── web_search.py              # Grounded Gemini + DuckDuckGo search (news/research/price/compare)
│   ├── browser_control.py         # Voice-driven Playwright browser automation
│   ├── browser_agent.py           # Risk-tiered goal-driven browser agent
│   ├── productivity_tasks.py      # SQLite Tasks manager (due dates, priorities, pagination)
│   ├── productivity_notes.py      # Isolated searchable Notes manager
│   ├── productivity_routines.py   # Single-trigger multi-step voice routines
│   ├── productivity_checkpoints.py# Encrypted workspace checkpoints & restore
│   ├── lecture_notes.py           # Continuous lecture recorder, transcriber & homework extractor
│   ├── file_processor.py          # Universal document/PDF/code reader & Q&A
│   ├── file_controller.py         # Undo-backed file & directory operations
│   ├── rag_docs.py                # Obsidian vault sync, RAG indexing & document generator
│   ├── dev_agent.py               # Autonomous multi-step software engineering helper
│   ├── code_helper.py             # Code review, refactoring & explanation tool
│   ├── shell_agent.py             # Background shell / PowerShell execution agent
│   ├── github_automation.py       # GitHub repository, commit & pull request automation
│   ├── web_studio.py              # Local web server, preview, SEO auditor & 9 theme presets
│   ├── image_generation.py        # AI image generation (Gemini Imagen / local SD)
│   ├── video_player.py            # Renders local/streamed video directly in the HUD avatar slot
│   ├── youtube_video.py           # YouTube search, playback & summary integration
│   ├── music_selection.py         # Spotify playback control + selection summarize/translate
│   ├── send_message.py            # Cross-app desktop messaging automation
│   ├── reminder.py                # OS-native scheduled notifications (Task Scheduler/LaunchAgent/systemd)
│   ├── calendar_monitor.py        # Proactive Calendar & Classroom deadline heads-ups
│   ├── accounts_center.py         # Per-account Ask / Full / ReadOnly / Paused permission control
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
├── skills/                        # 10 default Open Agent Skills (SKILL.md progressive-disclosure SOPs)
│   ├── README.md                  # Spec & authoring guide
│   ├── _template/                 # Starter template for new skills
│   ├── code-ship/                 # Bugfix, feature build, test verification & Git/PR shipping (+ checklist)
│   ├── daily-briefing/            # Executive briefing (calendar, tasks, live weather, news & memory)
│   ├── deep-research/             # Multi-wave cited synthesis (+ source reliability rubric)
│   ├── focus-mode/                # Deep-work orchestrator (checkpoints, heartbeat quiet, routines & timer)
│   ├── gui-autopilot/             # Tiered GUI automation (accessibility tree → SoM computer_use → coords)
│   ├── meeting-copilot/           # Live lecture/meeting capture → summary, tasks & deadline reminders
│   ├── safe-file-organizer/       # Dry-run folder triage, quarantine & undo-backed cleanup
│   ├── second-brain/              # Unified recall across memory, notes, RAG vault & FTS5 screen history
│   ├── system-doctor/             # Hardware, audio, network, storage & subsystem diagnostics
│   └── workspace-comms/           # Gmail, Docs, Drive, Calendar & omnichannel messaging SOP
│
├── memory/                        # Persistent local state & SQLite stores
│   ├── memory_manager.py          # Two-tier long-term memory, search, hygiene & session summaries
│   ├── config_manager.py          # Thread-safe config/api_keys.json preferences & toggles
│   ├── productivity.py            # SQLite backend for tasks, notes & productivity state
│   ├── accounts.py                # Connected service registry & permission tiers
│   └── routines.json              # Saved multi-step voice routines
│
├── dashboard/                     # Local HTTPS mobile companion server (QR pairing + phone mic relay)
├── smart_home/                    # Tuya & MQTT IoT protocol adapters
├── marketplace/                   # Versioned, isolated plugin marketplace installer
├── auth/                          # Opt-in email OTP + quota hosted authentication client
├── plugins/                       # Drop-in user plugins (_template.py starter included)
├── config/                        # Local runtime keys & self-signed TLS certs (git-ignored)
├── LICENSE                        # MIT License
└── tests/                         # 212+ pytest unit & integration tests across all phases
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).

