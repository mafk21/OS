"""Lifecycle regressions: never start a second browser against a live profile."""
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from core import social_hub as hub


@pytest.fixture
def lifecycle(tmp_path, monkeypatch):
    monkeypatch.delenv("JARVIS_SOCIALS_CDP_PORT", raising=False)
    monkeypatch.setenv("JARVIS_SOCIALS_DIR", str(tmp_path))
    profile = tmp_path / "browser_profile"
    profile.mkdir()
    spawn = Mock(side_effect=AssertionError("Unexpected second browser launch"))
    monkeypatch.setattr(hub, "_spawn_visible_or_hidden", spawn)
    monkeypatch.setattr(hub, "_profile_browser_processes", lambda _: [])
    browser = hub._NativeCdpSocialBrowser()
    return browser, profile, spawn


def version(port, token="/devtools/browser/expected"):
    return httpx.Response(200, json={"Browser": "Chrome/test", "webSocketDebuggerUrl": f"ws://127.0.0.1:{port}{token}"})


def test_reconnects_after_app_restart_and_preserves_profile_locks(lifecycle, monkeypatch):
    browser, profile, spawn = lifecycle
    (profile / "DevToolsActivePort").write_text("4567\n/devtools/browser/expected\n")
    lock = profile / "SingletonLock"
    lock.write_text("live owner")
    monkeypatch.setattr(hub.httpx, "get", lambda url, **kw: version(4567))
    assert browser.ensure_browser() == 4567
    assert browser._headless is None
    assert lock.read_text() == "live owner"
    spawn.assert_not_called()


def test_recovers_legacy_fixed_port_by_exact_profile_owner(lifecycle, monkeypatch):
    browser, _, spawn = lifecycle
    monkeypatch.setattr(hub, "_profile_browser_processes", lambda _: [(6789, True)])
    monkeypatch.setattr(hub.httpx, "get", lambda url, **kw: version(6789))
    assert browser.ensure_browser() == 6789
    spawn.assert_not_called()


def test_busy_profile_is_not_unlocked_or_launched_twice(lifecycle, monkeypatch):
    browser, profile, spawn = lifecycle
    lock = profile / "SingletonLock"
    lock.write_text("live owner")
    monkeypatch.setattr(hub, "_profile_browser_processes", lambda _: [(9876, True)])
    monkeypatch.setattr(hub.httpx, "get", lambda *a, **kw: httpx.Response(503))
    with pytest.raises(hub.SocialBrowserStartupError, match="browser:profile_busy"):
        browser.ensure_browser()
    assert lock.read_text() == "live owner"
    spawn.assert_not_called()


def test_stale_endpoint_token_cannot_attach_to_unrelated_browser(lifecycle, monkeypatch):
    browser, profile, _ = lifecycle
    (profile / "DevToolsActivePort").write_text("4567\n/devtools/browser/old\n")
    monkeypatch.setattr(hub.httpx, "get", lambda *a, **kw: version(4567, "/devtools/browser/different"))
    assert not browser._recover_profile_browser(profile)
    assert browser._port == 0


def test_external_port_is_validated_and_local_requests_bypass_proxies(lifecycle, monkeypatch):
    browser, _, spawn = lifecycle
    monkeypatch.setenv("JARVIS_SOCIALS_CDP_PORT", "1234")
    def get(url, **kwargs):
        assert kwargs["trust_env"] is False
        return httpx.Response(200, json={"not": "a browser"})
    monkeypatch.setattr(hub.httpx, "get", get)
    with pytest.raises(hub.SocialBrowserStartupError, match="browser:external_port"):
        browser.ensure_browser()
    spawn.assert_not_called()


def test_fast_browser_exit_reports_exit_code_without_waiting_45_seconds(lifecycle, monkeypatch):
    browser, profile, _ = lifecycle
    monkeypatch.setattr(hub, "find_chromium_binary", lambda: "chrome")
    process = SimpleNamespace(poll=lambda: 23)
    monkeypatch.setattr(hub, "_spawn_visible_or_hidden", lambda *a, **kw: process)
    monkeypatch.setattr(hub.time, "sleep", Mock(side_effect=AssertionError("Should fail immediately")))
    with pytest.raises(hub.SocialBrowserStartupError, match=r"browser:exited.*exit 23"):
        browser.ensure_browser()
    assert browser._port == 0 and browser._proc is None


