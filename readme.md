## 🚀 Capabilities
### Core Features
| Feature | Description |
|
---|---|
| 🧑‍🎤 Holographic Avatar | An animated human head in the HUD — real facial geometry, lit and drawn in software, no GPU or extra packages |
| 👄 Real Lip-Sync | ~50 mouth shapes a second from the audio's formants **and** the transcript — closures, spreads and rounds, not a volume meter |
| 🌍 Language-Free Mouth | Articulation is derived by Unicode reduction, so Latin, Cyrillic and Greek scripts all work from one rule set — and scripts that hide pronunciation fall back cleanly |
| 🙂 Facial Acting | Brows track the phrase, gaze saccades between fixations, natural blinking, a small nod on stressed syllables |
| 😐 Face as Status | Looks away while thinking, meets your eyes while listening, lids fall while asleep, glances down at new content |
| 🎚️ Push-to-Talk | Hold **Ctrl+Space** and the mic opens — closed the rest of the time. Truly global on Windows, window-scoped elsewhere |
| 🔇 Self-Echo Guard | Never answers its own last sentence: the tail of its own voice is recognised and dropped without muting you |
| 🪪 Runtime Self-Knowledge | Name, OS, abilities **and limits** are generated from the live system each session — rename it or add a plugin and it knows |
| 🎙️ Wake Word | Local **"Hey Jarvis"** detection — sleeps until called, auto-sleeps after 2 min of silence, and never streams audio while asleep |
| ⚡ Instant Acknowledgment | Speaks a short, context-aware reply in **your language** the instant a longer task starts — no more silent waiting |
| 🚀 Faster Live Engine | Runs on **Gemini 3.1 Flash Live** — roughly 2× faster time-to-first-word than the previous model |
| 🧩 Self-Describing Skills | Every bundled skill declares its own `TOOL` dict + handler and is auto-discovered at launch — adding one is a single file |
| 🧠 Recallable Memory | No size limit and nothing silently forgotten — the prompt carries what fits, the rest is looked up on demand from a local search |
| 👁️ Memory Panel | See every fact JARVIS has stored about you, when it learned it, and delete any of it in one click |
| ↩️ Undo | Take back what the assistant did — files it moved, renamed, created or wrote, and settings it changed |
| ⚠️ Real Confirmation | Shutdown, restart and WiFi wait for a button **you** press — the model cannot confirm its own irreversible actions |
| 🎧 Audio Device Picker | Choose the microphone and speakers by name, filtered to the short list your OS shows — and measured, so every entry actually works |
| 🔗 Session Continuity | A dropped connection, a voice change or a device change no longer wipes the conversation |
| 🧩 Plugin System | Drop a single `.py` file into `plugins/` — JARVIS learns a new skill on next launch |
| 📺 Video on the HUD | Plays YouTube, a local file or any video URL **where the avatar sits** — starts muted, sound on request |
| 🪜 Model Ladder | Nine Gemini models in one measured order — a quota, a timeout or an outage steps to the next rung instead of failing |
| 🎙️ Real-time Voice | Ultra-low latency conversation in any language via Gemini Live API |
| 🎨 Live Theming | Recolour the entire HUD from a hue wheel or hex — the avatar retints with it |
| 〰️ Reactive HUD | Waveform pulses to real audio — your mic while listening, JARVIS while speaking |
| 🎙️ Voice Picker | Choose from 5 native Gemini voices and switch live from the UI — no restart |
| ♾️ Unlimited Sessions | Sliding-window context compression — one conversation can last for hours |
| 🖥️ System Control | Launch apps, adjust volume/brightness, WiFi, shortcuts, power — all by voice |
| 🧩 Autonomous Tasks | High-level planning for complex multi-step goals via agent mode |
| 👁️ Visual Awareness | Screen capture and webcam vision piped into your main Gemini session, labelled by source |
| 🧠 Persistent Memory | Deeply remembers projects, preferences, and personal context across sessions |
| ⌨️ Hybrid Input | Seamlessly switch between keyboard typing and voice commands |
| 🌅 Morning Briefing | On first boot: greets you, reads the time, recaps yesterday, and fetches live news |
| 🔔 Proactive 2.0 | Time-aware, context-aware check-ins — knows the time of day, your projects, and what you've been discussing |
| 🔍 Deep Research | Multi-wave sourced reports with citations — compares options, verifies facts, delivers bottom-line-first answers |
| ⚡ Per-tool scheduling | Slow tools (web search, deep research, file processor, browser, messaging) run NON_BLOCKING with WHEN_IDLE delivery — results arrive in speech gaps, never cutting you off |
| 🖱️ Computer Use | Set-of-Mark visual grounding — capture screen, detect numbered elements, click/type by element ID |
| 💓 Heartbeat Autonomy | Observe/suggest/act levels with HEARTBEAT_OK silence and never-nag-twice — proactive suggestions that respect your quiet time |
| 🗓️ Session Memory | Summarises each conversation and mentions it naturally next morning — consumed after use, never repeats |
| 👁️‍🗨️ Background Monitoring | User-configured topic watching — checks for new headlines once a day and alerts naturally |
| 📊 Hardware Monitoring | Continuous CPU, RAM, GPU and temperature telemetry with localized voice alerts |
| 🌤️ Weather Report | Live weather data for your city, personalized from memory |
| 🗺️ Dynamic Content Panel | Scrollable display layer beneath the HUD that renders web results, news, and search data |
| 🔍 Multi-Mode Web Search | `news` / `research` / `price` / `compare` / `search` — Gemini Grounded first, DDG fallback |
| ⏰ Smart Reminders | OS-native scheduled notifications (Windows Task Scheduler / macOS LaunchAgent / Linux systemd) |
| 📂 File Processor | Read, summarize, and answer questions about local files |
| 🌐 Browser Control | Open URLs, navigate tabs, and interact with the browser by voice |
| 📨 Send Message | Compose and send messages through WhatsApp, Telegram, and more |
| 🖱️ Desktop Control | Taskbar, window management, and desktop-level operations |
| 🧑‍💻 Silent Language Memory | Detects spoken language on first use — all future sessions adapt automatically |
| 📱 Remote Dashboard | Control the assistant from your phone via QR code pairing |
| ⚡ Auto-Start on Boot | Registers with the OS startup system (registry / LaunchAgent / .desktop) |
| 📋 Clipboard Intelligence | Copy any text → floating panel with Translate / Summarise / Explain / Fix |
| 🪪 Assistant Customization | Change the assistant name, your name, voice, and colour from the UI — takes effect immediately |

