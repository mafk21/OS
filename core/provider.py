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


def _openai_available() -> bool:
    return bool(get_openai_cfg().get("api_key"))


def _local_available() -> bool:
    # local is always *attemptable* — llm_client will report if the server is down
    return get_offline_fallback_enabled()


# ── OpenAI-compatible one-shot ───────────────────────────────────────────

def _openai_call(contents, tier: str, config, timeout_ms: int, key: str = ""):
    """Try the OpenAI-compatible endpoint. Returns response-like or raises."""
    import requests
    oc = get_openai_cfg()
    api_key = key or oc["api_key"]
    if not api_key:
        raise RuntimeError("no openai_api_key configured")
    base = oc["base_url"]
    model = oc["model"]

    # contents -> messages (strip SDK Part wrapper)
    msgs: list[dict] = []
    if config:
        sys_txt = None
        if isinstance(config, dict):
            sys_txt = config.get("system_instruction")
        else:
            sys_txt = getattr(config, "system_instruction", None)
        if sys_txt:
            msgs.append({"role": "system", "content": str(sys_txt)})
    # contents can be str, list[str], or SDK Part objects
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

    payload = {
        "model": model,
        "messages": msgs,
        "max_tokens": 800,
    }
    # best-effort: if tier is SMART give more tokens
    if tier == SMART:
        payload["max_tokens"] = 1200

    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=max(10, timeout_ms / 1000 + 5),
    )
    resp.raise_for_status()
    data = resp.json()
    choice = (data.get("choices") or [{}])[0]
    text = (choice.get("message", {}).get("content") or "").strip()

    class _R:
        def __init__(self, t): self.text = t
    if not text:
        raise RuntimeError("openai provider returned empty reply")
    return _R(text)


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

def call(contents, tier: str = FAST, config=None, timeout_ms: int = DEFAULT_TIMEOUT_MS, key: str = ""):
    """
    Multi-provider `call()`. Tries in order:
      1. Explicit provider pin (provider == "openai" | "local" -> only that rung)
      2. Auto: Gemini ladder (includes Live one-shot) -> OpenAI rung if key exists -> local LLM if enabled
    Returns a response-like with `.text` or None if every rung failed.
    """
    provider = get_provider()

    # Pinned provider — honour it directly
    if provider == "openai":
        try:
            return _openai_call(contents, tier, config, timeout_ms, key)
        except Exception as e:
            print(f"[Provider] openai pinned failed: {e}")
            return None
    if provider in ("local", "ollama", "lmstudio"):
        try:
            return _local_call(contents, tier, config, timeout_ms)
        except Exception as e:
            print(f"[Provider] local pinned failed: {e}")
            return None
    if provider == "gemini":
        try:
            from core.gemini import call as gemini_call
            return gemini_call(contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key)
        except Exception as e:
            print(f"[Provider] gemini pinned failed: {e}")
            return None

    # AUTO: Gemini first (covers quota cooldown + ladder internally)
    try:
        from core.gemini import call as gemini_call
        r = gemini_call(contents, tier=tier, config=config, timeout_ms=timeout_ms, key=key)
        if r is not None and getattr(r, "text", ""):
            return r
    except Exception as e:
        print(f"[Provider] gemini auto rung error: {e}")

    # OpenAI rung if configured
    if _openai_available():
        try:
            return _openai_call(contents, tier, config, timeout_ms, key)
        except Exception as e:
            print(f"[Provider] openai auto rung skipped: {e}")

    # Local fallback
    if _local_available():
        try:
            return _local_call(contents, tier, config, timeout_ms)
        except Exception as e:
            print(f"[Provider] local auto rung skipped: {e}")

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