def test_new_launch_uses_chromium_bound_port_not_free_port_race(lifecycle, monkeypatch):
    browser, profile, _ = lifecycle
    monkeypatch.setattr(hub, "find_chromium_binary", lambda: "chrome")
    monkeypatch.setattr(browser, "get_all_cookies", lambda: [])
    monkeypatch.setattr(hub, "load_encrypted_cookies", lambda _: [])
    def spawn(args, **kw):
        assert "--remote-debugging-port=0" in args
        (profile / "DevToolsActivePort").write_text("4321\n/devtools/browser/expected\n")
        return SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(hub, "_spawn_visible_or_hidden", spawn)
    monkeypatch.setattr(hub.httpx, "get", lambda *a, **kw: version(4321))
    assert browser.ensure_browser() == 4321


def test_startup_timeout_stops_only_new_child_and_preserves_profile(lifecycle, monkeypatch):
    browser, profile, _ = lifecycle
    lock = profile / "SingletonLock"
    lock.write_text("test owner")
    monkeypatch.setattr(hub, "find_chromium_binary", lambda: "chrome")
    process = SimpleNamespace(poll=lambda: None, terminate=Mock(), wait=Mock(), kill=Mock())
    monkeypatch.setattr(hub, "_spawn_visible_or_hidden", lambda *a, **kw: process)
    clock = iter([0.0, 46.0])
    monkeypatch.setattr(hub.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(hub.time, "sleep", lambda _: None)
    with pytest.raises(hub.SocialBrowserStartupError, match="browser:endpoint_timeout"):
        browser.ensure_browser()
    process.terminate.assert_called_once()
    assert lock.read_text() == "test owner"
    assert browser._proc is None and browser._port == 0


def test_actual_managed_browser_reconnects_after_manager_restart(tmp_path, monkeypatch):
    import os
    from pathlib import Path
    binary = os.environ.get("JARVIS_TEST_CHROMIUM", "")
    if not binary or not Path(binary).is_file():
        pytest.skip("Set JARVIS_TEST_CHROMIUM for actual managed-browser lifecycle test")
    monkeypatch.delenv("JARVIS_SOCIALS_CDP_PORT", raising=False)
    monkeypatch.setenv("JARVIS_SOCIALS_DIR", str(tmp_path))
    monkeypatch.setenv("JARVIS_SOCIALS_BROWSER_BIN", binary)
    spawn = hub._spawn_visible_or_hidden
    count = []
    def isolated_spawn(args, **kw):
        # Sandbox cannot be enabled in this isolated CI container. Production
        # never disables Chromium's sandbox. No Instagram URL is navigated.
        count.append(args)
        return spawn([args[0], "--no-sandbox", "--disable-dev-shm-usage", "--disable-background-networking", *args[1:]], **kw)
    monkeypatch.setattr(hub, "_spawn_visible_or_hidden", isolated_spawn)
    first, restarted = hub._NativeCdpSocialBrowser(), hub._NativeCdpSocialBrowser()
    try:
        port = first.ensure_browser()
        assert first._proc.poll() is None
        assert restarted.ensure_browser() == port
        assert len(count) == 1, "Manager restart launched a second browser"
        assert restarted._proc is None
        assert restarted._endpoint_alive()
    finally:
        first.shutdown()



def test_profile_process_scan_never_adopts_unrelated_profile(tmp_path, monkeypatch):
    import psutil
    profile = tmp_path / "our profile"
    others = [
        SimpleNamespace(info={"cmdline": ["chrome", "--user-data-dir=/some/other/profile", "--remote-debugging-port=9999"]}),
        SimpleNamespace(info={"cmdline": ["chrome", f'--user-data-dir="{profile}"', "--remote-debugging-port=4321", "--headless=new"]}),
        SimpleNamespace(info={"cmdline": None}),
    ]
    monkeypatch.setattr(psutil, "process_iter", lambda _: others)
    assert hub._profile_browser_processes(profile) == [(4321, True)]
