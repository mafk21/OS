"""GitHub & Git Automation — Phase 6.2: local git status/diff + gh CLI + REST token."""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess


def _gh_token() -> str:
    env_tok = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if env_tok:
        return env_tok
    try:
        import memory.config_manager as cm
        return str(cm.load_api_keys().get("github_token", "") or "").strip()
    except Exception:
        return ""


def _run_cli(args: list[str], cwd: str = "", timeout: int = 15) -> tuple[int, str]:
    workdir = str(pathlib.Path(cwd).expanduser()) if cwd else None
    res = subprocess.run(
        args, capture_output=True, text=True, cwd=workdir, timeout=timeout
    )
    out = ((res.stdout or "") + ("\n" + res.stderr if res.stderr else "")).strip()
    return res.returncode, out[:4000]


def github_automation(parameters: dict, player=None, **_) -> str:
    action = str((parameters or {}).get("action", "") or "").strip().lower()
    cwd = str((parameters or {}).get("cwd", "") or "").strip()

    # Local git actions work in any checkout with zero token
    if action in ("git_status", "local_status"):
        code, out = _run_cli(["git", "status", "-sb"], cwd=cwd)
        if player and out:
            player.show_content("GIT STATUS", out)
        return out or ("Clean working tree." if code == 0 else "Not a git repository.")

    if action in ("git_diff", "diff"):
        code, out = _run_cli(["git", "diff", "--stat"], cwd=cwd)
        if player and out:
            player.show_content("GIT DIFF", out)
        return out or ("No unstaged changes." if code == 0 else "git diff failed.")

    token = _gh_token()
    has_gh = shutil.which("gh") is not None

    if not token and has_gh:
        repo = str((parameters or {}).get("repo") or "").strip()
        if action == "list_prs":
            cmd = ["gh", "pr", "list", "--limit", "15"] + (["-R", repo] if repo else [])
            _, out = _run_cli(cmd, cwd=cwd)
            if player and out:
                player.show_content("GITHUB PRS", out)
            return out or "No open pull requests."
        if action == "list_repos":
            _, out = _run_cli(["gh", "repo", "list", "--limit", "15"], cwd=cwd)
            if player and out:
                player.show_content("GITHUB REPOS", out)
            return out or "No repositories returned."
        if action == "status" and repo:
            _, out = _run_cli(["gh", "repo", "view", repo], cwd=cwd)
            return out or f"Could not inspect {repo}."

    if not token:
        return (
            "GitHub not configured — set github_token in config/api_keys.json "
            "(github.com/settings/tokens) or authenticate the `gh` CLI."
        )

    import requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    if action == "create_repo":
        name = str(parameters.get("name") or "").strip()
        if not name:
            return "Need name"
        private = bool(parameters.get("private", False))
        r = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={"name": name, "private": private},
            timeout=15,
        )
        if r.status_code in (200, 201):
            return f"Repo created: {r.json().get('html_url', '')}"
        return f"Create repo failed {r.status_code}: {r.text[:300]}"

    if action == "create_pr":
        repo = str(parameters.get("repo") or "").strip()
        title = str(parameters.get("title") or "").strip()
        head = str(parameters.get("head") or "main").strip()
        base = str(parameters.get("base") or "main").strip()
        body = str(parameters.get("body", "")).strip()
        if not repo or not title:
            return "Need repo (owner/repo) and title"
        r = requests.post(
            f"https://api.github.com/repos/{repo}/pulls",
            headers=headers,
            json={"title": title, "head": head, "base": base, "body": body},
            timeout=15,
        )
        if r.status_code in (200, 201):
            return f"PR created: {r.json().get('html_url', '')}"
        return f"Create PR failed {r.status_code}: {r.text[:400]}"

    if action == "list_prs":
        repo = str(parameters.get("repo") or "").strip()
        if not repo:
            return "Need repo (owner/repo) for list_prs"
        r = requests.get(
            f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=15",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            prs = r.json()
            out = "\n".join(
                f"  #{p['number']} {p['title']} ({p['user']['login']})" for p in prs
            )
            if player and out:
                player.show_content("GITHUB PRS", out)
            return out or "No open PRs"
        return f"List PRs failed {r.status_code}"

    if action == "status":
        repo = str(parameters.get("repo") or "").strip()
        if not repo:
            return "Need repo"
        r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
        if r.status_code == 200:
            j = r.json()
            return f"{repo}: ★{j.get('stargazers_count', 0)} {j.get('description', '')[:120]}"
        return f"Status failed {r.status_code}"

    if action == "list_repos":
        r = requests.get(
            "https://api.github.com/user/repos?per_page=20&sort=updated",
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            repos = r.json()
            out = "\n".join(
                f"  • {x['full_name']} — {(x.get('description') or '')[:60]}"
                for x in repos[:10]
            )
            if player:
                player.show_content("GITHUB REPOS", out)
            return out or "No repos"
        return f"List failed {r.status_code}"

    return (
        "GitHub actions: git_status, git_diff, list_prs (repo), create_repo "
        "(name, private), create_pr (repo, title, head, base, body), "
        "status (repo), list_repos"
    )


TOOL = {
    "name": "github_automation",
    "description": (
        "GitHub & Git Automation: local git_status/git_diff plus GitHub "
        "list_prs, create_pr, create_repo, status, and list_repos (via "
        "github_token or authenticated `gh` CLI)."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "git_status|git_diff|list_prs|create_repo|create_pr|status|list_repos",
            },
            "cwd": {"type": "STRING", "description": "Optional working directory"},
            "name": {"type": "STRING"},
            "private": {"type": "BOOLEAN"},
            "repo": {"type": "STRING", "description": "owner/repo"},
            "title": {"type": "STRING"},
            "head": {"type": "STRING"},
            "base": {"type": "STRING"},
            "body": {"type": "STRING"},
        },
        "required": ["action"],
    },
    "handler": github_automation,
}
