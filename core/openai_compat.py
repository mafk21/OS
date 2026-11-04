"""
core/openai_compat.py — Universal OpenAI Multimodal, Search, Image, STT & TTS Adapter.

Makes an OpenAI API key (`sk-...`) 100% drop-in compatible with every JARVIS
subsystem that calls `core.gemini` (`call`, `text`, `as_json`), vision/screen
grounding (`PIL.Image`, `types.Part`, `inline_data`), grounded web search,
image generation, and speech I/O across both Male and Female editions.
"""

from __future__ import annotations

import base64
import io
import json
import struct
import threading
import time
import wave
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from memory import config_manager as cfg

# ── Persona-Aware Voice Mapping (Gemini <-> OpenAI Realtime & TTS) ───────────

OPENAI_REALTIME_VOICES = (
    "ash",
    "alloy",
    "ballad",
    "coral",
    "echo",
    "sage",
    "shimmer",
    "verse",
)
OPENAI_TTS_VOICES = (
    "ash",
    "alloy",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
)

_GEMINI_TO_OPENAI_VOICE = {
    # Male voices
    "charon": "ash",
    "fenrir": "echo",
    "puck": "verse",
    "orus": "ash",
    # Female voices
    "aoede": "shimmer",
    "kore": "coral",
    "leda": "sage",
    "zephyr": "coral",
}


def map_voice_to_openai(voice: str = "", persona: str = "", *, realtime: bool = True) -> str:
    """Map any JARVIS / Gemini voice name or Male/Female persona to a valid OpenAI voice."""
    raw = (voice or cfg.get_voice() or "").strip().lower()
    allowed = OPENAI_REALTIME_VOICES if realtime else OPENAI_TTS_VOICES
    if raw in allowed:
        return raw
    mapped = _GEMINI_TO_OPENAI_VOICE.get(raw)
    if mapped and mapped in allowed:
        return mapped
    p = (persona or cfg.get_persona() or "male").strip().lower()
    if p == "female":
        return "shimmer" if "shimmer" in allowed else "coral"
    return "ash" if "ash" in allowed else ("onyx" if "onyx" in allowed else "echo")


# ── Response Shim Compatible with Both `.text` and `.candidates[0].content.parts` ──


class _CompatPart:
    __slots__ = ("text", "thought", "inline_data")

    def __init__(self, text: str):
        self.text = text
        self.thought = False
        self.inline_data = None


class _CompatContent:
    __slots__ = ("parts", "role")

    def __init__(self, text: str):
        self.parts = [_CompatPart(text)]
        self.role = "model"


class _CompatCandidate:
    __slots__ = ("content", "grounding_metadata")

    def __init__(self, text: str):
        self.content = _CompatContent(text)
        self.grounding_metadata = None


class CompatResponse:
    """Matches google-genai GenerateContentResponse surface used across all actions."""

    __slots__ = ("text", "candidates")

    def __init__(self, text: str):
        self.text = text
        self.candidates = [_CompatCandidate(text)]


# ── Cooldown Tracking ────────────────────────────────────────────────────────

_cool_lock = threading.Lock()
_cooldowns: dict[str, float] = {}


def _is_cooling(model: str) -> bool:
    with _cool_lock:
        exp = _cooldowns.get(model, 0.0)
        if exp and time.monotonic() < exp:
            return True
        _cooldowns.pop(model, None)
        return False


def _cool_model(model: str, seconds: float = 180.0) -> None:
    with _cool_lock:
        _cooldowns[model] = time.monotonic() + seconds


# ── Multimodal Content & Config Normalization ────────────────────────────────


def _detect_image_mime(raw: bytes) -> str | None:
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith(b"RIFF") and b"WEBP" in raw[:16]:
        return "image/webp"
    if raw.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    return None


