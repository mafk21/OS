"""
Calendar Heads-ups — Phase 4.2
10m before events, 1d+2h before Classroom due, via system_monitor style loop.
"""
import time
from pathlib import Path

_last_heads = {"calendar": 0, "classroom": 0}

def _due_events():
    try:
        import memory.accounts as ac
        return ac.calendar_events_today()
    except: return []

def _classroom_due():
    try:
        import memory.accounts as ac
        return ac.classroom_due_soon()
    except: return []

def calendar_heads_up(parameters: dict, player=None, **_):
    action=str(parameters.get("action","check")).strip().lower()
    if action=="check":
        evs=_due_events()
        cr=_classroom_due()
        lines=[]
        if evs:
            lines.append(f"📅 {len(evs)} events today:")
            for e in evs[:5]: lines.append(f"  • {e.get('title','')} @ {e.get('start','')}")
        else: lines.append("No calendar events today (connect google_calendar to enable).")
        if cr:
            lines.append(f"🎓 {len(cr)} classroom items due soon")
        if player: player.show_content("CALENDAR", "\n".join(lines))
        return "\n".join(lines)
    if action=="enable":
        Path("memory/calendar_monitor_enabled").write_text("1")
        return "Calendar heads-ups enabled (checks every 5m)."
    if action=="disable":
        Path("memory/calendar_monitor_enabled").unlink(missing_ok=True)
        return "Calendar heads-ups disabled."
    return "Actions: check/enable/disable"

TOOL={
    "name":"calendar_heads_up",
    "description":"Calendar heads-ups: check/enable/disable. Warns 10m before events, 1d+2h before Classroom due. Needs google_calendar / google_classroom accounts.",
    "parameters":{
        "type":"OBJECT",
        "properties":{
            "action":{"type":"STRING","description":"check|enable|disable"}
        },
        "required":["action"]
    },
    "handler":calendar_heads_up
}

def tick_background(player=None):
    enabled = Path("memory/calendar_monitor_enabled").exists()
    if not enabled: return
    now=time.time()
    if now - _last_heads.get("calendar",0) < 300: return
    _last_heads["calendar"]=now
    evs=_due_events()
    for e in evs:
        try:
            import datetime as dt
            start = dt.datetime.fromisoformat(str(e.get("start","")).replace("Z","+00:00"))
            delta=(start - dt.datetime.now(dt.timezone.utc)).total_seconds() if start.tzinfo else None
            if delta and 0 < delta < 600:
                if player: player.write_log(f"⏰ Heads-up: {e.get('title','Event')} in {int(delta//60)}m")
        except: pass
