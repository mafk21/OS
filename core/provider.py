"""
Multi-provider ladder — Phase 2.

Unifies Gemini, local Ollama/LM Studio, and OpenAI-compatible APIs behind the
same `call()` / `text()` / `as_json()` surface that core/gemini.py already exposes,
so every existing call site keeps working whether we add 2 providers or 10.

Design
------
* Gemini stays the primary — it's already measured, cached, and quota-cooled.
* Local (Ollama / LM Studio) is the offline fallback — zero API key, zero quota.
* OpenAI-compatible (OpenAI, Groq, Together, xAI, DeepSeek when they speak
  OpenAI) is an optional second cloud rung — one `openai_api_key` covers them
  all because they share the same /v1/chat/completions shape.

New config keys (all optional, backward-compatible):
  provider              "gemini" | "auto" | "openai" | "local"  (default auto)
  offline_fallback      bool  (default True) — use local LLM when Gemini is down
  openai_api_key        str   — enables the OpenAI-compatible rung
  openai_base_url       str   — overrides base (default api.openai.com)
  openai_model          str   — model for that provider (default gpt-4o-mini)
"""

from __future__ import annotations
import json
import time
from typing import Any

# Re-export the constants callers already import from gemini.py so they don't
# have to change imports. This file is additive, not a replacement.
try:
    from core.gemini import FAST, SMART, SEARCH, LIVE  # type: ignore
    from core.gemini import (  # noqa: F401
        DEFAULT_TIMEOUT_MS, LIVE_MODELS, LIVE_SLOTS,
        is_quota_error, is_unavailable_error, is_gone_error,
        live_model, note_live_failure, api_key, _cooling,
    )
except Exception:
    FAST = "fast"
    SMART = "smart"
    SEARCH = "search"
    LIVE = "live"
    DEFAULT_TIMEOUT_MS = 10_000


def get_provider() -> str:
    """Preferred cloud provider. 'auto' tries Gemini first, then OpenAI if configured."""
    try:
        import memory.config_manager as cm  # local import to avoid cycle
        return str(cm.load_api_keys().get("provider", "auto")).strip().lower() or "auto"
    except Exception:
        return "auto"


def get_offline_fallback_enabled() -> bool:
    try:
        import memory.config_manager as cm
        v = cm.load_api_keys().get("offline_fallback", True)
        return bool(v)
    except Exception:
        return True


def get_openai_cfg() -> dict:
    """Returns {api_key, base_url, model} for the OpenAI-compatible rung."""
    try:
        import memory.config_manager as cm
        cfg = cm.load_api_keys()
        return {
            "api_key":  str(cfg.get("openai_api_key", "") or "").strip(),
            "base_url": str(cfg.get("openai_base_url", "https://api.openai.com/v1") or "https://api.openai.com/v1").rstrip("/"),
            "model":    str(cfg.get("openai_model", "gpt-4o-mini") or "gpt-4o-mini").strip(),
        }
    except Exception:
        return {"api_key": "", "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"}


def get_anthropic_cfg() -> dict:
    try:
        import memory.config_manager as cm
        return cm.get_anthropic_cfg()
    except Exception:
        return {"api_key": "", "model": "claude-sonnet-4-5"}


def _openai_available() -> bool:
    return bool(get_openai_cfg().get("api_key"))


def _anthropic_available() -> bool:
    return bool(get_anthropic_cfg().get("api_key"))


def _local_available() -> bool:
    # local is always *attemptable* — llm_client will report if the server is down
    return get_offline_fallback_enabled()


# ── OpenAI-compatible one-shot ───────────────────────────────────────────

def _openai_call(contents, tier: str, config, timeout_ms: int, key: str = ""):
    """Try the OpenAI multimodal/JSON/search endpoint via core.openai_compat."""
    from core.openai_compat import openai_generate_content
    resp = openai_generate_content(
        contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key
    )
    if resp is None or not getattr(resp, "text", ""):
        raise RuntimeError("openai provider returned empty reply")
    return resp


def _anthropic_call(contents, tier: str, config, timeout_ms: int):
    """Call Anthropic's native Messages API for text reasoning."""
    import httpx

    cfg = get_anthropic_cfg()
    api_key = str(cfg.get("api_key") or "").strip()
    if not api_key:
        raise RuntimeError("anthropic API key is not configured")

    system_text = ""
    if config:
        if isinstance(config, dict):
            system_text = str(config.get("system_instruction") or "")
        else:
            system_text = str(getattr(config, "system_instruction", "") or "")
    items = contents if isinstance(contents, (list, tuple)) else [contents]
    user_parts: list[str] = []
    for item in items:
        if isinstance(item, str):
            user_parts.append(item)
        else:
            text_value = getattr(item, "text", None)
            if text_value:
                user_parts.append(str(text_value))
    payload: dict[str, Any] = {
        "model": str(cfg.get("model") or "claude-sonnet-4-5"),
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": "\n".join(user_parts).strip() or "hi"}],
    }
    if system_text:
        payload["system"] = system_text
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=max(1.0, timeout_ms / 1000),
    )
    response.raise_for_status()
    data = response.json()
    text_value = "".join(
        str(block.get("text") or "")
        for block in data.get("content", [])
        if isinstance(block, dict) and block.get("type") == "text"
    ).strip()
    if not text_value:
        raise RuntimeError("anthropic provider returned empty reply")

    class _R:
        def __init__(self, text: str):
            self.text = text
    return _R(text_value)


