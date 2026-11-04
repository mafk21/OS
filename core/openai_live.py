"""
core/openai_live.py — Full-Duplex OpenAI Live Session Engine for JARVIS.

Implements the exact async session contract expected by `JarvisLive` in `main.py`
(`send_realtime_input`, `send_client_content`, `send_tool_response`, `receive`,
`cancel_response`), providing:

1. **Tier 1 — `OpenAIRealtimeSession` (`wss://api.openai.com/v1/realtime`)**:
   Native speech-to-speech WebSocket with 16kHz->24kHz mic upsampling, 24kHz PCM
   playback, server VAD + instant barge-in (`response.cancel`), live input/output
   transcriptions (50Hz lip-sync visemes + Forever Timeline), vision (`screen_process`
   & webcam), Male/Female voices, and all 60 JARVIS tools.

2. **Tier 2 — `OpenAIRestLiveSession` (Automatic Universal Fallback)**:
   Activates transparently if an OpenAI key lacks Realtime WebSocket model access
   or uses a custom OpenAI-compatible `base_url`. Combines local utterance VAD +
   `/v1/audio/transcriptions` + `/v1/chat/completions` (all 60 tools + vision) +
   `/v1/audio/speech` (24kHz PCM16) behind the identical session interface.
"""

from __future__ import annotations

import asyncio
import base64
from collections import deque
from contextlib import asynccontextmanager
import json
import time
from typing import Any
from urllib.parse import urlparse

import httpx
import numpy as np

from core.openai_compat import (
    jarvis_decls_to_openai_chat_tools,
    jarvis_decls_to_openai_realtime_tools,
    map_voice_to_openai,
    openai_generate_content,
    openai_transcribe_pcm16,
    openai_tts_pcm24k,
)
from memory import config_manager as cfg

OPENAI_REALTIME_MODELS = (
    "gpt-4o-realtime-preview",
    "gpt-4o-mini-realtime-preview",
)


# ── Event Shims Matching `google.genai` LiveServerMessage ───────────────────


class _LiveText:
    __slots__ = ("text",)

    def __init__(self, text: str):
        self.text = text


class _LivePart:
    __slots__ = ("text", "thought")

    def __init__(self, text: str):
        self.text = text
        self.thought = False


class _LiveModelTurn:
    __slots__ = ("parts",)

    def __init__(self, text: str):
        self.parts = [_LivePart(text)] if text else []


class _LiveServerContent:
    __slots__ = (
        "interrupted",
        "model_turn",
        "output_transcription",
        "input_transcription",
        "turn_complete",
    )

    def __init__(
        self,
        *,
        interrupted: bool = False,
        model_text: str = "",
        output_text: str = "",
        input_text: str = "",
        turn_complete: bool = False,
    ):
        self.interrupted = interrupted
        self.model_turn = _LiveModelTurn(model_text) if model_text else None
        self.output_transcription = _LiveText(output_text) if output_text else None
        self.input_transcription = _LiveText(input_text) if input_text else None
        self.turn_complete = turn_complete


class _LiveFuncCall:
    __slots__ = ("id", "name", "args")

    def __init__(self, call_id: str, name: str, args: dict[str, Any]):
        self.id = call_id
        self.name = name
        self.args = args


class _LiveToolCall:
    __slots__ = ("function_calls",)

    def __init__(self, function_calls: list[_LiveFuncCall]):
        self.function_calls = function_calls


class LiveCompatEvent:
    """Exact duck-type of `google.genai` LiveServerMessage consumed by `main.py`."""

    __slots__ = (
        "data",
        "server_content",
        "tool_call",
        "session_resumption_update",
        "go_away",
    )

    def __init__(
        self,
        *,
        data: bytes | None = None,
        server_content: _LiveServerContent | None = None,
        tool_call: _LiveToolCall | None = None,
    ):
        self.data = data
        self.server_content = server_content
        self.tool_call = tool_call
        self.session_resumption_update = None
        self.go_away = None


# ── Fast Vectorized 16 kHz -> 24 kHz PCM16 Upsampler ────────────────────────


