import ctypes
import os
import platform
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

try:
    import send2trash
    _SEND2TRASH = True
except ImportError:
    _SEND2TRASH = False

from core.undo import push_undo

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"

# Undo keeps a file's previous contents in memory so `write` can be reversed.
# Above this size it does not — a 200 MB log would sit in RAM for the rest of
# the session to protect an edit nobody is going to take back.
_UNDO_CONTENT_LIMIT = 1_000_000

# Official Windows KNOWNFOLDERID GUIDs (handles OneDrive Desktop/Documents
# redirection and custom Downloads drives like D:\Downloads automatically).
_WIN_KNOWN_FOLDER_GUIDS: dict[str, str] = {
    "desktop":   "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}",
    "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
    "documents": "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}",
    "pictures":  "{33E28130-4E1E-4676-835A-98395C3BC3BB}",
    "music":     "{4BD8D571-6D19-48D3-BE97-422220080E43}",
    "videos":    "{18989B1D-99B5-455B-841C-AB7C74E4DDFC}",
}

_WIN_REG_SHELL_NAMES: dict[str, str] = {
    "desktop":   "Desktop",
    "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
    "documents": "Personal",
    "pictures":  "My Pictures",
    "music":     "My Music",
    "videos":    "My Video",
}

_KNOWN_FOLDER_CACHE: dict[str, Path] = {}

ORGANIZE_TYPE_MAP: dict[str, set[str]] = {
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".svg", ".ico", ".heic", ".avif", ".tiff", ".tif", ".raw",
    },
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".md",
        ".xls", ".xlsx", ".ppt", ".pptx", ".csv",
        ".odt", ".ods", ".odp", ".epub",
    },
    "Installers": {
        ".exe", ".msi", ".msix", ".appx", ".dmg", ".pkg",
        ".deb", ".rpm", ".appimage", ".apk",
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".iso",
    },
    "Videos": {
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v",
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus",
    },
    "Code": {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css",
        ".json", ".yaml", ".yml", ".xml", ".sql",
        ".cpp", ".c", ".h", ".java", ".cs", ".go", ".rs",
        ".sh", ".ps1", ".bat", ".cmd", ".ipynb",
    },
    "Design_3D": {
        ".psd", ".ai", ".fig", ".sketch", ".blend", ".stl", ".obj", ".fbx",
    },
}

# Files that should NEVER be swept away during folder organization:
# active browser downloads, Office lockfiles, OS folder metadata, & shortcuts.
_ORGANIZE_SKIP_EXTS = {
    ".lnk", ".url", ".webloc", ".desktop",
    ".crdownload", ".part", ".partial", ".tmp", ".download",
}
_ORGANIZE_SKIP_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_ubyte * 8),
    ]


def _win_known_folder(key: str) -> Path | None:
    if _OS != "Windows":
        return None
    if key in _KNOWN_FOLDER_CACHE:
        return _KNOWN_FOLDER_CACHE[key]

    guid_str = _WIN_KNOWN_FOLDER_GUIDS.get(key)
    if guid_str:
        try:
            guid = _GUID.from_buffer_copy(uuid.UUID(guid_str).bytes_le)
            ptr = ctypes.c_wchar_p()
            hr = ctypes.windll.shell32.SHGetKnownFolderPath(
                ctypes.byref(guid), 0, None, ctypes.byref(ptr)
            )
            if hr == 0 and ptr.value:
                val = Path(ptr.value)
                ctypes.windll.ole32.CoTaskMemFree(ptr)
                if val.exists():
                    _KNOWN_FOLDER_CACHE[key] = val
                    return val
            if ptr.value:
                ctypes.windll.ole32.CoTaskMemFree(ptr)
        except Exception:
            pass

    reg_name = _WIN_REG_SHELL_NAMES.get(key)
    if reg_name:
        try:
            import winreg
            sub = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as k:
                raw_val, _ = winreg.QueryValueEx(k, reg_name)
                if raw_val:
                    expanded = Path(os.path.expandvars(str(raw_val)))
                    if expanded.exists():
                        _KNOWN_FOLDER_CACHE[key] = expanded
                        return expanded
        except Exception:
            pass
    return None


def _undo_move(src: Path, dst: Path):
    """Reverse of a move: put it back where it came from."""
    def _fn():
        if not dst.exists():
            return f"'{dst.name}' is no longer there — nothing moved back."
        src.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(src))
        return f"'{src.name}' is back in {src.parent.name}/."
    return _fn


