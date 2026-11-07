"""Home Assistant / Matter smart-home control."""
from __future__ import annotations

def smart_home(parameters:dict, **_):
    from core.smart_home import call, _load
    config=_load(); base=str(config.get('url') or ''); token=str(config.get('token') or '')
    if not base or not token: return 'Home Assistant is not configured in Settings.'
    service=str(parameters.get('service') or '').strip(); entity=str(parameters.get('entity_id') or '').strip(); data=parameters.get('data')
    try: result=call(base,token,service,entity,data if isinstance(data,dict) else {})
    except Exception as exc: return f"Smart-home action failed: {type(exc).__name__}."
    if not result['ok']: return 'Smart-home action was not acknowledged.'
    suffix=f" Verified resulting state: {result['after']}." if result['verified'] else f" Acknowledged; resulting state observed as {result['after'] or 'unavailable'}."
    if result.get('undo_service'): suffix+=f" Undo is available with {result['undo_service']}."
    return f"Home Assistant applied {service} to {entity}.{suffix}"

TOOL={'name':'smart_home','description':'Control allowlisted Home Assistant or Matter entities. Requires explicit HUD confirmation.','parameters':{'type':'OBJECT','properties':{'service':{'type':'STRING','description':'Allowlisted service such as light.turn_on'},'entity_id':{'type':'STRING'},'data':{'type':'OBJECT','properties':{}}},'required':['service','entity_id']},'handler':smart_home,'safety':{'risk':'high','permission':'smart_home','confirmation':'required','side_effect':True,'reversible':False,'verification':'observed','idempotency':'window'}}
