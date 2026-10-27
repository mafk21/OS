"""No real installers, model downloads, external servers or approval UI in tests."""
import io
import json
from pathlib import Path
import tarfile
import threading
import time
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

import httpx
import pytest

from core import ollama_setup as setup


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(setup, "ROOT", tmp_path/"ollama")
    monkeypatch.setattr(setup, "_ACTIVE", {})
    monkeypatch.setattr(setup.shutil, "disk_usage", lambda _:SimpleNamespace(free=100*2**30))
    monkeypatch.setattr(setup, "hardware", lambda:{"ram_gb":16,"available_gb":11,"gpu_free_gb":0,"system":"Windows","arch":"AMD64"})


@pytest.mark.parametrize("free,gpu,total,model", [(2,0,8,"0.6b"),(4,0,8,"1.7b"),(6,0,12,"4b"),
    (11,0,16,"8b"),(20,14,32,"14b"),(28,24,64,"30b-a3b"),(28,0,64,"8b")])
def test_auto_fit_is_not_just_largest_model(free,gpu,total,model):
    assert setup.choose_model({"available_gb":free,"ram_gb":total,"gpu_free_gb":gpu})=="qwen3:"+model


def test_low_memory_fails():
    with pytest.raises(RuntimeError,match="2 GiB"):
        setup.choose_model({"available_gb":1,"ram_gb":4,"gpu_free_gb":0})


def test_model_and_boolean_parameters_cannot_be_shell(monkeypatch):
    with pytest.raises(ValueError):
        setup.start("qwen3; rm -rf /",False)
    with pytest.raises(ValueError):
        setup.start("auto","false")
    assert not setup._ACTIVE


@pytest.mark.parametrize("name", ["../outside", "/outside", "C:/outside", "..\\outside"])
def test_zip_cannot_escape_user_install(tmp_path,name):
    archive=tmp_path/"runtime.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr(name,"unsafe")
    with pytest.raises(ValueError):
        setup.extract(archive,tmp_path/"extract",threading.Event())
    assert not (tmp_path/"outside").exists()


def test_tar_rejects_escaping_symlink(tmp_path):
    archive=tmp_path/"runtime.tgz"
    with tarfile.open(archive,"w:gz") as tar:
        member=tarfile.TarInfo("bin/escape")
        member.type=tarfile.SYMTYPE;member.linkname="../../outside"
        tar.addfile(member)
    with pytest.raises(ValueError):
        setup.extract(archive,tmp_path/"extract",threading.Event())


def test_safe_tar_preserves_executable_but_not_setuid(tmp_path):
    archive=tmp_path/"runtime.tgz"
    with tarfile.open(archive,"w:gz") as tar:
        member=tarfile.TarInfo("bin/ollama");member.mode=0o4755;member.size=2
        tar.addfile(member,io.BytesIO(b"ok"))
    setup.extract(archive,tmp_path/"extract",threading.Event())
    binary=tmp_path/"extract/bin/ollama"
    assert binary.read_bytes()==b"ok"
    assert binary.stat().st_mode & 0o4000==0


def test_cancelled_extraction_does_not_run_anything(tmp_path):
    archive=tmp_path/"runtime.zip"
    with zipfile.ZipFile(archive,"w") as z:z.writestr("ollama.exe","not executed")
    event=threading.Event();event.set()
    with pytest.raises(setup.Cancelled):setup.extract(archive,tmp_path/"extract",event)


def test_launch_is_loopback_fixed_command_and_not_shell(monkeypatch):
    child=Mock()
    popen=Mock(return_value=child)
    monkeypatch.setenv("OLLAMA_HOST","0.0.0.0:11434")
    monkeypatch.setattr(setup.subprocess,"Popen",popen)
    assert setup.launch("/user/runtime/ollama")==child
    assert popen.call_args.args[0]==["/user/runtime/ollama","serve"]
    assert popen.call_args.kwargs["shell"] is False
    assert popen.call_args.kwargs["env"]["OLLAMA_HOST"]=="127.0.0.1:11434"


def api(monkeypatch, *, installed=False, pull_error=False, inference=True):
    requests=[]
    def handler(request):
        requests.append(request)
        if request.url.path=="/api/version":return httpx.Response(200,json={"version":"fixture"})
        if request.url.path=="/api/tags":return httpx.Response(200,json={"models":[{"name":"qwen3:8b"}] if installed else []})
        if request.url.path=="/api/pull":
            return httpx.Response(200,text=json.dumps({"error":"fixture failure"} if pull_error else {"status":"success"})+"\n")
        if request.url.path=="/api/chat":
            return httpx.Response(200,json={"done":inference,"message":{"content":"READY" if inference else ""}})
        raise AssertionError(str(request.url))
    monkeypatch.setattr(setup,"client",lambda:httpx.Client(base_url=setup.URL,transport=httpx.MockTransport(handler)))
    return requests


