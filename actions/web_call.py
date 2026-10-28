"""Call the user through their private free JARVIS web-call portal."""
from datetime import datetime
from core.web_call import configure, load_config, schedule_call, session_action, session_status, start_call, watch_replies

def web_call(parameters:dict,response=None,player=None,session_memory=None)->str:
    action=str(parameters.get("action") or "start").strip().lower()
    try:
        if action in {"configure","setup"}:
            supplied=str(parameters.get("pairing_code") or "").strip()
            if supplied:
                cfg=configure(str(parameters.get("url") or "https://jarvis-call-sigma.vercel.app"),supplied)
                return f"Web calling configured and saved for {cfg['url']}."
            cfg=load_config()
            if not cfg: return "Web calling needs one-time pairing. Ask the user for the pairing code shown in their JARVIS Call web app, then call web_call action=configure with it. Telegram is unrelated."
            return f"Web calling is configured for {cfg['url']}. The phone pairing code is installed."
        if action=="start":
            result=start_call(str(parameters.get("message") or ""),str(parameters.get("reason") or "JARVIS is calling"))
            watch_replies(result["session_id"])
            return f"Call sent and live reply bridge started. Session {result['session_id']}; {result.get('notifications',0)} paired device notification(s) delivered."
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
 "description":"The ONLY tool for 'call me', 'ring my phone', or JARVIS voice-call requests. Uses the private JARVIS Call website—not Telegram or remote_relay. Can configure once with the website pairing code, start now, schedule through the OS scheduler, check a session, reply, or end. Never claim calling is unconfigured before calling this tool with action=setup. Respect Soul quiet hours and snooze for proactive calls.",
 "parameters":{"type":"OBJECT","properties":{
  "action":{"type":"STRING","description":"configure | setup | start | schedule | status | reply | end"},
  "pairing_code":{"type":"STRING","description":"configure: private code shown in the JARVIS Call web app"},
  "url":{"type":"STRING","description":"configure: portal URL; defaults to the official deployed portal"},
  "message":{"type":"STRING","description":"What JARVIS will say during the call"},
  "reason":{"type":"STRING","description":"Short reason shown while ringing"},
  "date":{"type":"STRING","description":"schedule: YYYY-MM-DD local date"},
  "time":{"type":"STRING","description":"schedule: HH:MM local 24-hour time"},
  "session_id":{"type":"STRING","description":"status/reply/end call session UUID"}
 },"required":["action"]},"handler":web_call}
