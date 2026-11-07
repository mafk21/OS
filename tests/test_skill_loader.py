"""Tests — SKILL.md skills layer (Phase 8).

Covers the loader contract (discovery, spec validation, progressive
disclosure, path safety) and the wiring in main.py / prompt.txt.
Real files in tmp_path — no Qt, no network, no model.
"""
import hashlib
import json
import pathlib

from core.skill_loader import (
    discover_skills,
    parse_frontmatter,
    SkillRegistry,
)


def _mk_skill(folder, body, md_name="SKILL.md"):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / md_name).write_text(body, encoding="utf-8")
    return folder


GOOD = """---
name: {name}
description: {desc}
---

# Thing

1. Do the thing.
2. Verify the thing.
"""


# ── frontmatter ─────────────────────────────────────────────────────────────

def test_frontmatter_plain_and_quoted():
    fm, body = parse_frontmatter(
        '---\nname: my-skill\ndescription: "Does stuff: when asked"\n---\n\nBody here')
    assert fm["name"] == "my-skill"
    assert fm["description"] == "Does stuff: when asked"
    assert body == "Body here"


def test_frontmatter_multiline_block():
    fm, body = parse_frontmatter(
        "---\nname: s\ndescription: |\n  line one\n  line two\n---\nbody")
    # literal block keeps its line breaks
    assert fm["description"] == "line one\nline two"
    assert body == "body"


def test_frontmatter_absent_returns_whole_text():
    fm, body = parse_frontmatter("# just markdown\n")
    assert fm == {} and body == "# just markdown\n"


# ── discovery & spec validation ─────────────────────────────────────────────

def test_discover_valid_and_skips(tmp_path):
    _mk_skill(tmp_path / "alpha", GOOD.format(name="alpha", desc="A thing"))
    _mk_skill(tmp_path / "_template", GOOD.format(name="_template", desc="x"))
    (tmp_path / "no-md-folder").mkdir()               # no SKILL.md
    _mk_skill(tmp_path / "no-desc", "---\nname: no-desc\n---\nbody")  # invalid
    logs = []
    reg = discover_skills(tmp_path, logger=logs.append)
    assert reg.names() == {"alpha"}
    assert not any("_template" in ln and "rejected" in ln for ln in logs)
    assert any("rejected" in ln and "no-desc" in ln for ln in logs)
    assert any("discovery complete: 1 active" in ln for ln in logs)


def test_name_must_match_folder(tmp_path):
    _mk_skill(tmp_path / "real-folder", GOOD.format(name="other", desc="d"))
    reg = discover_skills(tmp_path, logger=lambda m: None)
    assert reg.names() == set()


def test_registry_read_body_and_resource(tmp_path):
    f = _mk_skill(tmp_path / "alpha", GOOD.format(name="alpha", desc="A thing"))
    (f / "references").mkdir()
    (f / "references" / "extra.md").write_text("deeper detail", encoding="utf-8")
    reg = discover_skills(tmp_path, logger=lambda m: None)
    body = reg.read("alpha")
    assert "Do the thing." in body
    assert not body.startswith("---")         # frontmatter not re-sent
    assert reg.read("alpha", "references/extra.md") == "deeper detail"


def test_manifest_verifies_resources_and_permissions(tmp_path):
    folder = _mk_skill(tmp_path / "safe", GOOD.format(name="safe", desc="Safe manifest"))
    (folder / "scripts").mkdir()
    script = folder / "scripts" / "run.py"
    script.write_text("print('safe')", encoding="utf-8")
    digest = hashlib.sha256(script.read_bytes()).hexdigest()
    (folder / "skill.json").write_text(json.dumps({"version": 1, "permissions": ["read_resources", "shell"], "resources": {"scripts/run.py": digest}}), encoding="utf-8")
    reg = discover_skills(tmp_path, logger=lambda _msg: None)
    assert reg.read("safe", "scripts\\run.py") == "print('safe')"


def test_manifest_rejects_tampering_and_undeclared_access(tmp_path):
    folder = _mk_skill(tmp_path / "safe", GOOD.format(name="safe", desc="Safe manifest"))
    (folder / "note.txt").write_text("private", encoding="utf-8")
    (folder / "skill.json").write_text(json.dumps({"version": 1, "permissions": ["read_resources"], "resources": {"note.txt": "0" * 64}}), encoding="utf-8")
    assert discover_skills(tmp_path, logger=lambda _msg: None).names() == set()


def test_manifest_rejects_unknown_capability(tmp_path):
    folder = _mk_skill(tmp_path / "unsafe", GOOD.format(name="unsafe", desc="Unsafe manifest"))
    (folder / "skill.json").write_text(json.dumps({"version": 1, "permissions": ["disable-safety"], "resources": {}}), encoding="utf-8")
    assert discover_skills(tmp_path, logger=lambda _msg: None).names() == set()


def test_read_unknown_skill_raises(tmp_path):
    reg = discover_skills(tmp_path, logger=lambda m: None)
    try:
        reg.read("ghost")
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "no skill named" in str(e).lower()


def test_path_traversal_blocked(tmp_path):
    f = _mk_skill(tmp_path / "alpha", GOOD.format(name="alpha", desc="d"))
    (tmp_path / "secret.txt").write_text("top secret", encoding="utf-8")
    reg = discover_skills(tmp_path, logger=lambda m: None)
    for evil in ("../secret.txt", "..", "/etc/passwd", "references/../../x"):
        try:
            reg.read("alpha", evil)
            raise AssertionError(f"expected ValueError for {evil!r}")
        except ValueError:
            pass


def test_listing_progressive_disclosure(tmp_path):
    _mk_skill(tmp_path / "alpha", GOOD.format(name="alpha", desc="A thing " + "x" * 400))
    reg = discover_skills(tmp_path, logger=lambda m: None)
    listing = reg.get_listing()
    assert "- alpha: A thing" in listing
    assert "x" * 400 not in listing            # truncated in the prompt block
    assert SkillRegistry({}, {}).get_listing().startswith("(No skills")


def test_empty_skill_dir_never_raises(tmp_path):
    reg = discover_skills(tmp_path / "does-not-exist-yet", logger=lambda m: None)
    assert len(reg) == 0


# ── wiring in main.py / prompt.txt ──────────────────────────────────────────

def test_main_wires_skills_layer():
    m = pathlib.Path("main.py").read_text(encoding="utf-8")
    assert "from core.skill_loader         import discover_skills" in m
    assert "self._skill_registry = discover_skills(" in m
    assert '"name": "skill_read"' in m
    assert 'args.get("path") or None' in m        # executor branch
    assert '"skills": self._skill_registry.get_listing()' in m
    p = pathlib.Path("core/prompt.txt").read_text(encoding="utf-8")
    assert "[SKILLS]" in p and "{skills}" in p
    assert "call skill_read with that name BEFORE" in p


def test_bundled_skills_are_discoverable():
    """Ship-with skills (deep-research, _template) parse under real rules."""
    reg = discover_skills(pathlib.Path("skills"), logger=lambda m: None)
    assert "deep-research" in reg.names()
    assert "_template" not in reg.names()        # underscore folders skipped
    body = reg.read("deep-research")
    assert "## Procedure" in body
    assert "source" in body.lower() and "search" in body.lower()
    assert "- deep-research:" in reg.get_listing()