def test_full_existing_server_pull_inference_then_configure(monkeypatch):
    requests=api(monkeypatch)
    save=Mock()
    monkeypatch.setattr(setup,"persist",save)
    monkeypatch.setattr(setup,"install",Mock(side_effect=AssertionError("Already running")))
    result=setup.run(threading.Event(),lambda *a:None)
    assert result["inference_verified"] is True
    save.assert_called_once_with("qwen3:8b",False)
    assert [r.url.path for r in requests][-2:]==["/api/pull","/api/chat"]


def test_existing_model_not_downloaded_again(monkeypatch):
    requests=api(monkeypatch,installed=True)
    monkeypatch.setattr(setup,"persist",Mock())
    setup.run(threading.Event(),lambda *a:None)
    assert not any(r.url.path=="/api/pull" for r in requests)


@pytest.mark.parametrize("kind", ["pull","inference"])
def test_failure_never_overwrites_working_provider(monkeypatch,kind):
    api(monkeypatch,pull_error=kind=="pull",inference=kind!="inference")
    save=Mock();monkeypatch.setattr(setup,"persist",save)
    with pytest.raises(RuntimeError):setup.run(threading.Event(),lambda *a:None)
    save.assert_not_called()


def test_preserves_cloud_keys_and_provider_unless_explicit(tmp_path,monkeypatch):
    from memory import config_manager as cfg
    path=tmp_path/"config.json"
    path.write_text(json.dumps({"provider":"gemini","gemini_api_key":{"encrypted":"unchanged"},"voice":"Charon"}))
    monkeypatch.setattr(cfg,"CONFIG_FILE",path)
    setup.persist("qwen3:8b",False)
    saved=json.loads(path.read_text())
    assert saved["provider"]=="gemini" and saved["voice"]=="Charon"
    assert saved["gemini_api_key"]=={"encrypted":"unchanged"}
    assert saved["llm_url"]==setup.URL and saved["llm_model"]=="qwen3:8b"
    setup.persist("qwen3:8b",True)
    assert json.loads(path.read_text())["provider"]=="local"


def test_corrupt_configuration_is_not_replaced(tmp_path,monkeypatch):
    from memory import config_manager as cfg
    path=tmp_path/"config.json";path.write_text("broken")
    monkeypatch.setattr(cfg,"CONFIG_FILE",path)
    with pytest.raises(ValueError):setup.persist("qwen3:8b",False)
    assert path.read_text()=="broken"


def test_queued_is_not_completed_and_duplicate_start_is_suppressed(monkeypatch):
    started=threading.Event();release=threading.Event()
    def run(event,*args):
        started.set();release.wait(3)
        setup.check(event)
        return {"inference_verified":True}
    monkeypatch.setattr(setup,"run",run)
    first=setup.start();assert first["status"]=="queued"
    assert started.wait(2)
    second=setup.start()
    assert second["job_id"]==first["job_id"] and second["status"]=="already_running"
    assert setup.cancel(first["job_id"])["status"]=="cancellation_requested"
    release.set()
    deadline=time.monotonic()+3
    while setup.status(first["job_id"])["status"] in ("queued","running") and time.monotonic()<deadline:time.sleep(.01)
    assert setup.status(first["job_id"])["status"]=="cancelled"


def test_interrupted_job_never_claims_ready():
    job="a"*16
    setup.atomic(setup.ROOT/"jobs"/(job+".json"),{"job_id":job,"status":"running"})
    assert setup.status(job)["status"]=="interrupted"


def test_action_has_no_approval_gate(monkeypatch):
    from actions.ollama_setup import ollama_setup
    start=Mock(return_value={"status":"queued","job_id":"a"*16})
    monkeypatch.setattr(setup,"start",start)
    assert json.loads(ollama_setup({"action":"setup"}))["status"]=="queued"
    start.assert_called_once()
    assert "confirm" not in Path("core/ollama_setup.py").read_text().lower()


