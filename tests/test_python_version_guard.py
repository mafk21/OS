"""Installer must fail early instead of compiling unsupported native packages."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import install_jarvis
import setup


def test_setup_rejects_python_315_before_dependency_install(monkeypatch, capsys) -> None:
    fake_sys = SimpleNamespace(version_info=(3, 15), exit=lambda code: (_ for _ in ()).throw(SystemExit(code)))
    monkeypatch.setattr(setup, "sys", fake_sys)
    monkeypatch.setattr(setup, "OS", "Windows")

    with pytest.raises(SystemExit) as exc:
        setup._check_python()

    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "Python 3.11–3.12" in output
    assert "py -3.12 setup.py" in output
    assert "Microsoft C++ Build Tools are not required" in output


@pytest.mark.parametrize(
    ("version", "supported"),
    [((3, 10), False), ((3, 11), True), ((3, 12), True), ((3, 13), False), ((3, 15), False)],
)
def test_native_installer_reports_only_tested_python_versions(monkeypatch, version, supported) -> None:
    monkeypatch.setattr(install_jarvis.sys, "version_info", version)
    assert install_jarvis.check_environment()["python_ok"] is supported
