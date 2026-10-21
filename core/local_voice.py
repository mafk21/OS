"""
Local voice loop — Phase 2.3

Graceful degrade: if whisper/faster-whisper/piper/edge-tts aren't installed,
every method returns a clear status and the cloud path stays primary.

Responsibilities
  - VAD: energy gate + optional Silero (if onnxruntime present)
  - STT: faster-whisper → whisper → offline stub
  - TTS: edge-tts → pyttsx3 → offline stub
  - Flow/Dictate hotkey helpers

The UI and main.py never import heavy deps directly — they call these helpers
which soft-fail with _AVAILABLE flags.
"""

from __future__ import annotations
import threading
import time
from pathlib import Path

_AVAILABLE = {
    "vad": False,
    "stt": False,
    "tts": False,
}

_VAD_THRESHOLD = 0.015  # rms energy gate fallback

# ── capability probe (no heavy imports at import time) ──────────────────

def probe_capabilities() -> dict:
    """Detect what's actually installed. Cheap, never raises."""
    caps = {"vad": False, "stt": False, "tts": False, "details": {}}
    # STT: faster-whisper or openai-whisper
    for mod in ("faster_whisper", "whisper"):
        try:
            __import__(mod)
            caps["stt"] = True
            caps["details"]["stt_backend"] = mod
            break
        except Exception:
            continue
    # TTS: edge_tts or pyttsx3
    for mod in ("edge_tts", "pyttsx3"):
        try:
            __import__(mod)
            caps["tts"] = True
            caps["details"]["tts_backend"] = mod
            break
        except Exception:
            continue
    # VAD: silero via onnxruntime or simple energy gate (always)
    try:
        import onnxruntime  # noqa: F401
        caps["vad"] = True
        caps["details"]["vad_backend"] = "silero"
    except Exception:
        caps["vad"] = False
        caps["details"]["vad_backend"] = "energy_gate"
    return caps


def local_voice_available() -> bool:
    c = probe_capabilities()
    return bool(c["stt"] or c["tts"])


# ── STT ───────────────────────────────────────────────────────────────────

_STT_MODEL = None
_STT_LOCK = threading.Lock()

def transcribe_file(wav_path: str | Path, language: str = "auto") -> str:
    """
    Transcribe a wav file offline. Returns text or raises with actionable message.
    Never imported by main loop unless local_stt_enabled is True.
    """
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"wav not found: {wav_path}")

    # Try faster-whisper first (best accuracy/speed on CPU)
    try:
        from faster_whisper import WhisperModel
        global _STT_MODEL
        with _STT_LOCK:
            if _STT_MODEL is None:
                _STT_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = _STT_MODEL.transcribe(str(wav_path), language=None if language == "auto" else language)
            return "".join(s.text for s in segments).strip()
    except ImportError:
        pass
    except Exception as e:
        raise RuntimeError(f"faster-whisper failed: {e}")

    # Fallback: openai whisper
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(str(wav_path), language=None if language == "auto" else language)
        return str(result.get("text", "")).strip()
    except ImportError:
        raise RuntimeError("No local STT installed. Install one:  pip install faster-whisper  OR  pip install openai-whisper")
    except Exception as e:
        raise RuntimeError(f"whisper failed: {e}")


def transcribe_pcm(pcm_bytes: bytes, sample_rate: int = 16000) -> str:
    """Transcribe raw 16-bit PCM (from sounddevice). Writes temp wav then calls transcribe_file."""
    import tempfile, wave, struct
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        with wave.open(tf.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        return transcribe_file(tf.name)


# ── TTS ───────────────────────────────────────────────────────────────────

_TTS_LOCK = threading.Lock()

def speak_text(text: str, voice: str = "", rate: int = 0) -> bool:
    """
    Speak text offline via best available engine. Returns True if audio was produced.
    Non-blocking friendly: caller should thread this.
    """
    text = (text or "").strip()
    if not text:
        return False

    # edge-tts (needs network for first fetch but caches; sounds best)
    try:
        import asyncio, edge_tts, tempfile, os, subprocess, platform
        async def _edge():
            tfile = tempfile.mktemp(suffix=".mp3")
            comm = edge_tts.Communicate(text, voice or "en-US-JennyNeural")
            await comm.save(tfile)
            return tfile

        mp3 = asyncio.run(_edge())
        # play
        if platform.system() == "Windows":
            os.startfile(mp3)  # type: ignore
        elif platform.system() == "Darwin":
            subprocess.Popen(["afplay", mp3])
        else:
            # try mpg123 / ffplay / aplay
            for cmd in (["mpg123", "-q", mp3], ["ffplay", "-nodisp", "-autoexit", mp3], ["aplay", mp3]):
                try:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
                except Exception:
                    continue
        return True
    except Exception:
        pass

    # pyttsx3 (fully offline, robotic but always works)
    try:
        import pyttsx3
        with _TTS_LOCK:
            engine = pyttsx3.init()
            if rate:
                engine.setProperty("rate", int(rate))
            if voice:
                # best-effort voice match
                for v in engine.getProperty("voices"):
                    if voice.lower() in v.name.lower() or voice.lower() in v.id.lower():
                        engine.setProperty("voice", v.id)
                        break
            engine.say(text)
            engine.runAndWait()
        return True
    except Exception:
        pass

    return False


# ── VAD ───────────────────────────────────────────────────────────────────

def is_speech_energy(pcm_bytes: bytes, threshold: float = _VAD_THRESHOLD) -> bool:
    """Cheap energy gate: rms of int16 PCM > threshold."""
    import struct, math
    if not pcm_bytes or len(pcm_bytes) < 4:
        return False
    # unpack as int16
    n = len(pcm_bytes) // 2
    fmt = f"<{n}h"
    try:
        samples = struct.unpack(fmt, pcm_bytes[: n * 2])
    except Exception:
        return False
    # rms normalized to 0..1
    sq = sum(s * s for s in samples) / max(1, len(samples))
    rms = math.sqrt(sq) / 32768.0
    return rms > threshold


# ── Dictation helpers ─────────────────────────────────────────────────────

def type_text(text: str) -> bool:
    """Type text into the currently focused window (cross-platform best-effort)."""
    try:
        import pyautogui
        pyautogui.write(text, interval=0.01)
        return True
    except Exception:
        pass
    # pynput fallback
    try:
        from pynput.keyboard import Controller
        Controller().type(text)
        return True
    except Exception:
        return False


# ── Flow recorder (push-to-flow) ─────────────────────────────────────────

class FlowRecorder:
    """
    Accumulates short utterances into a buffer; user double-taps Ctrl to flush.
    Main.py owns one instance when Flow hotkey is enabled.
    """
    def __init__(self, on_flush=None):
        self._buf: list[str] = []
        self._lock = threading.Lock()
        self._on_flush = on_flush
        self._last_tap = 0.0
        self._tap_window = 0.6  # seconds for double-tap

    def push_transcript(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        with self._lock:
            self._buf.append(text)

    def handle_flow_tap(self) -> str | None:
        """Call on every Ctrl press. Returns flushed text on double-tap, else None."""
        now = time.monotonic()
        if now - self._last_tap <= self._tap_window:
            # double-tap -> flush
            with self._lock:
                out = " ".join(self._buf).strip()
                self._buf.clear()
            self._last_tap = 0.0
            if out and self._on_flush:
                try:
                    self._on_flush(out)
                except Exception:
                    pass
            return out
        self._last_tap = now
        return None

    def clear(self):
        with self._lock:
            self._buf.clear()