def upsample_pcm16_16k_to_24k(pcm16_16k: bytes) -> bytes:
    """Convert 16 kHz 16-bit mono signed PCM to 24 kHz 16-bit mono signed PCM."""
    if not pcm16_16k:
        return b""
    if len(pcm16_16k) % 2 == 1:
        pcm16_16k = pcm16_16k[:-1]
    src = np.frombuffer(pcm16_16k, dtype=np.int16)
    n_in = src.shape[0]
    if n_in == 0:
        return b""
    n_out = int(round(n_in * 1.5))
    x_old = np.linspace(0.0, 1.0, num=n_in, endpoint=False)
    x_new = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
    dst = np.interp(x_new, x_old, src.astype(np.float32))
    return np.clip(dst, -32768, 32767).astype(np.int16).tobytes()


# ── Extract System Prompt & Tool Declarations from LiveConnectConfig ────────


def extract_live_instructions_and_tools(
    live_config: Any,
    fallback_decls: list[dict[str, Any]] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    sys_prompt = "You are JARVIS, a fast, capable, concise desktop AI assistant."
    decls: list[dict[str, Any]] = []

    if live_config is not None:
        si = getattr(live_config, "system_instruction", None)
        if isinstance(si, str) and si.strip():
            sys_prompt = si.strip()
        elif si is not None:
            parts = getattr(si, "parts", None) or (si.get("parts") if isinstance(si, dict) else None)
            if parts:
                txts = []
                for p in parts:
                    t = getattr(p, "text", None) or (p.get("text") if isinstance(p, dict) else None)
                    if t:
                        txts.append(str(t))
                if txts:
                    sys_prompt = "\n".join(txts).strip()

        raw_tools = getattr(live_config, "tools", None) or (
            live_config.get("tools") if isinstance(live_config, dict) else None
        )
        if raw_tools:
            for t in raw_tools:
                fds = getattr(t, "function_declarations", None) or (
                    t.get("function_declarations") if isinstance(t, dict) else None
                )
                if fds:
                    for fd in fds:
                        if isinstance(fd, dict):
                            decls.append(fd)
                        elif hasattr(fd, "model_dump"):
                            decls.append(fd.model_dump(exclude_none=True))

    if not decls and fallback_decls:
        decls = list(fallback_decls)
    return sys_prompt, decls


def _extract_turns_parts(turns: Any) -> list[dict[str, Any]]:
    """Normalize `send_client_content(turns=...)` into a flat list of part dicts."""
    if isinstance(turns, str):
        return [{"text": turns}]
    if isinstance(turns, dict):
        raw_parts = turns.get("parts") or []
        out = []
        for p in raw_parts:
            if isinstance(p, str):
                out.append({"text": p})
            elif isinstance(p, dict):
                out.append(p)
            elif getattr(p, "text", None):
                out.append({"text": str(p.text)})
        return out
    if isinstance(turns, (list, tuple)):
        out = []
        for t in turns:
            out.extend(_extract_turns_parts(t))
        return out
    return [{"text": str(turns)}]


# ── Tier 1: Native OpenAI Realtime WebSocket Session ────────────────────────


class OpenAIRealtimeSession:
    """Full-duplex WebSocket adapter for `wss://api.openai.com/v1/realtime`."""

    engine = "openai-realtime"

    def __init__(
        self,
        ws: Any,
        *,
        model: str,
        instructions: str,
        tool_decls: list[dict[str, Any]],
        voice: str = "",
        persona: str = "",
    ):
        self._ws = ws
        self.model = model
        self._instructions = instructions
        self._realtime_tools = jarvis_decls_to_openai_realtime_tools(tool_decls)
        self._voice = map_voice_to_openai(voice, persona, realtime=True)
        self._events: asyncio.Queue[LiveCompatEvent | BaseException | None] = asyncio.Queue()
        self._send_lock = asyncio.Lock()
        self._reader_task: asyncio.Task | None = None
        self._response_active = False
        self._pending_resp_task: asyncio.Task | None = None
        self._closed = False

    async def start(self) -> None:
        session_cfg = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self._instructions,
                "voice": self._voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.55,
                    "prefix_padding_ms": 280,
                    "silence_duration_ms": 520,
                    "create_response": True,
                },
                "tools": self._realtime_tools,
                "tool_choice": "auto",
            },
        }
        await self._ws_send(session_cfg)
        self._reader_task = asyncio.create_task(self._ws_reader_loop())

    async def close(self) -> None:
        self._closed = True
        if self._pending_resp_task and not self._pending_resp_task.done():
            self._pending_resp_task.cancel()
        if self._reader_task and not self._reader_task.done():
            self._reader_task.cancel()
        try:
            await self._ws.close()
        except Exception:
            pass

    async def _ws_send(self, payload: dict[str, Any]) -> None:
        if self._closed:
            raise ConnectionError("OpenAI Realtime WebSocket is closed")
        raw = json.dumps(payload)
        async with self._send_lock:
            await self._ws.send(raw)

    async def send_realtime_input(self, audio: Any = None, **_kwargs: Any) -> None:
        if audio is None:
            return
        pcm16k = getattr(audio, "data", None)
        if pcm16k is None and isinstance(audio, dict):
            pcm16k = audio.get("data")
        if not pcm16k:
            return
        pcm24k = upsample_pcm16_16k_to_24k(bytes(pcm16k))
        if not pcm24k:
            return
        await self._ws_send(
            {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(pcm24k).decode("ascii"),
            }
        )

    async def send_client_content(self, turns: Any = None, turn_complete: bool = True) -> None:
        if self._pending_resp_task and not self._pending_resp_task.done():
            self._pending_resp_task.cancel()

        parts = _extract_turns_parts(turns)
        text_chunks: list[str] = []
        image_parts: list[tuple[str, bytes]] = []

        for p in parts:
            if "inline_data" in p and isinstance(p["inline_data"], dict):
                inl = p["inline_data"]
                mime = str(inl.get("mime_type") or "image/jpeg")
                d = inl.get("data")
                raw_b = (
                    bytes(d)
                    if isinstance(d, (bytes, bytearray))
                    else base64.b64decode(str(d or ""))
                )
                image_parts.append((mime, raw_b))
            elif p.get("text"):
                text_chunks.append(str(p["text"]))

        prompt_text = "\n".join(text_chunks).strip()

        # Vision grounding via gpt-4o ensures every OpenAI Realtime model
        # (including preview models that only accept text/audio items) sees
        # exact screen/webcam details accurately!
        if image_parts:
            loop = asyncio.get_running_loop()
            v_contents: list[Any] = [
                {"inline_data": {"mime_type": m, "data": b}} for m, b in image_parts
            ]
            v_contents.append(
                "Describe everything relevant in this image accurately and concisely so it can be answered aloud:\n"
                + (prompt_text or "What is visible here?")
            )
            v_resp = await loop.run_in_executor(
                None,
                lambda: openai_generate_content(v_contents, tier="smart", timeout_ms=22_000),
            )
            visual_notes = getattr(v_resp, "text", "") if v_resp else ""
            if visual_notes:
                prompt_text = (
                    f"{prompt_text}\n\n[VISUAL ANALYSIS OF CAPTURED IMAGE]:\n{visual_notes}\n\n"
                    "Speak directly and naturally to the user answering their request based on what you see."
                ).strip()

        if prompt_text:
            await self._ws_send(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt_text}],
                    },
                }
            )
        if turn_complete:
            await self._ws_send({"type": "response.create"})

    async def send_tool_response(self, function_responses: list[Any]) -> None:
        for fr in function_responses or ():
            call_id = str(getattr(fr, "id", "") or "")
            resp_obj = getattr(fr, "response", None) or {"result": "Done."}
            out_str = (
                resp_obj if isinstance(resp_obj, str) else json.dumps(resp_obj, ensure_ascii=False)
            )
            await self._ws_send(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": out_str[:28000],
                    },
                }
            )

        # Coalesce with `_flush_pending_vision()` if `screen_process` is about to
        # inject an image + `response.create` 5ms later.
        async def _deferred_create() -> None:
            await asyncio.sleep(0.03)
            if not self._closed:
                await self._ws_send({"type": "response.create"})

        if self._pending_resp_task and not self._pending_resp_task.done():
            self._pending_resp_task.cancel()
        self._pending_resp_task = asyncio.create_task(_deferred_create())

    async def cancel_response(self) -> None:
        if self._closed:
            return
        try:
            if self._response_active:
                await self._ws_send({"type": "response.cancel"})
                self._response_active = False
        except Exception:
            pass

    async def _ws_reader_loop(self) -> None:
        try:
            async for raw in self._ws:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", errors="replace")
                try:
                    ev = json.loads(raw)
                except Exception:
                    continue
                etype = str(ev.get("type") or "")

                if etype == "response.created":
                    self._response_active = True

                elif etype in ("response.audio.delta", "response.output_audio.delta"):
                    b64 = ev.get("delta") or ""
                    if b64:
                        pcm_bytes = base64.b64decode(b64)
                        await self._events.put(LiveCompatEvent(data=pcm_bytes))

                elif etype in (
                    "response.audio_transcript.delta",
                    "response.output_audio_transcript.delta",
                ):
                    delta = str(ev.get("delta") or "")
                    if delta:
                        await self._events.put(
                            LiveCompatEvent(
                                server_content=_LiveServerContent(output_text=delta)
                            )
                        )

                elif etype in ("response.text.delta", "response.output_text.delta"):
                    delta = str(ev.get("delta") or "")
                    if delta:
                        await self._events.put(
                            LiveCompatEvent(
                                server_content=_LiveServerContent(model_text=delta)
                            )
                        )

                elif etype == "conversation.item.input_audio_transcription.completed":
                    transcript = str(ev.get("transcript") or "").strip()
                    if transcript:
                        await self._events.put(
                            LiveCompatEvent(
                                server_content=_LiveServerContent(input_text=transcript)
                            )
                        )

                elif etype == "input_audio_buffer.speech_started":
                    if self._response_active:
                        self._response_active = False
                        await self._events.put(
                            LiveCompatEvent(
                                server_content=_LiveServerContent(interrupted=True)
                            )
                        )

                elif etype == "response.done":
                    self._response_active = False
                    resp_obj = ev.get("response") or {}
                    output_items = resp_obj.get("output") or []
                    fn_calls: list[_LiveFuncCall] = []
                    for item in output_items:
                        if isinstance(item, dict) and item.get("type") == "function_call":
                            cid = str(item.get("call_id") or item.get("id") or "")
                            fname = str(item.get("name") or "")
                            raw_args = item.get("arguments") or "{}"
                            try:
                                parsed_args = (
                                    json.loads(raw_args)
                                    if isinstance(raw_args, str)
                                    else dict(raw_args)
                                )
                            except Exception:
                                parsed_args = {}
                            if fname:
                                fn_calls.append(_LiveFuncCall(cid, fname, parsed_args))

                    if fn_calls:
                        await self._events.put(
                            LiveCompatEvent(tool_call=_LiveToolCall(fn_calls))
                        )
                    else:
                        status = str(resp_obj.get("status") or "completed")
                        if status != "cancelled":
                            await self._events.put(
                                LiveCompatEvent(
                                    server_content=_LiveServerContent(turn_complete=True)
                                )
                            )

                elif etype == "error":
                    err_info = ev.get("error") or {}
                    code = str(err_info.get("code") or "")
                    msg = str(err_info.get("message") or err_info)
                    # Benign race when response.cancel arrives just after completion
                    if "cancel" in msg.lower() or code == "response_cancel_not_active":
                        continue
                    print(f"[OpenAI Realtime] Server notice ({code}): {msg}")
                    if any(
                        bad in msg.lower()
                        for bad in ("invalid api key", "incorrect api key", "unauthorized")
                    ):
                        await self._events.put(
                            RuntimeError(f"Invalid API key: {msg}")
                        )
                        return

            if not self._closed:
                await self._events.put(
                    ConnectionError("OpenAI Realtime WebSocket closed by server")
                )
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            if not self._closed:
                await self._events.put(exc)

    async def receive(self):
        while not self._closed:
            item = await self._events.get()
            if item is None:
                return
            if isinstance(item, BaseException):
                raise item
            yield item