def _item_to_content_blocks(item: Any) -> list[dict[str, Any]]:
    if item is None:
        return []
    if isinstance(item, str):
        return [{"type": "text", "text": item}] if item else []

    if isinstance(item, (bytes, bytearray)):
        b = bytes(item)
        mime = _detect_image_mime(b)
        if mime:
            b64 = base64.b64encode(b).decode("ascii")
            return [{"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]
        return [{"type": "text", "text": b.decode("utf-8", errors="replace")}]

    # PIL.Image.Image support (computer_use, computer_control, screen_processor, file_processor)
    if hasattr(item, "save") and hasattr(item, "size") and hasattr(item, "mode"):
        try:
            buf = io.BytesIO()
            img = item
            if getattr(img, "mode", "") not in ("RGB", "RGBA", "L"):
                img = img.convert("RGB")
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]
        except Exception:
            pass

    # google.genai.types.Part or duck-typed Part
    blob = getattr(item, "inline_data", None)
    if blob is not None:
        data = getattr(blob, "data", None)
        mime = str(getattr(blob, "mime_type", None) or "image/png").lower()
        if isinstance(data, (bytes, bytearray)):
            b64 = base64.b64encode(bytes(data)).decode("ascii")
        else:
            b64 = str(data or "")
        if mime.startswith("image/"):
            return [{"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]
        try:
            raw_txt = base64.b64decode(b64).decode("utf-8", errors="replace")
            return [{"type": "text", "text": raw_txt[:24000]}]
        except Exception:
            return []

    txt_attr = getattr(item, "text", None)
    if isinstance(txt_attr, str) and txt_attr:
        return [{"type": "text", "text": txt_attr}]

    if isinstance(item, dict):
        if "inline_data" in item and isinstance(item["inline_data"], dict):
            inl = item["inline_data"]
            mime = str(inl.get("mime_type") or "image/png").lower()
            d = inl.get("data")
            b64 = (
                base64.b64encode(bytes(d)).decode("ascii")
                if isinstance(d, (bytes, bytearray))
                else str(d or "")
            )
            if mime.startswith("image/"):
                return [{"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]
        if "text" in item and item["text"]:
            return [{"type": "text", "text": str(item["text"])}]
        if "parts" in item and isinstance(item["parts"], (list, tuple)):
            out: list[dict[str, Any]] = []
            for p in item["parts"]:
                out.extend(_item_to_content_blocks(p))
            return out

    if isinstance(item, (list, tuple)):
        out = []
        for sub in item:
            out.extend(_item_to_content_blocks(sub))
        return out

    return [{"type": "text", "text": str(item)}]


def _extract_config_options(config: Any) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "system": "",
        "json_mode": False,
        "google_search": False,
        "temperature": None,
        "max_tokens": None,
    }
    if config is None:
        return opts

    def _get(k: str) -> Any:
        if isinstance(config, dict):
            return config.get(k)
        return getattr(config, k, None)

    sys_inst = _get("system_instruction")
    if isinstance(sys_inst, str):
        opts["system"] = sys_inst.strip()
    elif sys_inst is not None:
        blocks = _item_to_content_blocks(sys_inst)
        opts["system"] = "\n".join(b["text"] for b in blocks if b.get("type") == "text").strip()

    mime = str(_get("response_mime_type") or "").lower()
    if "json" in mime:
        opts["json_mode"] = True

    temp = _get("temperature")
    if isinstance(temp, (int, float)):
        opts["temperature"] = float(temp)

    max_tok = _get("max_output_tokens")
    if isinstance(max_tok, int) and max_tok > 0:
        opts["max_tokens"] = int(max_tok)

    tools = _get("tools")
    if isinstance(tools, (list, tuple)):
        for t in tools:
            if isinstance(t, dict) and ("google_search" in t or "googleSearch" in t):
                opts["google_search"] = True
            elif getattr(t, "google_search", None) is not None:
                opts["google_search"] = True
    return opts


def _build_model_ladder(tier: str, configured_model: str, has_images: bool) -> list[str]:
    base_m = (configured_model or "gpt-4o").strip()
    t = (tier or "fast").strip().lower()
    if t == "smart" or has_images:
        candidates = ["gpt-4o", base_m, "gpt-4o-mini"]
    elif t in ("fast", "live", "search"):
        candidates = [base_m, "gpt-4o-mini", "gpt-4o"]
    elif t.startswith(("gpt-", "o1", "o3", "o4")):
        candidates = [tier, base_m, "gpt-4o", "gpt-4o-mini"]
    else:
        candidates = [base_m, "gpt-4o", "gpt-4o-mini"]

    ordered: list[str] = []
    for m in candidates:
        if m and m not in ordered:
            ordered.append(m)
    active = [m for m in ordered if not _is_cooling(m)]
    return active or ordered


def _augment_with_ddg_if_search(query_text: str) -> str:
    """Fetch live web results via DuckDuckGo so OpenAI answers grounded search accurately."""
    try:
        from actions.web_search import _ddg_search
        hits = _ddg_search(query_text[:280], max_results=6)
        if not hits:
            return query_text
        ctx_lines = ["[LIVE WEB SEARCH RESULTS]"]
        for i, h in enumerate(hits, 1):
            ctx_lines.append(
                f"{i}. {h.get('title', '')}\n   URL: {h.get('url', '')}\n   Snippet: {h.get('snippet', '')}"
            )
        ctx_lines.append(
            "\nUsing the live web results above, answer the user's query accurately and concisely:"
        )
        ctx_lines.append(query_text)
        return "\n".join(ctx_lines)
    except Exception:
        return query_text


def openai_generate_content(
    contents: Any,
    tier: str = "fast",
    config: Any = None,
    timeout_ms: int = 15_000,
    key: str = "",
) -> CompatResponse | None:
    """Drop-in OpenAI equivalent of `core.gemini.call(...)` supporting text,
    multimodal images (`PIL.Image`, `Part`, bytes), JSON mode, and grounded search."""
    oc = cfg.get_openai_cfg()
    api_key = (key or oc.get("api_key") or "").strip()
    if not api_key:
        return None
    base_url = (oc.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    configured_model = oc.get("model") or "gpt-4o"

    opts = _extract_config_options(config)
    blocks = _item_to_content_blocks(contents)
    if not blocks:
        blocks = [{"type": "text", "text": "Hello"}]

    has_images = any(b.get("type") == "image_url" for b in blocks)
    is_search = opts["google_search"] or str(tier).lower() == "search"

    # Extract plain text if there are no images (broadest compatibility across OpenAI endpoints)
    plain_text = "\n".join(b["text"] for b in blocks if b.get("type") == "text").strip()
    timeout_s = max(12.0, float(timeout_ms) / 1000.0 + 4.0)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 1. If grounded search requested, try OpenAI native web-search model first, then DDG-grounded chat
    if is_search and not has_images and (urlparse(base_url).hostname or "").lower() == "api.openai.com":
        for smodel in ("gpt-4o-search-preview", "gpt-4o-mini-search-preview"):
            if _is_cooling(smodel):
                continue
            try:
                s_msgs: list[dict[str, Any]] = []
                if opts["system"]:
                    s_msgs.append({"role": "system", "content": opts["system"]})
                s_msgs.append({"role": "user", "content": plain_text or "latest news"})
                with httpx.Client(timeout=timeout_s) as client:
                    r = client.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json={"model": smodel, "messages": s_msgs},
                    )
                if r.status_code == 200:
                    msg_obj = (r.json().get("choices") or [{}])[0].get("message") or {}
                    txt = str(msg_obj.get("content") or "").strip()
                    if txt:
                        return CompatResponse(txt)
                elif r.status_code in (403, 404, 400):
                    _cool_model(smodel, 3600.0)
                elif r.status_code == 429:
                    _cool_model(smodel, 300.0)
            except Exception:
                pass
        # Ground with live DuckDuckGo snippets for standard chat models
        grounded_text = _augment_with_ddg_if_search(plain_text)
        blocks = [{"type": "text", "text": grounded_text}]
        plain_text = grounded_text

    messages: list[dict[str, Any]] = []
    sys_prompt = opts["system"]
    if opts["json_mode"] and "json" not in sys_prompt.lower() and "json" not in plain_text.lower():
        sys_prompt = (sys_prompt + "\nRespond strictly with valid JSON.").strip()
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})

    if has_images:
        messages.append({"role": "user", "content": blocks})
    else:
        messages.append({"role": "user", "content": plain_text or "Hello"})

    ladder = _build_model_ladder(tier, configured_model, has_images)
    max_tok = opts["max_tokens"] or (2048 if str(tier).lower() == "smart" else 1024)

    for model in ladder:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tok,
        }
        if opts["temperature"] is not None:
            payload["temperature"] = opts["temperature"]
        if opts["json_mode"]:
            payload["response_format"] = {"type": "json_object"}

        try:
            with httpx.Client(timeout=timeout_s) as client:
                resp = client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            if resp.status_code == 400 and "max_tokens" in resp.text:
                payload.pop("max_tokens", None)
                payload["max_completion_tokens"] = max_tok
                with httpx.Client(timeout=timeout_s) as client:
                    resp = client.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
            if resp.status_code == 429:
                _cool_model(model, 180.0)
                print("[OpenAI] Model rate-limited (429) — trying next rung")
                continue
            if resp.status_code in (403, 404):
                _cool_model(model, 1800.0)
                print("[OpenAI] Model unavailable — trying next rung")
                continue
            resp.raise_for_status()
            data = resp.json()
            choice = (data.get("choices") or [{}])[0]
            txt = str((choice.get("message") or {}).get("content") or "").strip()
            if txt:
                return CompatResponse(txt)
        except Exception as exc:
            print(f"[OpenAI] request failed ({type(exc).__name__}); trying next model")
            continue

    return None


# ── OpenAI Image Generation (`dall-e-3` / `gpt-image-1`) ─────────────────────


def openai_generate_image(prompt: str, out_dir: Path | None = None) -> tuple[Path | None, str]:
    oc = cfg.get_openai_cfg()
    api_key = (oc.get("api_key") or "").strip()
    if not api_key:
        return None, "No openai_api_key configured."
    base_url = (oc.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    target_dir = out_dir or Path("memory")
    target_dir.mkdir(parents=True, exist_ok=True)

    for model in ("dall-e-3", "dall-e-2"):
        try:
            payload: dict[str, Any] = {
                "model": model,
                "prompt": prompt[:3800],
                "n": 1,
                "size": "1024x1024",
                "response_format": "b64_json",
            }
            with httpx.Client(timeout=60.0) as client:
                r = client.post(f"{base_url}/images/generations", headers=headers, json=payload)
            if r.status_code in (403, 404):
                continue
            r.raise_for_status()
            item = ((r.json().get("data") or [{}])[0]) or {}
            b64 = item.get("b64_json")
            if b64:
                out = target_dir / f"generated_{int(time.time())}.png"
                out.write_bytes(base64.b64decode(b64))
                return out, ""
            url = item.get("url")
            if url:
                with httpx.Client(timeout=30.0) as client:
                    img_r = client.get(url)
                    img_r.raise_for_status()
                    out = target_dir / f"generated_{int(time.time())}.png"
                    out.write_bytes(img_r.content)
                    return out, ""
        except Exception as exc:
            last_err = str(exc)
            continue
    return None, locals().get("last_err", "OpenAI image generation unavailable.")


# ── OpenAI Audio STT (`whisper-1`) & 24kHz PCM TTS (`tts-1`) ─────────────────


def pcm16_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def openai_transcribe_pcm16(
    pcm_bytes: bytes,
    sample_rate: int = 16000,
    language: str = "",
) -> str:
    oc = cfg.get_openai_cfg()
    api_key = (oc.get("api_key") or "").strip()
    if not api_key or not pcm_bytes:
        return ""
    base_url = (oc.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    wav_data = pcm16_to_wav_bytes(pcm_bytes, sample_rate=sample_rate)
    headers = {"Authorization": f"Bearer {api_key}"}

    for stt_model in ("gpt-4o-mini-transcribe", "whisper-1"):
        try:
            data_fields: dict[str, str] = {"model": stt_model}
            if language and len(language) == 2:
                data_fields["language"] = language.lower()
            with httpx.Client(timeout=20.0) as client:
                r = client.post(
                    f"{base_url}/audio/transcriptions",
                    headers=headers,
                    data=data_fields,
                    files={"file": ("speech.wav", wav_data, "audio/wav")},
                )
            if r.status_code in (400, 403, 404) and stt_model != "whisper-1":
                continue
            r.raise_for_status()
            return str(r.json().get("text") or "").strip()
        except Exception:
            continue
    return ""


def openai_tts_pcm24k(text: str, voice: str = "", persona: str = "") -> bytes:
    """Synthesize speech via OpenAI `/v1/audio/speech` returning 24 kHz 16-bit mono PCM."""
    clean = (text or "").strip()
    if not clean:
        return b""
    oc = cfg.get_openai_cfg()
    api_key = (oc.get("api_key") or "").strip()
    if not api_key:
        return b""
    base_url = (oc.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    oai_voice = map_voice_to_openai(voice, persona, realtime=False)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    for tts_model in ("gpt-4o-mini-tts", "tts-1"):
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(
                    f"{base_url}/audio/speech",
                    headers=headers,
                    json={
                        "model": tts_model,
                        "input": clean[:4000],
                        "voice": oai_voice,
                        "response_format": "pcm",
                    },
                )
            if r.status_code in (400, 403, 404) and tts_model != "tts-1":
                continue
            r.raise_for_status()
            raw = r.content
            # Ensure even byte count for int16 PCM
            if len(raw) % 2 == 1:
                raw = raw[:-1]
            return raw
        except Exception:
            continue
    return b""


# ── Tool Schema Conversion (JARVIS Gemini Uppercase -> OpenAI JSON Schema) ───


def _schema_to_json_schema(sch: Any) -> dict[str, Any]:
    if not isinstance(sch, dict):
        return {"type": "object", "properties": {}}
    out: dict[str, Any] = {}
    raw_t = str(sch.get("type") or "object").strip().lower()
    if raw_t not in ("object", "string", "integer", "number", "boolean", "array"):
        raw_t = "string"
    out["type"] = raw_t
    if "description" in sch and sch["description"]:
        out["description"] = str(sch["description"])
    if "enum" in sch and isinstance(sch["enum"], list):
        out["enum"] = list(sch["enum"])

    if raw_t == "object":
        raw_props = sch.get("properties")
        props = {
            str(k): _schema_to_json_schema(v)
            for k, v in (raw_props.items() if isinstance(raw_props, dict) else ())
        }
        out["properties"] = props
        req = sch.get("required")
        if isinstance(req, list):
            valid_req = [r for r in req if r in props]
            if valid_req:
                out["required"] = valid_req
    elif raw_t == "array":
        out["items"] = _schema_to_json_schema(
            sch.get("items") if isinstance(sch.get("items"), dict) else {"type": "string"}
        )
    return out


def jarvis_decls_to_openai_realtime_tools(decls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert JARVIS tool declarations into OpenAI Realtime `session.update` tools."""
    tools: list[dict[str, Any]] = []
    for d in decls or ():
        if not isinstance(d, dict) or not d.get("name"):
            continue
        tools.append(
            {
                "type": "function",
                "name": str(d["name"]),
                "description": str(d.get("description") or "")[:1024],
                "parameters": _schema_to_json_schema(
                    d.get("parameters") or {"type": "OBJECT", "properties": {}}
                ),
            }
        )
    return tools


def jarvis_decls_to_openai_chat_tools(decls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert JARVIS tool declarations into OpenAI `/v1/chat/completions` tools."""
    tools: list[dict[str, Any]] = []
    for d in decls or ():
        if not isinstance(d, dict) or not d.get("name"):
            continue
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": str(d["name"]),
                    "description": str(d.get("description") or "")[:1024],
                    "parameters": _schema_to_json_schema(
                        d.get("parameters") or {"type": "OBJECT", "properties": {}}
                    ),
                },
            }
        )
    return tools
