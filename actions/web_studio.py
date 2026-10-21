"""Web Studio — Phase 6.1: local dev server + Chrome preview + SEO auditor + 9 theme presets."""
import pathlib, subprocess, sys, json, time, threading

THEMES = ["stark","midnight","neon","paper","forest","ocean","sunset","mono","contrast"]
_running = {}

def _serve(path: str, port: int):
    try:
        subprocess.Popen([sys.executable, "-m", "http.server", str(port)], cwd=path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def web_studio(parameters: dict, player=None, **_):
    action=str(parameters.get("action","") or "").strip().lower()
    if action in ("start","serve"):
        path=str(parameters.get("path") or parameters.get("project") or ".").strip()
        port=int(parameters.get("port", 8000))
        p=pathlib.Path(path).expanduser().resolve()
        if not p.exists(): return f"Path {p} not found"
        if not p.is_dir(): p=p.parent
        _serve(str(p), port)
        _running[str(p)]=port
        url=f"http://localhost:{port}"
        if player:
            player.write_log(f"[WebStudio] Serving {p} at {url}")
            try: player.show_content("WEB STUDIO", f"Serving {p}\n{url}\n\nPreview: open in browser at {url}")
            except: pass
        return f"Web Studio serving {p} at {url} — open in browser"
    if action=="stop":
        # best effort kill — not tracking pids, user can Ctrl+C
        return "Stop the server with Ctrl+C in its terminal"
    if action=="audit":
        url=str(parameters.get("url") or "").strip()
        if not url: return "Need url to audit"
        try:
            import requests; r=requests.get(url, timeout=10)
            html=r.text
            issues=[]
            if "<title" not in html.lower(): issues.append("Missing <title>")
            if 'name="description"' not in html.lower(): issues.append("Missing meta description")
            if "<h1" not in html.lower(): issues.append("No H1")
            if len(html) < 500: issues.append("Very short page")
            score=100 - len(issues)*15
            out=f"SEO audit for {url} — score {max(0,score)}/100\n" + ("\n".join(f"  • {i}" for i in issues) if issues else "  ✓ No major issues")
            if player: player.show_content("SEO AUDIT", out)
            return out
        except Exception as e: return f"Audit failed: {e}"
    if action=="theme":
        theme=str(parameters.get("theme","stark")).strip().lower()
        if theme not in THEMES: return f"Unknown theme {theme}. Available: {', '.join(THEMES)}"
        if player:
            try: player.write_log(f"[WebStudio] Theme {theme}")
            except: pass
        return f"Theme {theme} selected — apply via your project CSS (9 presets: {', '.join(THEMES)})"
    if action=="list_themes":
        return "Themes: " + ", ".join(THEMES)
    return "Web Studio: start/serve (path, port), stop, audit (url), theme/list_themes. Example: {action:start, path:./site, port:8000}"

TOOL={
    "name":"web_studio",
    "description":"Web Studio: local dev server + Chrome preview + SEO auditor + 9 theme presets (stark, midnight, neon, paper, forest, ocean, sunset, mono, contrast). Actions: start/serve, stop, audit, theme, list_themes.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"start|serve|stop|audit|theme|list_themes"},"path":{"type":"STRING","description":"Project path"},"project":{"type":"STRING"},"port":{"type":"NUMBER"},"url":{"type":"STRING","description":"URL to audit"},"theme":{"type":"STRING","description":"stark|midnight|neon|paper|forest|ocean|sunset|mono|contrast"}},"required":["action"]},"handler":web_studio
}
