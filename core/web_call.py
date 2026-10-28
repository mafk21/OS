"""Private JARVIS web-call client and restart-safe OS scheduling.

Credentials live in ignored config/web_call.json. Calls are turn-based voice
sessions delivered through Web Push; no PSTN number or paid carrier is used.
"""
from __future__ import annotations
import json, os, re, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR=Path(__file__).resolve().parents[1]
CONFIG_PATH=BASE_DIR/"config"/"web_call.json"
_ID=re.compile(r"^[0-9a-f-]{36}$",re.I)

def load_config(path:Path=CONFIG_PATH)->dict[str,str]:
    try: raw=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {}
    return {k:str(raw.get(k) or "").strip() for k in ("url","call_secret","pairing_code")}

def _request(method:str,path:str,payload:dict[str,Any]|None=None,*,sender:bool=True,config:dict[str,str]|None=None)->dict[str,Any]:
    cfg=config or load_config(); base=cfg.get("url","").rstrip("/")
    if not base.startswith("https://") or not cfg.get("call_secret"): raise RuntimeError("Web calling is not configured")
    headers={"Content-Type":"application/json"}
    headers["Authorization" if sender else "x-pairing-code"]=("Bearer "+cfg["call_secret"]) if sender else cfg.get("pairing_code","")
    req=urllib.request.Request(base+path,data=json.dumps(payload or {}).encode(),headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=15) as response: return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        try: detail=json.loads(exc.read().decode()).get("error","")
        except Exception: detail=""
        raise RuntimeError(detail or f"Call service returned HTTP {exc.code}") from exc
    except (OSError,ValueError) as exc: raise RuntimeError(f"Call service unavailable: {exc}") from exc

def start_call(message:str,reason:str="JARVIS is calling",*,config=None)->dict[str,Any]:
    message=str(message or "").strip(); reason=str(reason or "").strip()
    if not message: raise ValueError("Call message is required")
    return _request("POST","/api/call",{"message":message[:2000],"reason":reason[:240]},config=config)

def session_action(session_id:str,action:str,message:str="",*,config=None)->dict[str,Any]:
    if not _ID.match(str(session_id)): raise ValueError("Invalid call session ID")
    if action not in {"reply","end"}: raise ValueError("Unsupported sender action")
    return _request("POST",f"/api/session/{session_id}",{"action":action,"message":str(message)[:2000]},config=config)

def session_status(session_id:str,*,config=None)->dict[str,Any]:
    if not _ID.match(str(session_id)): raise ValueError("Invalid call session ID")
    return _request("GET",f"/api/session/{session_id}",config=config)

def schedule_call(target:datetime,message:str,reason:str="Scheduled JARVIS call",*,config=None)->str:
    if target<=datetime.now(): raise ValueError("Scheduled call time has already passed")
    cfg=config or load_config()
    if not cfg.get("url","").startswith("https://") or not cfg.get("call_secret"): raise RuntimeError("Web calling is not configured")
    from actions import reminder as scheduler
    task=f"JARVISWebCall_{target.strftime('%Y%m%d_%H%M%S')}"
    script=scheduler._scripts_dir()/f"{task}.py"
    body=("# Auto-generated scheduled JARVIS web call\nimport json, pathlib, urllib.request\n"+
          f"url={json.dumps(cfg['url'].rstrip('/')+'/api/call')}\nsecret={json.dumps(cfg['call_secret'])}\n"+
          f"payload=json.dumps({{'message':{json.dumps(message[:2000])},'reason':{json.dumps(reason[:240])}}}).encode()\n"+
          "req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','Authorization':'Bearer '+secret},method='POST')\n"+
          "try:\n urllib.request.urlopen(req,timeout=20).read()\nfinally:\n pathlib.Path(__file__).unlink(missing_ok=True)\n")
    script.write_text(body,encoding="utf-8"); script.chmod(0o600)
    os_name=scheduler._get_os()
    try:
        if os_name=="windows": job=scheduler._schedule_windows(target,task,script,reason)
        elif os_name=="mac": job=scheduler._schedule_mac(target,task,script)
        else: job=scheduler._schedule_linux(target,task,script)
    except Exception: script.unlink(missing_ok=True); raise
    if not job: script.unlink(missing_ok=True); raise RuntimeError("The operating-system scheduler rejected the call")
    return job
