"""Capability, privacy, and health-aware provider routing policy."""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass, field
from typing import Iterable

@dataclass(frozen=True)
class ProviderRequest:
    data_class: str = "standard"  # standard | private | restricted
    capabilities: frozenset[str] = field(default_factory=frozenset)
    allow_cloud_fallback: bool = True

_CAPABILITIES = {
    "gemini": {"text", "json", "vision", "search"},
    "anthropic": {"text", "json"},
    "openai": {"text", "json", "vision"},
    "local": {"text", "json"},
}
_FAILURES: dict[str, tuple[int, float]] = {}
_LOCK = threading.Lock()
COOLDOWN_SECONDS = 60.0


def note_result(provider: str, success: bool) -> None:
    with _LOCK:
        if success:
            _FAILURES.pop(provider, None)
        else:
            count, _ = _FAILURES.get(provider, (0, 0.0))
            _FAILURES[provider] = (count + 1, time.monotonic())


def cooling(provider: str, now: float | None = None) -> bool:
    with _LOCK:
        count, at = _FAILURES.get(provider, (0, 0.0))
    return count >= 2 and (time.monotonic() if now is None else now) - at < COOLDOWN_SECONDS


def route(preference: str, request: ProviderRequest, available: Iterable[str]) -> list[str]:
    available_set = set(available)
    required = set(request.capabilities or {"text"})
    if request.data_class not in {"standard", "private", "restricted"}:
        raise ValueError("unsupported provider data classification")
    if preference not in {"auto", "gemini", "anthropic", "openai", "local", "ollama", "lmstudio"}:
        preference = "auto"
    preferred = "local" if preference in {"ollama", "lmstudio"} else preference
    if preferred != "auto":
        candidates = [preferred]
    elif request.data_class in {"private", "restricted"}:
        candidates = ["local"]
    else:
        candidates = ["gemini", "anthropic", "openai", "local"]
    if not request.allow_cloud_fallback and candidates:
        candidates = candidates[:1]
    return [p for p in candidates if p in available_set and required <= _CAPABILITIES.get(p, set()) and not cooling(p)]