def _undo_create(target: Path):
    """Reverse of a create: remove what we made — and only if we still made it.

    Deliberately refuses to touch a directory that has since been filled: the
    undo for 'create a folder' is not 'delete whatever ended up in it'."""
    def _fn():
        if not target.exists():
            return f"'{target.name}' is already gone."
        if target.is_dir():
            if any(target.iterdir()):
                return (f"'{target.name}' is not empty any more — "
                        f"leaving it alone rather than deleting your files.")
            target.rmdir()
        else:
            target.unlink()
        return f"Removed '{target.name}'."
    return _fn


def _undo_write(target: Path, previous: str | None):
    """Reverse of a write: restore the old contents, or remove a file that did
    not exist before the write created it."""
    def _fn():
        if previous is None:
            if target.exists():
                target.unlink()
                return f"Removed '{target.name}' — it did not exist before."
            return f"'{target.name}' is already gone."
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(previous, encoding="utf-8")
        return f"Restored the previous contents of '{target.name}'."
    return _fn


def _restore_from_trash(original: Path) -> str:
    """Best-effort undelete."""
    if _OS == "Windows":
        try:
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            bin_folder = shell.NameSpace(10)      # ssfBITBUCKET
            for item in bin_folder.Items():
                if str(bin_folder.GetDetailsOf(item, 1)).strip().lower() == \
                        str(original.parent).strip().lower():
                    if str(item.Name).strip().lower() == original.name.strip().lower():
                        item.InvokeVerb("UNDELETE")
                        return f"'{original.name}' restored from the Recycle Bin."
        except Exception as e:
            print(f"[file] Recycle Bin restore failed: {e}")
    return (f"'{original.name}' is in the Recycle Bin — I could not pull it back "
            f"automatically, but it is there and can be restored by hand.")


def _get_desktop() -> Path:
    win_p = _win_known_folder("desktop")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DESKTOP_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Desktop"


def _get_downloads() -> Path:
    win_p = _win_known_folder("downloads")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DOWNLOAD_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Downloads"


def _get_documents() -> Path:
    win_p = _win_known_folder("documents")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DOCUMENTS_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Documents"


def _get_pictures() -> Path:
    win_p = _win_known_folder("pictures")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_PICTURES_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Pictures"


def _get_music() -> Path:
    win_p = _win_known_folder("music")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_MUSIC_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Music"


