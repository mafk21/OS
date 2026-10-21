"""Career Helpers — Phase 6.6: LinkedIn agent, sysadmin diagnostic hub, voice KB."""
import pathlib

def career_helpers(parameters: dict, player=None, **_):
    action=str(parameters.get("action","") or "").strip().lower()
    if action in ("linkedin","linkedin_post","summarize_profile"):
        text=str(parameters.get("text") or parameters.get("url") or "").strip()
        if not text: return "Provide LinkedIn text/url or profile summary request"
        try:
            from core.provider import text as prov_text
            out=prov_text(f"Polish this for LinkedIn (professional, concise):\n\n{text[:4000]}", tier="smart", default="")
            if player: player.show_content("LINKEDIN", out or text[:1500])
            return out or "LinkedIn polish unavailable (LLM offline)"
        except Exception as e: return f"LinkedIn helper failed: {e}"
    if action in ("sysadmin","diagnose","health"):
        # Delegates to diagnostics_check for sysadmin hub
        try:
            import actions.diagnostics as diag
            return diag.diagnostics_check({"action":"full"}, player=player)
        except Exception as e: return f"Sysadmin check failed: {e}"
    if action in ("kb","voice_kb","knowledge","search_kb"):
        q=str(parameters.get("query") or parameters.get("text") or "").strip()
        if not q: return "Need query for voice KB search"
        # Search RAG index + memory
        try:
            import memory.memory_manager as mm
            hits=mm.search_memory(q, limit=5) if hasattr(mm, "search_memory") else "—"
            return f"KB results for '{q}':\n{hits}"
        except Exception as e: return f"KB search failed: {e}"
    return "Career: linkedin (text/url), sysadmin/diagnose, kb (query). Example: {action:linkedin, text:'Draft post about AI...'}"

TOOL={
    "name":"career_helpers",
    "description":"Career Helpers: LinkedIn agent (polish posts), sysadmin diagnostic hub, voice KB search.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"linkedin|sysadmin|diagnose|kb"},"text":{"type":"STRING"},"url":{"type":"STRING"},"query":{"type":"STRING"}},"required":["action"]},"handler":career_helpers
}
