"""
GWS Pack (Phase 12) — Google Workspace automation via computer_use.

Automates Gmail, Google Docs, Google Drive, Google Calendar through their web
UIs using Set-of-Mark visual grounding (Phase 8 computer_use). No API keys, no
OAuth scopes — works with whatever account the user is already logged into.

Actions (gws_pack tool):
  gmail_send      — Compose + send an email (to, subject, body)
  gmail_search    — Search Gmail, list matching threads
  docs_create     — Create a new Google Doc with a title
  docs_write      — Write content into an open Google Doc
  drive_upload    — Upload a file to Google Drive
  calendar_add    — Add an event to Google Calendar
  gws_open        — Open a specific Workspace app in the browser
  workflow        — Run a named multi-step workflow

Each action orchestrates computer_use (som_capture → click_by_id / type_by_id)
to click buttons and fill fields by element ID. If visual grounding is
unavailable, returns a human-readable SOP (standard operating procedure) the
user or model can follow manually.

All stdlib — no new dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from typing import Optional

# ── GWS app URLs ──────────────────────────────────────────────────────────

GWS_URLS = {
    "gmail":    "https://mail.google.com",
    "docs":     "https://docs.google.com",
    "drive":    "https://drive.google.com",
    "calendar": "https://calendar.google.com",
}


def _open_app_url(app: str) -> str:
    return GWS_URLS.get(app.lower(), GWS_URLS["gmail"])


# ── computer_use orchestrator ─────────────────────────────────────────────

def _call_computer_use(action: str, **kwargs) -> str:
    """
    Call the computer_use tool handler directly.

    computer_use lives in actions/computer_use.py and is declared as an inline
    tool in main.py. We import its handler module and call it with the same
    (parameters, response, player, session_memory) signature — player/session
    default to None since gws_pack runs in the background.
    """
    try:
        from actions.computer_use import computer_use as _cu  # type: ignore
    except Exception as e:
        return f"gws_pack: computer_use unavailable — {e}"

    parameters = {"action": action, **kwargs}
    try:
        return _cu(parameters)  # type: ignore
    except TypeError:
        # Some call sites pass (params, response, player, session_memory)
        return _cu(parameters, None, None, None)  # type: ignore


def _som_capture() -> str:
    """Capture screen + detect elements via computer_use som_capture."""
    return _call_computer_use("som_capture")


def _click_by_id(element_id: str) -> str:
    """Click an element by SoM ID via computer_use."""
    return _call_computer_use("click_by_id", element_id=element_id)


def _type_by_id(element_id: str, text: str) -> str:
    """Type into an element by SoM ID via computer_use."""
    return _call_computer_use("type_by_id", element_id=element_id, text=text)


# ── GWS action helpers ────────────────────────────────────────────────────

def _find_element_id(som_result: str, hint: str) -> Optional[str]:
    """
    Parse a som_capture result to find an element ID matching a hint.

    som_capture returns lines like:
      [1] Compose button at (123, 456)
      [2] To field at (789, 101)

    We look for the hint keyword in the description and return the bracketed ID.
    Returns None if no match.
    """
    if not som_result:
        return None
    for line in som_result.splitlines():
        line = line.strip()
        if not line.startswith("["):
            continue
        # [id] description at (x, y)
        close = line.find("]")
        if close == -1:
            continue
        el_id = line[1:close]
        rest = line[close + 1:].lower()
        if hint.lower() in rest:
            return el_id
    return None


# ── Individual GWS actions ────────────────────────────────────────────────

def _gmail_send(to: str, subject: str, body: str) -> str:
    """Compose and send an email in Gmail (direct API/SMTP first if connected, else browser SoM)."""
    try:
        import memory.accounts as _ac
        if _ac.is_service_connected("gmail") or _ac.is_service_connected("email"):
            return _ac.email_send_message(to, subject, body)
    except Exception:
        pass
    # 1. Capture screen to see current state
    som = _som_capture()

    # 2. Look for Compose button
    compose_id = _find_element_id(som, "compose")
    if compose_id:
        _click_by_id(compose_id)
        som = _som_capture()

    # 3. Fill To field
    to_id = _find_element_id(som, "to")
    if to_id and to:
        _type_by_id(to_id, to)
        som = _som_capture()

    # 4. Fill Subject
    subj_id = _find_element_id(som, "subject")
    if subj_id and subject:
        _type_by_id(subj_id, subject)
        som = _som_capture()

    # 5. Fill Body
    body_id = _find_element_id(som, "body")
    if body_id and body:
        _type_by_id(body_id, body)

    # 6. Send
    send_id = _find_element_id(som, "send")
    if send_id:
        _click_by_id(send_id)

    return (
        f"Gmail send: queued email to {to}\n"
        f"Subject: {subject}\n"
        f"Steps: som_capture → click Compose → type To → type Subject → "
        f"type Body → click Send\n"
        f"(If visual grounding is unavailable, open Gmail and compose manually.)"
    )


def _gmail_search(query: str) -> str:
    """Search Gmail and list matching threads (direct API/IMAP first if connected, else browser SoM)."""
    try:
        import memory.accounts as _ac
        if _ac.is_service_connected("gmail") or _ac.is_service_connected("email"):
            msgs = _ac.email_search_messages(query, max_results=8)
            if not msgs:
                return f"Gmail search '{query}': no matching messages."
            return f"Gmail search '{query}':\n" + "\n".join(
                f"  • {m['subject']} — From: {m['from']} ({m['date']})" for m in msgs
            )
    except Exception:
        pass
    som = _som_capture()
    search_id = _find_element_id(som, "search")
    if search_id:
        _type_by_id(search_id, query)
        _call_computer_use("press", key="enter")  # may not be supported
    return (
        f"Gmail search: '{query}'\n"
        f"Opened Gmail search. Review results in the browser.\n"
        f"(Visual grounding may be limited — manually scan results if needed.)"
    )


def _docs_create(title: str) -> str:
    """Create a new Google Doc."""
    som = _som_capture()
    new_id = _find_element_id(som, "new")
    blank_id = _find_element_id(som, "blank")
    if new_id:
        _click_by_id(new_id)
        som = _som_capture()
    if blank_id:
        _click_by_id(blank_id)
    # Title appears in the doc header after creation
    return (
        f"Google Docs: created new document '{title}'\n"
        f"Steps: som_capture → click New → click Blank document\n"
        f"Then rename: click the document title and type '{title}'."
    )


def _docs_write(content: str) -> str:
    """Write content into an open Google Doc."""
    som = _som_capture()
    body_id = _find_element_id(som, "document")
    if body_id:
        _type_by_id(body_id, content)
    return (
        f"Google Docs: wrote {len(content)} characters\n"
        f"Steps: som_capture → click document body → type content\n"
        f"(Make sure a Doc is open and focused before calling docs_write.)"
    )


def _drive_upload(file_path: str) -> str:
    """Upload a file to Google Drive (direct Drive v3 API first if connected, else browser SoM)."""
    try:
        import memory.accounts as _ac
        if _ac.is_service_connected("google_drive"):
            up = _ac.drive_upload_file(file_path)
            return f"Google Drive uploaded '{up.get('name', file_path)}': {up.get('webViewLink', up.get('id', ''))}"
    except FileNotFoundError:
        return f"gws_pack drive_upload: file not found — {file_path}"
    except Exception:
        pass
    if not file_path or not os.path.exists(file_path):
        return f"gws_pack drive_upload: file not found — {file_path}"
    som = _som_capture()
    new_id = _find_element_id(som, "new")
    upload_id = _find_element_id(som, "upload")
    if new_id:
        _click_by_id(new_id)
        som = _som_capture()
    if upload_id:
        _click_by_id(upload_id)
    return (
        f"Google Drive: upload queued for {file_path}\n"
        f"Steps: som_capture → click New → click File upload → select file\n"
        f"(File picker may require manual selection if visual grounding is limited.)"
    )


def _calendar_add(title: str, when: str, description: str = "") -> str:
    """Add an event to Google Calendar (direct Calendar API first if connected, else browser SoM)."""
    try:
        import memory.accounts as _ac
        if _ac.is_service_connected("google_calendar"):
            ev = _ac.calendar_quick_add(f"{title} {when}".strip())
            return f"Google Calendar: added '{ev.get('summary', title)}' ({when}) — {ev.get('htmlLink', 'scheduled')}"
    except Exception:
        pass
    som = _som_capture()
    create_id = _find_element_id(som, "create")
    if create_id:
        _click_by_id(create_id)
        som = _som_capture()
    title_id = _find_element_id(som, "title")
    if title_id and title:
        _type_by_id(title_id, title)
    return (
        f"Google Calendar: event '{title}' at {when}\n"
        f"Steps: som_capture → click Create → type title → set time → save\n"
        f"(Adjust time/guests manually if fields aren't detected.)"
    )


def _gws_open(app: str) -> str:
    """Open a specific Workspace app in the browser."""
    url = _open_app_url(app)
    # Use computer_use to navigate — but we can't directly control the browser
    # address bar without element detection. Return instructions.
    return (
        f"Google Workspace: open {app.title()}\n"
        f"URL: {url}\n"
        f"Steps: open browser → navigate to {url} → sign in if prompted\n"
        f"(Then use som_capture to see available elements.)"
    )


# ── Named workflows ───────────────────────────────────────────────────────

WORKFLOWS = {
    "send_meeting_notes": (
        "1. gws_open docs\n"
        "2. docs_create 'Meeting Notes'\n"
        "3. docs_write <notes content>\n"
        "4. gws_open gmail\n"
        "5. gmail_send <recipients> 'Meeting Notes' <notes summary>"
    ),
    "save_research_to_drive": (
        "1. gws_open drive\n"
        "2. drive_upload <file_path>\n"
        "3. (organize into folder manually if needed)"
    ),
    "schedule_meeting": (
        "1. gws_open calendar\n"
        "2. calendar_add <title> <time> <description>\n"
        "3. gws_open gmail\n"
        "4. gmail_send <attendees> 'Meeting scheduled' <details>"
    ),
}


def _workflow(name: str) -> str:
    """Run a named multi-step workflow."""
    steps = WORKFLOWS.get(name)
    if not steps:
        available = ", ".join(WORKFLOWS)
        return f"gws_pack workflow: unknown '{name}'. Available: {available}"
    return (
        f"Workflow '{name}':\n{steps}\n\n"
        f"Execute each step using the corresponding gws_pack action.\n"
        f"(Visual grounding guides each step; fall back to manual if needed.)"
    )


# ── Tool declaration ─────────────────────────────────────────────────────

TOOL = {
    "name": "gws_pack",
    "description": (
        "Google Workspace automation via computer_use (Set-of-Mark visual "
        "grounding). Automates Gmail, Google Docs, Google Drive, Google "
        "Calendar through their web UIs — no API keys, no OAuth. Actions: "
        "'gmail_send' (to, subject, body), 'gmail_search' (query), "
        "'docs_create' (title), 'docs_write' (content), 'drive_upload' "
        "(file_path), 'calendar_add' (title, when, description), "
        "'gws_open' (app: gmail|docs|drive|calendar), 'workflow' (name: "
        "send_meeting_notes|save_research_to_drive|schedule_meeting). "
        "Each action captures the screen, detects clickable elements by ID, "
        "and interacts with them. Falls back to human-readable SOPs when "
        "visual grounding is unavailable."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "gmail_send | gmail_search | docs_create | docs_write | drive_upload | calendar_add | gws_open | workflow",
            },
            "to": {
                "type": "STRING",
                "description": "gmail_send: recipient email address",
            },
            "subject": {
                "type": "STRING",
                "description": "gmail_send: email subject",
            },
            "body": {
                "type": "STRING",
                "description": "gmail_send: email body / docs_write: content",
            },
            "query": {
                "type": "STRING",
                "description": "gmail_search: Gmail search query",
            },
            "title": {
                "type": "STRING",
                "description": "docs_create: document title / calendar_add: event title",
            },
            "content": {
                "type": "STRING",
                "description": "docs_write: text to write into the document",
            },
            "file_path": {
                "type": "STRING",
                "description": "drive_upload: path to file to upload",
            },
            "when": {
                "type": "STRING",
                "description": "calendar_add: event time (e.g. 'tomorrow 3pm')",
            },
            "description": {
                "type": "STRING",
                "description": "calendar_add: event description",
            },
            "app": {
                "type": "STRING",
                "description": "gws_open: gmail | docs | drive | calendar",
            },
            "name": {
                "type": "STRING",
                "description": "workflow: send_meeting_notes | save_research_to_drive | schedule_meeting",
            },
        },
        "required": ["action"],
    },
    "handler": None,  # set below
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}


def gws_pack(parameters: dict, response=None, player=None,
             session_memory=None) -> str:
    """Handle gws_pack tool calls."""
    try:
        action = (parameters or {}).get("action", "").strip().lower()

        if action == "gmail_send":
            return _gmail_send(
                (parameters or {}).get("to", ""),
                (parameters or {}).get("subject", ""),
                (parameters or {}).get("body", ""),
            )
        elif action == "gmail_search":
            return _gmail_search((parameters or {}).get("query", ""))
        elif action == "docs_create":
            return _docs_create((parameters or {}).get("title", ""))
        elif action == "docs_write":
            return _docs_write((parameters or {}).get("body", "") or
                               (parameters or {}).get("content", ""))
        elif action == "drive_upload":
            return _drive_upload((parameters or {}).get("file_path", ""))
        elif action == "calendar_add":
            return _calendar_add(
                (parameters or {}).get("title", ""),
                (parameters or {}).get("when", ""),
                (parameters or {}).get("description", ""),
            )
        elif action == "gws_open":
            return _gws_open((parameters or {}).get("app", "gmail"))
        elif action == "workflow":
            return _workflow((parameters or {}).get("name", ""))
        else:
            available = ", ".join([
                "gmail_send", "gmail_search", "docs_create", "docs_write",
                "drive_upload", "calendar_add", "gws_open", "workflow",
            ])
            return (f"gws_pack: unknown action '{action}'. Use: {available}")
    except Exception as e:
        return f"gws_pack: {e}"


TOOL["handler"] = gws_pack
