"""Exercise the native-composer fallback without a browser or real messages."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core import instagram_web as web
from core.instagram_direct import DeliveryUnknown, RecipientError


class Locator:
    def __init__(self, page, kind):
        self.page, self.kind = page, kind

    @property
    def first(self):
        return self

    def wait_for(self, **_):
        pass

    def count(self):
        return self.page.counts.get(self.kind, 1)

    def get_attribute(self, name):
        return self.page.canonical if name == "href" else None

    def click(self):
        if self.kind == "message":
            self.page.url = "https://www.instagram.com/direct/t/intended-thread/"
        elif self.kind == "send":
            self.page.attempts += 1
            if self.page.click_error:
                raise TimeoutError("click may already have submitted")
            if self.page.ack:
                self.page.observer(response({"status": "ok", "payload": {"item_id": "native-server-id"}}))

    def evaluate(self, _):
        return self.page.textarea

    def input_value(self):
        return self.page.draft

    def inner_text(self):
        return self.page.draft

    def fill(self, text):
        self.page.filled.append(text)
        if self.page.on_fill:
            self.page.on_fill()

    def is_enabled(self):
        return self.page.enabled


class Page:
    url = "https://www.instagram.com/sarah/"
    canonical = "https://www.instagram.com/sarah/"
    enabled = True
    textarea = True
    draft = ""
    ack = True
    click_error = False
    on_fill = None

    def __init__(self):
        self.counts = {}
        self.attempts = 0
        self.filled = []

    def set_default_timeout(self, _):
        pass

    def wait_for_load_state(self, _):
        pass

    def wait_for_url(self, url):
        if isinstance(url, str):
            assert url == self.url
        else:
            assert url.match(self.url)

    def locator(self, selector):
        return Locator(self, "canonical" if "canonical" in selector else "composer")

    def get_by_role(self, _role, name):
        return Locator(self, "message" if name.match("Message") else "send")

    def on(self, event, observer):
        assert event == "response"
        self.observer = observer

    def wait_for_timeout(self, _):
        pass


def response(payload, *, path="/api/v1/direct_v2/threads/broadcast/text/", operation="", status=200):
    return SimpleNamespace(request=SimpleNamespace(method="POST", post_data=operation), status=status,
                           url="https://www.instagram.com" + path, json=lambda: payload)


@pytest.fixture
def native(monkeypatch):
    page = Page()
    session = SimpleNamespace(send=lambda _: {"targetInfo": {"targetId": "background-target"}}, detach=Mock())
    context = SimpleNamespace(pages=[page], new_cdp_session=lambda _: session)
    stop = Mock()
    playwright = SimpleNamespace(chromium=SimpleNamespace(connect_over_cdp=lambda *_a, **_kw: SimpleNamespace(contexts=[context])), stop=stop)
    monkeypatch.setattr(web, "_playwright", lambda: SimpleNamespace(start=lambda: playwright))
    clock = iter([0, 16])
    monkeypatch.setattr(web, "time", SimpleNamespace(monotonic=lambda: next(clock)))
    permission = {"allowed": True}
    cookies = {"sessionid": "fake-session", "ds_user_id": "1"}
    hub = SimpleNamespace(
        _CDP=SimpleNamespace(_port=1234, get_or_open_tab=Mock(return_value={"id": "background-target"})),
        accounts=SimpleNamespace(check_permission=lambda *_: (permission["allowed"], "read-only")),
        _cookie_dict=lambda _: cookies,
    )
    return SimpleNamespace(page=page, hub=hub, stop=stop, permission=permission, cookies=cookies)


def test_native_web_sends_once_only_after_exact_profile_and_provider_receipt(native):
    result = web.send_instagram_message(native.hub, "@Sarah", "مرحبا", expected_sender=dict(native.cookies))
    assert "Instagram acknowledgment: native-server-id" in result
    assert native.page.attempts == 1 and native.page.filled == ["مرحبا"]
    assert native.hub._CDP.get_or_open_tab.call_args.kwargs["headless"] is True
    assert native.hub._CDP.get_or_open_tab.call_args.kwargs["purpose"] == "send"
    native.stop.assert_called_once()


@pytest.mark.parametrize("fault", ["canonical", "draft", "ambiguous_message", "ambiguous_composer", "ambiguous_send", "disabled_send", "revoked", "different_actor"])
def test_native_web_refuses_uncertain_identity_draft_or_policy(native, fault):
    if fault == "canonical":
        native.page.canonical = "https://www.instagram.com/not-sarah/"
    elif fault == "draft":
        native.page.draft = "User's unsent private draft"
    elif fault.startswith("ambiguous_"):
        native.page.counts[fault.split("_", 1)[1]] = 2
    elif fault == "disabled_send":
        native.page.enabled = False
    elif fault == "revoked":
        native.page.on_fill = lambda: native.permission.update(allowed=False)
    elif fault == "different_actor":
        native.page.on_fill = lambda: native.cookies.update(ds_user_id="999")
    with pytest.raises((RecipientError, RuntimeError)):
        web.send_instagram_message(native.hub, "sarah", "hello", expected_sender=dict(native.cookies))
    assert native.page.attempts == 0
    native.stop.assert_called_once()


@pytest.mark.parametrize("fault", ["no_ack", "click_timeout"])
def test_native_send_without_receipt_is_unknown_and_never_repeated(native, fault):
    native.page.ack = False
    native.page.click_error = fault == "click_timeout"
    with pytest.raises(DeliveryUnknown, match="[Cc]heck the chat"):
        web.send_instagram_message(native.hub, "sarah", "hello", expected_sender=dict(native.cookies))
    assert native.page.attempts == 1
    native.stop.assert_called_once()


@pytest.mark.parametrize("payload,path,operation,expected", [
    ({"status": "ok", "payload": {"item_id": "id"}}, "/api/v1/direct_v2/threads/broadcast/text/", "", "id"),
    ({"status": "ok"}, "/api/v1/direct_v2/threads/broadcast/text/", "", ""),
    ({"data": {"send_message": {"message_id": "id"}}}, "/graphql/query/", "SendMessageMutation", "id"),
    ({"data": {"message_id": "id"}}, "/graphql/query/", "ReadMessagesQuery", ""),
    ({"data": {"send_message": {"offline_threading_id": "optimistic"}}}, "/graphql/query/", "SendMessageMutation", ""),
    ({"errors": ["rejected"], "data": {"message_id": "id"}}, "/graphql/query/", "SendMessageMutation", ""),
    ({"data": {"send_message": {"success": False, "message_id": "id"}}}, "/graphql/query/", "SendMessageMutation", ""),
])
def test_only_send_mutation_server_receipts_count(payload, path, operation, expected):
    assert web._send_ack(response(payload, path=path, operation=operation)) == expected
