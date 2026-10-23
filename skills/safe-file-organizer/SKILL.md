---
name: safe-file-organizer
description: Dry-run folder triage and undo-safe cleanup — use when organizing Downloads or Desktop, batch-renaming files, sorting folders, or undoing file moves.
---

# Safe file organizer

Clean up messy directories (`Downloads`, `Desktop`, `Documents`, project folders) and batch-organize files with exact path targeting, zero empty ghost folders, zero silent deletions, and full `undo` rollback safety.

## When to use

"Clean up my Downloads", "organize my files in Downloads", "organize my Desktop by type/date", "remove empty folders on Desktop", "move PDFs into Invoices", or "undo those file changes".

## Procedure

1. **Always pass the user's exact target folder (`path`)**:
   - Never omit `path`! Pass `path="downloads"` for Downloads, `path="desktop"` for Desktop, `path="documents"` for Documents, or the exact folder path the user asked for. If the user just says "organize my files" without naming a folder, ask in one short question whether they mean `Downloads` or `Desktop`.
2. **Dry-run preview & single-step atomic organization**:
   - For general folder organization ("organize my Downloads" / "sort my Desktop"), call `file_controller(action="organize", path="<target>", dry_run=True)` first if you want to preview counts, then execute `file_controller(action="organize", path="<target>", mode="by_type")` (`mode="by_date"` when asked to sort by date).
   - Prefer `action="organize"` over manually calling `create_folder` + dozens of individual `move` calls: `organize` creates category folders (`Images/`, `Documents/`, `Installers/`, `Archives/`, `Videos/`, `Audio/`, `Code/`, `Design_3D/`) **only** when matching files exist, moves every file atomically without overwriting duplicates, and registers a single `undo` entry.
   - For custom rules ("move all PDFs in Downloads into `Downloads/Invoices`"), pass full or explicit paths (`action="move"`, `path="downloads"`, `files=[...]`, `destination="downloads/Invoices"`).
   - To clean up leftover empty folders, call `file_controller(action="clean_empty_folders", path="<target>")`.
3. **Execute non-destructively**:
   - **Never permanently delete user files** during an organization pass; quarantine unwanted items or ask before `delete` (which sends to Recycle Bin / Trash).
4. **Verify & remind of rollback**:
   - Report the exact folder path organized and how many files moved into each category folder.
   - If the user dislikes the layout or says "put it back", call `undo` immediately.

## Pitfalls

- Never call `desktop_control` when the user asked to organize `Downloads` or another folder — always use `file_controller(action="organize", path="downloads")`.
- Never call `create_folder` without specifying `path` (e.g. `path="downloads", name="Invoices"`), and never pre-create empty folders before verifying matching files exist.
- Never overwrite an existing destination file silently, and never touch `.git/`, system folders, shortcuts (`.lnk`/`.url`), or active incomplete downloads (`~$*`, `*.part`, `*.crdownload`).

## Verification

Exact requested folder (`Downloads` vs `Desktop`) targeted? Zero empty folders created? Every moved file verified in its destination subfolder? Reversible in one step via `undo`?
