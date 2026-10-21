"""GitHub Automation — Phase 6.2: repo/PR/commit via github_token."""
import pathlib, subprocess, json, os

def _gh_token():
    try:
        import memory.config_manager as cm
        return str(cm.load_api_keys().get("github_token","") or "").strip()
    except: return ""

def github_automation(parameters: dict, player=None, **_):
    action=str(parameters.get("action","") or "").strip().lower()
    token=_gh_token()
    if not token: return "GitHub not configured — set github_token in config/api_keys.json (github.com/settings/tokens)"
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    import requests
    if action=="create_repo":
        name=str(parameters.get("name") or "").strip()
        if not name: return "Need name"
        private=bool(parameters.get("private", False))
        r=requests.post("https://api.github.com/user/repos", headers=headers, json={"name": name, "private": private}, timeout=15)
        if r.status_code in (200,201): return f"Repo created: {r.json().get('html_url','')}"
        return f"Create repo failed {r.status_code}: {r.text[:300]}"
    if action=="create_pr":
        repo=str(parameters.get("repo") or "").strip()  # owner/repo
        title=str(parameters.get("title") or "").strip()
        head=str(parameters.get("head") or "main").strip()
        base=str(parameters.get("base") or "main").strip()
        body=str(parameters.get("body","")).strip()
        if not repo or not title: return "Need repo (owner/repo) and title"
        r=requests.post(f"https://api.github.com/repos/{repo}/pulls", headers=headers, json={"title": title, "head": head, "base": base, "body": body}, timeout=15)
        if r.status_code in (200,201): return f"PR created: {r.json().get('html_url','')}"
        return f"Create PR failed {r.status_code}: {r.text[:400]}"
    if action=="status":
        repo=str(parameters.get("repo") or "").strip()
        if not repo: return "Need repo"
        r=requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
        if r.status_code==200:
            j=r.json()
            return f"{repo}: ★{j.get('stargazers_count',0)} {j.get('description','')[:120]}"
        return f"Status failed {r.status_code}"
    if action=="list_repos":
        r=requests.get("https://api.github.com/user/repos?per_page=20&sort=updated", headers=headers, timeout=10)
        if r.status_code==200:
            repos=r.json()
            out="\n".join(f"  • {x['full_name']} — {x.get('description','')[:60]}" for x in repos[:10])
            if player: player.show_content("GITHUB REPOS", out)
            return out or "No repos"
        return f"List failed {r.status_code}"
    return "GitHub: create_repo (name, private), create_pr (repo, title, head, base, body), status (repo), list_repos"

TOOL={
    "name":"github_automation",
    "description":"GitHub Automation: repo/PR/commit via github_token. Actions: create_repo, create_pr, status, list_repos.",
    "parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"create_repo|create_pr|status|list_repos"},"name":{"type":"STRING"},"private":{"type":"BOOLEAN"},"repo":{"type":"STRING","description":"owner/repo"},"title":{"type":"STRING"},"head":{"type":"STRING"},"base":{"type":"STRING"},"body":{"type":"STRING"}},"required":["action"]},"handler":github_automation
}
