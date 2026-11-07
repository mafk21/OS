"""Local authenticated boundary for the optional browser companion extension."""
from __future__ import annotations
import json,secrets,time
from pathlib import Path
PATH=Path(__file__).resolve().parent.parent/'config'/'browser_companion.json'
MAX_TEXT=12000

def _load():
    try:return json.loads(PATH.read_text(encoding='utf-8'))
    except (OSError,ValueError):return {}
def pairing_token()->str:
    data=_load(); token=str(data.get('token') or '')
    if not token:
        token=secrets.token_urlsafe(32); PATH.parent.mkdir(parents=True,exist_ok=True); PATH.write_text(json.dumps({'token':token}),encoding='utf-8'); PATH.chmod(0o600)
    return token
def authorized(token:str)->bool: return secrets.compare_digest(str(token or ''),str(_load().get('token') or ''))
def sanitize_context(data:dict)->dict:
    url=str(data.get('url') or '')[:2048]
    if not url.startswith(('http://','https://')): raise ValueError('unsupported page URL')
    return {'url':url,'title':str(data.get('title') or '')[:300],'selection':str(data.get('selection') or '')[:MAX_TEXT],'text':str(data.get('text') or '')[:MAX_TEXT],'received_at':time.time()}
