import io, json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
import pytest
from core import web_call

CFG={"url":"https://jarvis-call.example","call_secret":"secret","pairing_code":"pair"}
class Response:
 def __init__(self,data): self.data=data
 def __enter__(self): return self
 def __exit__(self,*a): pass
 def read(self): return json.dumps(self.data).encode()

def test_configure_bootstraps_and_saves_owner_only_config(tmp_path):
 seen={}
 def open_(req,timeout):
  seen.update(url=req.full_url,code=req.headers["X-pairing-code"]);return Response({"call_secret":"issued-secret"})
 path=tmp_path/"web_call.json"
 with patch("urllib.request.urlopen",open_): result=web_call.configure("https://calls.example/","owner-code",path=path)
 assert seen=={"url":"https://calls.example/api/bootstrap","code":"owner-code"}
 assert result["call_secret"]=="issued-secret"
 assert path.stat().st_mode & 0o777 == 0o600
 assert json.loads(path.read_text())==result


def test_start_call_uses_authenticated_https_endpoint():
 seen={}
 def open_(req,timeout):
  seen.update(url=req.full_url,auth=req.headers["Authorization"],body=json.loads(req.data));return Response({"ok":True,"session_id":"123"})
 with patch("urllib.request.urlopen",open_): result=web_call.start_call("Wake up","Morning",config=CFG)
 assert result["session_id"]=="123"
 assert seen=={"url":"https://jarvis-call.example/api/call","auth":"Bearer secret","body":{"message":"Wake up","reason":"Morning"}}

def test_rejects_missing_config_bad_ids_and_empty_message():
 with pytest.raises(RuntimeError): web_call.start_call("hello",config={})
 with pytest.raises(ValueError): web_call.start_call("",config=CFG)
 with pytest.raises(ValueError): web_call.session_status("not-a-uuid",config=CFG)

def test_status_and_sender_reply_never_use_pairing_code():
 sid="12345678-1234-1234-1234-123456789abc"; seen=[]
 def open_(req,timeout): seen.append((req.method,req.full_url,req.headers.get("Authorization")));return Response({"ok":True,"session":{"status":"answered"},"messages":[]})
 with patch("urllib.request.urlopen",open_):
  web_call.session_status(sid,config=CFG);web_call.session_action(sid,"reply","On my way",config=CFG)
 assert all(auth=="Bearer secret" for _,_,auth in seen)

def test_schedule_writes_owner_only_script_without_shell_interpolation(tmp_path,monkeypatch):
 from actions import reminder
 monkeypatch.setattr(reminder,"_scripts_dir",lambda:tmp_path)
 monkeypatch.setattr(reminder,"_get_os",lambda:"linux")
 captured={}
 def scheduled(target,name,script): captured.update(name=name,script=script);return name
 monkeypatch.setattr(reminder,"_schedule_linux",scheduled)
 target=datetime.now()+timedelta(hours=1)
 job=web_call.schedule_call(target,"It's time; $(touch /tmp/no)",config=CFG)
 script=captured["script"]
 assert job.startswith("JARVISWebCall_") and script.exists()
 assert script.stat().st_mode & 0o777 == 0o600
 text=script.read_text()
 assert "urllib.request.Request" in text and "subprocess" not in text
 assert "$(touch /tmp/no)" in text
