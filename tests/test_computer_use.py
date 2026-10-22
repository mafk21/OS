"""Tests — computer use (Phase 8): Set-of-Mark visual agent."""
import actions.computer_use as cu


# ── Tool declaration ──────────────────────────────────────────────────────

def test_tool_declaration():
    assert cu.TOOL["name"] == "computer_use"
    assert cu.TOOL["handler"] is cu.computer_use
    assert cu.TOOL["behavior"] == "NON_BLOCKING"
    assert cu.TOOL["scheduling"] == "WHEN_IDLE"
    assert cu.TOOL["parameters"]["required"] == ["action"]
    assert "action" in cu.TOOL["parameters"]["properties"]
    assert "element_id" in cu.TOOL["parameters"]["properties"]


# ── Action dispatch ───────────────────────────────────────────────────────

def test_som_capture_no_capture_lib():
    """som_capture degrades gracefully when screen capture unavailable."""
    result = cu.computer_use({"action": "som_capture"}, player=None)
    assert "screen capture failed" in result or "element(s)" in result or "No elements" in result


def test_unknown_action():
    result = cu.computer_use({"action": "bogus"})
    assert "unknown action" in result.lower()


def test_click_by_id_no_capture():
    result = cu.computer_use({"action": "click_by_id", "element_id": "1"})
    assert "som_capture first" in result or "need element_id" in result.lower()


def test_click_by_coords_no_pyautogui():
    result = cu.computer_use({"action": "click_by_id", "x": 100, "y": 200})
    assert "PyAutoGUI not installed" in result or "not installed" in result


def test_type_by_id_no_capture():
    result = cu.computer_use({"action": "type_by_id", "element_id": "1", "text": "hello"})
    assert "som_capture first" in result or "need element_id" in result.lower()


def test_type_by_coords_no_pyautogui():
    result = cu.computer_use({"action": "type_by_id", "x": 100, "y": 200, "text": "hello"})
    assert "PyAutoGUI not installed" in result or "not installed" in result


def test_hover_by_id_no_capture():
    result = cu.computer_use({"action": "hover_by_id", "element_id": "1"})
    assert "som_capture first" in result or "need element_id" in result.lower()


def test_hover_by_coords_no_pyautogui():
    result = cu.computer_use({"action": "hover_by_id", "x": 100, "y": 200})
    assert "PyAutoGUI not installed" in result or "not installed" in result


# ── Element detection + annotation (graceful) ─────────────────────────────

def test_detect_elements_returns_list():
    els = cu._detect_elements_som()
    assert isinstance(els, list)


def test_annotate_returns_original_when_no_elements():
    result, id_map = cu._annotate_som(b"fake-image-bytes", [])
    assert result == b"fake-image-bytes"
    assert id_map == {}


def test_annotate_returns_original_when_no_pil():
    result, id_map = cu._annotate_som(b"fake-bytes", [{"id": "1", "x": 10, "y": 20}])
    assert result == b"fake-bytes"
    assert id_map == {}