## ⚡ Quick Start

```bash
git clone https://github.com/mafk21/OS.git
cd OS
python setup.py        # installs deps for YOUR OS + the browser automation engine
python main.py
```

`setup.py` only ever installs what your operating system needs — the Windows-only libraries are skipped automatically on macOS and Linux, and vice-versa. It also checks your Python version up front, so a wrong interpreter fails with a sentence instead of a wall of pip output. Prefer to do it by hand? `pip install -r requirements.txt` works too.

> ⚠️ **Installation Note:** If you hit a `ModuleNotFoundError` for an OS-specific package, install it with `pip install <module_name>`. The optional **wake word** engine is *not* installed here — grab it in one click from **⚙ → WAKE WORD** inside the app.

---

## 📋 Requirements

| Requirement | Details |
| --- | --- |
| **OS** | Windows 10/11, macOS, or Linux |
| **Python** | 3.11 – 3.15 |
| **Microphone** | Required for voice interaction (and for the "Hey Jarvis" wake word) |
| **Speakers** | Required for voice replies |
| **API Key** | Free Gemini API key (entered on first launch → `config/api_keys.json`) |
| **GPU** | **Not required.** The avatar is rendered in software, and so is HUD video |
| **YouTube on the HUD** | `yt-dlp`, installed by `setup.py`. Without it, local files and direct URLs still play and YouTube links open in the browser with an explanation |
| **Wake word** *(optional)* | One-click download from ⚙ → WAKE WORD (`openwakeword`, a few MB, fully local) |

---

## 🗂️ Project Structure

