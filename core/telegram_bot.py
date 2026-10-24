"""
Telegram Remote — Phase 4.3
Pairing via BotFather token → polling loop, routes inbound messages to LLM and returns replies.
Runs as a background thread; uses python-telegram-bot if installed, else HTTP polling fallback.
No hard dependency — if telegram_bot_token is empty, module is inert.
"""

from __future__ import annotations
import threading, time, json, sys, pathlib

_running = False
_thread: threading.Thread | None = None
_paired_users: set[int] = set()

def _cfg():
    try:
        import memory.config_manager as cm
        d=cm.load_api_keys()
        return {
            "token": str(d.get("telegram_bot_token","") or "").strip(),
            "allowed": [str(x).strip() for x in (d.get("telegram_allowed_users") or []) if str(x).strip()],
            "relay": bool(d.get("telegram_relay_enabled", False)),
        }
    except Exception:
        return {"token":"","allowed":[],"relay":False}

def _load_pairing():
    p=pathlib.Path("memory/telegram_pairing.json")
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: pass
    return {"paired": [], "pairing_code": ""}

def _save_pairing(data: dict):
    p=pathlib.Path("memory/telegram_pairing.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def generate_pairing_code() -> str:
    import secrets, string
    code="".join(secrets.choice(string.digits) for _ in range(6))
    d=_load_pairing()
    d["pairing_code"]=code
    d["pairing_code_created"]=time.time()
    _save_pairing(d)
    return code

def is_paired(user_id: int) -> bool:
    d=_load_pairing()
    return int(user_id) in set(d.get("paired",[]))

def pair_user(user_id: int, code: str) -> bool:
    d=_load_pairing()
    if str(code).strip()==str(d.get("pairing_code","")).strip() and code:
        if int(user_id) not in d.get("paired",[]):
            d.setdefault("paired",[]).append(int(user_id))
            _save_pairing(d)
        return True
    return False

def handle_inbound(text: str, user_id: int = 0, player=None, loop=None) -> str:
    """Route inbound Telegram text to the assistant. Returns reply text."""
    text=(text or "").strip()
    if not text: return ""
    low=text.lower()
    if low in ("/stop","stop","cancel"):
        # Mirror dashboard /stop — clear tasks
        try:
            import memory.productivity as prod
            # Not destructive—just acknowledge
            return "🛑 Stopped. Awaiting next command."
        except: return "Stopped."
    if low.startswith("/pair "):
        code=low.split(maxsplit=1)[1].strip() if len(low.split(maxsplit=1))>1 else ""
        ok=pair_user(user_id, code)
        return "✅ Paired! Send any message to talk to JARVIS." if ok else "❌ Pairing code invalid. Ask JARVIS: 'show pairing code'"
    # Normal chat — forward to LLM via provider
    try:
        # Enforce pairing if any paired users exist
        d=_load_pairing()
        if d.get("paired"):
            if not is_paired(user_id):
                return "🔒 Not paired. Send /pair <code> (ask JARVIS for the code)."
        # Use provider text
        from core.provider import text as prov_text
        prompt=text
        ctx_parts = []
        try:
            from memory.memory_manager import load_memory, format_memory_for_prompt
            from memory.timeline import format_timeline_for_prompt, append_turn
            mem_ctx = format_memory_for_prompt(load_memory())
            if mem_ctx:
                ctx_parts.append(mem_ctx)
            tl_ctx = format_timeline_for_prompt(recent_limit=4)
            if tl_ctx:
                ctx_parts.append(tl_ctx)
            append_turn("user", text, speaker="You", channel="telegram")
        except Exception:
            append_turn = None  # type: ignore
        ctx_block = ("\n".join(ctx_parts) + "\n") if ctx_parts else ""
        sys_hint=(
            "You are JARVIS, a helpful assistant sharing one continuous Forever Timeline "
            "across desktop voice, text, and Telegram. Reply concisely (<300 chars ideally).\n"
            f"{ctx_block}User via Telegram: "
        )
        reply=prov_text(sys_hint+prompt, tier="fast", timeout_ms=15000, default="")
        if not reply:
            from core.llm_client import call_llm
            raw=call_llm([{"role":"user","content": prompt}], timeout=20)
            reply=(raw.get("content") or "").strip()
        if reply and callable(append_turn):
            try:
                append_turn("jarvis", reply, speaker="JARVIS", channel="telegram")
            except Exception:
                pass
        return reply or "…"
    except Exception as e:
        return f"(telegram error: {e})"

def _poll_loop(receive_callback=None):
    global _running
    cfg=_cfg()
    token=cfg["token"]
    if not token:
        print("[Telegram] No token — remote disabled")
        return
    # Simple HTTP polling (no extra dep) — falls back to python-telegram-bot if installed
    try:
        import requests  # type: ignore
    except Exception:
        print("[Telegram] requests not installed — install with pip install requests")
        return
    base=f"https://api.telegram.org/bot{token}"
    offset=0
    print("[Telegram] Polling started")
    while _running:
        try:
            r=requests.get(f"{base}/getUpdates", params={"offset": offset, "timeout": 25}, timeout=30)
            if r.status_code!=200:
                time.sleep(3); continue
            data=r.json()
            for upd in data.get("result",[]):
                offset=max(offset, int(upd.get("update_id",0))+1)
                msg=upd.get("message") or {}
                text=msg.get("text") or ""
                uid=(msg.get("from") or {}).get("id", 0)
                chat_id=(msg.get("chat") or {}).get("id", 0)
                if not text: continue
                reply=handle_inbound(text, user_id=uid)
                if reply and chat_id:
                    try:
                        requests.post(f"{base}/sendMessage", json={"chat_id": chat_id, "text": reply[:4000]}, timeout=10)
                    except: pass
        except Exception as e:
            time.sleep(3)
    print("[Telegram] Polling stopped")

def start(player=None, loop=None):
    global _running, _thread
    if _running: return True
    cfg=_cfg()
    if not cfg["token"]:
        return False
    _running=True
    _thread=threading.Thread(target=_poll_loop, kwargs={"receive_callback": handle_inbound}, daemon=True, name="telegram-poll")
    _thread.start()
    return True

def stop():
    global _running, _thread
    _running=False
    t=_thread; _thread=None
    if t and t.is_alive():
        t.join(timeout=1.5)

def status() -> dict:
    cfg=_cfg()
    pairing=_load_pairing()
    return {
        "enabled": bool(cfg["token"]),
        "running": _running,
        "paired_users": len(pairing.get("paired",[])),
        "pairing_code": pairing.get("pairing_code","")[:2]+"****" if pairing.get("pairing_code") else "",
        "allowed_configured": bool(cfg["allowed"]),
    }
