"""State-machine and privacy tests independent of Instagram's live service."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core import instagram_web as web
from core.instagram_direct import DeliveryUnknown, RecipientError


def thread(thread_id, username="sarah", **extra):
    return {"thread_id": thread_id, "users": [{"username": username}], **extra}


def engine(tmp_path, responses):
    page = SimpleNamespace(evaluate=Mock(side_effect=responses))
    hub = SimpleNamespace(socials_root_dir=lambda: tmp_path)
    run = web.InstagramMessageRun(hub, "sarah", "PRIVATE MESSAGE", {"sessionid": "PRIVATE COOKIE"})
    run.page = page
    return run


def test_exact_existing_thread_does_not_depend_on_profile_button_or_picker(tmp_path):
    run = engine(tmp_path, [{"threads": [thread("123")], "cursor": ""}])
    assert run.existing_thread() == "123"
    assert run.history == ["session_thread_lookup"]
    assert not run.attempted


def test_lookup_pagination_and_group_exclusion(tmp_path):
    run = engine(tmp_path, [
        {"threads": [thread("group", is_group=True)], "cursor": "next"},
        {"threads": [thread("123")], "cursor": ""},
    ])
    assert run.existing_thread() == "123"
    assert run.page.evaluate.call_count == 2


def test_multiple_verified_threads_are_not_guessed(tmp_path):
    run = engine(tmp_path, [{"threads": [thread("one")], "cursor": "next"},
                           {"threads": [thread("two")], "cursor": ""}])
    with pytest.raises(RecipientError, match="More than one"):
        run.existing_thread()
    assert not run.attempted


@pytest.mark.parametrize("payload", [None, True, {}, {"threads": "not a list"}, {"threads": [thread("../bad")]}])
def test_unavailable_read_api_leaves_native_resolution_available(tmp_path, payload):
    run = engine(tmp_path, [payload])
    assert run.existing_thread() is None
    assert not run.attempted


def test_failure_diagnostic_is_allowlisted_and_never_contains_private_content(tmp_path):
    run = engine(tmp_path, [{"visible_inputs": 1, "exact_rows": 0, "login_form": False,
                           "cookies": "SECRET", "body": "PRIVATE MESSAGE", "url": "private"}])
    run.progress("compose_exact_recipient")
    with pytest.raises(RuntimeError, match="search did not produce one verifiable"):
        run.fail(TimeoutError("PRIVATE MESSAGE SECRET"))
    diagnostic = json.loads((tmp_path / "instagram_last_failure.json").read_text())
    assert diagnostic["stage"] == "compose_exact_recipient"
    assert diagnostic["visible_inputs"] == 1
    assert diagnostic["attempted"] is False
    raw = json.dumps(diagnostic)
    for secret in ("PRIVATE", "SECRET", "sessionid", "sarah", "body", "url"):
        assert secret not in raw


def test_submission_boundary_forbids_recovery_and_reports_unknown(tmp_path):
    run = engine(tmp_path, [{}])
    run.progress("submit_once")
    run.attempted = True
    with pytest.raises(DeliveryUnknown, match="No automatic retry"):
        run.fail(TimeoutError("click may already have submitted"))
    assert run.history == ["submit_once"]


def test_resolved_thread_redirect_cannot_fill_another_chat(tmp_path, monkeypatch):
    run = engine(tmp_path, [])
    run.existing_thread = lambda: "verified-thread"
    run.page.url = "https://www.instagram.com/direct/t/wrong-thread/"
    run.page.goto = Mock()
    monkeypatch.setattr(web, "_wait_chat", lambda *_: run.page)
    with pytest.raises(RecipientError, match="different conversation"):
        run.open_chat()
    assert not run.attempted


@pytest.mark.parametrize("state", ["login", "security_check", "encrypted_storage", "restricted", "cookie_consent", "app_interstitial"])
def test_known_interstitial_never_runs_recipient_search_or_clicks_through(monkeypatch, state):
    page = SimpleNamespace(evaluate=Mock(return_value=state))
    stages = []
    with pytest.raises(RecipientError):
        web._prepare_inbox(page, stages.append)
    assert stages == ["inbox_" + state]
    assert page.evaluate.call_count == 1


def test_load_error_reloads_at_most_once():
    page = SimpleNamespace(evaluate=Mock(return_value="load_error"), reload=Mock())
    with pytest.raises(RecipientError, match="after one safe reload"):
        web._prepare_inbox(page, lambda _: None)
    page.reload.assert_called_once_with(wait_until="domcontentloaded")
