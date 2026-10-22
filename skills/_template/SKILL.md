---
name: _template
description: Not a real skill — copy this folder, rename it, and write what your skill does and when to use it.
---

# Skill template

Rename this folder (lowercase-with-hyphens, e.g. `my-skill/`), then edit the
frontmatter above: `name` must match the folder exactly, and `description` is
the ONLY thing the model sees before the task hits — say both **what it does**
and **when to use it**, in the words a user would actually say.

## Instructions

Write the procedure as numbered steps the model can follow without guessing.

1. First concrete step.
2. Second concrete step.
3. How to verify the result before answering.

## Pitfalls

- What has gone wrong before, and what to do instead.

## Bundled files (optional)

- `references/*.md` — long detail the model opens with
  `skill_read {name, path: "references/x.md"}` only when needed.
- `scripts/*` — run them through the **shell** tool; only their output should
  enter the conversation.

Folders starting with `_` are ignored by discovery, which is why this one is
safe to keep installed.
