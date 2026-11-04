from __future__ import annotations

import pytest

from actions import desktop


@pytest.mark.parametrize("payload", [
    "().__class__.__subclasses__()",
    "getattr(Path('.'), '__class__')",
    "import os\nprint(os.environ)",
    "open('/etc/passwd').read()",
])
def test_generated_desktop_code_rejects_escape_payloads(payload: str) -> None:
    result = desktop._execute_generated_code(payload)
    assert result.startswith("Execution error:")


def test_generated_desktop_code_allows_basic_safe_logic() -> None:
    result = desktop._execute_generated_code("values = [1, 2, 3]\nprint(sum(values))")
    assert result == "6"
