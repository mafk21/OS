"""SKILL.md skill discovery — the open Agent Skills standard (agentskills.io).

A skill is a **folder** containing a ``SKILL.md`` file::

    skills/
      deep-research/
        SKILL.md          <- YAML frontmatter + markdown instructions
        references/       <- optional, read on demand by the model
        scripts/          <- optional, run through the shell tool

    ---
    name: deep-research
    description: What it does AND when to use it (the trigger text).
    ---
    # Instructions...

Why this exists — **progressive disclosure**, the whole point of the format:

* Level 1: name + description enter the system prompt at startup (~100 tokens
  each) via ``{skills}``. That is all the model sees until a task matches.
* Level 2: the SKILL.md body (<5k tokens) loads on demand through the
  ``skill_read`` tool — nothing costs context until it is used.
* Level 3: bundled references/scripts are read only when the body points at
  them. Scripts execute through the existing shell tool, so only their output
  enters context — this loader never executes anything.

The format is an open standard (Anthropic, Dec 2025) loaded by Claude Code,
GitHub Copilot, VS Code, Codex, Cursor and Gemini CLI — so any SKILL.md from
the public registries (skills.sh, ClawHub, google/skills …) drops straight in.

Contract mirrors ``core.action_loader``: import/validation problems are logged
and the folder is skipped — ``discover_skills`` NEVER raises.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# Spec rules for the name field: lowercase letters, numbers, single hyphens,
# 1-64 chars, and it must match the folder it lives in.
_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Cap what a single skill_read may return so one bloated file cannot flood the
# context window.
_MAX_BODY = 100_000          # chars
# Listing cap: metadata only, but 100 lines is already ~3-4k tokens.
_LISTING_LIMIT = 100
_DESC_IN_LISTING = 160       # chars per description in the {skills} block


@dataclass
class SkillRecord:
    name: str
    description: str = ""
    dir: str = ""             # folder name on disk (lookup key fallback)
    path: Optional[Path] = None
    valid: bool = False
    error: str = ""
    resources: list = field(default_factory=list)   # bundled files, relative


# ── frontmatter ─────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split SKILL.md into (frontmatter dict, body).

    Dependency-free on purpose: this project has no PyYAML and a skill loader
    is the wrong reason to add one. Supports what the spec actually uses —
    ``key: value`` single lines (quotes stripped) and folded/literal block
    values (``key: |`` / ``key: >``) whose continuation lines are indented.
    Returns ({}, full text) when no frontmatter block is present.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    # opening fence must be exactly --- (allow trailing whitespace)
    if lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}, text                      # unterminated block — not frontmatter
    fm: dict[str, str] = {}
    key: Optional[str] = None
    mode: Optional[str] = None               # None | "|" | ">"
    for raw in lines[1:end]:
        if mode is not None:
            if raw[:1] in (" ", "\t") and raw.strip():
                piece = raw.strip()
                if not fm.get(key):
                    fm[key] = piece
                elif mode == ">":
                    fm[key] = fm[key] + " " + piece
                else:
                    fm[key] = fm[key] + "\n" + piece
                continue
            mode = None                      # dedent ends the block value
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t"):
            continue                         # stray indentation — ignore
        if ":" not in raw:
            continue
        k, _, v = raw.partition(":")
        k = k.strip().lower()
        v = v.strip()
        if not k:
            continue
        if v in ("|", ">", "|-", ">-"):
            mode = v[0]
            fm[k] = ""
            key = k          # continuations below append to THIS key
        else:
            fm[k] = _unquote(v)
            key = k
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return fm, body


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


# ── registry ────────────────────────────────────────────────────────────────

class SkillRegistry:
    def __init__(self, skills: dict[str, "SkillRecord"], all_records: list):
        self._skills = skills          # name -> record, VALID entries only
        self._all = all_records

    def __len__(self) -> int:
        return len(self._skills)

    def names(self) -> set[str]:
        return set(self._skills)

    # -- prompt side (Level 1: metadata only) ────────────────────────────────
    def get_listing(self, limit: int = _LISTING_LIMIT) -> str:
        """"- name: description" lines for the {skills} prompt block.

        Description is truncated (that is what triggers matching — the full
        text lives in SKILL.md). Empty registry returns a short marker so the
        prompt reads deliberately rather than with a hole in it.
        """
        if not self._skills:
            return ("(No skills installed — skill folders live in the "
                    "skills/ directory next to main.py.)")
        out = []
        for i, name in enumerate(sorted(self._skills)):
            if i >= limit:
                out.append(f"- …and {len(self._skills) - limit} more "
                           f"(say 'list skills' to hear them)")
                break
            rec = self._skills[name]
            desc = " ".join(rec.description.split())[:_DESC_IN_LISTING]
            out.append(f"- {name}: {desc}" if desc else f"- {name}")
        return "\n".join(out)

    # -- tool side (Level 2/3: body + bundled files) ─────────────────────────
    def read(self, name: str, relpath: Optional[str] = None) -> str:
        """Return a skill's SKILL.md body, or one bundled file.

        ``relpath`` is resolved strictly inside the skill's folder — absolute
        paths, ``..`` escapes and symlink tricks raise ValueError. This tool
        only ever reads; execution (of scripts) is the shell tool's job.
        """
        key = str(name or "").strip().lower()
        rec = self._skills.get(key)
        if rec is None:
            known = ", ".join(sorted(self._skills)) or "(none)"
            raise ValueError(
                f"No skill named '{name}'. Installed skills: {known}")
        base = (rec.path or Path(".")).resolve()
        if not relpath:
            text = _read_capped(base / "SKILL.md", what=f"skill '{key}'")
            # Level 2 is the instructions, not the frontmatter — the metadata
            # is already in the {skills} block; don't pay for it twice.
            _, body = parse_frontmatter(text)
            return body if body.strip() else text
        rel = str(relpath).strip().replace("\\", "/")
        if not rel or rel.startswith("/") or ":" in rel.split("/")[0]:
            raise ValueError(f"'{relpath}' must be a relative path inside the skill")
        target = (base / rel).resolve()
        if not target.is_relative_to(base) or target == base:
            raise ValueError(f"'{relpath}' points outside skill '{key}'")
        if not target.is_file():
            raise ValueError(f"Skill '{key}' has no file '{relpath}'"
                             f" (bundled: {', '.join(rec.resources) or 'none'})")
        return _read_capped(target, what=f"'{relpath}'")


def _read_capped(path: Path, what: str) -> str:
    if not path.is_file():
        raise ValueError(f"{what} not found at {path.name}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > _MAX_BODY:
        text = text[:_MAX_BODY] + f"\n\n… [truncated at {_MAX_BODY} chars]"
    return text


# ── discovery ───────────────────────────────────────────────────────────────

def discover_skills(skills_dir: Path,
                    logger: Callable[[str], None] = print) -> SkillRegistry:
    """Scan skills_dir for folders containing SKILL.md.

    Folders starting with '_' (the template) and files are skipped silently —
    same convention as actions/*.py. A folder with an SKILL.md that fails the
    spec (missing description, bad/mismatched name) is LOGGED and skipped.
    Never raises.
    """
    try:
        skills_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    valid: dict[str, SkillRecord] = {}
    all_records: list[SkillRecord] = []
    try:
        folders = sorted((p for p in skills_dir.iterdir() if p.is_dir()),
                         key=lambda p: p.name)
    except Exception as e:
        logger(f"Skill discovery failed: {e}")
        return SkillRegistry(valid, all_records)

    for folder in folders:
        if folder.name.startswith("_"):
            continue
        md = folder / "SKILL.md"
        if not md.is_file():
            md = folder / "skill.md"
            if not md.is_file():
                continue
        rec = SkillRecord(name=folder.name, dir=folder.name, path=folder)
        try:
            fm, body = parse_frontmatter(md.read_text(encoding="utf-8",
                                                      errors="replace"))
            name = str(fm.get("name", "")).strip()
            desc = str(fm.get("description", "")).strip()
            if not name:
                raise ValueError("frontmatter missing 'name'")
            if not desc:
                raise ValueError("frontmatter missing 'description' "
                                 "(must say what it does AND when to use it)")
            if not _NAME_RE.match(name) or len(name) > 64:
                raise ValueError(f"invalid name '{name}' — lowercase letters, "
                                 f"numbers and hyphens, max 64 chars")
            if name != folder.name:
                raise ValueError(f"name '{name}' must match folder "
                                 f"'{folder.name}'")
            if not body.strip():
                raise ValueError("SKILL.md body is empty — nothing to follow")
            rec.name, rec.description = name, desc
            rec.valid = True
            rec.resources = [
                str(p.relative_to(folder))
                for p in sorted(folder.rglob("*"))
                if p.is_file() and p.name not in ("SKILL.md", "skill.md")
            ][:40]
            if name in valid:
                raise ValueError(f"duplicate skill name '{name}'")
            valid[name] = rec
            logger(f"Skill loaded: {name} ({folder.name}/SKILL.md)"
                   + (f" +{len(rec.resources)} file(s)" if rec.resources else ""))
        except Exception as e:
            rec.valid = False
            rec.error = str(e)
            logger(f"Skill '{folder.name}' rejected: {e}")
        all_records.append(rec)

    logger(f"Skill discovery complete: {len(valid)} active.")
    return SkillRegistry(valid, all_records)
