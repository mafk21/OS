"""
Behavior Interviews, Adaptive Style Learning, Custom Specialist Companions,
Visual Skills Studio (custom_skills/), and Theme Presets — Phase 3.

100% local-first (stored in `memory/companions.json` and `memory/custom_skills/`).
Never touches `skills/` so the protected core default skills contract stays pristine.
"""

from __future__ import annotations

import json
import re
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from core.skill_loader import _NAME_RE, discover_skills
from memory import config_manager as cfg
from memory import memory_manager as mm

BASE_DIR = Path(__file__).resolve().parent.parent
COMPANIONS_FILE = BASE_DIR / "memory" / "companions.json"
CORE_SKILLS_DIR = BASE_DIR / "skills"
CUSTOM_SKILLS_DIR = BASE_DIR / "memory" / "custom_skills"

_LOCK = threading.RLock()

INTERVIEW_QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "tone",
        "question": "How should your assistant sound in conversation?",
        "options": [
            "Concise & Tactical",
            "Warm & Collaborative",
            "Executive & Analytical",
            "Witty & Conversational",
        ],
    },
    {
        "id": "verbosity",
        "question": "What default response depth do you prefer?",
        "options": [
            "Crisp 1-3 sentence summaries",
            "Balanced summary + key bullets",
            "Deep technical detail with examples",
        ],
    },
    {
        "id": "proactivity",
        "question": "How proactive should tool execution be?",
        "options": [
            "Execute safe read/search steps immediately",
            "Outline plan briefly before multi-step runs",
            "Strictly wait for explicit instructions",
        ],
    },
    {
        "id": "domain_focus",
        "question": "What is your primary daily workflow focus?",
        "options": [
            "Software Engineering & Architecture",
            "Founder / Executive Operations",
            "Research, Writing & Strategy",
            "Product, Design & Growth",
        ],
    },
    {
        "id": "formatting",
        "question": "How should deliverables & HUD cards be formatted?",
        "options": [
            "Natural spoken voice + structured Markdown cards",
            "Actionable bullet lists first",
            "Code, commands & concrete diffs first",
        ],
    },
]

THEME_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        "id": "default",
        "name": "Edition Default",
        "description": "Cyan & Stark Gold (Male) / Rose & Orchid (Female)",
        "primary": "",
        "secondary": "",
    },
    "emerald_matrix": {
        "id": "emerald_matrix",
        "name": "Emerald Matrix",
        "description": "Bio-luminescent emerald core with mint-gold telemetry",
        "primary": "#10f59b",
        "secondary": "#facc15",
    },
    "arctic_ice": {
        "id": "arctic_ice",
        "name": "Arctic Ice",
        "description": "Glacial sky-blue core with silver-violet rings",
        "primary": "#38bdf8",
        "secondary": "#a78bfa",
    },
    "solar_amber": {
        "id": "solar_amber",
        "name": "Solar Amber",
        "description": "Warm fusion gold core with ember-orange highlights",
        "primary": "#fbbf24",
        "secondary": "#fb7185",
    },
    "crimson_ops": {
        "id": "crimson_ops",
        "name": "Crimson Tactical",
        "description": "High-contrast tactical ruby core with titanium amber",
        "primary": "#ff4d6d",
        "secondary": "#ff9f1c",
    },
    "violet_nova": {
        "id": "violet_nova",
        "name": "Violet Nova",
        "description": "Deep cosmic amethyst core with neon rose filaments",
        "primary": "#a855f7",
        "secondary": "#ec4899",
    },
}

# Adaptive correction trigger patterns when user corrects style/behavior in chat
_CORRECTION_PATTERNS = [
    re.compile(r"\b(?:from now on|always|never|stop\s+\w+ing|don'?t\s+(?:ever\s+)?use|please\s+don'?t|keep\s+(?:your\s+)?(?:replies|answers|responses)\b)[^.!?\n]{3,140}", re.IGNORECASE),
    re.compile(r"\b(?:call me|address me as|my preferred language is|respond in)\s+[^.!?\n]{2,80}", re.IGNORECASE),
]

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _default_state() -> dict[str, Any]:
    return {
        "active_companion_id": "default",
        "interview": {},
        "learned_rules": [],
        "companions": [],
        "theme": {
            "preset": "default",
            "custom_primary": "",
            "custom_secondary": "",
        },
    }


