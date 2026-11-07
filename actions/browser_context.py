"""Read context explicitly shared by the local browser companion."""
from __future__ import annotations

def browser_context(parameters:dict, **_):
    from core.browser_companion import current_context
    context=current_context(clear=bool((parameters or {}).get('clear',False)))
    if not context: return 'No browser tab has been shared. Ask the user to press Send in the JARVIS Browser Companion.'
    return {'url':context['url'],'title':context['title'],'selection':context['selection'],'page_text':context['text'],'shared_at':context['received_at']}

TOOL={'name':'browser_context','description':'Read the active browser tab context that the user explicitly shared through the JARVIS Browser Companion. Never reads tabs by itself.','parameters':{'type':'OBJECT','properties':{'clear':{'type':'BOOLEAN','description':'Clear the shared context after reading it'}}},'handler':browser_context,'safety':{'risk':'low','permission':'browser_context','confirmation':'none','side_effect':False,'reversible':False,'verification':'observed'}}