def _get_videos() -> Path:
    win_p = _win_known_folder("videos")
    if win_p is not None:
        return win_p
    if _OS == "Linux":
        xdg = os.environ.get("XDG_VIDEOS_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Videos"


_SAFE_ROOTS: list[Path] = [
    Path.home(),
]


def _effective_safe_roots() -> list[Path]:
    roots = list(_SAFE_ROOTS)
    for fn in (_get_desktop, _get_downloads, _get_documents, _get_pictures, _get_music, _get_videos):
        try:
            p = fn()
            if p not in roots:
                roots.append(p)
        except Exception:
            continue
    return roots


def _is_safe_path(target: Path) -> bool:
    """Is the given path inside _SAFE_ROOTS or a known user folder?"""
    try:
        resolved = target.resolve()
        return any(
            resolved == root.resolve() or resolved.is_relative_to(root.resolve())
            for root in _effective_safe_roots()
        )
    except Exception:
        return False


def _shortcuts_map() -> dict[str, Path]:
    dl = _get_downloads()
    dt = _get_desktop()
    dc = _get_documents()
    pc = _get_pictures()
    mu = _get_music()
    vd = _get_videos()
    return {
        "desktop":          dt,
        "my desktop":       dt,
        "downloads":        dl,
        "download":         dl,
        "my downloads":     dl,
        "downloads folder": dl,
        "desktop folder":   dt,
        "documents":        dc,
        "my documents":     dc,
        "documents folder": dc,
        "docs":             dc,
        "pictures":         pc,
        "photos":           pc,
        "my pictures":      pc,
        "music":            mu,
        "videos":           vd,
        "home":             Path.home(),
    }


def _resolve_path(raw: str) -> Path:
    shortcuts = _shortcuts_map()
    cleaned = (raw or "").strip().strip('"').strip("'")
    cleaned = re.sub(r"^(the|my)\s+", "", cleaned, flags=re.IGNORECASE).strip()
    lower = cleaned.lower().rstrip("/\\")
    if lower in shortcuts:
        return shortcuts[lower]

    norm = cleaned.replace("\\", "/")
    head, sep, rest = norm.partition("/")
    head_clean = re.sub(r"^(the|my)\s+", "", head.strip(), flags=re.IGNORECASE).lower()
    if sep and head_clean in shortcuts:
        rest = rest.strip("/")
        return shortcuts[head_clean] / rest if rest else shortcuts[head_clean]

    expanded = Path(os.path.expandvars(cleaned)).expanduser()
    return expanded


def _resolve_destination(src: Path, destination: str) -> Path:
    """Resolve `destination` smartly relative to `src.parent` when a bare folder
    or subfolder name is given (e.g. moving `Downloads/a.pdf` -> `Documents` or
    `Images` puts it in `Downloads/Documents` or `Downloads/Images`, NOT into
    JARVIS's working directory and NOT hijacked to `~/Documents` when a local
    `Downloads/Documents` subfolder exists or when organizing a folder)."""
    dest_raw = (destination or "").strip().strip('"').strip("'")
    norm = dest_raw.replace("\\", "/")
    is_bare_name = (
        "/" not in norm
        and ":" not in norm
        and not dest_raw.startswith("~")
    )
    if is_bare_name:
        low = dest_raw.lower()
        # Local subfolder inside src.parent always wins if it already exists
        local_sub = src.parent / dest_raw
        if local_sub.exists() and local_sub.is_dir():
            return local_sub
        # Top-level OS locations explicitly named ("downloads", "desktop", "home")
        if low in ("desktop", "my desktop", "downloads", "download", "my downloads", "home"):
            return _resolve_path(dest_raw)
        # Category names ("Images", "Archives", "Installers", "PDFs", "Invoices", etc.)
        # belong inside `src.parent`, NEVER inside JARVIS's CWD!
        if low not in _shortcuts_map() or low in ("documents", "pictures", "music", "videos"):
            if low in ("documents", "pictures", "music", "videos") and not (src.parent == _get_downloads() or src.parent == _get_desktop()):
                return _resolve_path(dest_raw)
            if low not in _shortcuts_map():
                return local_sub

    resolved = _resolve_path(dest_raw)
    if not resolved.is_absolute():
        return src.parent / dest_raw
    return resolved


def _unique_dest_path(dst: Path) -> Path:
    """Return `dst` if unused, otherwise `stem (2).ext`, `stem (3).ext`, etc."""
    if not dst.exists():
        return dst
    stem = dst.stem
    suffix = dst.suffix
    parent = dst.parent
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _format_size(b: int) -> str:
    val = float(b)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024:
            return f"{val:.1f} {unit}"
        val /= 1024
    return f"{val:.1f} TB"


def _safe_trash(target: Path) -> str:
    if not _SEND2TRASH:
        return (
            "send2trash is not installed. "
            "Run: pip install send2trash — "
            "Permanent deletion is disabled for safety."
        )
    send2trash.send2trash(str(target))
    return f"Moved to Trash: {target.name}"


def list_files(path: str = "desktop", show_hidden: bool = False) -> str:
    try:
        target = _resolve_path(path)
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        if not target.exists():
            return f"Path not found: {target}"
        if not target.is_dir():
            return f"Not a directory: {target}"

        items = []
        for item in sorted(target.iterdir()):
            if not show_hidden and item.name.startswith("."):
                continue
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = _format_size(item.stat().st_size)
                items.append(f"📄 {item.name} ({size})")

        if not items:
            return f"Directory is empty: {target} ({target.name}/)"

        return f"Contents of {target} ({len(items)} items):\n" + "\n".join(items)

    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error listing files: {e}"


def create_file(path: str, name: str = "", content: str = "") -> str:
    try:
        if not path:
            return "Specify 'path' (for example 'downloads', 'desktop', or a folder path)."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        previous = None
        if existed:
            try:
                previous = target.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                previous = None
        target.write_text(content, encoding="utf-8")
        push_undo(f"created {target.name}",
                  _undo_write(target, previous) if existed else _undo_create(target))
        return f"File created: {target}"
    except Exception as e:
        return f"Could not create file: {e}"


def create_folder(path: str, name: str = "") -> str:
    try:
        if not path and not name:
            return "Specify 'path' (for example 'downloads/Images' or path='downloads', name='Images')."
        if not path and name:
            if "/" in name or "\\" in name:
                target = _resolve_path(name)
            else:
                return (
                    f"Specify which parent folder to create '{name}' inside via 'path' "
                    f"(e.g. path='downloads' or path='desktop') — refusing to guess Desktop."
                )
        else:
            base = _resolve_path(path)
            target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        already = target.exists()
        target.mkdir(parents=True, exist_ok=True)
        if not already:
            push_undo(f"created folder {target.name}", _undo_create(target))
        return f"Folder created: {target}"
    except Exception as e:
        return f"Could not create folder: {e}"


def delete_file(path: str, name: str = "") -> str:
    try:
        if not path:
            return "Specify 'path' of the file or folder to delete."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        if not target.exists():
            return f"Not found: {target}"

        protected = {
            _get_desktop(), _get_downloads(), _get_documents(),
            _get_pictures(), _get_music(), _get_videos(), Path.home()
        }
        if target.resolve() in {p.resolve() for p in protected}:
            return f"Protected directory, cannot delete: {target.name}"

        original = target.resolve()
        result = _safe_trash(target)
        if result.startswith("Moved to Trash"):
            push_undo(f"deleted {original.name}",
                      lambda p=original: _restore_from_trash(p))
        return result

    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Could not delete: {e}"


def _move_single(src: Path, destination: str) -> tuple[bool, str, tuple[Path, Path] | None]:
    if not src.exists():
        return False, f"Source not found: {src}", None
    if not destination:
        return False, "No destination specified.", None

    dst_raw = destination.strip()
    dst = _resolve_destination(src, dst_raw)

    if not _is_safe_path(src):
        return False, f"Access denied (source): {src}", None
    if not _is_safe_path(dst):
        return False, f"Access denied (destination): {dst}", None

    treat_as_dir = (
        dst.is_dir()
        or dst_raw.endswith(("/", "\\"))
        or (not dst.exists() and dst.suffix == "")
    )
    if treat_as_dir:
        dst.mkdir(parents=True, exist_ok=True)
        final_dst = _unique_dest_path(dst / src.name)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        final_dst = _unique_dest_path(dst)

    if src.resolve() == final_dst.resolve():
        return True, f"Already in place: {src.name}", None

    origin = src.resolve()
    shutil.move(str(src), str(final_dst))
    return True, f"{origin.name} → {final_dst.parent.name}/{final_dst.name}", (origin, final_dst.resolve())


def move_file(
    path: str,
    name: str = "",
    destination: str = "",
    files: list[str] | None = None,
) -> str:
    try:
        if not path and not files:
            return "Specify 'path' (e.g. 'downloads' or 'downloads/report.pdf') and 'destination'."
        if not destination:
            return "No destination specified."

        if files:
            base = _resolve_path(path) if path else None
            moved_msgs: list[str] = []
            errors: list[str] = []
            journal: list[tuple[Path, Path]] = []
            for f_item in files:
                src = (base / f_item) if (base and not Path(f_item).is_absolute() and "/" not in f_item and "\\" not in f_item) else _resolve_path(f_item)
                ok, msg, pair = _move_single(src, destination)
                if ok:
                    moved_msgs.append(msg)
                    if pair:
                        journal.append(pair)
                else:
                    errors.append(msg)
            if journal:
                def _undo_batch(entries=tuple(journal)):
                    restored = 0
                    for orig, cur in entries:
                        if cur.exists():
                            orig.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(cur), str(orig))
                            restored += 1
                    return f"Restored {restored} moved file(s)."
                push_undo(f"moved {len(journal)} file(s)", _undo_batch)
            summary = f"Moved {len(moved_msgs)} file(s)."
            if moved_msgs:
                summary += "\n" + "\n".join(moved_msgs[:10])
            if errors:
                summary += "\nErrors:\n" + "\n".join(errors[:5])
            return summary

        base = _resolve_path(path)
        src = (base / name) if name else base
        ok, msg, pair = _move_single(src, destination)
        if not ok:
            return msg
        if pair:
            origin, final_dst = pair
            push_undo(
                f"moved {origin.name} to {final_dst.parent.name}/",
                _undo_move(origin, final_dst),
            )
        return f"Moved: {msg}"

    except Exception as e:
        return f"Could not move: {e}"


