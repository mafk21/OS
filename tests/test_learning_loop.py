"""Tests — learning loop (Phase 9): skill_manage + self-authoring registry.

The loop's contract: whatever the model writes through skill_manage must
validate under the SAME rules as discovery (survives restart), take effect
immediately for skill_read, and be gated by prompt + hint wiring in main.py.
"""
import pathlib

from core.skill_loader import discover_skills


BODY = """## Instructions

1. Step one.
2. Step two.

## Pitfalls

- Watch out.

## Verification

- Confirm result.
"""


def _reg(tmp_path):
    return discover_skills(tmp_path, logger=lambda m: None)


# ── authoring ───────────────────────────────────────────────────────────────

def test_create_then_read_immediately(tmp_path):
    reg = _reg(tmp_path)
    msg = reg.write("weekly-report", "Weekly report: when asked for a status digest",
                    BODY)
    assert "created" in msg and "weekly-report" in msg
    # registered in-session — no rediscovery needed
    assert "weekly-report" in reg.names()
    assert "Step one." in reg.read("weekly-report")
    assert "- weekly-report:" in reg.get_listing()


def test_written_skill_survives_restart(tmp_path):
    reg = _reg(tmp_path)
    reg.write("weekly-report", "When asked for the weekly digest", BODY)
    reg2 = _reg(tmp_path)                      # fresh discovery, as at boot
    assert "weekly-report" in reg2.names()
    fm_text = (tmp_path / "weekly-report" / "SKILL.md").read_text(encoding="utf-8")
    assert fm_text.startswith("---\nname: weekly-report\n")
    assert "## Instructions" in fm_text


def test_create_refuses_duplicate_update_replaces(tmp_path):
    reg = _reg(tmp_path)
    reg.write("s1", "First skill description", BODY)
    try:
        reg.write("s1", "x", BODY)
        raise AssertionError("duplicate create must fail")
    except ValueError as e:
        assert "already exists" in str(e)
    msg = reg.write("s1", "Improved trigger line", BODY + "\nNew step.", update=True)
    assert "updated" in msg
    assert "New step." in reg.read("s1")
    assert "Improved trigger line" in reg.get_listing()


def test_update_without_existing_skill_fails(tmp_path):
    reg = _reg(tmp_path)
    try:
        reg.write("ghost", "d", BODY, update=True)
        raise AssertionError("update of nothing must fail")
    except ValueError as e:
        assert "no skill" in str(e).lower()


def test_write_validation_matches_spec(tmp_path):
    reg = _reg(tmp_path)
    bad_calls = [
        dict(name="Bad Name", description="d", body=BODY),      # uppercase/space
        dict(name="ok-name", description="", body=BODY),        # missing trigger
        dict(name="ok-name", description="d", body="   "),      # empty body
    ]
    for kwargs in bad_calls:
        try:
            reg.write(**kwargs)
            raise AssertionError(f"expected ValueError for {kwargs}")
        except ValueError:
            pass
    assert reg.names() == set()


def test_write_flattens_multiline_description(tmp_path):
    reg = _reg(tmp_path)
    reg.write("s1", "line one\nline two", BODY)
    fm_head = (tmp_path / "s1" / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    assert "line one line two" in fm_head       # single line in frontmatter


# ── wiring in main.py / prompt.txt ──────────────────────────────────────────

def test_main_wires_learning_loop():
    m = pathlib.Path("main.py").read_text(encoding="utf-8")
    assert '"name": "skill_manage"' in m
    assert "self._skill_registry.write(" in m
    # census + once-per-process hint attached to the shared FunctionResponse
    assert "self._skill_window_tools" in m
    assert '_resp["learning_hint"]' in m
    assert "not self._skill_hinted" in m
    assert 'print(f"[Skills] 💡 learning hint' in m
    p = pathlib.Path("core/prompt.txt").read_text(encoding="utf-8")
    assert "[LEARNING]" in p
    assert "skill_manage" in p
    assert "never become skills" in p
