def manage_checkpoints(parameters: dict, player=None, **_):
    import memory.productivity as prod
    from pathlib import Path
    action=str(parameters.get("action","list")).strip().lower()
    try:
        if action in ("create","add","save"):
            name=str(parameters.get("name") or parameters.get("title") or "").strip()
            paths=parameters.get("paths") or parameters.get("files") or []
            if isinstance(paths,str):
                import json
                try: paths=json.loads(paths)
                except: paths=[p.strip() for p in paths.split(",")]
            if not name or not paths: return "Need name and paths. Example: create checkpoint 'Exam' paths=['~/Notes','~/Project']"
            # Expand ~ and absolutify for validation only; store as given
            abs_paths=[str(Path(p).expanduser()) for p in paths]
            res=prod.create_checkpoint(name, abs_paths, str(parameters.get("note","")))
            if player: player.write_log(f"[Checkpoint] + #{res['id']} {name}")
            return f"Checkpoint #{res['id']} '{name}' saved ({len(abs_paths)} paths)."
        elif action=="list":
            rows=prod.list_checkpoints()
            if not rows: return "No checkpoints yet."
            lines=["Checkpoints:"]
            for r in rows: lines.append(f"  #{r['id']} {r['name']} — {len(r['paths'])} paths — {r['created']}")
            if player: player.show_content("CHECKPOINTS", "\n".join(lines))
            return "\n".join(lines)
        elif action=="restore":
            cid=int(parameters.get("id") or parameters.get("checkpoint_id") or 0)
            if not cid: return "Which checkpoint id to restore?"
            dry=bool(parameters.get("dry_run", True))
            data=prod.restore_checkpoint(cid, dry_run=dry)
            existing=data["existing"]; missing=data["missing"]
            lines=[f"Checkpoint '{data['checkpoint']['name']}' — would open {len(existing)} paths:"]
            for p in existing: lines.append(f"  ✓ {p}")
            for p in missing: lines.append(f"  ✗ missing {p}")
            if not dry and player:
                # Best-effort open in UI thread: player has open_file/open_app helpers if available
                for p in existing:
                    try:
                        if hasattr(player,"open_path"): player.open_path(p)
                        elif Path(p).is_dir():
                            import subprocess, platform, os
                            if platform.system()=="Windows": os.startfile(p)
                            elif platform.system()=="Darwin": subprocess.Popen(["open",p])
                            else: subprocess.Popen(["xdg-open",p])
                    except Exception: pass
                lines.append("Opened existing paths.")
            elif dry:
                lines.append("Dry run — say 'restore checkpoint 2 confirm' to actually open.")
            return "\n".join(lines)
        elif action in ("delete","remove"):
            cid=int(parameters.get("id") or 0); return prod.delete_checkpoint(cid)
        else: return "Actions: create/list/restore/delete"
    except Exception as e: return f"Checkpoints error: {e}"

TOOL={"name":"manage_checkpoints","description":"Manage encrypted checkpoints that reopen folders/apps/pages: create/list/restore/delete. Checkpoint stores paths to reopen later with review step.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"create|list|restore|delete"},"name":{"type":"STRING"},"paths":{"type":"ARRAY","items":{"type":"STRING"},"description":"Paths to save"},"files":{"type":"ARRAY","items":{"type":"STRING"}},"note":{"type":"STRING"},"id":{"type":"NUMBER"},"checkpoint_id":{"type":"NUMBER"},"dry_run":{"type":"BOOLEAN","description":"If true just show what would open"}},"required":["action"]},"handler":manage_checkpoints}
