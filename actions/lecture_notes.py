def manage_lecture(parameters: dict, player=None, **_):
    import memory.productivity as prod
    action=str(parameters.get("action","start")).strip().lower()
    try:
        if action=="start":
            title=str(parameters.get("title") or parameters.get("topic") or "Lecture")
            res=prod.lecture_start(title)
            if player:
                player.write_log(f"[Lecture] Started — {res['file']}")
                player.set_state("PROCESSING")
            return f"Lecture capture started: '{title}'. Speak or type notes — they will be appended. Say 'stop lecture' when done."
        elif action=="append":
            text=str(parameters.get("text") or parameters.get("content") or "")
            if not text: return "No text to append."
            prod.lecture_append(text)
            return "Appended."
        elif action=="status":
            s=prod.lecture_status()
            return f"Lecture {'active: '+s['file']+' '+str(s.get('chars'))+' chars' if s.get('active') else 'not active'}"
        elif action in ("stop","finish","end","summarize"):
            summ=bool(parameters.get("summarize", True))
            res=prod.lecture_stop(summarize=summ)
            if "error" in res: return res["error"]
            msg=f"Lecture saved: {res['file']} ({res['transcript_chars']} chars)"
            if res.get("summary"):
                msg+=f"\n\nSummary:\n{res['summary']}"
                if res.get("note_id"): msg+=f"\nNote #{res['note_id']} created."
            if player:
                player.write_log(f"[Lecture] Stopped — {res['file']}")
                if res.get("summary"): player.show_content("LECTURE SUMMARY", res["summary"])
            return msg
        else: return "Actions: start/append/status/stop"
    except Exception as e: return f"Lecture error: {e}"

TOOL={"name":"manage_lecture","description":"Lecture Notes: continuous capture → live transcribe → summary on stop. Actions: start (title), append (text), status, stop (summarize). Use when user says 'start lecture notes', 'stop the notes'.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"start|append|status|stop"},"title":{"type":"STRING"},"topic":{"type":"STRING"},"text":{"type":"STRING","description":"Text to append in append action"},"content":{"type":"STRING"},"summarize":{"type":"BOOLEAN","description":"Whether to summarize on stop (default true)"}},"required":["action"]},"handler":manage_lecture}
