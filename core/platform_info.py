"""Actual host platform helpers for native operations.

These deliberately do not read the onboarding profile: repositories and config
folders are often copied between computers, while native commands must always
follow the machine currently executing them.
"""
from __future__ import annotations
import platform


def get_os() -> str:
    return {"Windows": "windows", "Darwin": "mac", "Linux": "linux"}.get(
        platform.system(), platform.system().lower()
    )


def is_windows() -> bool: return get_os() == "windows"
def is_mac() -> bool: return get_os() == "mac"
def is_linux() -> bool: return get_os() == "linux"
