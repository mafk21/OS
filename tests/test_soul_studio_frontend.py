"""Phase 12 Soul Studio frontend contract tests.

The UI has no browser-test dependency, so these tests pin its API wiring and
all required views/states while the production Next build performs type/JSX
validation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = (ROOT / "apex_ui/components/SoulStudioPanel.tsx").read_text(encoding="utf-8")
MODAL = (ROOT / "apex_ui/components/StudioModal.tsx").read_text(encoding="utf-8")


def test_soul_studio_is_reachable_without_replacing_existing_studio_tabs():
    assert 'import SoulStudioPanel from "./SoulStudioPanel"' in MODAL
    assert '<SoulStudioPanel primary={PRIMARY} secondary={SECONDARY} />' in MODAL
    for tab in ("soul", "companions", "interview", "skills", "themes"):
        assert f'id: "{tab}"' in MODAL


def test_soul_studio_has_all_eight_separate_views():
    for view in ("identity", "affect", "relationship", "commitments", "initiative", "traits", "history", "privacy"):
        assert f'id: "{view}"' in PANEL
        assert f'view === "{view}"' in PANEL


def test_soul_studio_handles_loading_empty_error_conflict_and_recovery():
    for marker in (
        "LOADING SOUL STATE", "Soul state unavailable", "No active projected commitments",
        "No evidence-backed relationship claims yet", "No learned traits", "No Soul mutations recorded",
        "Soul changed elsewhere. Reloaded the latest revision.", "soul.recovery", "soul.degraded", "RETRY",
    ):
        assert marker in PANEL


def test_soul_studio_exposes_revision_safe_controls_and_context_preview():
    assert "expected_revision: soul?.revision" in PANEL
    for operation in ("identity", "initiative", "privacy", "trait", "forget_relationship", "undo", "reset", "runtime"):
        assert f'operation:"{operation}"' in PANEL or f'operation: "{operation}"' in PANEL
    assert "/api/hud/soul/export" in PANEL
    assert "CANONICAL CONTEXT PREVIEW" in PANEL
    assert "SOUL DIAGNOSTICS" in PANEL
    for diagnostic in ("last_successful_save", "last_backup", "last_reflection", "context_size", "completed_migrations"):
        assert diagnostic in PANEL
