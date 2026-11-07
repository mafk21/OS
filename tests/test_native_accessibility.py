from core.native_accessibility import AccessibleNode, execute, find


class FakeAdapter:
    def __init__(self, nodes):
        self.items = nodes
        self.calls = []

    def nodes(self):
        yield from self.items

    def perform(self, node, action, value=""):
        self.calls.append((node.name, action, value))
        if action == "set_value":
            node.value = value
        elif action == "toggle":
            node.selected = not bool(node.selected)

    def observe(self, node):
        return node


def test_exact_semantic_match_beats_partial_match():
    exact = AccessibleNode("Send", "button")
    adapter = FakeAdapter([AccessibleNode("Send later", "button"), exact])
    node, quality = find(adapter, "Send")
    assert node is exact and quality == "exact"


def test_ambiguous_partial_match_fails_closed():
    adapter = FakeAdapter([AccessibleNode("Send now", "button"), AccessibleNode("Send later", "button")])
    result = execute(adapter, "Send", "invoke")
    assert result["ok"] is False
    assert "ambiguous" in result["error"]
    assert adapter.calls == []


def test_role_disambiguates_and_value_is_verified():
    adapter = FakeAdapter([AccessibleNode("Name", "label"), AccessibleNode("Name", "edit")])
    result = execute(adapter, "Name", "set_value", value="Pepper", role="edit")
    assert result["ok"] is True and result["verified"] is True
    assert result["control"]["value"] == "Pepper"


def test_disabled_control_is_not_invoked():
    adapter = FakeAdapter([AccessibleNode("Delete", "button", enabled=False)])
    result = execute(adapter, "Delete", "invoke")
    assert result == {"ok": False, "verified": True, "error": "matching control is disabled"}
    assert not adapter.calls


def test_unsupported_action_never_reaches_backend():
    adapter = FakeAdapter([AccessibleNode("Terminal", "window")])
    result = execute(adapter, "Terminal", "run_shell")
    assert result["ok"] is False
    assert adapter.calls == []
