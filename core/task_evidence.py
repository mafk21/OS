"""Evidence contracts for durable task outcomes.

Evidence records contain bounded metadata, never raw private payloads. Tool
failures and authoritative observations outrank conversational success wording.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_EXTERNAL_SIDE_EFFECT_TOOLS = frozenset({
    "send_message", "social_hub", "instagram_direct", "instagram_web",
    "computer_control", "computer_settings", "device_manager", "browser_agent",
    "cloud_integrations", "github_automation",
})


@dataclass(frozen=True)
class Evidence:
    state: str  # observed | verified | uncertain | contradicted
    source: str
    summary: str
    observed_at: float
    authoritative: bool = False
    reference: str = ""
    digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def requirement_for(tool: str, declared: str = "") -> str:
    declared = str(declared or "").strip().lower()
    if declared in {"observed", "verified"}:
        return declared
    return "verified" if str(tool).strip().lower() in _EXTERNAL_SIDE_EFFECT_TOOLS else "observed"


def _digest(value: Any) -> str:
    try:
        payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        payload = repr(type(value).__name__)
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()[:16]


def from_result(value: Any, *, tool: str, started_at: float,
                requirement: str = "observed") -> Evidence:
    """Convert a tool result to bounded evidence without trusting prose alone."""
    now = time.time()
    if isinstance(value, dict):
        status = str(value.get("status") or "").lower()
        explicit_failure = value.get("ok") is False or value.get("success") is False or status in {
            "failed", "failure", "error", "cancelled",
        }
        if explicit_failure:
            return Evidence("contradicted", "tool_result", "The tool authoritatively reported failure.",
                            now, True, digest=_digest(value))
        raw_time = value.get("observed_at") or value.get("verified_at") or now
        try:
            observed_at = float(raw_time)
        except (TypeError, ValueError):
            observed_at = now
        if observed_at + 1e-6 < started_at:
            return Evidence("uncertain", "tool_result", "The supplied evidence predates this execution.",
                            observed_at, False, digest=_digest(value))
        verified = bool(value.get("verified")) or status == "verified"
        summary = str(value.get("evidence") or value.get("summary") or "Tool returned a structured outcome.")[:500]
        reference = str(value.get("evidence_reference") or "")[:240]
        return Evidence("verified" if verified else "observed", "tool_result", summary,
                        observed_at, bool(value.get("authoritative", verified)), reference, _digest(value))
    if value is False:
        return Evidence("contradicted", "tool_result", "The tool returned false.", now, True, digest=_digest(value))
    return Evidence("observed", "tool_result", "The action returned without a structured failure.",
                    now, False, digest=_digest(value))


def evaluate_postcondition(postcondition: dict[str, Any] | None, result: Any) -> Evidence | None:
    """Evaluate small deterministic postconditions; arbitrary code is forbidden."""
    if not postcondition:
        return None
    kind = str(postcondition.get("type") or "").strip().lower()
    now = time.time()
    if kind == "file_exists":
        path = Path(str(postcondition.get("path") or "")).expanduser()
        ok = path.is_file()
        return Evidence("verified" if ok else "contradicted", "postcondition",
                        "Required file exists." if ok else "Required file does not exist.",
                        now, True, reference=str(path))
    if kind == "result_contains":
        token = str(postcondition.get("value") or "")
        ok = bool(token) and token in str(result)
        return Evidence("verified" if ok else "contradicted", "postcondition",
                        "Required result marker was observed." if ok else "Required result marker was absent.",
                        now, True)
    if kind == "structured_field":
        field = str(postcondition.get("field") or "")
        expected = postcondition.get("equals")
        ok = isinstance(result, dict) and field in result and result[field] == expected
        return Evidence("verified" if ok else "contradicted", "postcondition",
                        "Required structured field matched." if ok else "Required structured field did not match.",
                        now, True)
    return Evidence("uncertain", "postcondition", "Unsupported postcondition was not executed.", now, False)


def satisfies(evidence: Evidence, requirement: str) -> bool:
    if evidence.state in {"contradicted", "uncertain"}:
        return False
    return evidence.state == "verified" if requirement == "verified" else evidence.state in {"observed", "verified"}