@pytest.mark.parametrize("valid_digest", [True,False])
def test_official_portable_download_verified_before_install(tmp_path,monkeypatch,valid_digest):
    import hashlib
    archive=io.BytesIO()
    with zipfile.ZipFile(archive,"w") as z:z.writestr("ollama.exe",b"fixture binary not executed")
    content=archive.getvalue()
    digest=hashlib.sha256(content).hexdigest() if valid_digest else "0"*64
    url="https://github.com/ollama/ollama/releases/download/v1.2.3/ollama-windows-amd64.zip"
    def handler(request):
        if str(request.url)==setup.RELEASE:
            return httpx.Response(200,json={"tag_name":"v1.2.3","assets":[{"name":"ollama-windows-amd64.zip",
                "size":len(content),"digest":"sha256:"+digest,"browser_download_url":url}]})
        assert str(request.url)==url
        return httpx.Response(200,content=content)
    original=httpx.Client
    monkeypatch.setattr(setup.httpx,"Client",lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    if valid_digest:
        binary=setup.install(setup.hardware(),threading.Event(),lambda *a:None)
        assert Path(binary).read_bytes()==b"fixture binary not executed"
        assert setup.executable()==binary
    else:
        with pytest.raises(RuntimeError,match="SHA-256"):
            setup.install(setup.hardware(),threading.Event(),lambda *a:None)
        assert not (setup.ROOT/"install.json").exists()
    assert not list(setup.ROOT.glob("install-*"))


def test_release_cannot_redirect_to_arbitrary_installer(monkeypatch):
    original=httpx.Client
    def handler(request):
        return httpx.Response(200,json={"tag_name":"v1.2.3","assets":[{"name":"ollama-windows-amd64.zip",
            "size":20,"digest":"sha256:"+"0"*64,"browser_download_url":"https://evil.invalid/install.exe"}]})
    monkeypatch.setattr(setup.httpx,"Client",lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    with pytest.raises(RuntimeError,match="not an official"):
        setup.install(setup.hardware(),threading.Event(),lambda *a:None)


def test_normal_local_client_restarts_user_runtime(monkeypatch):
    from core import llm_client
    monkeypatch.setattr(llm_client,"get_llm_settings",lambda:(setup.URL,"qwen3:8b"))
    monkeypatch.setattr(llm_client,"get_llm_provider",lambda:"ollama")
    monkeypatch.setattr(llm_client.requests,"get",Mock(side_effect=[SimpleNamespace(status_code=503),SimpleNamespace(status_code=200)]))
    monkeypatch.setattr(llm_client.time,"sleep",lambda _:None)
    monkeypatch.setattr(setup,"executable",lambda:"/private/verified/ollama")
    launch=Mock();monkeypatch.setattr(setup,"launch",launch)
    assert llm_client.ensure_ollama_running()
    launch.assert_called_once_with("/private/verified/ollama")


def test_nonlocal_config_does_not_start_unrelated_server(monkeypatch):
    from core import llm_client
    monkeypatch.setattr(llm_client,"get_llm_settings",lambda:("http://example.invalid:11434","model"))
    monkeypatch.setattr(llm_client,"get_llm_provider",lambda:"ollama")
    monkeypatch.setattr(llm_client.requests,"get",Mock(return_value=SimpleNamespace(status_code=503)))
    launch=Mock();monkeypatch.setattr(setup,"launch",launch)
    assert not llm_client.ensure_ollama_running()
    launch.assert_not_called()


def test_action_is_discoverable_and_nonblocking():
    from core.action_loader import discover_actions
    from actions.ollama_setup import TOOL
    registry=discover_actions(Path("actions"),logger=lambda _:None)
    assert registry.has("ollama_setup")
    assert TOOL["behavior"]=="NON_BLOCKING"


def test_only_owned_failed_server_is_stopped(monkeypatch):
    api(monkeypatch,inference=False)
    monkeypatch.setattr(setup,"healthy",Mock(side_effect=[False,True]))
    monkeypatch.setattr(setup,"executable",lambda:"fixture-executable")
    owned=Mock();owned.poll.return_value=None
    monkeypatch.setattr(setup,"launch",Mock(return_value=owned))
    save=Mock();monkeypatch.setattr(setup,"persist",save)
    with pytest.raises(RuntimeError,match="inference"):
        setup.run(threading.Event(),lambda *a:None)
    owned.terminate.assert_called_once()
    save.assert_not_called()


def test_completion_callback_failure_does_not_change_verified_status(monkeypatch):
    monkeypatch.setattr(setup,"run",lambda *a:{"inference_verified":True})
    result=setup.start(notify=Mock(side_effect=RuntimeError("HUD unavailable")))
    deadline=time.monotonic()+3
    while setup.status(result["job_id"])["status"] in ("queued","running") and time.monotonic()<deadline:time.sleep(.01)
    state=setup.status(result["job_id"])
    assert state["status"]=="completed" and state["inference_verified"]
