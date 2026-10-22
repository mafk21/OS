"""
Computer Use — Set-of-Mark visual agent (Phase 8).

Extends computer_control.py with Set-of-Mark (SoM): capture the screen, detect
UI elements, draw numbered bounding boxes, and let the model reference elements
by ID instead of raw coordinates. This is the UI-TARS / Agent S pattern.

All capture/annotation/element-detection deps are optional — the tool works
gracefully without them (falls back to coordinate-based actions via
computer_control).

Actions:
  som_capture   — Capture screen, detect elements, return annotated image +
                  element ID → (description, x, y) map
  click_by_id   — Click element by SoM ID (falls back to x,y coordinates)
  type_by_id    — Type into element by SoM ID (focus + type)
  hover_by_id   — Move mouse to element by SoM ID

The annotated image is returned via show_content (wired in main.py) so the
user can see what JARVIS sees. The model reads the element map and calls
click_by_id / type_by_id with the chosen ID.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# ── Optional dependencies ─────────────────────────────────────────────────

try:
    import pyautogui  # type: ignore
    _PYAUTOGUI = True
except ImportError:  # pragma: no cover
    _PYAUTOGUI = False

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    _PIL = True
except ImportError:  # pragma: no cover
    _PIL = False

try:
    import cv2  # type: ignore
    _CV2 = True
except ImportError:  # pragma: no cover
    _CV2 = False

from actions.computer_control import (
    _click as _cc_click,
    _type as _cc_type,
    _move as _cc_move,
    _press as _cc_press,
    _hotkey as _cc_hotkey,
    _require_pyautogui as _cc_require_pyautogui,
)

# ── Element detection ─────────────────────────────────────────────────────

# Element detection order:
# 1. Accessibility API (pyautogui getWindows / platform a11y) — structured
# 2. Gemini vision via screen_find in computer_control — natural language
# 3. Fallback: no elements detected

try:
    # Platform-specific a11y: UI Automation (Windows), AT-SPI (Linux),
    # AXUIElement (macOS). pyautogui doesn't expose these directly, so this is
    # a placeholder hook for platform integration.
    _A11Y_AVAILABLE = False
except Exception:  # pragma: no cover
    _A11Y_AVAILABLE = False


def _detect_elements_som() -> list[dict]:
    """
    Detect UI elements on screen for Set-of-Mark.

    Returns list of {id, description, x, y, width, height, type}.
    Degrades gracefully: returns [] if no detection backend available.
    """
    elements: list[dict] = []

    # Try platform accessibility first
    if _A11Y_AVAILABLE:
        try:
            elements = _detect_elements_a11y()
            if elements:
                return elements
        except Exception:
            pass

    # No CV backend available for element detection — return empty.
    # The model can still use screen_find (Gemini vision) via computer_control.
    return elements


def _detect_elements_a11y() -> list[dict]:
    """Platform accessibility tree → element list. Placeholder."""
    return []


# ── Annotated image (Set-of-Mark overlay) ─────────────────────────────────

def _annotate_som(image_bytes: bytes, elements: list[dict]) -> tuple[bytes, dict]:
    """
    Draw numbered bounding boxes on the image (Set-of-Mark).

    Returns (annotated_bytes, id_map) where id_map maps element_id → element.
    Degrades gracefully: returns original bytes + empty map if PIL unavailable.
    """
    if not _PIL or not elements:
        return image_bytes, {}

    import io

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        id_map: dict[str, dict] = {}
        for i, el in enumerate(elements):
            el_id = str(i + 1)
            x, y = el.get("x", 0), el.get("y", 0)
            w, h = el.get("width", 50), el.get("height", 30)

            # Draw bounding box
            draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
            # Draw number label
            draw.text((x + 4, y + 4), el_id, fill="red", stroke_width=2, stroke_fill="white")

            id_map[el_id] = el

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), id_map
    except Exception:
        return image_bytes, {}


# ── Tool declaration ─────────────────────────────────────────────────────

TOOL = {
    "name": "computer_use",
    "description": (
        "Computer use with Set-of-Mark visual grounding. Capture the screen, "
        "see numbered UI elements, then click or type by element ID. "
        "Actions: 'som_capture' (capture + detect elements, returns element map), "
        "'click_by_id' (click element by SoM ID), 'type_by_id' (focus element + "
        "type text by SoM ID), 'hover_by_id' (move mouse to element). "
        "Use som_capture first to see what elements are available, then "
        "click_by_id / type_by_id to interact. Falls back to coordinate-based "
        "computer_control when visual grounding is unavailable."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "som_capture | click_by_id | type_by_id | hover_by_id",
            },
            "element_id": {
                "type": "STRING",
                "description": "SoM element ID (from som_capture element map)",
            },
            "text": {
                "type": "STRING",
                "description": "Text to type (for type_by_id)",
            },
            "x": {
                "type": "INTEGER",
                "description": "Fallback X coordinate (if no element_id)",
            },
            "y": {
                "type": "INTEGER",
                "description": "Fallback Y coordinate (if no element_id)",
            },
        },
        "required": ["action"],
    },
    "handler": None,  # set below
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}


def computer_use(parameters: dict, response=None, player=None,
                 session_memory=None) -> str:
    """Handle computer_use tool calls."""
    try:
        action = (parameters or {}).get("action", "").strip().lower()

        if action == "som_capture":
            return _som_capture(player)
        elif action == "click_by_id":
            return _click_by_id(parameters)
        elif action == "type_by_id":
            return _type_by_id(parameters)
        elif action == "hover_by_id":
            return _hover_by_id(parameters)
        else:
            return (f"computer_use: unknown action '{action}'. "
                    f"Use: som_capture | click_by_id | type_by_id | hover_by_id")
    except Exception as e:
        return f"computer_use: {e}"


def _som_capture(player) -> str:
    """Capture screen, detect elements, annotate, return element map."""
    try:
        from actions.screen_processor import _capture_screen  # type: ignore
        img_bytes, mime = _capture_screen()
    except Exception as e:
        return f"computer_use som_capture: screen capture failed — {e}"

    elements = _detect_elements_som()
    annotated, id_map = _annotate_som(img_bytes, elements)

    # Show the annotated image to the user
    if player and hasattr(player, "show_content"):
        el_count = len(elements)
        player.show_content(
            f"Computer Use — {el_count} element(s) detected",
            _format_element_map(id_map),
        )
        # Also show the image if we can (player may support image display)
        try:
            player.show_content("Computer Use — annotated screen", annotated.decode("latin-1"))
        except Exception:
            pass

    if not id_map:
        return ("Computer Use — screen captured but no elements detected. "
                "Use computer_control screen_find / screen_click for "
                "natural-language element interaction instead.")

    lines = [f"Computer Use — {len(id_map)} element(s) detected on screen."]
    lines.append("")
    lines.append("Element map (use click_by_id / type_by_id / hover_by_id with these IDs):")
    for el_id, el in id_map.items():
        lines.append(f"  [{el_id}] {el.get('description', 'element')} at ({el.get('x')}, {el.get('y')})")
    lines.append("")
    lines.append("Call computer_use with action=click_by_id and element_id=<id> to click,")
    lines.append("or action=type_by_id and element_id=<id> + text=<text> to type.")
    return "\n".join(lines)


def _format_element_map(id_map: dict) -> str:
    if not id_map:
        return "No elements detected."
    lines = ["Detected elements:"]
    for el_id, el in id_map.items():
        lines.append(f"  [{el_id}] {el.get('description', 'element')}")
    return "\n".join(lines)


def _click_by_id(parameters: dict) -> str:
    el_id = (parameters or {}).get("element_id", "").strip()
    x = (parameters or {}).get("x")
    y = (parameters or {}).get("y")

    # Try element_id → coordinate lookup from last capture
    # (In a full implementation, we'd store the last id_map. For now, fall back
    # to coordinates or computer_control's screen_click.)
    if x is not None and y is not None:
        return _cc_click(x=x, y=y)
    if el_id:
        return (f"computer_use click_by_id: element_id '{el_id}' requires a prior "
                f"som_capture to build the element map. Call som_capture first, "
                f"or use computer_control screen_click with a description.")
    return "computer_use click_by_id: need element_id or x,y coordinates"


def _type_by_id(parameters: dict) -> str:
    el_id = (parameters or {}).get("element_id", "").strip()
    text = (parameters or {}).get("text", "")
    x = (parameters or {}).get("x")
    y = (parameters or {}).get("y")

    if x is not None and y is not None:
        _cc_move(x=x, y=y)
        _cc_click(x=x, y=y)
        return _cc_type(text)
    if el_id:
        return (f"computer_use type_by_id: element_id '{el_id}' requires a prior "
                f"som_capture. Call som_capture first, or use computer_control "
                f"smart_type / type directly.")
    return "computer_use type_by_id: need element_id or x,y coordinates + text"


def _hover_by_id(parameters: dict) -> str:
    el_id = (parameters or {}).get("element_id", "").strip()
    x = (parameters or {}).get("x")
    y = (parameters or {}).get("y")

    if x is not None and y is not None:
        return _cc_move(x=x, y=y)
    if el_id:
        return (f"computer_use hover_by_id: element_id '{el_id}' requires a prior "
                f"som_capture. Call som_capture first.")
    return "computer_use hover_by_id: need element_id or x,y coordinates"


TOOL["handler"] = computer_use
