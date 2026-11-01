"""Small, dependency-free helpers for classifying Live session failures."""
from __future__ import annotations


def leaf_errors(exc: BaseException):
    """Yield non-group failures inside a possibly nested TaskGroup exception."""
    if isinstance(exc, BaseExceptionGroup):
        for sub in exc.exceptions:
            yield from leaf_errors(sub)
    else:
        yield exc


def flatten_error_text(exc: BaseException) -> str:
    """Expose TaskGroup leaf failures so reconnect policy sees the real cause."""
    if isinstance(exc, BaseExceptionGroup):
        leaves = [f"{type(item).__name__}: {item}" for item in leaf_errors(exc)]
        return " | ".join(leaves) or str(exc)
    return str(exc)


def is_realtime_send_stall(error_text: str) -> bool:
    """Identify the audio transport watchdog, not an API-config rejection."""
    text = str(error_text or "").lower()
    return "send_realtime_input stalled" in text and "timed out" in text
