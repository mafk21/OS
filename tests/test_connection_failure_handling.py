from pathlib import Path

from core import connection_diagnostics as diagnostics


def test_connection_messages_are_actionable():
    assert "timed out" in diagnostics.user_message("TimeoutError during opening handshake").lower()
    assert "dns" in diagnostics.user_message("getaddrinfo failed").lower()
    assert "secure connection" in diagnostics.user_message("SSL certificate verify failed").lower()
    assert "firewall" in diagnostics.user_message("ConnectionRefusedError").lower()


def test_diagnostic_log_redacts_credentials(monkeypatch, tmp_path):
    log = tmp_path / "connection-errors.log"
    monkeypatch.setattr(diagnostics, "LOG_PATH", log)
    try:
        raise TimeoutError(
            "request failed api_key=AIza123456789012345678901234567890 "
            "Authorization: sk-123456789012345678901234"
        )
    except TimeoutError as exc:
        written = diagnostics.write_failure(exc, engine="gemini", model="live-test")

    text = written.read_text(encoding="utf-8")
    assert "AIza123" not in text
    assert "sk-123" not in text
    assert "[REDACTED]" in text or "[REDACTED_GEMINI_KEY]" in text
    assert "engine=gemini" in text
    assert "TimeoutError" in text


def test_terminal_traceback_is_replaced_by_diagnostic_logging():
    source = Path("main.py").read_text(encoding="utf-8")
    section = source[source.index("_network_markers ="):source.index("# Out of quota", source.index("_network_markers ="))]
    assert "traceback.print_exc" not in section
    assert "_write_connection_failure" in section
    assert "_connection_user_message" in section
