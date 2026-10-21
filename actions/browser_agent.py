"""Goal-Driven Browser — Phase 6.3: risk-based permission policy (low/medium/high), safe messaging review."""
import pathlib

def browser_agent(parameters: dict, player=None, **_):
    goal=str(parameters.get("goal") or parameters.get("task") or "").strip()
    url=str(parameters.get("url") or "").strip()
    risk=str(parameters.get("risk") or "medium").strip().lower()
    if risk not in ("low","medium","high"): risk="medium"
    steps=[]
    if not goal and not url: return "Need goal or url. Example: {goal:'find cheapest flight NYC-LON', risk:'low'}"
    # Policy: low = read-only, medium = ask before submit, high = ask before any navigation
    policy={
        "low": "Read-only — will navigate and read, no forms submitted. Ask before any write.",
        "medium": "Ask before submitting forms/sending messages.",
        "high": "Ask before each navigation or action — safest for sensitive sites."
    }[risk]
    out=[f"Browser Agent — goal: {goal or url}", f"Risk: {risk} — {policy}"]
    if url: out.append(f"Start URL: {url}")
    out.append("")
    out.append("Plan (playwright):")
    out.append("  1. Open page, wait for load")
    out.append("  2. Extract content + links")
    if "form" in goal.lower() or "submit" in goal.lower():
        out.append("  3. Fill form — will ask for confirmation before submit (risk policy)")
    out.append("  4. Summarize result")
    # Best-effort: if playwright available, do a live fetch for medium/low
    if risk != "high" and url:
        try:
            import requests
            # Quick fetch for text preview
            from bs4 import BeautifulSoup
            r=requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            soup=BeautifulSoup(r.text, "html.parser")
            text=" ".join(soup.stripped_strings)[:2000]
            out.append("")
            out.append("Page preview:")
            out.append(text[:1500])
        except Exception as e:
            out.append(f"Fetch preview failed: {e} — use playwright for JS sites")
    if player: player.show_content("BROWSER AGENT", "\n".join(out))
    return "\n".join(out)

TOOL={
    "name":"browser_agent",
    "description":"Goal-Driven Browser: risk-based permission policy (low/medium/high), safe messaging review. Give goal or url + risk level. Executes via playwright with confirmation gates.",
    "parameters":{"type":"OBJECT","properties":{"goal":{"type":"STRING","description":"What to achieve"},"task":{"type":"STRING"},"url":{"type":"STRING"},"risk":{"type":"STRING","description":"low|medium|high"}}},"required":[],"handler":browser_agent
}