```
Mark LV/
├── main.py                   # Core loop — Gemini Live session, audio I/O, viseme extraction, tool dispatch
├── ui.py                     # PyQt6 HUD — avatar canvas, waveform, log panel, settings drawer, camera feed
├── setup.py                  # OS-aware installer (skips wrong-OS dependencies, checks your Python)
├── .gitignore                # Keeps your API key, TLS key and memories out of the repository
├── plugins/
│   └── _template.py          # Copy this to write a new skill — one file, drop in, done
├── actions/                  # Bundled skills — each self-describes via a TOOL dict + handler
│                             #   Everything here drives the COMPUTER, which is what decides
│                             #   whether a new skill belongs in this folder at all.
│   ├── web_search.py         # Gemini + DDG parallel search (news, research, price, compare)
│   ├── deep_research.py      # Phase 5: multi-wave sourced research reports with citations
│   ├── screen_processor.py   # Screen & webcam capture for vision
│   ├── background_monitor.py # User-configured topic watching — daily DDG check
│   ├── proactive.py          # Proactive 2.0 — time/context/rotation-aware check-ins
│   ├── reminder.py           # OS-native scheduled notifications
│   ├── system_monitor.py     # CPU / RAM / GPU / temperature telemetry
│   ├── computer_settings.py  # Volume, brightness, WiFi, power (per-OS)
│   ├── computer_control.py   # Keyboard shortcuts, mouse, window management
│   ├── computer_use.py       # Phase 8: Set-of-Mark visual agent — element IDs + click/type
│   ├── open_app.py           # Application launcher (per-OS name map)
│   ├── browser_control.py    # Web browser control
│   ├── file_controller.py    # File system operations
│   ├── file_processor.py     # Document reading and summarization
│   ├── send_message.py       # Messaging integration
│   ├── weather_report.py     # Live weather data
│   ├── video_player.py       # Plays video on the HUD, where the avatar normally is
│   └── desktop.py            # Desktop and taskbar control
├── memory/
│   ├── memory_manager.py     # Load/save long_term.json — sessions, monitors, identity
│   ├── config_manager.py     # api_keys.json access — key, OS, name, voice, colour, toggles
│   └── long_term.json        # Persistent store — created on first run
├── core/
│   ├── gemini.py             # One place for every one-shot Gemini call — model ladder, timeouts, cooldowns
│   ├── prompt.txt            # All prompt wording — {tokens} are filled from the live system at startup
│   ├── avatar.py             # Avatar renderer — lighting, pose, expression, mouth (QPainter)
│   ├── avatar_mesh.py        # Head geometry — loads the face, generates skull/neck/rigs
│   ├── face_model.obj        # The face itself (MediaPipe canonical model, Apache-2.0, 25 KB)
│   ├── viseme.py             # Transcript → mouth shapes, fused with the audio's timing
│   ├── echo.py               # Tells your voice from the assistant's own echo; self-calibrating
│   ├── hotkey.py             # Push-to-talk chord — global on Windows, windowed fallback elsewhere
│   ├── undo.py               # One shared undo stack — actions register how to reverse themselves
│   ├── confirm.py            # Irreversible-action gate — the token is issued by the UI, not the model
│   ├── audio_devices.py      # Microphone / speaker list — filtered, measured, resolved by name
│   ├── plugin_loader.py      # Plugin engine — discovery, validation, crash isolation
│   ├── action_loader.py      # Bundled-action engine — the built-in twin of plugin_loader
│   ├── wake_word.py          # Local "Hey Jarvis" detector — own thread, offline, opt-in
│   ├── heartbeat.py          # Phase 4: observe/suggest/act levels, HEARTBEAT_OK silence, never-nag-twice
│   └── screen_memory.py      # Phase 7: event-driven screen capture, OCR, FTS5 search
└── config/
    ├── api_keys.json         # API key, name, voice, colour, toggles — created on first launch (git-ignored)
    └── certs/                # Self-signed TLS pair for the phone dashboard — generated locally (git-ignored)
```

---

## ⚡️ Per-Tool Scheduling

Slow, network-backed tools (`web_search`, `deep_research`, `file_processor`,
`browser_control`, `send_message`) declare `behavior: NON_BLOCKING` +
`scheduling: WHEN_IDLE`. The model is never held up waiting for them —
results are delivered in a natural gap in speech instead of cutting in.
Fast tools (memory, system status, skills) keep the default blocking behavior.
