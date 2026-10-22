"""Tests — GWS Pack (Phase 12): Google Workspace automation via computer_use."""
from core.gws_pack import gws_pack, TOOL, GWS_URLS, _open_app_url


# ── Constants ─────────────────────────────────────────────────────────────

def test_gws_urls():
    assert "gmail" in GWS_URLS
    assert "docs" in GWS_URLS
    assert "drive" in GWS_URLS
    assert "calendar" in GWS_URLS
    assert "mail.google.com" in GWS_URLS["gmail"]


def test_open_app_url():
    assert "mail.google.com" in _open_app_url("gmail")
    assert "docs.google.com" in _open_app_url("docs")
    assert "drive.google.com" in _open_app_url("drive")
    assert "calendar.google.com" in _open_app_url("calendar")
    # Unknown app falls back to gmail
    assert "mail.google.com" in _open_app_url("unknown")


# ── Tool declaration ──────────────────────────────────────────────────────

def test_tool_declaration():
    assert TOOL["name"] == "gws_pack"
    assert TOOL["handler"] is gws_pack
    assert TOOL["behavior"] == "NON_BLOCKING"
    assert TOOL["scheduling"] == "WHEN_IDLE"
    assert TOOL["parameters"]["required"] == ["action"]
    props = TOOL["parameters"]["properties"]
    for key in ("action", "to", "subject", "body", "query", "title",
                "content", "file_path", "when", "description", "app", "name"):
        assert key in props
    assert "gmail" in TOOL["description"]
    assert "docs" in TOOL["description"]
    assert "drive" in TOOL["description"]
    assert "calendar" in TOOL["description"]


# ── Tool actions ──────────────────────────────────────────────────────────

def test_gws_open():
    result = gws_pack({"action": "gws_open", "app": "gmail"})
    assert "Gmail" in result or "gmail" in result
    assert "mail.google.com" in result


def test_gws_open_unknown_app():
    result = gws_pack({"action": "gws_open", "app": "nonexistent"})
    assert "mail.google.com" in result  # falls back to gmail URL


def test_gmail_send():
    result = gws_pack({"action": "gmail_send",
                       "to": "alice@example.com",
                       "subject": "Hello",
                       "body": "Meeting at 3pm"})
    assert "alice@example.com" in result
    assert "Hello" in result


def test_gmail_send_minimal():
    result = gws_pack({"action": "gmail_send", "to": "bob@example.com"})
    assert "bob@example.com" in result


def test_gmail_search():
    result = gws_pack({"action": "gmail_search", "query": "invoice"})
    assert "invoice" in result


def test_docs_create():
    result = gws_pack({"action": "docs_create", "title": "Project Plan"})
    assert "Project Plan" in result


def test_docs_write():
    result = gws_pack({"action": "docs_write", "content": "Draft content here"})
    assert "wrote" in result
    assert "characters" in result


def test_docs_write_via_body():
    result = gws_pack({"action": "docs_write", "body": "via body param"})
    assert "wrote" in result


def test_drive_upload():
    result = gws_pack({"action": "drive_upload", "file_path": "/tmp/report.pdf"})
    assert "report.pdf" in result


def test_drive_upload_missing_file():
    result = gws_pack({"action": "drive_upload", "file_path": "/nonexistent/file.pdf"})
    assert "not found" in result.lower()


def test_calendar_add():
    result = gws_pack({"action": "calendar_add",
                       "title": "Team Sync",
                       "when": "tomorrow 3pm",
                       "description": "Weekly sync"})
    assert "Team Sync" in result
    assert "tomorrow 3pm" in result


def test_workflow_known():
    result = gws_pack({"action": "workflow", "name": "send_meeting_notes"})
    assert "send_meeting_notes" in result
    assert "docs_create" in result or "docs" in result.lower()


def test_workflow_unknown():
    result = gws_pack({"action": "workflow", "name": "bogus"})
    assert "unknown" in result.lower()
    assert "send_meeting_notes" in result


def test_unknown_action():
    result = gws_pack({"action": "bogus"})
    assert "unknown action" in result.lower()


def test_no_action():
    result = gws_pack({})
    assert "unknown action" in result.lower()
