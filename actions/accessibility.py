"""
Accessibility Tree — Phase 5.1
AT-SPI on Linux, UI Automation on Windows, press buttons by name in Discord/VS Code/Electron.
Falls back to image search / coordinate click when native APIs unavailable.
"""
import platform
import time

_os = platform.system().lower()

def _press_windows(name: str, action: str = "press") -> str:
    # Try uiautomation / pywinauto if installed
    for mod_name in ("uiautomation", "pywinauto"):
        try:
            if mod_name == "uiautomation":
                import uiautomation as auto
                # Search for control by name in foreground window
                ctrl = auto.Control(searchDepth=6, Name=name)
                if ctrl.Exists(0.5):
                    if action in ("press", "click", "invoke"): ctrl.Click()
                    elif action == "double_click": ctrl.DoubleClick()
                    else: ctrl.Click()
                    return f"✓ {action} '{name}' via uiautomation"
            elif mod_name == "pywinauto":
                from pywinauto import Desktop
                dlg = Desktop(backend="uia").window(title_re=".*")
                # brute search is expensive — try find by name
                for win in dlg.descendants():
                    if name.lower() in str(getattr(win, "window_text", lambda: "")() or "").lower():
                        try:
                            win.click_input()
                            return f"✓ {action} '{name}' via pywinauto"
                        except: pass
        except Exception as e:
            continue
    return ""

def _press_linux(name: str, action: str = "press") -> str:
    # AT-SPI via pyatspi2 or atk
    try:
        import pyatspi
        registry = pyatspi.Registry
        desktop = registry.getDesktop(0)
        # Depth-first search for widget by name
        stack = [desktop]
        while stack:
            node = stack.pop()
            try:
                if name.lower() in (node.name or "").lower():
                    # Try to invoke action
                    act = node.queryAction() if hasattr(node, "queryAction") else None
                    if act:
                        for i in range(act.nActions):
                            if "press" in act.getName(i).lower() or "click" in act.getName(i).lower() or action.lower() in act.getName(i).lower():
                                act.doAction(i)
                                return f"✓ {action} '{name}' via AT-SPI"
                        act.doAction(0)
                        return f"✓ {action} '{name}' via AT-SPI"
                    # Fallback: click at center
                    comp = node.queryComponent() if hasattr(node, "queryComponent") else None
                    if comp:
                        ext = comp.getExtents(pyatspi.DESKTOP_COORDS)
                        import pyautogui
                        pyautogui.click(ext.x + ext.width//2, ext.y + ext.height//2)
                        return f"✓ {action} '{name}' via AT-SPI click"
            except: pass
            try:
                for i in range(node.childCount):
                    stack.append(node.getChildAtIndex(i))
            except: pass
    except ImportError:
        pass
    except Exception:
        pass
    return ""

def accessibility_control(parameters: dict, player=None, **_):
    target = str(parameters.get("target", "") or parameters.get("name", "") or parameters.get("button", "")).strip()
    action = str(parameters.get("action", "press")).strip().lower()  # press/click/type/list
    text = str(parameters.get("text", "") or parameters.get("value", "")).strip()
    if not target and action != "list":
        return "Need target: e.g. {\"action\":\"press\",\"target\":\"Send\"} or {\"action\":\"list\"} to dump tree"
    if action == "list":
        # Dump top-level window names for discovery
        out = []
        try:
            if _os == "windows":
                import uiautomation as auto
                root = auto.GetRootControl()
                for c, _ in auto.WalkControl(root):
                    if c.Name: out.append(c.Name)
                    if len(out) > 80: break
            else:
                import pyatspi
                desktop = pyatspi.Registry.getDesktop(0)
                for i in range(min(desktop.childCount, 20)):
                    try: out.append(desktop.getChildAtIndex(i).name or f"window-{i}")
                    except: pass
            return "Accessible windows/controls:\n" + "\n".join(f"  • {n}" for n in out[:40]) if out else "No AT-SPI controls found (is at-spi running?)"
        except Exception as e:
            return f"List unavailable: {e} — install pyatspi (Linux) or uiautomation/pywinauto (Windows)"
    # Try native path first
    msg = ""
    if _os == "windows":
        msg = _press_windows(target, action)
    elif _os == "linux":
        msg = _press_linux(target, action)
    else:
        # macOS: try AXUI via atomacos if installed
        try:
            import atomacos
            # atomacos search
            for app in atomacos.getApps():
                try:
                    for el in app.findElementsR(AXRole="AXButton"):
                        if target.lower() in (el.AXTitle or "").lower():
                            el.Press()
                            return f"✓ press '{target}' via atomacos"
                except: pass
        except: pass
    if msg: return msg
    # Fallback: type / hotkey via pyautogui
    if action in ("type", "write") and text:
        try:
            import pyautogui
            pyautogui.write(text, interval=0.02)
            return f"✓ typed '{text}' (fallback, target '{target}' not natively found)"
        except Exception as e: return f"Fallback type failed: {e}"
    return f"Could not find control '{target}' natively — install uiautomation/pywinauto (Windows) or pyatspi (Linux) for direct access. Tried { _os } backends."

TOOL={
    "name":"accessibility_control",
    "description":"Accessibility Tree: press buttons by name in Discord/VS Code/Electron via AT-SPI (Linux) / UI Automation (Windows). Actions: press/click/type/list. target=button label to press.",
    "parameters":{
        "type":"OBJECT",
        "properties":{
            "action":{"type":"STRING","description":"press|click|double_click|type|list"},
            "target":{"type":"STRING","description":"Button/label name to press, or empty for list"},
            "name":{"type":"STRING"},
            "button":{"type":"STRING"},
            "text":{"type":"STRING","description":"Text to type when action=type"},
            "value":{"type":"STRING"}
        },
        "required":["action"]
    },
    "handler":accessibility_control
}