def copy_file(path: str, name: str = "", destination: str = "") -> str:
    try:
        if not path:
            return "Specify 'path' of the source file or folder."
        if not destination:
            return "No destination specified."

        base = _resolve_path(path)
        src = (base / name) if name else base
        if not src.exists():
            return f"Source not found: {src}"

        dst = _resolve_destination(src, destination)
        if not _is_safe_path(src):
            return f"Access denied (source): {src}"
        if not _is_safe_path(dst):
            return f"Access denied (destination): {dst}"

        treat_as_dir = (
            dst.is_dir()
            or destination.strip().endswith(("/", "\\"))
            or (not dst.exists() and dst.suffix == "")
        )
        if treat_as_dir:
            dst.mkdir(parents=True, exist_ok=True)
            final_dst = _unique_dest_path(dst / src.name)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            final_dst = _unique_dest_path(dst)

        if src.is_dir():
            shutil.copytree(str(src), str(final_dst))
        else:
            shutil.copy2(str(src), str(final_dst))

        _copy = final_dst.resolve()

        def _undo_copy():
            if not _copy.exists():
                return f"The copy '{_copy.name}' is already gone."
            if _copy.is_dir():
                shutil.rmtree(_copy)
            else:
                _copy.unlink()
            return f"Removed the copy in {_copy.parent.name}/."

        push_undo(f"copied {src.name} to {final_dst.parent.name}/", _undo_copy)
        return f"Copied: {src.name} → {final_dst.parent.name}/{final_dst.name}"

    except Exception as e:
        return f"Could not copy: {e}"


