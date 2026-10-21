"""
Plugin marketplace — Phase 7.2: one-click install, versioned, isolated.
"""
import pathlib, json, requests, shutil, zipfile, time

REGISTRY_URL = "https://raw.githubusercontent.com/mafk21/OS-marketplace/main/registry.json"
INSTALL_DIR = pathlib.Path("plugins")
CACHE = pathlib.Path("memory/marketplace_cache.json")

def _fetch_registry():
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < 3600:
        return json.loads(CACHE.read_text())
    try:
        r = requests.get(REGISTRY_URL, timeout=10)
        if r.ok:
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(r.text)
            return r.json()
    except: pass
    return {"plugins":[]}

def list_marketplace():
    return _fetch_registry().get("plugins", [])

def install_plugin(name: str, version: str = "latest"):
    reg = _fetch_registry()
    for p in reg.get("plugins", []):
        if p["name"] == name:
            url = p.get("zip_url","") or p.get("url","")
            if not url: return f"Plugin {name} has no download URL"
            try:
                zpath = pathlib.Path(f"memory/{name}.zip")
                zpath.parent.mkdir(parents=True, exist_ok=True)
                data = requests.get(url, timeout=30).content
                zpath.write_bytes(data)
                with zipfile.ZipFile(zpath) as z:
                    z.extractall(INSTALL_DIR / name)
                return f"Installed {name}@{version} to plugins/{name} — restart to load"
            except Exception as e: return f"Install failed: {e}"
    return f"Plugin {name} not found in marketplace"

def remove_plugin(name: str):
    target = INSTALL_DIR / name
    if not target.exists(): return f"Plugin {name} not installed"
    shutil.rmtree(target)
    return f"Removed {name}"
