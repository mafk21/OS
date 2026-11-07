"""Independent deterministic review for consequential plans."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import json, time
from pathlib import Path
REPORT_PATH=Path(__file__).resolve().parent.parent/'config'/'workflow_review.json'
def latest_review()->dict:
    try: return json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    except (OSError,ValueError): return {}

DANGEROUS = {"send_message", "shell", "computer_settings", "file_controller", "accessibility_control"}

@dataclass(frozen=True)
class Review:
    approved: bool
    findings: tuple[str, ...]
    required_confirmation: bool
    required_verification: str


def review_steps(steps: list[dict[str, Any]]) -> Review:
    findings=[]; confirmation=False; verification="observed"
    if not steps: return Review(False, ("plan has no steps",), False, verification)
    if len(steps)>50: findings.append("plan exceeds the 50-step safety bound")
    seen=set()
    for index, step in enumerate(steps):
        tool=str(step.get("tool") or "").strip(); params=step.get("params")
        if not tool: findings.append(f"step {index+1} has no tool")
        if not isinstance(params, dict): findings.append(f"step {index+1} parameters are not an object")
        signature=(tool, repr(sorted(params.items())) if isinstance(params,dict) else "")
        if signature in seen and tool in DANGEROUS: findings.append(f"step {index+1} duplicates a consequential action")
        seen.add(signature)
        if tool in DANGEROUS:
            confirmation=True; verification="verified"
            if not step.get("evidence_requirement"): findings.append(f"step {index+1} lacks explicit evidence policy")
        if step.get("retry_safe") is False and int(step.get("max_attempts") or 1)>1:
            findings.append(f"step {index+1} retries a non-idempotent action")
    review=Review(not findings, tuple(findings), confirmation, verification)
    try:
        REPORT_PATH.parent.mkdir(parents=True,exist_ok=True)
        REPORT_PATH.write_text(json.dumps({'timestamp':time.time(),'approved':review.approved,'findings':list(review.findings),'required_confirmation':review.required_confirmation,'required_verification':review.required_verification,'step_count':len(steps)}),encoding='utf-8')
    except OSError: pass
    return review