def _local_call(contents, tier: str, config, timeout_ms: int):
    """Try the local LLM via core/llm_client. Returns response-like or raises."""
    from core.llm_client import call_llm
    # Build messages
    msgs: list[dict] = []
    if config:
        sys_txt = None
        if isinstance(config, dict):
            sys_txt = config.get("system_instruction")
        else:
            sys_txt = getattr(config, "system_instruction", None)
        if sys_txt:
            msgs.append({"role": "system", "content": str(sys_txt)})
    items = contents if isinstance(contents, (list, tuple)) else [contents]
    user_text = ""
    for it in items:
        if isinstance(it, str):
            user_text += it + "\n"
        else:
            t = getattr(it, "text", None)
            if t:
                user_text += str(t) + "\n"
    user_text = user_text.strip() or "hi"
    msgs.append({"role": "user", "content": user_text})

    data = call_llm(msgs, timeout=int(timeout_ms / 1000) or 60)
    text = (data.get("content") or "").strip()
    if not text:
        raise RuntimeError("local LLM returned empty reply")

    class _R:
        def __init__(self, t): self.text = t
    return _R(text)


# ── Public API — mirrors core/gemini.call/text/as_json ──────────────────
_LAST_ROUTE={}
def last_route()->dict:
    return dict(_LAST_ROUTE)

def call(contents, tier: str = FAST, config=None, timeout_ms: int = DEFAULT_TIMEOUT_MS, key: str = "", request_policy=None):
    """Route a model request with explicit capability/privacy policy and safe fallback."""
    from core.provider_routing import ProviderRequest, note_result, route
    if isinstance(request_policy, ProviderRequest):
        request = request_policy
    else:
        try:
            from core.provider_preferences import get as get_routing_preferences
            routing_cfg = get_routing_preferences()
            request = ProviderRequest(
                cost_priority=routing_cfg["cost_priority"],
                latency_priority=routing_cfg["latency_priority"],
            )
        except Exception:
            request = ProviderRequest()
    preference = get_provider()
    available = {"gemini"}
    if _anthropic_available(): available.add("anthropic")
    if _openai_available(): available.add("openai")
    if _local_available(): available.add("local")
    # A pinned provider remains strict and is attempted even when configuration
    # is incomplete, preserving a useful provider-specific failure.
    pinned = "local" if preference in {"local", "ollama", "lmstudio"} else preference
    if pinned != "auto": available.add(pinned)
    candidates = route(preference, request, available)
    route_started = time.monotonic()
    for route_index, provider in enumerate(candidates):
        try:
            if provider == "gemini":
                from core.gemini import call as gemini_call
                response = gemini_call(contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key)
            elif provider == "anthropic":
                response = _anthropic_call(contents, tier, config, timeout_ms)
            elif provider == "openai":
                response = _openai_call(contents, tier, config, timeout_ms, key)
            else:
                response = _local_call(contents, tier, config, timeout_ms)
            if response is not None and getattr(response, "text", ""):
                note_result(provider, True)
                # Response metadata is deliberately non-secret and lets every UI
                # explain which brain answered and whether fallback occurred.
                try:
                    response.provider = provider
                    response.route_latency_ms = round((time.monotonic() - route_started) * 1000)
                    response.fallback_used = route_index > 0
                    response.data_class = request.data_class
                    _LAST_ROUTE.clear(); _LAST_ROUTE.update({'provider':provider,'model':str(tier),'latency_ms':response.route_latency_ms,'fallback_used':response.fallback_used,'data_class':request.data_class,'timestamp':time.time()})
                except Exception:
                    pass
                return response
            raise RuntimeError("provider returned an empty reply")
        except Exception:
            note_result(provider, False)
            # Provider configuration and exception text can be credential-tainted.
            # Keep the runtime notice deliberately constant and non-sensitive.
            print("[Provider] configured rung failed safely")
    return None


def text(contents, tier: str = FAST, config=None, timeout_ms: int = DEFAULT_TIMEOUT_MS, key: str = "", default: str = "") -> str:
    resp = call(contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key)
    if resp is None:
        return default
    return (getattr(resp, "text", None) or "").strip() or default


def as_json(contents, tier: str = FAST, config=None, timeout_ms: int = DEFAULT_TIMEOUT_MS, key: str = "", default=None):
    raw = text(contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key)
    if not raw:
        return default
    if "{" in raw and "}" in raw:
        raw = raw[raw.find("{"): raw.rfind("}") + 1]
    elif "[" in raw and "]" in raw:
        raw = raw[raw.find("["): raw.rfind("]") + 1]
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"[Provider] reply was not JSON: {e}")
        return default