def rename_file(path: str, name: str = "", new_name: str = "") -> str:
    try:
        if not path:
            return "Specify 'path' of the file or folder to rename."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        if not target.exists():
            return f"Not found: {target.name}"
        if not new_name:
            return "No new name provided."

        new_path = target.parent / new_name
        if new_path.exists():
            return f"A file named '{new_name}' already exists here."

        old_path = target.resolve()
        target.rename(new_path)
        push_undo(f"renamed {old_path.name} to {new_name}",
                  _undo_move(old_path, new_path.resolve()))
        return f"Renamed: {target.name} → {new_name}"

    except Exception as e:
        return f"Could not rename: {e}"


def read_file(path: str, name: str = "", max_chars: int = 4000) -> str:
    try:
        if not path:
            return "Specify 'path' of the file to read."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        if not target.exists():
            return f"File not found: {target.name}"
        if not target.is_file():
            return f"Not a file: {target.name}"

        content = target.read_text(encoding="utf-8", errors="ignore")
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n[Truncated — {len(content)} total chars]"
        return content

    except Exception as e:
        return f"Could not read file: {e}"


def write_file(path: str, name: str = "", content: str = "",
               append: bool = False) -> str:
    try:
        if not path:
            return "Specify 'path' of the file to write."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)

        previous: str | None = None
        undoable = True
        if target.exists():
            try:
                if target.stat().st_size > _UNDO_CONTENT_LIMIT:
                    undoable = False
                else:
                    previous = target.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                undoable = False

        mode = "a" if append else "w"
        with open(target, mode, encoding="utf-8") as f:
            f.write(content)

        action = "Appended to" if append else "Written to"
        if undoable:
            push_undo(f"wrote to {target.name}", _undo_write(target, previous))
            return f"{action}: {target.name}"
        return (f"{action}: {target.name}. "
                f"(Too large to keep a copy of the old contents, so this one "
                f"cannot be undone.)")
    except Exception as e:
        return f"Could not write file: {e}"


def find_files(name: str = "", extension: str = "",
               path: str = "home", max_results: int = 20) -> str:
    try:
        search_path = _resolve_path(path or "home")
        if not _is_safe_path(search_path):
            return f"Access denied: {search_path}"
        if not search_path.exists():
            return f"Search path not found: {path}"

        results = []
        dir_count = 0
        max_dirs = 500

        ext_norm = ""
        if extension:
            ext_norm = extension.lower() if extension.startswith(".") else f".{extension.lower()}"

        for item in search_path.rglob("*"):
            if item.is_dir():
                dir_count += 1
                if dir_count > max_dirs:
                    break
                continue
            if not item.is_file():
                continue
            if ext_norm and item.suffix.lower() != ext_norm:
                continue
            if name and name.lower() not in item.name.lower():
                continue
            size = _format_size(item.stat().st_size)
            results.append(f"📄 {item.name} ({size}) — {item.parent}")
            if len(results) >= max_results:
                break

        if not results:
            query = name or extension or "files"
            return f"No {query} found in {search_path.name}/"

        return f"Found {len(results)} file(s):\n" + "\n".join(results)

    except Exception as e:
        return f"Search error: {e}"


def get_largest_files(path: str = "downloads", count: int = 10) -> str:
    count = min(count, 50)
    try:
        search_path = _resolve_path(path or "downloads")
        if not _is_safe_path(search_path):
            return f"Access denied: {search_path}"
        if not search_path.exists():
            return f"Path not found: {path}"

        files = []
        for item in search_path.rglob("*"):
            if item.is_file():
                try:
                    files.append((item.stat().st_size, item))
                except Exception:
                    continue

        files.sort(reverse=True)
        top = files[:count]

        if not top:
            return "No files found."

        lines = [f"Top {len(top)} largest files in {search_path.name}/:"]
        for size, f in top:
            lines.append(f"  {_format_size(size):>10}  {f.name}  ({f.parent})")

        return "\n".join(lines)

    except Exception as e:
        return f"Error: {e}"


