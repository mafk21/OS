"""Local authenticated boundary for the optional browser companion extension."""
from __future__ import annotations
import json,secrets,time,threading
from pathlib import Path
PATH=Path(__file__).resolve().parent.parent/'config'/'browser_companion.json'
MAX_TEXT=12000
_LOCK=threading.Lock()
_CONTEXT:dict={}

def _load():
    try:return json.loads(PATH.read_text(encoding='utf-8'))
    except (OSError,ValueError):return {}
def pairing_token()->str:
    data=_load(); token=str(data.get('token') or '')
    if not token:
        token=secrets.token_urlsafe(32); PATH.parent.mkdir(parents=True,exist_ok=True); PATH.write_text(json.dumps({'token':token}),encoding='utf-8'); PATH.chmod(0o600)
    return token
def authorized(token:str)->bool: return secrets.compare_digest(str(token or ''),str(_load().get('token') or ''))
def revoke()->None:
    with _LOCK:
        PATH.unlink(missing_ok=True); _CONTEXT.clear()
def status()->dict:
    data=_load()
    with _LOCK: context=dict(_CONTEXT)
    return {'paired':bool(data.get('token')),'connected':bool(context),'last_received_at':context.get('received_at')}
def store_context(data:dict)->dict:
    context=sanitize_context(data)
    with _LOCK:
        _CONTEXT.clear(); _CONTEXT.update(context)
    return context
def current_context(clear:bool=False)->dict:
    with _LOCK:
        result=dict(_CONTEXT)
        if clear: _CONTEXT.clear()
    return result
def sanitize_context(data:dict)->dict:
    url=str(data.get('url') or '')[:2048]
    if not url.startswith(('http://','https://')): raise ValueError('unsupported page URL')
    return {'url':url,'title':str(data.get('title') or '')[:300],'selection':str(data.get('selection') or '')[:MAX_TEXT],'text':str(data.get('text') or '')[:MAX_TEXT],'received_at':time.time()}
