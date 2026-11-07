"""Home Assistant / Matter smart-home control."""
from __future__ import annotations

def smart_home(parameters:dict, **_):
    from memory import config_manager as cfg
    from core.smart_home import call
    config=cfg.load_api_keys(); base=str(config.get('home_assistant_url') or ''); token=str(config.get('home_assistant_token') or '')
    if not base or not token: return 'Home Assistant is not configured in Settings.'
    service=str(parameters.get('service') or '').strip(); entity=str(parameters.get('entity_id') or '').strip(); data=parameters.get('data')
    try: result=call(base,token,service,entity,data if isinstance(data,dict) else {})
    except Exception as exc: return f"Smart-home action failed: {type(exc).__name__}."
    return f"Home Assistant acknowledged {service} for {entity}." if result['ok'] and result['acknowledged'] else 'Smart-home action was not acknowledged.'

TOOL={'name':'smart_home','description':'Control allowlisted Home Assistant or Matter entities. Requires explicit HUD confirmation.','parameters':{'type':'OBJECT','properties':{'service':{'type':'STRING','description':'Allowlisted service such as light.turn_on'},'entity_id':{'type':'STRING'},'data':{'type':'OBJECT','properties':{}}},'required':['service','entity_id']},'handler':smart_home,'safety':{'risk':'high','permission':'smart_home','confirmation':'required','side_effect':True,'reversible':False,'verification':'observed','idempotency':'window'}}
