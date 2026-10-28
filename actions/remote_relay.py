def manage_remote(parameters: dict, player=None, **_):
    import memory.config_manager as cm
    import core.telegram_bot as tg
    action=str(parameters.get("action","status")).strip().lower()
    try:
        if action=="status":
            lines=["Remote status:"]
            try: lines.append(f"  Dashboard: {'running' if hasattr(player,'_dashboard') and player._dashboard else 'not running'}")
            except: pass
            s=tg.status()
            lines.append(f"  Telegram: {'enabled' if s['enabled'] else 'disabled'} running={s['running']} paired={s['paired_users']}")
            if not s['enabled']: lines.append("  → Set telegram_bot_token in config/api_keys.json (talk to @BotFather) then restart")
            lines.append(f"  Internet relay: {'on' if cm.get_relay_enabled() else 'off'} (opt-in hosted proxy)")
            if player: player.show_content("REMOTE", "\n".join(lines))
            return "\n".join(lines)
        if action=="pairing_code":
            code=tg.generate_pairing_code()
            msg=f"Pairing code: {code} (share with Telegram user, they send /pair {code})"
            if player: player.write_log(f"[Telegram] {msg}")
            return msg
        if action=="start":
            ok=tg.start(player=player)
            return "Telegram polling started." if ok else "Telegram not configured (telegram_bot_token missing) or already running."
        if action=="stop":
            tg.stop()
            return "Telegram polling stopped."
        if action=="enable_relay":
            cm.save_relay_enabled(True)
            return "Internet relay enabled (opt-in). Requires hosted proxy URL in relay_url."
        if action=="disable_relay":
            cm.save_relay_enabled(False)
            return "Internet relay disabled."
        return "Actions: status/pairing_code/start/stop/enable_relay/disable_relay"
    except Exception as e: return f"Remote error: {e}"

TOOL={
    "name":"manage_remote",
    "description":"Telegram text-command relay and LAN/hosted dashboard access only: status/pairing_code/start/stop/enable_relay/disable_relay. This tool NEVER places voice calls, never rings the user's phone, and must not be used for 'call me' requests; use web_call for those.",
    "parameters":{
        "type":"OBJECT",
        "properties":{
            "action":{"type":"STRING","description":"status|pairing_code|start|stop|enable_relay|disable_relay"}
        },
        "required":["action"]
    },
    "handler":manage_remote
}
