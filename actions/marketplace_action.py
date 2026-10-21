"""Plugin marketplace action — Phase 7.2"""
def marketplace_action(parameters: dict, player=None, **_):
    action=str(parameters.get("action","list")).strip().lower()
    if action=="list":
        try:
            import marketplace.marketplace as mp
            plugins=mp.list_marketplace()
            if not plugins: return "Marketplace empty or offline — check registry URL"
            out="\n".join(f"  • {p['name']} v{p.get('version','?')} — {p.get('description','')[:80]}" for p in plugins[:15])
            if player: player.show_content("MARKETPLACE", out)
            return out
        except Exception as e: return f"Marketplace list failed: {e}"
    if action=="install":
        name=str(parameters.get("name","")).strip()
        if not name: return "Need plugin name"
        import marketplace.marketplace as mp
        return mp.install_plugin(name, str(parameters.get("version","latest")))
    if action=="remove":
        name=str(parameters.get("name","")).strip()
        import marketplace.marketplace as mp
        return mp.remove_plugin(name)
    return "Marketplace: list/install/remove. Example: {action:install, name:weather-pro}"

TOOL={
    "name":"marketplace",
    "description":"Plugin marketplace: one-click install, versioned, isolated. Actions: list/install/remove.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"list|install|remove"},"name":{"type":"STRING"},"version":{"type":"STRING"}},"required":["action"]},"handler":marketplace_action
}
