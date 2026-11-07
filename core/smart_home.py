"""Permission-scoped Home Assistant connector; Matter devices flow through HA."""
from __future__ import annotations
from urllib.parse import urlparse
import json, urllib.request
ALLOWED_SERVICES={'light.turn_on','light.turn_off','light.toggle','scene.turn_on','climate.set_temperature','lock.lock','lock.unlock','cover.open_cover','cover.close_cover'}
def call(base_url:str, token:str, service:str, entity_id:str, data:dict|None=None)->dict:
    parsed=urlparse(base_url)
    if parsed.scheme not in {'http','https'} or not parsed.hostname: raise ValueError('invalid Home Assistant URL')
    if service not in ALLOWED_SERVICES: raise ValueError('service is not allowlisted')
    if not entity_id or any(ch in entity_id for ch in '\r\n\0'): raise ValueError('invalid entity id')
    domain,action=service.split('.',1); payload={'entity_id':entity_id,**(data or {})}
    req=urllib.request.Request(f"{base_url.rstrip('/')}/api/services/{domain}/{action}",data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {token}','Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=10) as response:
        body=json.loads(response.read().decode() or '[]')
        return {'ok':200<=response.status<300,'status':response.status,'acknowledged':isinstance(body,list)}
