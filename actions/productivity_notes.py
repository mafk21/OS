def manage_notes(parameters: dict, player=None, **_):
    import memory.productivity as prod
    action = str(parameters.get("action","list")).strip().lower()
    try:
        if action in ("add","create","save"):
            title = str(parameters.get("title") or "").strip()
            content = str(parameters.get("content") or parameters.get("text") or parameters.get("note") or "").strip()
            if not content: return "Tell me what to save — e.g. 'add note Shopping list: milk, eggs'"
            tags = str(parameters.get("tags",""))
            res = prod.add_note(title or content[:40], content, tags)
            if player: player.write_log(f"[Notes] + #{res['id']} {res['title']}")
            return f"Note #{res['id']} saved: {res['title']}"
        elif action == "list":
            page = int(parameters.get("page",1))
            inc = bool(parameters.get("include_archived", False))
            data = prod.list_notes(include_archived=inc, page=page)
            if not data["notes"]: return "No notes yet."
            lines=[f"Notes ({data['total']} total, page {data['page']}/{data['pages']}):"]
            for n in data["notes"]:
                lines.append(f"  #{n['id']} {n['title']} — {n['content'][:60]}")
            if player: player.show_content("NOTES", "\n".join(lines))
            return "\n".join(lines)
        elif action == "search":
            q=str(parameters.get("query") or parameters.get("title") or "")
            data=prod.search_notes(q)
            if not data["notes"]: return f"No notes matching '{q}'."
            return "\n".join(f"#{n['id']} {n['title']}: {n['content'][:80]}" for n in data["notes"])
        elif action == "get":
            nid=int(parameters.get("id") or 0)
            if not nid: return "Which note id?"
            n=prod.get_note(nid)
            return f"#{n['id']} {n['title']}\n{n['content']}" if n else f"Note {nid} not found."
        elif action == "archive":
            nid=int(parameters.get("id") or 0); return prod.archive_note(nid, True)
        elif action == "restore":
            nid=int(parameters.get("id") or 0); return prod.archive_note(nid, False)
        elif action in ("delete","remove"):
            nid=int(parameters.get("id") or 0); return prod.delete_note(nid)
        else: return "Actions: add/list/search/get/archive/restore/delete"
    except Exception as e: return f"Notes error: {e}"

TOOL={"name":"manage_notes","description":"Manage notes: add/list/search/get/archive/restore/delete. Use when user says add note, save note, list notes, search notes, etc.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"add|list|search|get|archive|restore|delete"},"title":{"type":"STRING"},"content":{"type":"STRING","description":"Note body"},"text":{"type":"STRING"},"note":{"type":"STRING"},"tags":{"type":"STRING"},"query":{"type":"STRING"},"id":{"type":"NUMBER"},"page":{"type":"NUMBER"},"include_archived":{"type":"BOOLEAN"}},"required":["action"]},"handler":manage_notes}
