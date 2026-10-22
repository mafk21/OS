---
name: safe-file-organizer
description: Dry-run folder triage and undo-safe cleanup — use when organizing Downloads or Desktop, batch-renaming files, sorting folders, or undoing file moves.
---

# Safe file organizer

Clean up messy directories (`Downloads`, `Desktop`, project folders) and batch-organize files with a mandatory dry-run inventory, zero silent deletions, and full `undo` rollback safety.

## When to use

"Clean up my Downloads", "organize my Desktop by type/date", "rename all screenshots in this folder", "move PDFs into Invoices", or "undo those file changes".

## Procedure

1. **Inventory first (read-only)**:
   - Inspect the target folder via `file_controller` (list/inspect) before moving or renaming anything.
   - Group files logically (e.g. `Documents/`, `Images/`, `Archives/`, `Installers/`, `Code/`) while leaving active project repos, dotfiles, and shortcuts untouched.
2. **Checkpoint & preview before bulk changes**:
   - If moving or renaming **more than 5 files**, summarize the exact plan in one short spoken line (counts + target folders) and optionally save key paths via `manage_checkpoints` (`action="create"`).
3. **Execute non-destructively**:
   - Move and rename via `file_controller` so every operation registers on the shared Undo Stack (`core/undo.py`).
   - **Never permanently delete user files** during an organization pass; quarantine duplicates or old installers into a `_To_Review/` subfolder instead unless the user explicitly names specific files to delete.
4. **Verify & remind of rollback**:
   - Confirm final file counts in destination folders so zero files were dropped or overwritten.
   - If the user dislikes the layout or says "put it back", call `undo` immediately.

## Pitfalls

- Never overwrite an existing destination file silently — append a numeric suffix or date stamp on filename collision.
- Never touch `.git/`, system folders, VirtualBox/Docker volumes, or currently open lockfiles (`~$*`, `*.part`, `*.crdownload`).

## Verification

Source + destination file counts match pre-move total? Zero files overwritten or silently deleted? Operations reversible via `undo`?
