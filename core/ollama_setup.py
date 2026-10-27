"""User-authorized, unprivileged Ollama bootstrap. No shell or approval tokens.

Only official release assets + a bounded model catalog are accepted. Cloud voice
settings/keys are not replaced. Completion requires a real local inference.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import threading
import time
import uuid
import zipfile

import httpx
import psutil

URL = "http://127.0.0.1:11434"
RELEASE = "https://api.github.com/repos/ollama/ollama/releases/latest"
ROOT = Path.home()/".jarvis"/"ollama"
# Approximate download sizes, not benchmark claims or universal quality rankings.
MODELS = {"qwen3:0.6b": .6, "qwen3:1.7b": 1.5, "qwen3:4b": 3., "qwen3:8b": 5.5,
          "qwen3:14b": 10., "qwen3:30b-a3b": 20.}
_LOCK = threading.Lock()
_ACTIVE = {}


class Cancelled(RuntimeError):
    pass


def check(event):
    if event.is_set():
        raise Cancelled("Ollama setup cancelled. Existing models/configuration were not removed.")


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+"."+uuid.uuid4().hex+".tmp")
    try:
        with temp.open("x", encoding="utf-8") as stream:
            os.chmod(temp, 0o600)
            json.dump(value, stream, indent=2)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def hardware():
    vm = psutil.virtual_memory()
    vram = 0.
    nvidia = shutil.which("nvidia-smi")
    if nvidia:
        try:
            result = subprocess.run([nvidia, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                                    capture_output=True, text=True, timeout=8, check=True)
            vram = max(float(v.strip())/1024 for v in result.stdout.splitlines() if v.strip())
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    return {"ram_gb": round(vm.total/2**30, 1), "available_gb": round(vm.available/2**30, 1),
            "gpu_free_gb": round(vram, 1), "system": platform.system(), "arch": platform.machine()}


def choose_model(hw):
    free, total, gpu = hw["available_gb"], hw["ram_gb"], hw["gpu_free_gb"]
    if gpu >= 23 and free >= 26 and total >= 32:
        return "qwen3:30b-a3b"
    if gpu >= 12 and free >= 18 and total >= 32:
        return "qwen3:14b"
    if free >= 10 and total >= 16:
        return "qwen3:8b"
    if free >= 6:
        return "qwen3:4b"
    if free >= 3.5:
        return "qwen3:1.7b"
    if free >= 2:
        return "qwen3:0.6b"
    raise RuntimeError("Less than 2 GiB RAM available. Close memory-heavy apps before local-model setup.")


def executable():
    try:
        saved = json.loads((ROOT/"install.json").read_text())["executable"]
        path = Path(saved).resolve()
        if path.is_relative_to((ROOT/"runtime").resolve()) and path.is_file():
            return str(path)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    found = shutil.which("ollama")
    if found:
        return found
    for path in (Path(os.environ.get("LOCALAPPDATA", str(Path.home())))/"Programs"/"Ollama"/"ollama.exe",
                 Path("/Applications/Ollama.app/Contents/Resources/ollama")):
        if path.is_file():
            return str(path)
    return None


def client():
    # Never use proxy environment variables to reach a local unauthenticated API.
    return httpx.Client(base_url=URL, trust_env=False, follow_redirects=False, timeout=httpx.Timeout(30, connect=3))


def healthy(api):
    try:
        version = api.get("/api/version")
        tags = api.get("/api/tags")
        return (version.status_code == 200 and isinstance(version.json().get("version"), str)
                and tags.status_code == 200 and isinstance(tags.json().get("models"), list))
    except (httpx.HTTPError, ValueError, AttributeError):
        return False


def asset_name(system, arch):
    arch = arch.lower()
    cpu = "amd64" if arch in ("amd64", "x86_64") else "arm64" if arch in ("arm64", "aarch64") else None
    if system == "Windows" and cpu:
        return f"ollama-windows-{cpu}.zip"
    if system == "Linux" and cpu:
        return f"ollama-linux-{cpu}.tar.zst"
    if system == "Darwin" and cpu:
        return "ollama-darwin.tgz"
    raise RuntimeError(f"No supported unprivileged Ollama runtime for {system}/{arch}.")


def extract(archive, folder, event):
    """Bounded extraction; no absolute paths, escaping links or special devices."""
    folder.mkdir(parents=True, exist_ok=True)
    def target(name):
        if "\\" in name or ":" in name or name.startswith("/"):
            raise ValueError("Unsafe archive path")
        path = (folder/name).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError("Archive path escapes installation directory")
        return path
    used = 0
    def copy(source, dest, size):
        nonlocal used
        used += size
        if used > 16*2**30:
            raise ValueError("Archive exceeds 16 GiB extraction budget")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as out:
            while chunk := source.read(1024*1024):
                check(event)
                out.write(chunk)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                check(event)
                dest = target(member.filename)
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("ZIP symlinks are not supported")
                if member.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    with z.open(member) as source:
                        copy(source, dest, member.file_size)
        return
    import contextlib
    with contextlib.ExitStack() as stack:
        source = stack.enter_context(archive.open("rb"))
        if archive.name.endswith(".zst"):
            import zstandard
            source = stack.enter_context(zstandard.ZstdDecompressor().stream_reader(source))
            tar = stack.enter_context(tarfile.open(fileobj=source, mode="r|"))
        else:
            tar = stack.enter_context(tarfile.open(fileobj=source, mode="r|gz"))
        for member in tar:
            check(event)
            dest = target(member.name)
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                with tar.extractfile(member) as data:
                    copy(data, dest, member.size)
                dest.chmod(member.mode & 0o755)  # Never retain setuid/setgid bits.
            elif member.issym() or member.islnk():
                if member.issym():
                    linked = target(str(Path(member.name).parent/member.linkname))
                else:
                    linked = target(member.linkname)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if member.issym():
                    dest.symlink_to(os.path.relpath(linked, dest.parent))
                else:
                    os.link(linked, dest)
            else:
                raise ValueError("Unsupported archive entry")


def install(hw, event, progress):
    name = asset_name(hw["system"], hw["arch"])
    progress("resolving_official_release", {})
    with httpx.Client(trust_env=False, follow_redirects=True, timeout=60) as net:
        response = net.get(RELEASE, headers={"Accept":"application/vnd.github+json"})
        response.raise_for_status()
        release = response.json()
        tag = release.get("tag_name", "")
        if not re.fullmatch(r"v[0-9][A-Za-z0-9._-]{0,60}", tag):
            raise RuntimeError("Official release metadata had an invalid version")
        asset = next((a for a in release.get("assets", []) if a.get("name") == name), None)
        if not asset or not re.fullmatch(r"sha256:[a-f0-9]{64}", asset.get("digest") or ""):
            raise RuntimeError("No official runtime asset with a SHA-256 digest is available; no unverified installer ran.")
        url = asset.get("browser_download_url", "")
        if url != f"https://github.com/ollama/ollama/releases/download/{tag}/{name}":
            raise RuntimeError("Release asset URL is not an official Ollama download")
        size = int(asset.get("size", 0))
        if not 0 < size <= 3*2**30:
            raise RuntimeError("Runtime asset exceeds supported download size")
        ROOT.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(ROOT).free < size*4+5*2**30:
            raise RuntimeError("Insufficient disk for runtime download/extraction plus 5 GiB reserve")
        staging = ROOT/("install-"+uuid.uuid4().hex)
        staging.mkdir()
        archive = staging/name
        try:
            digest = hashlib.sha256()
            received = 0
            progress("downloading_runtime", {"release":tag, "download_bytes":size})
            with net.stream("GET", url) as stream, archive.open("wb") as out:
                stream.raise_for_status()
                deadline = time.monotonic()+3600
                for chunk in stream.iter_bytes(1024*1024):
                    check(event)
                    if time.monotonic() > deadline:
                        raise TimeoutError("Runtime download exceeded one hour")
                    received += len(chunk)
                    if received > size:
                        raise RuntimeError("Runtime download exceeded official size")
                    digest.update(chunk)
                    out.write(chunk)
                    progress("downloading_runtime", {"runtime_received_bytes":received})
            if received != size or digest.hexdigest() != asset["digest"].split(":")[1]:
                raise RuntimeError("Runtime SHA-256/size verification failed; installer was not executed")
            progress("extracting_runtime", {})
            extract(archive, staging/"runtime", event)
            candidates = list((staging/"runtime").rglob("ollama.exe" if hw["system"] == "Windows" else "ollama"))
            binaries = [p for p in candidates if p.is_file() and not p.is_symlink()]
            if len(binaries) != 1:
                raise RuntimeError("Official archive did not contain one unique Ollama executable")
            relative = binaries[0].relative_to(staging/"runtime")
            destination = ROOT/"runtime"/(tag+"-"+uuid.uuid4().hex[:8])
            destination.parent.mkdir(parents=True, exist_ok=True)
            (staging/"runtime").rename(destination)
            binary = destination/relative
            binary.chmod(binary.stat().st_mode | 0o700)
            atomic(ROOT/"install.json", {"release":tag, "executable":str(binary)})
            return str(binary)
        finally:
            shutil.rmtree(staging, ignore_errors=True)


def launch(binary):
    ROOT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(OLLAMA_HOST="127.0.0.1:11434", OLLAMA_NO_CLOUD="1",
               OLLAMA_ORIGINS="http://localhost,http://127.0.0.1")
    kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session":True}
    with (ROOT/"server.log").open("ab") as log:
        return subprocess.Popen([binary, "serve"], stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                env=env, shell=False, **kwargs)


def persist(model, activate):
    from memory import config_manager as cfg
    # Preserve encrypted values as stored, rather than decrypting and writing keys.
    with _LOCK:
        path = cfg.CONFIG_FILE
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if not isinstance(data, dict):
            raise ValueError("Existing configuration is not an object; it was not overwritten")
        data.update(llm_provider="ollama", llm_url=URL, llm_model=model, offline_fallback=True)
        if activate:
            data["provider"] = "local"
        atomic(path, data)


def run(event, progress, model="auto", activate=False):
    hw = hardware()
    selected = choose_model(hw) if model == "auto" else model
    if selected not in MODELS:
        raise ValueError("Choose auto or a supported local model")
    if hw["available_gb"] < MODELS[selected]*1.3:
        raise RuntimeError("Selected model does not fit currently available RAM conservatively; use auto or close apps")
    progress("hardware_plan", {"hardware":hw, "model":selected, "estimated_model_gb":MODELS[selected]})
    owned = None
    configured = False
    with client() as api:
        try:
            check(event)
            if not healthy(api):
                binary = executable() or install(hw, event, progress)
                check(event)
                progress("starting_local_server", {})
                owned = launch(binary)
                deadline = time.monotonic()+45
                while not healthy(api):
                    check(event)
                    if owned.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError("Ollama server failed to start. Inspect ~/.jarvis/ollama/server.log; no readiness claimed.")
                    event.wait(.5)
            progress("checking_model", {})
            response = api.get("/api/tags"); response.raise_for_status()
            installed = {m.get("name") for m in response.json().get("models", [])}
            if selected not in installed:
                models = Path(os.environ.get("OLLAMA_MODELS", str(Path.home()/".ollama"/"models"))).expanduser()
                disk = models
                while not disk.exists():
                    disk = disk.parent
                if shutil.disk_usage(disk).free < (MODELS[selected]+5)*2**30:
                    raise RuntimeError("Insufficient model storage plus 5 GiB reserve")
                progress("pulling_model", {})
                with api.stream("POST", "/api/pull", json={"name":selected, "stream":True}, timeout=60) as stream:
                    stream.raise_for_status()
                    success = False
                    deadline = time.monotonic()+7200
                    for line in stream.iter_lines():
                        check(event)
                        if time.monotonic() > deadline:
                            raise TimeoutError("Model download exceeded two hours")
                        if not line:
                            continue
                        item = json.loads(line)
                        if item.get("error"):
                            raise RuntimeError("Ollama model pull failed: "+str(item["error"])[:200])
                        if item.get("status") == "success":
                            success = True
                        progress("pulling_model", {k:item[k] for k in ("completed","total") if k in item})
                    if not success:
                        raise RuntimeError("Model download ended without Ollama success acknowledgment")
            check(event)
            progress("testing_inference", {})
            response = api.post("/api/chat", json={"model":selected, "messages":[{"role":"user", "content":"Reply with READY."}],
                "stream":False, "think":False, "options":{"num_ctx":4096, "num_predict":64}}, timeout=300)
            response.raise_for_status()
            data = response.json()
            if data.get("error") or data.get("done") is not True or not (data.get("message") or {}).get("content", "").strip():
                raise RuntimeError("Local model did not complete a nonempty inference; configuration was not changed")
            check(event)
            persist(selected, activate)
            configured = True
            return {"model":selected, "url":URL, "inference_verified":True,
                    "mode":"local_text_provider" if activate else "offline_fallback", "hardware":hw,
                    "note":"Cloud live voice remains separate. Hardware-based selection, not a universal best-model benchmark."}
        finally:
            # Never stop an existing user server. Only clean up our own failed setup.
            if owned is not None and not configured and owned.poll() is None:
                owned.terminate()
                try:
                    owned.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    owned.kill()
                    owned.wait(timeout=5)


def status(job_id):
    if not re.fullmatch(r"[a-f0-9]{16}", str(job_id)):
        raise ValueError("Use a job_id returned by Ollama setup")
    path = ROOT/"jobs"/(job_id+".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    with _LOCK:
        active = job_id in _ACTIVE
    if data["status"] in ("queued", "running") and not active:
        data.update(status="interrupted", stage="interrupted", error="JARVIS restarted before setup completed")
        atomic(path, data)
    return data


def start(model="auto", activate=False, notify=None):
    if model != "auto" and model not in MODELS:
        raise ValueError("Unsupported model; use auto")
    if not isinstance(activate, bool):
        raise ValueError("activate must be a boolean")
    with _LOCK:
        if _ACTIVE:
            job_id = next(iter(_ACTIVE))
            return {"job_id":job_id, "status":"already_running", "message":"Existing setup retained; no duplicate installation started."}
        job_id = uuid.uuid4().hex[:16]
        event = threading.Event()
        _ACTIVE[job_id] = event
    path = ROOT/"jobs"/(job_id+".json")
    data = {"job_id":job_id, "status":"queued", "stage":"queued", "created_at":time.time()}
    try:
        atomic(path, data)
    except Exception:
        with _LOCK:
            _ACTIVE.pop(job_id, None)
        raise
    def worker():
        last = [0., ""]
        def progress(stage, extra):
            check(event)
            data.update(status="running", stage=stage, updated_at=time.time(), **extra)
            now = time.monotonic()
            if stage != last[1] or now-last[0] >= 2:
                atomic(path, data)
                last[:] = [now, stage]
                if notify:
                    try:
                        notify(dict(data))
                    except Exception:
                        pass
        try:
            result = run(event, progress, model, activate)
            data.update(status="completed", stage="verified", **result)
        except Cancelled as exc:
            data.update(status="cancelled", stage="cancelled", error=str(exc))
        except Exception as exc:
            data.update(status="failed", stage="failed", error=f"{type(exc).__name__}: {str(exc)[:400]}")
        finally:
            data["updated_at"] = time.time()
            try:
                atomic(path, data)
            finally:
                with _LOCK:
                    _ACTIVE.pop(job_id, None)
        if notify:
            try:
                notify(dict(data))
            except Exception:
                pass
    threading.Thread(target=worker, daemon=True, name="ollama-setup-"+job_id).start()
    return {"job_id":job_id, "status":"queued", "message":"Ollama setup started without another approval. Not ready until status completed."}


def cancel(job_id):
    data = status(job_id)
    with _LOCK:
        event = _ACTIVE.get(job_id)
        if event:
            event.set()
    return {"job_id":job_id, "status":"cancellation_requested" if event else data["status"],
            "note":"A pending HTTP read may take its timeout to notice cancellation; partial model blobs can remain resumable."}


def doctor():
    with client() as api:
        ready = healthy(api)
    return {"server_ready":ready, "url":URL, "executable":executable(), "hardware":hardware(),
            "note":"Server health alone does not prove the selected model is installed or inference works."}
