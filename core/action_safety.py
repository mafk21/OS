"""Shared action lifecycle, risk policy, confirmation, verification, and audit.

Every built-in action passes through this boundary. Audit records contain only
bounded metadata and parameter names—never message bodies, credentials, file
contents, or model reasoning.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core import confirm
from core.task_evidence import from_result, satisfies

ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = ROOT / "config" / "action_audit.jsonl"
MAX_AUDIT_BYTES = 1_000_000
RISKS = {"low", "medium", "high", "critical"}


@dataclass(frozen=True)
class ActionPolicy:
    risk: str = "low"
    permission: str = "local"
    confirmation: str = "none"  # none | required
    side_effect: bool = False
    reversible: bool = False
    verification: str = "observed"

    @classmethod
    def from_metadata(cls, value: Any) -> "ActionPolicy":
        data = value if isinstance(value, dict) else {}
        risk = str(data.get("risk") or "low").lower()
        confirmation = str(data.get("confirmation") or "none").lower()
        verification = str(data.get("verification") or "observed").lower()
        if risk not in RISKS: risk = "low"
        if confirmation not in {"none", "required"}: confirmation = "none"
        if verification not in {"observed", "verified"}: verification = "observed"
        return cls(risk, str(data.get("permission") or "local")[:80], confirmation,
                   bool(data.get("side_effect", False)), bool(data.get("reversible", False)),
                   verification)


_DEFAULT_POLICIES = {
    "file_controller": ActionPolicy("medium", "filesystem", "none", True, True, "observed"),
    "computer_settings": ActionPolicy("medium", "device_settings", "none", True, True, "observed"),
}


def policy_for(action: str, metadata: Any) -> ActionPolicy:
    if isinstance(metadata, dict) and metadata:
        return ActionPolicy.from_metadata(metadata)
    return _DEFAULT_POLICIES.get(str(action), ActionPolicy())


_AUDIT_LOCK = threading.Lock()


def _audit(event: dict[str, Any]) -> None:
    safe = {
        "timestamp": time.time(), "execution_id": str(event.get("execution_id") or "")[:80],
        "action": str(event.get("action") or "")[:64], "stage": str(event.get("stage") or "")[:32],
        "risk": str(event.get("risk") or "")[:16], "permission": str(event.get("permission") or "")[:80],
        "outcome": str(event.get("outcome") or "")[:40],
        "parameter_keys": sorted(str(k)[:64] for k in (event.get("parameter_keys") or []))[:40],
        "evidence_state": str(event.get("evidence_state") or "")[:24],
        "reversible": bool(event.get("reversible", False)),
    }
    with _AUDIT_LOCK:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if AUDIT_PATH.exists() and AUDIT_PATH.stat().st_size >= MAX_AUDIT_BYTES:
            backup = AUDIT_PATH.with_suffix(".jsonl.1")
            backup.unlink(missing_ok=True)
            AUDIT_PATH.replace(backup)
        with AUDIT_PATH.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(safe, ensure_ascii=False) + "\n")


def _scope(action: str, parameters: dict[str, Any]) -> str:
    nonsecret = "|".join(str(parameters.get(key) or "")[:120]
                         for key in ("receiver", "platform", "service", "action", "path"))
    return hashlib.sha256(f"{action}|{nonsecret}".encode()).hexdigest()[:12]


def _confirmation_detail(action: str, parameters: dict[str, Any], policy: ActionPolicy) -> str:
    destination = str(parameters.get("receiver") or parameters.get("service") or parameters.get("path") or "the requested destination")[:160]
    return (
        f"Allow {action} to perform a {policy.risk}-risk {policy.permission} action for {destination}? "
        "Private content is intentionally omitted from this confirmation."
    )


def _validate_boundary(parameters: dict[str, Any], policy: ActionPolicy) -> str:
    if policy.permission == "external_communication":
        destination = str(parameters.get("receiver") or parameters.get("service") or "").strip()
        if not destination:
            return "External communication requires an explicit recipient or service."
        if any(ord(char) < 32 for char in destination):
            return "The external destination contains invalid control characters."
    for key in ("path", "destination", "target"):
        value = parameters.get(key)
        if isinstance(value, str) and "\x00" in value:
            return f"The {key} contains an invalid null character."
    return ""


def execute(action: str, parameters: dict[str, Any], policy: ActionPolicy,
            handler: Callable[[], Any]) -> Any:
    """Run understand→plan→confirm→execute→verify→report for one action."""
    params = parameters if isinstance(parameters, dict) else {}
    sensitive_keys = {str(key).lower() for key in params if any(token in str(key).lower() for token in ("password", "token", "secret", "api_key", "credential"))}
    if sensitive_keys and policy.confirmation == "none":
        policy = ActionPolicy("high", policy.permission, "required", policy.side_effect,
                              policy.reversible, policy.verification)
    execution_id = f"act-{uuid.uuid4().hex[:12]}"
    common = {
        "execution_id": execution_id, "action": action, "risk": policy.risk,
        "permission": policy.permission, "parameter_keys": params.keys(),
        "reversible": policy.reversible,
    }
    boundary_error = _validate_boundary(params, policy)
    if boundary_error:
        _audit({**common, "stage": "understand", "outcome": "rejected"})
        return boundary_error
    _audit({**common, "stage": "understand", "outcome": "accepted"})
    _audit({**common, "stage": "plan", "outcome": "confirmation_required" if policy.confirmation == "required" else "ready"})

    def run() -> Any:
        _audit({**common, "stage": "execute", "outcome": "started"})
        try:
            result = handler()
        except BaseException:
            _audit({**common, "stage": "report", "outcome": "exception"})
            raise
        evidence = from_result(result, tool=action, started_at=time.time() - 0.001,
                               requirement=policy.verification)
        _audit({**common, "stage": "verify", "outcome": "satisfied" if satisfies(evidence, policy.verification) else "unsatisfied",
                "evidence_state": evidence.state})
        if policy.reversible:
            try:
                from core.undo import can_undo
                undo_outcome = "available" if can_undo() else "not_registered"
            except Exception:
                undo_outcome = "unavailable"
            _audit({**common, "stage": "undo", "outcome": undo_outcome,
                    "evidence_state": evidence.state})
        verified = satisfies(evidence, policy.verification)
        _audit({**common, "stage": "report", "outcome": "returned" if verified else "unverified", "evidence_state": evidence.state})
        if not verified:
            if evidence.state == "contradicted":
                return f"Action failed verification: {evidence.summary}"
            return (
                "Action executed, but completion is unverified. Do not claim success. "
                f"Observed outcome: {evidence.summary}"
            )
        return result

    if policy.confirmation == "required":
        key = f"action-{action}-{_scope(action, params)}"
        return confirm.request(key, f"Confirm {action.replace('_', ' ')}?",
                               _confirmation_detail(action, params, policy), run)
    return run()
