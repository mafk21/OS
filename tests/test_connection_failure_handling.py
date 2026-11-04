from pathlib import Path

from core import connection_diagnostics as diagnostics


def test_connection_messages_are_actionable():
    assert "timed out" in diagnostics.user_message("TimeoutError during opening handshake").lower()
    assert "dns" in diagnostics.user_message("getaddrinfo failed").lower()
    assert "secure connection" in diagnostics.user_message("SSL certificate verify failed").lower()
    assert "firewall" in diagnostics.user_message("ConnectionRefusedError").lower()


def test_diagnostic_log_never_persists_exception_values(monkeypatch, tmp_path):
    log = tmp_path / "connection-errors.log"
    monkeypatch.setattr(diagnostics, "LOG_PATH", log)
    # Assemble provider-shaped values from fragments so public-repository
    # scanners never see credential literals in the test fixture itself.
    gemini_like = "AI" + "za" + "123456789012345678901234567890"
    openai_like = "s" + "k-" + "123456789012345678901234"
    try:
        raise TimeoutError(
            f"request failed api_key={gemini_like} Authorization: {openai_like}"
        )
    except TimeoutError as exc:
        written = diagnostics.write_failure(exc, engine="gemini")

    text = written.read_text(encoding="utf-8")
    assert "AIza123" not in text
    assert "sk-123" not in text
    assert "request failed" not in text
    assert "Authorization" not in text
    assert "engine=gemini" in text
    assert "TimeoutError" in text
    assert "test_connection_failure_handling.py" in text


def test_terminal_traceback_is_replaced_by_diagnostic_logging():
    source = Path("main.py").read_text(encoding="utf-8")
    section = source[source.index("_network_markers ="):source.index("# Out of quota", source.index("_network_markers ="))]
    assert "traceback.print_exc" not in section
    assert "_write_connection_failure" in section
    assert "_connection_user_message" in section