def _load() -> dict[str, Any]:
    with _LOCK:
        if not COMPANIONS_FILE.exists():
            return _default_state()
        try:
            raw = json.loads(COMPANIONS_FILE.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return _default_state()
            base = _default_state()
            base.update(raw)
            if not isinstance(base.get("interview"), dict):
                base["interview"] = {}
            if not isinstance(base.get("learned_rules"), list):
                base["learned_rules"] = []
            if not isinstance(base.get("companions"), list):
                base["companions"] = []
            if not isinstance(base.get("theme"), dict):
                base["theme"] = _default_state()["theme"]
            return base
        except Exception:
            return _default_state()


def _save(state: dict[str, Any]) -> None:
    with _LOCK:
        COMPANIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = COMPANIONS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(COMPANIONS_FILE)


# ── Behavior Interview & Adaptive Style Learning ──────────────────────────────

def save_behavior_interview(answers: dict[str, str]) -> dict[str, Any]:
    clean: dict[str, str] = {}
    for q in INTERVIEW_QUESTIONS:
        qid = q["id"]
        val = str((answers or {}).get(qid) or "").strip()
        if val:
            clean[qid] = val[:200]
            try:
                mm.remember(f"behavior_{qid}", val[:200], category="preferences", manual=True)
            except Exception:
                pass
    with _LOCK:
        st = _load()
        st["interview"].update(clean)
        _save(st)
        return dict(st["interview"])


def detect_and_record_correction(user_text: str) -> str | None:
    """Detect conversational behavior corrections and save them when Adaptive Learning is on."""
    if not cfg.get_adaptive_learning_enabled():
        return None
    txt = (user_text or "").strip()
    if len(txt) < 8 or len(txt) > 500:
        return None
    matched_rule: str | None = None
    for pat in _CORRECTION_PATTERNS:
        m = pat.search(txt)
        if m:
            matched_rule = m.group(0).strip(" .,;:")
            break
    if not matched_rule:
        return None

    with _LOCK:
        st = _load()
        rules: list[dict[str, Any]] = st["learned_rules"]
        lower_existing = {str(r.get("rule", "")).lower() for r in rules}
        if matched_rule.lower() not in lower_existing:
            rules.append(
                {
                    "id": f"rule-{uuid.uuid4().hex[:8]}",
                    "rule": matched_rule[:180],
                    "ts": time.strftime("%Y-%m-%d %H:%M"),
                }
            )
            st["learned_rules"] = rules[-30:]
            _save(st)
            try:
                mm.remember(
                    f"style_rule_{len(rules)}",
                    matched_rule[:180],
                    category="preferences",
                    manual=False,
                )
            except Exception:
                pass
    return matched_rule


def add_learned_rule(rule_text: str) -> dict[str, Any] | None:
    clean = (rule_text or "").strip()
    if not clean:
        return None
    rec = {
        "id": f"rule-{uuid.uuid4().hex[:8]}",
        "rule": clean[:180],
        "ts": time.strftime("%Y-%m-%d %H:%M"),
    }
    with _LOCK:
        st = _load()
        st["learned_rules"].append(rec)
        st["learned_rules"] = st["learned_rules"][-30:]
        _save(st)
    return rec


def delete_learned_rule(rule_id: str) -> bool:
    with _LOCK:
        st = _load()
        before = len(st["learned_rules"])
        st["learned_rules"] = [r for r in st["learned_rules"] if r.get("id") != rule_id]
        if len(st["learned_rules"]) != before:
            _save(st)
            return True
    return False


# ── Custom Specialist Companions ──────────────────────────────────────────────

def _default_companion_record() -> dict[str, Any]:
    persona = cfg.get_persona()
    return {
        "id": "default",
        "name": cfg.get_assistant_name(),
        "role": "Primary Full-Access Operating Companion",
        "persona": persona,
        "voice": cfg.get_voice(),
        "instructions": "Full capabilities across all tools, skills, and connected apps.",
        "allowed_tools": [],  # empty = all tools permitted
        "assigned_skills": [],
        "builtin": True,
    }


def list_companions() -> list[dict[str, Any]]:
    st = _load()
    return [_default_companion_record(), *st["companions"]]


def get_active_companion() -> dict[str, Any]:
    st = _load()
    active_id = st.get("active_companion_id") or "default"
    if active_id == "default":
        return _default_companion_record()
    for c in st["companions"]:
        if c.get("id") == active_id:
            return c
    return _default_companion_record()


def save_companion(data: dict[str, Any]) -> dict[str, Any]:
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("Companion name is required.")
    persona = "female" if str(data.get("persona") or "").lower() == "female" else "male"
    default_voice = "Aoede" if persona == "female" else "Charon"
    voice = str(data.get("voice") or default_voice).strip() or default_voice
    cid = str(data.get("id") or "").strip() or f"comp-{uuid.uuid4().hex[:8]}"
    if cid == "default":
        cid = f"comp-{uuid.uuid4().hex[:8]}"

    raw_tools = data.get("allowed_tools")
    allowed_tools = [str(t).strip() for t in raw_tools if str(t).strip()] if isinstance(raw_tools, list) else []
    raw_skills = data.get("assigned_skills")
    assigned_skills = [str(s).strip() for s in raw_skills if str(s).strip()] if isinstance(raw_skills, list) else []

    rec = {
        "id": cid,
        "name": name[:48],
        "role": str(data.get("role") or "Specialist Companion").strip()[:96],
        "persona": persona,
        "voice": voice,
        "instructions": str(data.get("instructions") or "").strip()[:2000],
        "allowed_tools": allowed_tools,
        "assigned_skills": assigned_skills,
        "builtin": False,
    }
    with _LOCK:
        st = _load()
        replaced = False
        for i, existing in enumerate(st["companions"]):
            if existing.get("id") == cid:
                st["companions"][i] = rec
                replaced = True
                break
        if not replaced:
            st["companions"].append(rec)
        _save(st)
    return rec


def delete_companion(companion_id: str) -> bool:
    if not companion_id or companion_id == "default":
        return False
    with _LOCK:
        st = _load()
        before = len(st["companions"])
        st["companions"] = [c for c in st["companions"] if c.get("id") != companion_id]
        if st.get("active_companion_id") == companion_id:
            st["active_companion_id"] = "default"
        if len(st["companions"]) != before:
            _save(st)
            return True
    return False


def set_active_companion(companion_id: str) -> dict[str, Any]:
    cid = (companion_id or "default").strip()
    with _LOCK:
        st = _load()
        valid_ids = {"default"} | {str(c.get("id")) for c in st["companions"]}
        if cid not in valid_ids:
            cid = "default"
        st["active_companion_id"] = cid
        _save(st)
    comp = get_active_companion()
    if cid != "default":
        cfg.save_persona(comp.get("persona", "male"), voice_name=comp.get("voice"))
    return comp


def is_tool_allowed_for_active_companion(tool_name: str) -> tuple[bool, str]:
    """Enforce scoped tool permissions when a Specialist Companion is active."""
    comp = get_active_companion()
    allowed = comp.get("allowed_tools") or []
    if not allowed:
        return True, ""
    # Always allow core read-only memory/skill lookup so the companion can think
    always_ok = {"recall_memory", "skill_read"}
    if tool_name in always_ok or tool_name in allowed:
        return True, ""
    return (
        False,
        f"Blocked by Specialist Companion '{comp.get('name')}' tool scope. "
        f"Allowed tools: {', '.join(allowed)}",
    )


def format_behavior_and_companion_for_prompt(*, include_personalization: bool = True) -> str:
    """Build behavior, custom-skill, and active specialist prompt overlays.

    Soul already renders migrated behavior preferences, so callers may exclude
    only that portion while preserving custom skills and specialist scoping.
    """
    parts: list[str] = []
    st = _load()

    if include_personalization and cfg.get_personalization_enabled():
        iv = st.get("interview") or {}
        if iv:
            lines = ["[BEHAVIOR INTERVIEW PREFERENCES]"]
            for k, v in iv.items():
                lines.append(f"  • {k.replace('_', ' ').title()}: {v}")
            parts.append("\n".join(lines))

        rules = st.get("learned_rules") or []
        if rules:
            rlines = ["[ADAPTIVE STYLE & BEHAVIOR RULES — follow strictly]"]
            for r in rules[-12:]:
                rlines.append(f"  • {r.get('rule')}")
            parts.append("\n".join(rlines))

    if CUSTOM_SKILLS_DIR.is_dir():
        cust_listing = discover_skills(CUSTOM_SKILLS_DIR, logger=lambda _: None).get_listing()
        if cust_listing and not cust_listing.startswith("("):
            parts.append(f"[CUSTOM USER SKILLS — load via skill_read]\n{cust_listing}")

    comp = get_active_companion()
    if comp.get("id") != "default":
        clines = [
            f"[ACTIVE SPECIALIST COMPANION: {comp.get('name')} — {comp.get('role')}]",
        ]
        if comp.get("instructions"):
            clines.append(f"Instructions: {comp['instructions']}")
        if comp.get("allowed_tools"):
            clines.append(f"Scoped Tools ONLY: {', '.join(comp['allowed_tools'])}")
        if comp.get("assigned_skills"):
            clines.append(f"Prioritize Skills: {', '.join(comp['assigned_skills'])}")
        parts.append("\n".join(clines))

    return "\n\n".join(parts)


# ── Visual Skills Studio (Core Inspector + Custom SKILL.md Authoring) ─────────

def list_all_skills_for_studio() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    core_reg = discover_skills(CORE_SKILLS_DIR, logger=lambda _: None)
    for name in sorted(core_reg.names()):
        rec = core_reg._skills[name]
        out.append(
            {
                "name": rec.name,
                "description": rec.description,
                "body": core_reg.read(name),
                "builtin": True,
                "resources": list(rec.resources),
            }
        )

    if CUSTOM_SKILLS_DIR.is_dir():
        cust_reg = discover_skills(CUSTOM_SKILLS_DIR, logger=lambda _: None)
        for name in sorted(cust_reg.names()):
            rec = cust_reg._skills[name]
            out.append(
                {
                    "name": rec.name,
                    "description": rec.description,
                    "body": cust_reg.read(name),
                    "builtin": False,
                    "resources": list(rec.resources),
                }
            )
    return out


def save_custom_skill(name: str, description: str, body: str) -> dict[str, Any]:
    slug = (name or "").strip().lower()
    if not _NAME_RE.match(slug):
        raise ValueError(
            "Skill name must be lowercase letters, numbers, and single hyphens (e.g. 'sprint-planner')."
        )
    core_names = discover_skills(CORE_SKILLS_DIR, logger=lambda _: None).names()
    if slug in core_names:
        raise ValueError(
            f"'{slug}' is one of the protected core skills. Choose a distinct custom name (e.g. '{slug}-custom')."
        )
    CUSTOM_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    reg = discover_skills(CUSTOM_SKILLS_DIR, logger=lambda _: None)
    exists = slug in reg.names()
    msg = reg.write(name=slug, description=description.strip(), body=body.strip(), update=exists)
    return {"name": slug, "message": msg}


def delete_custom_skill(name: str) -> bool:
    slug = (name or "").strip().lower()
    if not _NAME_RE.match(slug):
        return False
    target = (CUSTOM_SKILLS_DIR / slug).resolve()
    if not str(target).startswith(str(CUSTOM_SKILLS_DIR.resolve())):
        return False
    if target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
        return True
    return False


# ── Custom Theme Presets & Accent Overrides ───────────────────────────────────

def get_theme_customization() -> dict[str, Any]:
    st = _load()
    th = st.get("theme") or {}
    preset_id = str(th.get("preset") or "default")
    if preset_id not in THEME_PRESETS:
        preset_id = "default"
    preset = THEME_PRESETS[preset_id]
    c_pri = str(th.get("custom_primary") or "").strip()
    c_sec = str(th.get("custom_secondary") or "").strip()
    eff_primary = c_pri if _HEX_RE.match(c_pri) else preset["primary"]
    eff_secondary = c_sec if _HEX_RE.match(c_sec) else preset["secondary"]
    return {
        "preset": preset_id,
        "custom_primary": c_pri if _HEX_RE.match(c_pri) else "",
        "custom_secondary": c_sec if _HEX_RE.match(c_sec) else "",
        "effective_primary": eff_primary,
        "effective_secondary": eff_secondary,
        "presets": list(THEME_PRESETS.values()),
    }


def save_theme_customization(
    preset: str = "default",
    custom_primary: str = "",
    custom_secondary: str = "",
) -> dict[str, Any]:
    pid = preset if preset in THEME_PRESETS else "default"
    cp = custom_primary.strip() if _HEX_RE.match((custom_primary or "").strip()) else ""
    cs = custom_secondary.strip() if _HEX_RE.match((custom_secondary or "").strip()) else ""
    with _LOCK:
        st = _load()
        st["theme"] = {
            "preset": pid,
            "custom_primary": cp,
            "custom_secondary": cs,
        }
        _save(st)
    return get_theme_customization()


def get_studio_snapshot(available_tools: list[str] | None = None) -> dict[str, Any]:
    st = _load()
    return {
        "interview_questions": INTERVIEW_QUESTIONS,
        "interview_answers": st.get("interview") or {},
        "learned_rules": st.get("learned_rules") or [],
        "active_companion": get_active_companion(),
        "companions": list_companions(),
        "skills": list_all_skills_for_studio(),
        "theme": get_theme_customization(),
        "available_tools": sorted(set(available_tools or [])),
    }
