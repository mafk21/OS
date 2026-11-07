from core import provider_routing as routing


def setup_function():
    routing._FAILURES.clear()


def test_private_requests_never_cross_cloud_boundary():
    request = routing.ProviderRequest(data_class="private")
    assert routing.route("auto", request, {"gemini", "openai", "local"}) == ["local"]
    assert routing.route("auto", request, {"gemini", "openai"}) == []


def test_capability_filter_prevents_invalid_fallback():
    request = routing.ProviderRequest(capabilities=frozenset({"vision"}))
    assert routing.route("auto", request, {"gemini", "anthropic", "openai", "local"}) == ["gemini", "openai"]


def test_pinned_provider_does_not_silently_fallback():
    request = routing.ProviderRequest()
    assert routing.route("anthropic", request, {"anthropic", "openai", "local"}) == ["anthropic"]


def test_repeated_failure_opens_bounded_circuit(monkeypatch):
    routing.note_result("gemini", False)
    routing.note_result("gemini", False)
    assert routing.route("auto", routing.ProviderRequest(), {"gemini", "local"}) == ["local"]
    routing.note_result("gemini", True)
    assert routing.route("auto", routing.ProviderRequest(), {"gemini", "local"}) == ["gemini", "local"]
