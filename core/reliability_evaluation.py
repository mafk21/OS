"""Deterministic evaluation registry and truthful release-over-release reporting."""
from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "config" / "reliability_evaluations.json"
MATRIX = {
    "voice": ("noise", "barge_in", "wake_word", "push_to_talk"),
    "providers": ("outage", "rate_limit", "empty_response", "privacy_route"),
    "recovery": ("restart", "crash", "network_loss", "corrupt_state"),
    "adversarial": ("prompt_injection", "duplicate_action", "path_escape", "credential_leak"),
    "platforms": ("windows_311", "windows_312", "macos_311", "macos_312", "linux_311", "linux_312"),
}


def record(release: str, category: str, case: str, passed: bool, evidence: str = "") -> None:
    if category not in MATRIX or case not in MATRIX[category]: raise ValueError("unknown evaluation case")
    try: data = json.loads(RESULTS.read_text(encoding="utf-8"))
    except (OSError, ValueError): data = {"version": 1, "runs": []}
    data.setdefault("runs", []).append({"release": str(release)[:80], "category": category, "case": case,
                                         "passed": bool(passed), "evidence": str(evidence)[:240], "at": time.time()})
    data["runs"] = data["runs"][-2000:]
    RESULTS.parent.mkdir(parents=True, exist_ok=True); temp = RESULTS.with_suffix(".tmp")
    temp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8"); os.replace(temp, RESULTS)


def report(release: str, previous: str = "") -> dict[str, Any]:
    try: runs = json.loads(RESULTS.read_text(encoding="utf-8")).get("runs", [])
    except (OSError, ValueError): runs = []
    def stats(version: str):
        selected = [r for r in runs if r.get("release") == version]
        passed = sum(bool(r.get("passed")) for r in selected); total = len(selected)
        return {"passed": passed, "total": total, "rate": passed / total if total else None}
    current, prior = stats(release), stats(previous) if previous else None
    delta = None if not prior or current["rate"] is None or prior["rate"] is None else current["rate"] - prior["rate"]
    covered = sorted({f"{r.get('category')}/{r.get('case')}" for r in runs if r.get("release") == release})
    expected = sum(len(cases) for cases in MATRIX.values())
    return {"release": release, "current": current, "previous": prior, "delta": delta,
            "coverage": {"covered": len(covered), "expected": expected, "cases": covered},
            "claim": "measured_only_no_absolute_reliability_claim"}
