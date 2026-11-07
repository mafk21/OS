"""Wait for the old JARVIS process to exit, then launch its replacement."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


def _parent_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        parent_index = args.index("--parent")
        cwd_index = args.index("--cwd")
        separator = args.index("--")
        parent = int(args[parent_index + 1])
        cwd = Path(args[cwd_index + 1]).resolve()
        command = args[separator + 1:]
        installation_id = ""
        if "--installation-id" in args:
            identity_index = args.index("--installation-id")
            installation_id = args[identity_index + 1]
    except (ValueError, IndexError):
        return 2
    if not command or not cwd.is_dir():
        return 2
    if installation_id:
        try:
            import json
            marker = json.loads((cwd / "config" / "installation.json").read_text(encoding="utf-8"))
            if marker.get("installation_id") != installation_id:
                return 4
        except (OSError, ValueError, json.JSONDecodeError):
            return 4

    deadline = time.monotonic() + 30
    while _parent_alive(parent) and time.monotonic() < deadline:
        time.sleep(0.15)
    if _parent_alive(parent):
        return 3

    kwargs: dict[str, object] = {"cwd": str(cwd), "close_fds": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(command, **kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
