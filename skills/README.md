# Skills — the SKILL.md standard

A **skill** is a folder with a `SKILL.md` file (YAML frontmatter + markdown
instructions). It is the open Agent Skills standard — the same format loaded
by Claude Code, GitHub Copilot, VS Code, Codex, Cursor and Gemini CLI — so
any skill from skills.sh, ClawHub, or github.com/google/skills drops in
unchanged.

```
skills/
  my-skill/
    SKILL.md          # required — name + description frontmatter, body below
    references/       # optional — long detail, read on demand
    scripts/          # optional — run via the shell tool
```

## How it loads (progressive disclosure)

| Level | What | When it costs context |
|---|---|---|
| 1 | `name` + `description` frontmatter | Always — one line each in the prompt's `[SKILLS]` block |
| 2 | The SKILL.md body | Only when the model calls `skill_read {name}` and the task matches the description |
| 3 | Bundled references/scripts | Only when the body points at them (`skill_read {name, path}`) |

## Adding a skill

1. `cp -r skills/_template skills/my-skill`
2. Edit the frontmatter: `name` must equal the folder name; `description`
   must say **what it does and when to use it** (this is the trigger).
3. Restart JARVIS — discovery runs at startup: `[Skills] Skill loaded: …`

Rules enforced by the loader: lowercase-hyphen name ≤64 chars matching the
folder, non-empty description, non-empty body. Folders starting with `_` are
ignored (that's the template).
