"""
actions/brain_control.py — Direct voice & tool interface to JARVIS's Brain & Forever Timeline.

Lets JARVIS search, store, forget, ingest local files into the Brain, and browse
past conversation history or generated outputs across both Male and Female editions.
"""

from __future__ import annotations

from actions.file_controller import _resolve_path
from memory import memory_manager as mm
from memory import timeline as tl


def brain_control(parameters: dict, player=None, **_kwargs) -> str:
    params = parameters or {}
    action = str(params.get("action") or "search").strip().lower()

    if action == "search":
        q = str(params.get("query") or "").strip()
        out = tl.unified_brain_search(q, limit=int(params.get("limit") or 8))
        if player and q:
            player.show_content(f"BRAIN RECALL — {q}", out)
        return out

    if action == "remember":
        key = str(params.get("key") or "").strip()
        val = str(params.get("value") or params.get("content") or "").strip()
        cat = str(params.get("category") or "notes").strip().lower()
        if not key or not val:
            return "Provide both 'key' and 'value' to store in the Brain."
        return mm.remember(key, val, category=cat)

    if action == "forget":
        key = str(params.get("key") or "").strip()
        cat = str(params.get("category") or "notes").strip().lower()
        if not key:
            return "Provide 'key' (and optional 'category') to forget."
        return mm.forget(key, category=cat)

    if action == "ingest_file":
        fp_str = str(params.get("file_path") or "").strip()
        note_text = str(params.get("content") or "").strip()
        title = str(params.get("title") or "brain_note.md").strip()
        if fp_str:
            fp = _resolve_path(fp_str)
            if not fp.exists() or not fp.is_file():
                return f"File not found: {fp}"
            rec = tl.ingest_knowledge_file(fp.name, fp.read_bytes())
            return (
                f"Added '{rec['filename']}' to the Brain "
                f"({rec['chunk_count']} searchable chunk(s))."
            )
        if note_text:
            fname = title if "." in title else f"{title}.md"
            rec = tl.ingest_knowledge_file(fname, note_text)
            return f"Saved note '{rec['filename']}' into the Brain ({rec['chunk_count']} chunk(s))."
        return "Provide 'file_path' or 'content' to add to the Brain."

    if action == "timeline":
        q = str(params.get("query") or "").strip()
        ch = str(params.get("channel") or "").strip()
        rows = tl.search_timeline(q, limit=int(params.get("limit") or 12), channel=ch)
        if not rows:
            return "No matching Forever Timeline messages found."
        lines = ["Forever Timeline:"]
        for r in rows:
            lines.append(
                f"  • [{r['created_at']} · {r['channel']}] {r['speaker']}: {r['content'][:220]}"
            )
        return "\n".join(lines)

    if action == "outputs":
        q = str(params.get("query") or "").strip()
        outs = tl.list_outputs(q, limit=int(params.get("limit") or 10))
        if not outs:
            return "No saved outputs found in the Brain."
        lines = ["Saved Brain Outputs:"]
        for o in outs:
            pin = "📌 " if o.get("pinned") else ""
            lines.append(f"  • {pin}[id={o['id']}] {o['title']} ({o['created_at']})")
        return "\n".join(lines)

    return (
        f"Unknown action '{action}'. Available: search, remember, forget, "
        "ingest_file, timeline, outputs."
    )


TOOL = {
    "name": "brain_control",
    "description": (
        "Access JARVIS's unified Brain & Forever Timeline: search across personal "
        "memories, uploaded knowledge files, past voice/text/Telegram conversations, "
        "and generated reports; remember or forget facts; or ingest local files/notes "
        "into the Brain. Actions: search | remember | forget | ingest_file | timeline | outputs."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "search | remember | forget | ingest_file | timeline | outputs",
            },
            "query": {"type": "STRING", "description": "Search query across Brain & Timeline"},
            "category": {
                "type": "STRING",
                "description": "Memory category: identity | preferences | projects | relationships | wishes | notes",
            },
            "key": {"type": "STRING", "description": "Memory key for remember/forget"},
            "value": {"type": "STRING", "description": "Memory value to store"},
            "file_path": {"type": "STRING", "description": "Local file path to ingest into Brain"},
            "title": {"type": "STRING", "description": "Title for a saved Brain note"},
            "content": {"type": "STRING", "description": "Text content for a Brain note"},
            "channel": {"type": "STRING", "description": "Optional timeline channel filter: voice | text | telegram"},
            "limit": {"type": "INTEGER", "description": "Max results"},
        },
        "required": ["action"],
    },
    "handler": brain_control,
}
