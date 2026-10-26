# Pinned full Brag runtime

Node.js >=22. From repository root: `npm --prefix tools/brag-runtime ci`.
The JARVIS `brag_video setup` action runs this only after actual HUD approval.
Lockfile pins Hyperframes 0.8.205 and FFprobe installer 2.1.2 (plus transitives).
Do not vendor node_modules, browsers, render outputs or model weights.

`brag_video doctor` checks runtime version, installed programs and optional Kokoro
readiness. It is dependency preflight, not proof Chrome launches or the provider
creates a good film. Generation runs the real browser checks and render gates.
Install Chrome/Edge/Chromium separately. Existing imageio-ffmpeg supplies FFmpeg.
Windows also needs a working Python `python` command for upstream Kokoro if used.

Optional executable/runtime overrides:

- JARVIS_BRAG_RUNTIME: directory containing node_modules/hyperframes and FFprobe.
- HYPERFRAMES_BROWSER_PATH: installed Chrome/Chromium/Edge executable.
- HYPERFRAMES_FFMPEG_PATH, HYPERFRAMES_FFPROBE_PATH: actual installed executables.
- HYPERFRAMES_PREVIEW_HOST: upstream studio bind override; default desktop-only.
  Do not expose an unauthenticated editable studio to the public internet.

Telemetry and automatic agent-skill installation are disabled for controller calls.
The configured JARVIS provider directs JSON planning, composition and visual
critique; no Claude CLI or separate account is invoked. Full tests use fixture
provider responses to avoid charges; passing them is not a live model audition.

Voice is off by default. Explicitly install `kokoro-onnx soundfile` in the Python
environment used by the runtime, then run the pinned CLI's `tts` command yourself
to authorize its model/voice download (~311 MB + ~27 MB). Both cache files must
exist before voice generation is allowed. No automatic package/model installation
occurs in generate. Missing voice setup fails, never substitutes cloud speech.

Tests (repo virtualenv and prerequisites installed):

```
.venv/bin/python -m pytest tests/test_brag_full.py tests/test_brag_video.py -q
JARVIS_TEST_HYPERFRAMES=1 .venv/bin/python -m pytest tests/test_brag_full.py -q
```

The opt-in test runs actual multi-scene Hyperframes check/snapshot/render using
licensed music, FFprobe duration/dimension/audio checks, settled poster frame0
replacement and whole-file decode. It does not contact a live provider or install
Kokoro weights. Public website capture requires outbound access to the requested
site; environment network restrictions still apply.
