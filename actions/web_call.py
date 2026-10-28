"""Call the user through their private free JARVIS web-call portal."""
from datetime import datetime
from core.web_call import load_config, schedule_call, session_action, session_status, start_call

def web_call(parameters:dict,response=None,player=None,session_memory=None)->str:
    action=str(parameters.get("action") or "start").strip().lower()
    try:
        if action=="setup":
            cfg=load_config()
            if not cfg: return "Web calling is not configured on this device."
            return f"Open {cfg['url']} and enter pairing code {cfg['pairing_code']}. Keep the code private."
        if action=="start":
            result=start_call(str(parameters.get("message") or ""),str(parameters.get("reason") or "JARVIS is calling"))
            return f"Call sent. Session {result['session_id']}; {result.get('notifications',0)} paired device notification(s) delivered."
        if action=="schedule":
            date=str(parameters.get("date") or ""); time=str(parameters.get("time") or "")
            target=datetime.strptime(f"{date} {time}","%Y-%m-%d %H:%M")
            schedule_call(target,str(parameters.get("message") or ""),str(parameters.get("reason") or "Scheduled JARVIS call"))
            return f"Web call scheduled for {target.strftime('%B %d at %I:%M %p')}."
        sid=str(parameters.get("session_id") or "")
        if action=="status":
            data=session_status(sid); s=data["session"]
            replies=[m["body"] for m in data.get("messages",[]) if m.get("sender")=="user"]
            return f"Call is {s['status']}."+(f" Latest user reply: {replies[-1]}" if replies else " No user reply yet.")
        if action in {"reply","end"}:
            session_action(sid,action,str(parameters.get("message") or "")); return "Call updated."
        return "Unsupported web-call action."
    except ValueError as exc: return str(exc)
    except Exception as exc: return f"Web call failed: {exc}"

TOOL={
 "name":"web_call",
 "description":"Call the user through their private free web voice line. Can start now, schedule through the OS scheduler, check a session, reply, end, or show setup. Calls are allowed only when the user asks, for configured important alerts, or for user-created schedules; respect Soul quiet hours and snooze for proactive calls.",
 "parameters":{"type":"OBJECT","properties":{
  "action":{"type":"STRING","description":"start | schedule | status | reply | end | setup"},
  "message":{"type":"STRING","description":"What JARVIS will say during the call"},
  "reason":{"type":"STRING","description":"Short reason shown while ringing"},
  "date":{"type":"STRING","description":"schedule: YYYY-MM-DD local date"},
  "time":{"type":"STRING","description":"schedule: HH:MM local 24-hour time"},
  "session_id":{"type":"STRING","description":"status/reply/end call session UUID"}
 },"required":["action"]},"handler":web_call}
