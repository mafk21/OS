"""
Tasks tool — voice: "add task buy milk tomorrow high", "list tasks", "complete task 3", etc.
"""

def manage_tasks(parameters: dict, player=None, session_memory=None, **_):
    import memory.productivity as prod
    action = str(parameters.get("action", "list")).strip().lower()
    try:
        if action in ("add", "create"):
            title = str(parameters.get("title") or parameters.get("task") or parameters.get("text") or "").strip()
            if not title:
                return "Tell me the task title — e.g. 'add task buy milk'"
            res = prod.add_task(
                title=title,
                due=str(parameters.get("due", "")),
                priority=str(parameters.get("priority", "normal")),
                description=str(parameters.get("description", "")),
            )
            if player: player.write_log(f"[Tasks] + #{res['id']} {title}")
            return f"Task #{res['id']} added: {title} ({res['priority']})" + (f" due {res['due']}" if res.get("due") else "")
        elif action == "list":
            status = str(parameters.get("status", "open"))
            page = int(parameters.get("page", 1))
            data = prod.list_tasks(status=status, page=page)
            if not data["tasks"]:
                return f"No {status} tasks — page {page}."
            lines = [f"Tasks ({data['total']} total, page {data['page']}/{data['pages']}):"]
            for t in data["tasks"]:
                due = f" due {t['due']}" if t.get("due") else ""
                lines.append(f"  #{t['id']} [{t['status']}/{t['priority']}] {t['title']}{due}")
            if player:
                player.show_content(f"TASKS — {status}", "\n".join(lines))
            return "\n".join(lines)
        elif action == "search":
            q = str(parameters.get("query") or parameters.get("title") or "")
            data = prod.search_tasks(q)
            if not data["tasks"]:
                return f"No tasks matching '{q}'."
            return "\n".join(f"#{t['id']} [{t['status']}] {t['title']}" for t in data["tasks"])
        elif action in ("complete", "done", "finish"):
            tid = int(parameters.get("id") or parameters.get("task_id") or 0)
            if not tid: return "Which task id to complete? e.g. 'complete task 3'"
            return prod.complete_task(tid)
        elif action in ("reopen", "undo"):
            tid = int(parameters.get("id") or parameters.get("task_id") or 0)
            return prod.reopen_task(tid)
        elif action in ("archive",):
            tid = int(parameters.get("id") or 0)
            return prod.archive_task(tid, True)
        elif action in ("restore",):
            tid = int(parameters.get("id") or 0)
            return prod.archive_task(tid, False)
        elif action in ("delete", "remove"):
            tid = int(parameters.get("id") or 0)
            return prod.delete_task(tid)
        else:
            return "Actions: add/list/search/complete/reopen/archive/restore/delete. Example: add task 'Buy milk' due tomorrow."
    except Exception as e:
        return f"Tasks error: {e}"

TOOL = {
    "name": "manage_tasks",
    "description": "Manage to-do tasks: add/list/search/complete/reopen/archive/restore/delete. Use when user says add task, list tasks, complete task, show my tasks, etc.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "add|list|search|complete|reopen|archive|restore|delete"},
            "title": {"type": "STRING", "description": "Task title for add/search"},
            "task": {"type": "STRING", "description": "Alias for title"},
            "description": {"type": "STRING"},
            "due": {"type": "STRING", "description": "Due date/time free text e.g. tomorrow 5pm"},
            "priority": {"type": "STRING", "description": "low|normal|high|urgent"},
            "status": {"type": "STRING", "description": "open|done|all filter for list"},
            "query": {"type": "STRING", "description": "Search query"},
            "id": {"type": "NUMBER", "description": "Task id for complete/reopen/archive/delete"},
            "task_id": {"type": "NUMBER", "description": "Alias for id"},
            "page": {"type": "NUMBER", "description": "Page number for list pagination (20/page)"},
        },
        "required": ["action"]
    },
    "handler": manage_tasks,
}
