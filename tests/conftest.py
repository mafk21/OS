"""Keep legacy confirmation tests in explicit opt-in mode.

Deployment defaults to no Instagram send prompt at the user's request; tests
of that preference explicitly clear this environment override.
"""
import pytest

@pytest.fixture(autouse=True)
def explicit_confirmation_test_mode(monkeypatch):
    monkeypatch.setenv("JARVIS_INSTAGRAM_CONFIRM_SEND", "1")
