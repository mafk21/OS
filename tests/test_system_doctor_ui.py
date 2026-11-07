from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODAL = (ROOT / "apex_ui" / "components" / "SystemDoctorModal.tsx").read_text(encoding="utf-8")
OVERLAYS = (ROOT / "apex_ui" / "components" / "JarvisHudOverlays.tsx").read_text(encoding="utf-8")
CLASSIC = (ROOT / "ui.py").read_text(encoding="utf-8")


def test_apex_health_center_exposes_identity_evidence_and_states():
    for token in (
        "installation_id", "install_type", "revision", "Python", "platform",
        "Evidence:", "Recommendation:", "healthy", "degraded", "unavailable",
        "not_configured",
    ):
        assert token in MODAL


def test_apex_health_center_has_accessible_controls_and_redacted_export():
    assert 'role="dialog"' in MODAL
    assert 'aria-modal="true"' in MODAL
    assert 'aria-label="JARVIS System Doctor"' in MODAL
    assert 'aria-live="polite"' in MODAL
    assert "Export redacted report" in MODAL
    assert 'event.key === "Escape"' in MODAL
    assert "maxHeight" in MODAL and "overflow" in MODAL
    assert "Make this installation active" in MODAL
    assert "Unregister this metadata" in MODAL
    assert "Unregister obsolete metadata" in MODAL
    assert 'action: "installation_lifecycle"' in MODAL


def test_repairs_are_staged_not_executed_by_frontend():
    assert 'operation: "repair"' in MODAL
    assert "Stage verified repair" in MODAL
    assert "confirmed" not in MODAL.lower()
    assert "SYSTEM DOCTOR" in OVERLAYS


def test_classic_ui_has_health_and_report_parity():
    assert "def _run_system_doctor" in CLASSIC
    assert 'diagnostics_check({"action": "system"})' in CLASSIC
    assert "def _export_system_doctor_report" in CLASSIC
    assert "EXPORT REDACTED HEALTH REPORT" in CLASSIC
    assert "desktop_shortcut.create()" in CLASSIC
    assert "desktop_shortcut.verify()" in CLASSIC
    assert "pythonw" not in CLASSIC[CLASSIC.index("def _create_desktop_shortcut"):CLASSIC.index("def _run_system_doctor")]
