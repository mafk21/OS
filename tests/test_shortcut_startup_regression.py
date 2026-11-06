from __future__ import annotations

import asyncio

import pytest

from core.apex_bridge import ApexHudBridge


class _ReadyUI:
    muted = False
    paused = False

    def __init__(self):
        self._win = type("Win", (), {"_ready": True, "_paused_ui": False})()


def test_bridge_start_fails_closed_instead_of_opening_dead_browser(monkeypatch):
    class FailedServer:
        started = False
        should_exit = False

        def __init__(self, _config):
            pass

        async def serve(self):
            await asyncio.sleep(0)
            raise OSError("port unavailable")

    import uvicorn
    monkeypatch.setattr(uvicorn, "Server", FailedServer)
    bridge = ApexHudBridge(_ReadyUI(), host="127.0.0.1", port=0)

    with pytest.raises(RuntimeError, match="failed to start"):
        bridge.start(timeout=1)

    assert bridge._start_error is not None
