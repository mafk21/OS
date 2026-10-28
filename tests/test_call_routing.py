from actions.remote_relay import TOOL as REMOTE
from actions.web_call import TOOL as CALL


def test_call_tool_owns_phone_call_intents():
    text=CALL["description"].lower()
    assert "only tool" in text
    assert "call me" in text and "ring my phone" in text
    assert "telegram" in text and "not telegram" in text
    assert "configure" in CALL["parameters"]["properties"]["action"]["description"]


def test_telegram_remote_tool_explicitly_excludes_voice_calls():
    text=REMOTE["description"].lower()
    assert "never places voice calls" in text
    assert "use web_call" in text