def get_disk_usage(path: str = "home") -> str:
    try:
        target = _resolve_path(path or "home")
        usage = shutil.disk_usage(target)
        pct = usage.used / usage.total * 100
        return (
            f"Disk usage ({target}):\n"
            f"  Total : {_format_size(usage.total)}\n"
            f"  Used  : {_format_size(usage.used)} ({pct:.1f}%)\n"
            f"  Free  : {_format_size(usage.free)}"
        )
    except Exception as e:
        return f"Could not get disk usage: {e}"


def _classify_extension(ext: str) -> str:
    ext_low = (ext or "").lower()
    for folder, exts in ORGANIZE_TYPE_MAP.items():
        if ext_low in exts:
            return folder
    return "Others"


def organize_folder(
    path: str,
    mode: str = "by_type",
    dry_run: bool = False,
) -> str:
    """Organize files inside ANY safe user folder (`Downloads`, `Desktop`,
    `Documents`, or a custom path) by file type or date.

    Guarantees:
    - Never defaults silently to Desktop when organizing another folder.
    - Never creates empty category folders — folders are created only when
      at least one real file moves into them.
    - Never overwrites or skips colliding filenames (appends ` (2)`, ` (3)`).
    - Skips shortcuts (`.lnk`/`.url`), incomplete downloads (`.crdownload`/`.part`),
      and active Office lockfiles (`~$*`).
    - Registers a single atomic Undo action reversing every move and removing
      newly created empty category folders.
    """
    if not path or not str(path).strip():
        return (
            "Please specify which folder to organize in 'path' "
            "(for example 'downloads', 'desktop', or 'documents') — "
            "refusing to guess Desktop."
        )

    try:
        folder = _resolve_path(path)
        if not _is_safe_path(folder):
            return f"Access denied: {folder}"
        if not folder.exists():
            return f"Folder not found: {folder}"
        if not folder.is_dir():
            return f"Not a directory: {folder}"

        mode_clean = (mode or "by_type").strip().lower()
        category_names = set(ORGANIZE_TYPE_MAP.keys()) | {"Others", "Music", "Executables"}
        plan: list[tuple[Path, str]] = []
        counts: dict[str, int] = {}
        untouched_shortcuts = 0

        for item in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if item.is_dir():
                continue
            nm = item.name
            nm_low = nm.lower()
            if nm.startswith(".") or nm.startswith("~$") or nm_low in _ORGANIZE_SKIP_NAMES:
                continue
            if nm in category_names:
                continue
            ext = item.suffix.lower()
            if ext in _ORGANIZE_SKIP_EXTS:
                untouched_shortcuts += 1
                continue

            if mode_clean in ("by_date", "date"):
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                cat = mtime.strftime("%Y-%m")
            else:
                cat = _classify_extension(ext)

            plan.append((item, cat))
            counts[cat] = counts.get(cat, 0) + 1

        if not plan:
            note = f" ({untouched_shortcuts} shortcut/in-progress file(s) left untouched)" if untouched_shortcuts else ""
            return f"Nothing to organize in {folder}{note} — no loose files found."

        if dry_run:
            breakdown = ", ".join(f"{cat}/ ({cnt})" for cat, cnt in sorted(counts.items()))
            preview_lines = [f"  • {it.name} → {cat}/" for it, cat in plan[:12]]
            more = f"\n  ... and {len(plan) - 12} more." if len(plan) > 12 else ""
            return (
                f"[DRY RUN] Would organize {len(plan)} file(s) inside {folder}:\n"
                f"Categories: {breakdown}\n"
                + "\n".join(preview_lines)
                + more
            )

        moved: list[str] = []
        renamed_collisions = 0
        created_dirs: list[Path] = []
        journal: list[tuple[Path, Path]] = []

        for item, cat in plan:
            target_dir = folder / cat
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                created_dirs.append(target_dir.resolve())

            desired = target_dir / item.name
            final_dst = _unique_dest_path(desired)
            if final_dst.name != item.name:
                renamed_collisions += 1

            origin = item.resolve()
            shutil.move(str(item), str(final_dst))
            journal.append((origin, final_dst.resolve()))
            moved.append(f"{item.name} → {cat}/{final_dst.name if final_dst.name != item.name else ''}".rstrip("/"))

        if journal:
            folder_label = folder.name or str(folder)

            def _undo_organize(entries=tuple(journal), made_dirs=tuple(created_dirs), label=folder_label):
                restored = 0
                for origin, moved_to in entries:
                    try:
                        if moved_to.exists():
                            origin.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(moved_to), str(origin))
                            restored += 1
                    except Exception as e:
                        print(f"[file] undo organize: {moved_to.name}: {e}")
                for d in set(made_dirs) | {m.parent for _o, m in entries}:
                    try:
                        if d.exists() and d.is_dir() and not any(d.iterdir()):
                            d.rmdir()
                    except Exception:
                        pass
                return f"{restored} file(s) restored back to {label}/."

            push_undo(f"organized {folder_label} ({len(journal)} files)", _undo_organize)

        breakdown = ", ".join(f"{cat}/ ({cnt})" for cat, cnt in sorted(counts.items()))
        result = f"Organized {folder} ({len(moved)} file(s) moved into {breakdown})."
        if moved:
            result += "\n" + "\n".join(moved[:10])
            if len(moved) > 10:
                result += f"\n... and {len(moved) - 10} more."
        if renamed_collisions:
            result += f"\n({renamed_collisions} duplicate filename(s) kept safely with numeric suffixes.)"
        return result

    except Exception as e:
        return f"Could not organize '{path}': {e}"


