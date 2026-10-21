def manage_routines(parameters: dict, player=None, **_):
    import memory.productivity as prod
    action=str(parameters.get("action","list")).strip().lower()
    try:
        if action in ("add","create","save"):
            name=str(parameters.get("name") or parameters.get("title") or "").strip()
            trigger=str(parameters.get("trigger") or "").strip()
            steps=parameters.get("steps")
            if isinstance(steps,str):
                import json
                try: steps=json.loads(steps)
                except: steps=[steps]
            if not name or not trigger or not steps:
                return "Need name, trigger, and steps. Example: add routine 'Study mode' trigger 'study mode' steps=['close Discord','open notes','50m timer']"
            res=prod.add_routine(name,trigger,steps,str(parameters.get("description","")))
            if player: player.write_log(f"[Routines] + {name} -> {trigger}")
            return f"Routine '{name}' saved for trigger '{trigger}' ({len(steps)} steps)."
        elif action=="list":
            rows=prod.list_routines()
            if not rows: return "No routines yet. Say 'when I say study mode, close Discord...'"
            lines=["Routines:"]
            for r in rows: lines.append(f"  {r['name']} — trigger '{r['trigger']}' — {len(r['steps'])} steps")
            if player: player.show_content("ROUTINES","\n".join(lines))
            return "\n".join(lines)
        elif action=="run":
            trigger=str(parameters.get("trigger") or parameters.get("name") or "").strip()
            r=prod.get_routine_by_trigger(trigger.lower())
            if not r: return f"No routine for trigger '{trigger}'."
            # Execute: steps are textual instructions — delegate to LLM planning via player
            out=[f"Running routine '{r['name']}' ({r['trigger']}):"]
            for i,s in enumerate(r["steps"],1):
                out.append(f"  {i}. {s}")
                # Best-effort: if step mentions open/close apps, try open_app/computer_control via player context
                # We just log for now; full execution can be added when shell/background agent lands in Phase5
            out.append("Routine steps shown — tell me if you want me to execute them.")
            return "\n".join(out)
        elif action in ("delete","remove"):
            name=str(parameters.get("name") or "").strip()
            return prod.delete_routine(name)
        else: return "Actions: add/list/run/delete"
    except Exception as e: return f"Routines error: {e}"

TOOL={"name":"manage_routines","description":"Manage routines: add/list/run/delete. Routines are 'when I say X, do steps...' triggers. Steps are strings like 'close Discord, open notes, 50m timer'.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"add|list|run|delete"},"name":{"type":"STRING","description":"Routine name"},"trigger":{"type":"STRING","description":"Voice trigger phrase lowercased"},"steps":{"type":"ARRAY","items":{"type":"STRING"},"description":"Ordered step strings or JSON array"},"description":{"type":"STRING"}},"required":["action"]},"handler":manage_routines}
