"""Safe user messaging and private diagnostics for cloud connection failures."""
from __future__ import annotations

import re
import traceback
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "connection-errors.log"
_MAX_BYTES = 1_000_000
_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_ -]?key|authorization|token|secret)(\s*[:=]\s*)([^\s,;&]+)"),
    re.compile(r"(?i)([?&](?:key|api_key|token)=)([^&\s]+)"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bsk-[0-9A-Za-z_-]{16,}\b"),
)


def redact(text: str) -> str:
    value = str(text or "")
    value = _SECRET_PATTERNS[0].sub(r"\1\2[REDACTED]", value)
    value = _SECRET_PATTERNS[1].sub(r"\1[REDACTED]", value)
    value = _SECRET_PATTERNS[2].sub("[REDACTED_GEMINI_KEY]", value)
    return _SECRET_PATTERNS[3].sub("[REDACTED_OPENAI_KEY]", value)


def user_message(error_text: str) -> str:
    """Convert transport detail into a short, actionable message."""
    low = str(error_text or "").lower()
    if "timed out" in low or "timeouterror" in low:
        return "Cloud connection timed out. Check your internet, VPN, or firewall, then retry."
    if "getaddrinfo" in low or "name resolution" in low or "nodename" in low:
        return "The cloud service address could not be resolved. Check DNS and your internet connection."
    if "certificate" in low or "ssl" in low or "tls" in low:
        return "A secure connection could not be established. Check the system clock, proxy, or antivirus HTTPS inspection."
    if "refused" in low or "cannot connect" in low or "network is unreachable" in low:
        return "The cloud service could not be reached. Check your network, proxy, VPN, or firewall."
    return "The live AI connection was interrupted. JARVIS will keep local features available while it retries."


def write_failure(exc: BaseException, *, engine: str = "unknown", model: str = "") -> Path:
    """Append a redacted traceback to a bounded local diagnostic log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists() and LOG_PATH.stat().st_size > _MAX_BYTES:
        rotated = LOG_PATH.with_suffix(".log.1")
        try:
            rotated.unlink(missing_ok=True)
            LOG_PATH.replace(rotated)
        except OSError:
            pass
    stamp = datetime.now(timezone.utc).isoformat()
    detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    entry = redact(
        f"\n[{stamp}] engine={engine} model={model or 'unknown'} "
        f"error={type(exc).__name__}\n{detail}\n"
    )
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return LOG_PATH