def organize_desktop(path: str = "desktop", mode: str = "by_type", dry_run: bool = False) -> str:
    """Backwards-compatible wrapper that honors explicit non-desktop paths if passed."""
    return organize_folder(path or "desktop", mode=mode, dry_run=dry_run)


def clean_empty_folders(path: str) -> str:
    """Remove empty top-level subdirectories in `path` (e.g. leftover empty folders on Desktop)."""
    if not path or not str(path).strip():
        return "Specify 'path' (e.g. 'desktop' or 'downloads') to clean empty folders."
    try:
        folder = _resolve_path(path)
        if not _is_safe_path(folder):
            return f"Access denied: {folder}"
        if not folder.exists() or not folder.is_dir():
            return f"Folder not found: {folder}"

        removed: list[Path] = []
        for item in sorted(folder.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                try:
                    if not any(item.iterdir()):
                        resolved = item.resolve()
                        item.rmdir()
                        removed.append(resolved)
                except Exception:
                    continue

        if not removed:
            return f"No empty folders found in {folder}."

        def _undo_clean(dirs=tuple(removed)):
            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)
            return f"Restored {len(dirs)} empty folder(s)."

        push_undo(f"removed {len(removed)} empty folder(s) in {folder.name}", _undo_clean)
        names = ", ".join(d.name for d in removed)
        return f"Removed {len(removed)} empty folder(s) from {folder}: {names}"
    except Exception as e:
        return f"Could not clean empty folders: {e}"


def get_file_info(path: str, name: str = "") -> str:
    try:
        if not path:
            return "Specify 'path' of the file or folder."
        base = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Access denied: {target}"
        if not target.exists():
            return f"Not found: {target.name}"

        stat = target.stat()
        info = {
            "Name":      target.name,
            "Type":      "Folder" if target.is_dir() else "File",
            "Size":      _format_size(stat.st_size),
            "Location":  str(target.parent),
            "Created":   datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
            "Modified":  datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "Extension": target.suffix or "—",
        }
        return "\n".join(f"  {k}: {v}" for k, v in info.items())

    except Exception as e:
        return f"Could not get file info: {e}"


