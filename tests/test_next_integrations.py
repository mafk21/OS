import json
from core import browser_companion, local_voice_profile, owner_auth, provider, smart_home, strategy_experiments, workflow_reviewer


def test_browser_companion_token_and_context_are_bounded(monkeypatch,tmp_path):
    monkeypatch.setattr(browser_companion,'PATH',tmp_path/'pair.json')
    token=browser_companion.pairing_token()
    assert browser_companion.authorized(token) and not browser_companion.authorized(token+'x')
    result=browser_companion.sanitize_context({'url':'https://example.com','title':'x','text':'a'*20000})
    assert len(result['text'])==browser_companion.MAX_TEXT
    assert token not in json.dumps(result)


def test_browser_companion_rejects_non_web_pages():
    try: browser_companion.sanitize_context({'url':'file:///private'})
    except ValueError: pass
    else: raise AssertionError('file pages must be rejected')


def test_workflow_reviewer_rejects_duplicate_side_effects():
    step={'tool':'send_message','params':{'receiver':'A'},'evidence_requirement':'verified'}
    review=workflow_reviewer.review_steps([step,dict(step)])
    assert not review.approved and review.required_confirmation
    assert any('duplicates' in item for item in review.findings)


def test_workflow_reviewer_accepts_bounded_read_plan():
    review=workflow_reviewer.review_steps([{'tool':'weather_report','params':{}}])
    assert review.approved and not review.required_confirmation


def test_experiment_rolls_back_worse_candidate(monkeypatch,tmp_path):
    monkeypatch.setattr(strategy_experiments,'PATH',tmp_path/'experiments.json')
    strategy_experiments.set_enabled(True); strategy_experiments.propose('routing','a','b')
    for _ in range(10): strategy_experiments.record('routing','baseline',True)
    for _ in range(10): strategy_experiments.record('routing','candidate',False)
    assert strategy_experiments.snapshot()['experiments']['routing']['state']=='rolled_back'


def test_owner_auth_fails_closed_when_native_auth_unavailable(monkeypatch):
    monkeypatch.setattr(owner_auth,'_which',lambda _name:None)
    assert not owner_auth.available('linux')
    assert not owner_auth.authenticate(system='windows')


def test_local_voice_snapshot_is_truthful(monkeypatch):
    monkeypatch.setattr(local_voice_profile.importlib.util,'find_spec',lambda name: object() if name in {'openwakeword','kokoro'} else None)
    result=local_voice_profile.snapshot()
    assert result['selected']['wake']=='openwakeword'
    assert result['selected']['stt']=='unavailable'
    assert result['offline_ready'] is False


def test_smart_home_allowlist_rejects_arbitrary_service():
    try: smart_home.call('http://homeassistant.local','secret','shell_command.run','x',{})
    except ValueError as exc: assert 'allowlisted' in str(exc)
    else: raise AssertionError('arbitrary services must be rejected')
