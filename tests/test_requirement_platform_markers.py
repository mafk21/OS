"""Regression tests for dependencies that are needed on only one OS."""
from __future__ import annotations

from packaging.requirements import Requirement


def _requirement(name: str) -> Requirement:
    for raw in open("requirements.txt", encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if line and Requirement(line).name.lower() == name.lower():
            return Requirement(line)
    raise AssertionError(f"{name} is missing from requirements.txt")


def test_zstandard_is_linux_only() -> None:
    """Windows/macOS Ollama archives do not need the zstandard C extension."""
    requirement = _requirement("zstandard")
    assert requirement.marker is not None
    assert requirement.marker.evaluate({"sys_platform": "linux"})
    assert not requirement.marker.evaluate({"sys_platform": "win32"})
    assert not requirement.marker.evaluate({"sys_platform": "darwin"})