def file_controller(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    action = str(params.get("action") or "").lower().strip()

    # Accept natural parameter aliases emitted by LLMs (folder, directory, source, target)
    # without silently falling back to "desktop" on mutating commands!
    explicit_path = (
        params.get("path")
        or params.get("folder")
        or params.get("directory")
        or params.get("source")
        or params.get("src")
        or params.get("target")
        or ""
    )
    explicit_path = str(explicit_path).strip()
    name = str(params.get("name") or params.get("filename") or "").strip()
    destination = str(
        params.get("destination")
        or params.get("dest")
        or params.get("to")
        or params.get("target_folder")
        or ""
    ).strip()
    mode = str(params.get("mode") or "by_type").strip()
    dry_run = bool(params.get("dry_run", False))
    files_arg = params.get("files") if isinstance(params.get("files"), list) else None

    if player:
        player.write_log(f"[file] {action} {name or explicit_path}")

    try:
        if action == "list":
            return list_files(explicit_path or "desktop", show_hidden=bool(params.get("show_hidden", False)))

        elif action == "create_file":
            return create_file(explicit_path, name=name, content=str(params.get("content") or ""))

        elif action == "create_folder":
            return create_folder(explicit_path, name=name)

        elif action == "delete":
            return delete_file(explicit_path, name=name)

        elif action == "move":
            return move_file(explicit_path, name=name, destination=destination, files=files_arg)

        elif action == "copy":
            return copy_file(explicit_path, name=name, destination=destination)

        elif action == "rename":
            return rename_file(explicit_path, name=name, new_name=str(params.get("new_name") or ""))

        elif action == "read":
            return read_file(explicit_path, name=name)

        elif action == "write":
            return write_file(
                explicit_path, name=name,
                content=str(params.get("content") or ""),
                append=bool(params.get("append", False)),
            )

        elif action == "find":
            return find_files(
                name=name,
                extension=str(params.get("extension") or ""),
                path=explicit_path or "home",
                max_results=min(int(params.get("max_results", 20)), 50),
            )

        elif action == "largest":
            return get_largest_files(
                path=explicit_path or "downloads",
                count=int(params.get("count", 10)),
            )

        elif action == "disk_usage":
            return get_disk_usage(explicit_path or "home")

        elif action in ("organize", "organize_folder"):
            return organize_folder(explicit_path, mode=mode, dry_run=dry_run)

        elif action == "organize_downloads":
            return organize_folder(explicit_path or "downloads", mode=mode, dry_run=dry_run)

        elif action == "organize_desktop":
            return organize_desktop(explicit_path or "desktop", mode=mode, dry_run=dry_run)

        elif action in ("clean_empty_folders", "remove_empty_folders"):
            return clean_empty_folders(explicit_path)

        elif action == "info":
            return get_file_info(explicit_path, name=name)

        elif action in ("open", "launch", "reveal"):
            from core.os_control import open_path_verified
            if not explicit_path and not name:
                return "Specify 'path' (e.g. 'downloads', 'desktop', or a file path) to open."
            base = _resolve_path(explicit_path) if explicit_path else Path.home()
            target = (base / name) if name else base
            if not _is_safe_path(target):
                return f"Access denied: {target}"
            return open_path_verified(str(target))["message"]

        else:
            return f"Unknown action: '{action}'"

    except Exception as e:
        return f"File controller error ({action}): {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "file_controller",
    "description": (
        "Manages and organizes files and folders in Downloads, Desktop, Documents, "
        "or any path under the user's home directory. Use action='organize' with "
        "path='downloads' (or 'desktop', 'documents', etc.) to sort loose files "
        "into category folders (Images, Documents, Installers, Archives, Videos, "
        "Audio, Code) safely in one undoable step without creating empty folders."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "organize | organize_downloads | organize_desktop | clean_empty_folders | "
                    "list | create_file | create_folder | delete | move | copy | rename | "
                    "read | write | find | largest | disk_usage | info | open"
                ),
            },
            "path": {
                "type": "STRING",
                "description": (
                    "Target folder or file path/shortcut: 'downloads', 'desktop', "
                    "'documents', 'pictures', 'videos', 'music', 'home', or a subpath "
                    "like 'downloads/report.pdf'. REQUIRED for organize/create/move/delete."
                ),
            },
            "name": {
                "type": "STRING",
                "description": "File or subfolder name within 'path' (for create_folder, move, delete, rename, read, find).",
            },
            "destination": {
                "type": "STRING",
                "description": "Destination folder or path for move/copy (e.g. 'downloads/Documents' or subfolder 'Images').",
            },
            "files": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Optional batch list of filenames inside 'path' to move together.",
            },
            "mode": {
                "type": "STRING",
                "description": "For organize: 'by_type' (default) or 'by_date' (YYYY-MM folders).",
            },
            "dry_run": {
                "type": "BOOLEAN",
                "description": "If true on action='organize', previews counts & planned moves without moving files yet.",
            },
            "new_name": {
                "type": "STRING",
                "description": "New filename for action='rename'.",
            },
            "content": {
                "type": "STRING",
                "description": "Text content for create_file or write.",
            },
            "extension": {
                "type": "STRING",
                "description": "File extension filter for action='find' (e.g. '.pdf').",
            },
            "count": {
                "type": "INTEGER",
                "description": "Number of results for action='largest'.",
            },
        },
        "required": ["action"],
    },
    "handler": file_controller,
}
