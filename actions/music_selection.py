"""Music & Selection — Phase 5.5: Spotify next/prev/what's playing, summarize selection, translate."""
import time

def _spotify_client():
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        # Needs SPOTIPY_CLIENT_ID etc in env or config
        import memory.config_manager as cm
        cfg=cm.load_api_keys()
        cid=cfg.get("spotify_client_id") or ""
        if not cid: return None, "Spotify not configured — set spotify_client_id/secret in config/api_keys.json"
        auth=SpotifyOAuth(client_id=cid, client_secret=cfg.get("spotify_client_secret",""), redirect_uri=cfg.get("spotify_redirect_uri","http://localhost:8888/callback"), scope="user-read-playback-state user-modify-playback-state")
        sp=spotipy.Spotify(auth_manager=auth)
        return sp, "ok"
    except Exception as e:
        return None, f"Spotify unavailable: {e} — pip install spotipy"

def music_selection(parameters: dict, player=None, **_):
    action=str(parameters.get("action","") or parameters.get("command","")).strip().lower()
    # Spotify controls
    if action in ("next","skip","next_track"):
        sp,msg=_spotify_client()
        if not sp: return msg
        try: sp.next_track(); return "⏭ Next track"
        except Exception as e: return f"Spotify next failed: {e}"
    if action in ("prev","previous","prev_track"):
        sp,msg=_spotify_client()
        if not sp: return msg
        try: sp.previous_track(); return "⏮ Previous track"
        except Exception as e: return f"Spotify prev failed: {e}"
    if action in ("playing","whats_playing","now","status"):
        sp,msg=_spotify_client()
        if not sp: return msg
        try:
            cur=sp.current_playback()
            if not cur or not cur.get("item"): return "Nothing playing"
            item=cur["item"]; name=item.get("name",""); artist=", ".join(a.get("name","") for a in item.get("artists",[]))
            return f"▶ {artist} — {name}"
        except Exception as e: return f"Spotify status failed: {e}"
    # Selection ops: summarize/translate via clipboard
    if action in ("summarize","summarize_selection"):
        try:
            import pyperclip
            sel=pyperclip.paste() or str(parameters.get("text",""))
            if not sel.strip(): return "No selection — copy text first (Ctrl+C), then say 'summarize selection'"
            from core.provider import text as prov_text
            summary=prov_text(f"Summarize concisely:\n\n{sel[:4000]}", tier="fast", default="")
            if player: player.show_content("SELECTION SUMMARY", summary or sel[:2000])
            return summary or "No summary (LLM unavailable)"
        except Exception as e: return f"Summarize failed: {e}"
    if action in ("translate","translate_selection"):
        try:
            import pyperclip
            sel=pyperclip.paste() or str(parameters.get("text",""))
            target=str(parameters.get("target","English") or parameters.get("language","English"))
            if not sel.strip(): return "No selection — copy text first"
            from core.provider import text as prov_text
            out=prov_text(f"Translate to {target}:\n\n{sel[:4000]}", tier="fast", default="")
            if player: player.show_content(f"TRANSLATE → {target}", out or sel[:2000])
            return out or "No translation (LLM unavailable)"
        except Exception as e: return f"Translate failed: {e}"
    # Clipboard type helper
    if action=="paste":
        txt=str(parameters.get("text",""))
        if txt and player and hasattr(player, "_input"):
            try: player._input.setText(txt); return f"Pasted to input: {txt[:80]}"
            except: pass
        return f"Text: {txt}"
    return "Music: next/prev/playing. Selection: summarize/translate (copies from clipboard). Example: action=next or action=summarize"

TOOL={
    "name":"music_selection",
    "description":"Music & Selection: Spotify next/prev/what's playing, summarize selection (clipboard), translate selection.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"next|prev|playing|summarize|translate|paste"},"command":{"type":"STRING"},"text":{"type":"STRING"},"target":{"type":"STRING","description":"Target language for translate"},"language":{"type":"STRING"}},"required":["action"]},"handler":music_selection
}
