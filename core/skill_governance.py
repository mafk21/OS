"""Review, rollback, and evidence-based reliability for manifested skills."""
from __future__ import annotations
import json, os, shutil, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "config" / "skill_reliability.json"
BACKUPS = ROOT / "config" / "skill_backups"


def propose(skill_dir: Path, proposed_markdown: str) -> Path:
    skill_dir = Path(skill_dir).resolve()
    if skill_dir.name.startswith(".") or not proposed_markdown.strip(): raise ValueError("invalid skill proposal")
    proposal = skill_dir / "SKILL.md.proposed"
    proposal.write_text(proposed_markdown, encoding="utf-8")
    return proposal


def approve(skill_dir: Path) -> str:
    skill_dir = Path(skill_dir).resolve(); current = skill_dir / "SKILL.md"; proposal = skill_dir / "SKILL.md.proposed"
    if not proposal.is_file(): raise ValueError("no reviewable proposal exists")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / f"{skill_dir.name}-{int(time.time() * 1000)}.md"
    if current.exists(): shutil.copy2(current, backup)
    os.replace(proposal, current)
    return str(backup) if backup.exists() else ""


def rollback(skill_dir: Path, backup: Path) -> None:
    skill_dir = Path(skill_dir).resolve(); backup = Path(backup).resolve()
    if not backup.is_relative_to(BACKUPS.resolve()) or not backup.is_file(): raise ValueError("invalid skill backup")
    shutil.copy2(backup, skill_dir / "SKILL.md")


def record_outcome(name: str, verified: bool) -> None:
    try: data = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError): data = {}
    row = data.setdefault(str(name)[:64], {"verified": 0, "failed": 0})
    row["verified" if verified else "failed"] += 1
    STATE.parent.mkdir(parents=True, exist_ok=True); temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, sort_keys=True), encoding="utf-8"); os.replace(temp, STATE)


def reliability(name: str) -> dict[str, Any]:
    try: row = json.loads(STATE.read_text(encoding="utf-8")).get(name, {})
    except (OSError, ValueError): row = {}
    passed, failed = int(row.get("verified", 0)), int(row.get("failed", 0)); total = passed + failed
    return {"verified": passed, "failed": failed, "score": (passed / total if total else None), "sample_size": total}