# ── Tier 2: Universal OpenAI REST Live Session (STT + Chat+60 Tools + TTS) ──


class OpenAIRestLiveSession:
    """Universal full-duplex fallback using OpenAI Whisper STT + Chat Completions
    (with all 60 tools & vision) + OpenAI 24kHz PCM TTS. Works on EVERY OpenAI key
    tier and OpenAI-compatible endpoint."""

    engine = "openai-rest-live"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        instructions: str,
        tool_decls: list[dict[str, Any]],
        voice: str = "",
        persona: str = "",
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self.model = model or "gpt-4o"
        self._instructions = instructions
        self._chat_tools = jarvis_decls_to_openai_chat_tools(tool_decls)
        self._voice = voice
        self._persona = persona

        self._history: list[dict[str, Any]] = [
            {"role": "system", "content": self._instructions}
        ]
        self._events: asyncio.Queue[LiveCompatEvent | BaseException | None] = asyncio.Queue()
        self._tool_waiters: dict[str, asyncio.Future[str]] = {}
        self._active_turn_task: asyncio.Task | None = None
        self._closed = False

        # Utterance VAD state (16 kHz mono int16)
        self._preroll: deque[bytes] = deque(maxlen=5)
        self._speech_buf = bytearray()
        self._in_utterance = False
        self._silence_frames = 0
        self._speech_frames = 0

    async def start(self) -> None:
        return None

    async def close(self) -> None:
        self._closed = True
        await self.cancel_response()
        await self._events.put(None)

    async def cancel_response(self) -> None:
        if self._active_turn_task and not self._active_turn_task.done():
            self._active_turn_task.cancel()
        for fut in list(self._tool_waiters.values()):
            if not fut.done():
                fut.cancel()
        self._tool_waiters.clear()

    async def send_realtime_input(self, audio: Any = None, **_kwargs: Any) -> None:
        if self._closed or audio is None:
            return
        pcm = getattr(audio, "data", None)
        if pcm is None and isinstance(audio, dict):
            pcm = audio.get("data")
        if not pcm:
            return
        raw = bytes(pcm)
        arr = np.frombuffer(raw[: len(raw) - (len(raw) % 2)], dtype=np.int16)
        if arr.size == 0:
            return
        rms = float(np.sqrt(np.mean((arr.astype(np.float32) / 32768.0) ** 2)))

        if not self._in_utterance:
            self._preroll.append(raw)
            if rms >= 0.018:
                self._speech_frames += 1
                if self._speech_frames >= 2:
                    self._in_utterance = True
                    self._silence_frames = 0
                    self._speech_buf.clear()
                    for pr in self._preroll:
                        self._speech_buf.extend(pr)
            else:
                self._speech_frames = 0
        else:
            self._speech_buf.extend(raw)
            if rms < 0.012:
                self._silence_frames += 1
            else:
                self._silence_frames = 0

            # ~640ms silence (10 * 64ms) or 18s ceiling commits utterance
            if self._silence_frames >= 10 or len(self._speech_buf) >= 16000 * 2 * 18:
                utterance_bytes = bytes(self._speech_buf)
                self._speech_buf.clear()
                self._in_utterance = False
                self._silence_frames = 0
                self._speech_frames = 0
                asyncio.create_task(self._handle_spoken_utterance(utterance_bytes))

    async def _handle_spoken_utterance(self, pcm16k: bytes) -> None:
        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(
            None, lambda: openai_transcribe_pcm16(pcm16k, sample_rate=16000)
        )
        if not transcript or len(transcript.strip()) < 2:
            return
        await self._events.put(
            LiveCompatEvent(
                server_content=_LiveServerContent(input_text=transcript.strip())
            )
        )
        await self._start_chat_turn([{"type": "text", "text": transcript.strip()}])

    async def send_client_content(self, turns: Any = None, turn_complete: bool = True) -> None:
        parts = _extract_turns_parts(turns)
        content_blocks: list[dict[str, Any]] = []
        for p in parts:
            if "inline_data" in p and isinstance(p["inline_data"], dict):
                inl = p["inline_data"]
                mime = str(inl.get("mime_type") or "image/jpeg")
                d = inl.get("data")
                b64 = (
                    base64.b64encode(bytes(d)).decode("ascii")
                    if isinstance(d, (bytes, bytearray))
                    else str(d or "")
                )
                content_blocks.append(
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                )
            elif p.get("text"):
                content_blocks.append({"type": "text", "text": str(p["text"])})

        if not content_blocks:
            return
        if turn_complete:
            await self._start_chat_turn(content_blocks)
        else:
            self._history.append({"role": "user", "content": content_blocks})

    async def send_tool_response(self, function_responses: list[Any]) -> None:
        for fr in function_responses or ():
            cid = str(getattr(fr, "id", "") or "")
            resp_obj = getattr(fr, "response", None) or {"result": "Done."}
            out_str = (
                resp_obj if isinstance(resp_obj, str) else json.dumps(resp_obj, ensure_ascii=False)
            )
            fut = self._tool_waiters.get(cid)
            if fut and not fut.done():
                fut.set_result(out_str[:28000])

    async def _start_chat_turn(self, content_blocks: list[dict[str, Any]]) -> None:
        await self.cancel_response()
        self._active_turn_task = asyncio.create_task(self._run_chat_turn(content_blocks))

    async def _run_chat_turn(self, content_blocks: list[dict[str, Any]]) -> None:
        try:
            has_img = any(b.get("type") == "image_url" for b in content_blocks)
            if has_img:
                self._history.append({"role": "user", "content": content_blocks})
            else:
                txt = "\n".join(b["text"] for b in content_blocks if b.get("type") == "text")
                self._history.append({"role": "user", "content": txt})

            # Keep rolling history bounded
            if len(self._history) > 36:
                self._history = [self._history[0]] + self._history[-30:]

            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }

            for _step in range(8):
                payload: dict[str, Any] = {
                    "model": self.model,
                    "messages": self._history,
                }
                if self._chat_tools:
                    payload["tools"] = self._chat_tools
                    payload["tool_choice"] = "auto"

                async with httpx.AsyncClient(timeout=45.0) as client:
                    r = await client.post(
                        f"{self._base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                if r.status_code in (401, 403) and "api key" in r.text.lower():
                    await self._events.put(RuntimeError(f"Invalid API key: {r.text[:160]}"))
                    return
                r.raise_for_status()
                msg = ((r.json().get("choices") or [{}])[0]).get("message") or {}
                tool_calls = msg.get("tool_calls") or []

                if tool_calls:
                    self._history.append(msg)
                    live_fcs: list[_LiveFuncCall] = []
                    loop = asyncio.get_running_loop()
                    wait_futs: list[tuple[str, asyncio.Future[str]]] = []
                    for tc in tool_calls:
                        cid = str(tc.get("id") or f"call_{int(time.time()*1000)}")
                        fn = tc.get("function") or {}
                        fname = str(fn.get("name") or "")
                        raw_args = fn.get("arguments") or "{}"
                        try:
                            p_args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
                        except Exception:
                            p_args = {}
                        fut: asyncio.Future[str] = loop.create_future()
                        self._tool_waiters[cid] = fut
                        wait_futs.append((cid, fut))
                        live_fcs.append(_LiveFuncCall(cid, fname, p_args))

                    await self._events.put(LiveCompatEvent(tool_call=_LiveToolCall(live_fcs)))

                    for cid, fut in wait_futs:
                        res_str = await asyncio.wait_for(fut, timeout=120.0)
                        self._tool_waiters.pop(cid, None)
                        self._history.append(
                            {
                                "role": "tool",
                                "tool_call_id": cid,
                                "content": res_str,
                            }
                        )
                    continue

                reply_text = str(msg.get("content") or "").strip()
                if reply_text:
                    self._history.append({"role": "assistant", "content": reply_text})
                    await self._events.put(
                        LiveCompatEvent(
                            server_content=_LiveServerContent(output_text=reply_text)
                        )
                    )
                    loop = asyncio.get_running_loop()
                    pcm24k = await loop.run_in_executor(
                        None,
                        lambda: openai_tts_pcm24k(
                            reply_text, voice=self._voice, persona=self._persona
                        ),
                    )
                    if pcm24k:
                        await self._events.put(LiveCompatEvent(data=pcm24k))

                await self._events.put(
                    LiveCompatEvent(server_content=_LiveServerContent(turn_complete=True))
                )
                return

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            print(f"[OpenAI REST Live] Turn error: {exc}")
            await self._events.put(
                LiveCompatEvent(server_content=_LiveServerContent(turn_complete=True))
            )

    async def receive(self):
        while not self._closed:
            item = await self._events.get()
            if item is None:
                return
            if isinstance(item, BaseException):
                raise item
            yield item


# ── Unified Async Context Manager Matching `client.aio.live.connect(...)` ───


@asynccontextmanager
async def connect_openai_live(
    *,
    api_key: str,
    live_config: Any,
    fallback_decls: list[dict[str, Any]] | None = None,
    voice: str = "",
    persona: str = "",
):
    """Open an OpenAI full-duplex Live session (Realtime WebSocket first, with
    automatic zero-config fallback to REST STT+Chat+TTS if Realtime WS isn't
    enabled on the key or endpoint)."""
    oc = cfg.get_openai_cfg()
    resolved_key = (api_key or oc.get("api_key") or "").strip()
    if not resolved_key:
        raise RuntimeError("Invalid API key: no openai_api_key configured")

    base_url = (oc.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    rt_pref = (oc.get("realtime_model") or "gpt-4o-realtime-preview").strip()
    chat_model = (oc.get("model") or "gpt-4o").strip()
    instructions, decls = extract_live_instructions_and_tools(live_config, fallback_decls)

    session_obj: OpenAIRealtimeSession | OpenAIRestLiveSession | None = None

    # Attempt Tier 1: Native OpenAI Realtime WebSocket when pointing at OpenAI (or wss-capable host)
    if (urlparse(base_url).hostname or "").lower() == "api.openai.com":
        try:
            import websockets

            rt_candidates: list[str] = []
            for m in (rt_pref, *OPENAI_REALTIME_MODELS):
                if m and m not in rt_candidates:
                    rt_candidates.append(m)

            ws_base = base_url.replace("https://", "wss://").replace("http://", "ws://")
            extra_hdrs = {
                "Authorization": f"Bearer {resolved_key}",
                "OpenAI-Beta": "realtime=v1",
            }

            for rt_model in rt_candidates:
                ws_url = f"{ws_base}/realtime?model={rt_model}"
                try:
                    # `additional_headers` in websockets >=14, `extra_headers` in <=13
                    try:
                        ws = await asyncio.wait_for(
                            websockets.connect(
                                ws_url,
                                additional_headers=extra_hdrs,
                                max_size=16 * 1024 * 1024,
                                ping_interval=20,
                                ping_timeout=20,
                            ),
                            timeout=12.0,
                        )
                    except TypeError:
                        ws = await asyncio.wait_for(
                            websockets.connect(
                                ws_url,
                                extra_headers=extra_hdrs,
                                max_size=16 * 1024 * 1024,
                                ping_interval=20,
                                ping_timeout=20,
                            ),
                            timeout=12.0,
                        )

                    rt_sess = OpenAIRealtimeSession(
                        ws,
                        model=rt_model,
                        instructions=instructions,
                        tool_decls=decls,
                        voice=voice,
                        persona=persona,
                    )
                    await rt_sess.start()
                    session_obj = rt_sess
                    print("[OpenAI Live] ⚡ Connected via Realtime WebSocket")
                    break
                except Exception as ws_exc:
                    emsg = str(ws_exc).lower()
                    if "401" in emsg or "invalid api key" in emsg or "incorrect api key" in emsg:
                        raise RuntimeError("Invalid API key") from ws_exc
                    print(
                        f"[OpenAI Live] Realtime model unavailable ({type(ws_exc).__name__}) — trying next..."
                    )
                    continue
        except RuntimeError:
            raise
        except Exception as outer_exc:
            print(f"[OpenAI Live] Realtime WebSocket unavailable ({type(outer_exc).__name__}) — falling back to REST Live")

    # Tier 2: Universal OpenAI REST Live Session
    if session_obj is None:
        rest_sess = OpenAIRestLiveSession(
            api_key=resolved_key,
            base_url=base_url,
            model=chat_model,
            instructions=instructions,
            tool_decls=decls,
            voice=voice,
            persona=persona,
        )
        await rest_sess.start()
        session_obj = rest_sess
        print("[OpenAI Live] 🌐 Connected via Universal REST Live")

    try:
        yield session_obj
    finally:
        await session_obj.close()
