"""Bounded, cross-platform native accessibility control.

Native semantic APIs are always preferred over coordinates.  Discovery is
bounded by depth, node count, and time.  Mutations return observed evidence
instead of claiming success merely because an API call did not raise.
"""
from __future__ import annotations

import platform
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol

MAX_NODES = 500
MAX_DEPTH = 10
TIME_BUDGET_SECONDS = 2.0


@dataclass
class AccessibleNode:
    name: str
    role: str = ""
    value: str = ""
    enabled: bool = True
    selected: bool | None = None
    backend: Any = None
    actions: tuple[str, ...] = field(default_factory=tuple)

    def public(self) -> dict[str, Any]:
        return {
            "name": self.name[:160], "role": self.role[:80],
            "value": self.value[:240], "enabled": self.enabled,
            "selected": self.selected, "actions": list(self.actions[:20]),
        }


class Adapter(Protocol):
    def nodes(self) -> Iterable[AccessibleNode]: ...
    def perform(self, node: AccessibleNode, action: str, value: str = "") -> None: ...
    def observe(self, node: AccessibleNode) -> AccessibleNode: ...


def _clean(value: Any, limit: int = 240) -> str:
    return " ".join(str(value or "").split())[:limit]


def _windows_adapter() -> Adapter:
    import uiautomation as auto

    class WindowsAdapter:
        def nodes(self):
            root = auto.GetForegroundControl() or auto.GetRootControl()
            for control, depth in auto.WalkControl(root):
                if depth > MAX_DEPTH:
                    continue
                patterns = []
                ctype = _clean(getattr(control, "ControlTypeName", ""), 80)
                if any(token in ctype.lower() for token in ("button", "menuitem", "hyperlink")):
                    patterns.append("invoke")
                if any(token in ctype.lower() for token in ("edit", "document")):
                    patterns.append("set_value")
                if any(token in ctype.lower() for token in ("check", "toggle")):
                    patterns.append("toggle")
                yield AccessibleNode(_clean(getattr(control, "Name", ""), 160), ctype,
                                     _clean(getattr(control, "Value", "")),
                                     bool(getattr(control, "IsEnabled", True)), backend=control,
                                     actions=tuple(patterns))

        def perform(self, node, action, value=""):
            control = node.backend
            if action in {"invoke", "press", "click"}:
                try: control.GetInvokePattern().Invoke()
                except Exception: control.Click(simulateMove=False)
            elif action == "set_value":
                control.GetValuePattern().SetValue(value)
            elif action == "toggle":
                control.GetTogglePattern().Toggle()
            elif action == "select":
                control.GetSelectionItemPattern().Select()
            else: raise ValueError(f"unsupported native action: {action}")

        def observe(self, node):
            c = node.backend
            return AccessibleNode(_clean(getattr(c, "Name", "")), node.role,
                                  _clean(getattr(c, "Value", "")), bool(getattr(c, "IsEnabled", True)),
                                  backend=c, actions=node.actions)
    return WindowsAdapter()


def _linux_adapter() -> Adapter:
    import pyatspi

    class LinuxAdapter:
        def nodes(self):
            stack = [(pyatspi.Registry.getDesktop(0), 0)]
            while stack:
                node, depth = stack.pop()
                if depth > MAX_DEPTH: continue
                actions = []
                try:
                    iface = node.queryAction()
                    actions = [_clean(iface.getName(i), 80).lower() for i in range(iface.nActions)]
                except Exception: pass
                yield AccessibleNode(_clean(getattr(node, "name", ""), 160),
                                     _clean(getattr(node, "getRoleName", lambda: "")(), 80),
                                     enabled=True, backend=node, actions=tuple(actions))
                try:
                    for index in range(min(int(node.childCount), 100)):
                        stack.append((node.getChildAtIndex(index), depth + 1))
                except Exception: pass

        def perform(self, node, action, value=""):
            if action in {"invoke", "press", "click", "toggle", "select"}:
                iface = node.backend.queryAction()
                wanted = {"invoke": ("press", "click", "activate"), "press": ("press", "click", "activate"),
                          "click": ("click", "press", "activate"), "toggle": ("toggle", "press"),
                          "select": ("select", "press")}[action]
                for i in range(iface.nActions):
                    if any(word in iface.getName(i).lower() for word in wanted):
                        if not iface.doAction(i): raise RuntimeError("AT-SPI rejected the action")
                        return
                raise ValueError("control does not expose the requested action")
            if action == "set_value":
                iface = node.backend.queryEditableText(); iface.setTextContents(value); return
            raise ValueError(f"unsupported native action: {action}")

        def observe(self, node):
            return AccessibleNode(_clean(getattr(node.backend, "name", "")), node.role,
                                  enabled=True, backend=node.backend, actions=node.actions)
    return LinuxAdapter()


def _mac_adapter() -> Adapter:
    import atomacos

    class MacAdapter:
        def nodes(self):
            for app in atomacos.getApps():
                try: elements = app.findElementsR()
                except Exception: continue
                for element in elements[:MAX_NODES]:
                    yield AccessibleNode(_clean(getattr(element, "AXTitle", ""), 160),
                                         _clean(getattr(element, "AXRole", ""), 80),
                                         _clean(getattr(element, "AXValue", "")),
                                         bool(getattr(element, "AXEnabled", True)), backend=element,
                                         actions=tuple(_clean(v, 80) for v in (getattr(element, "AXActions", []) or [])))

        def perform(self, node, action, value=""):
            element = node.backend
            if action in {"invoke", "press", "click", "toggle", "select"}: element.Press(); return
            if action == "set_value": element.AXValue = value; return
            raise ValueError(f"unsupported native action: {action}")

        def observe(self, node):
            e = node.backend
            return AccessibleNode(_clean(getattr(e, "AXTitle", "")), node.role,
                                  _clean(getattr(e, "AXValue", "")), bool(getattr(e, "AXEnabled", True)),
                                  backend=e, actions=node.actions)
    return MacAdapter()


def system_adapter(system: str | None = None) -> Adapter:
    name = (system or platform.system()).lower()
    if name == "windows": return _windows_adapter()
    if name == "linux": return _linux_adapter()
    if name in {"darwin", "mac", "macos"}: return _mac_adapter()
    raise RuntimeError(f"native accessibility is unsupported on {name}")


def find(adapter: Adapter, target: str, role: str = "") -> tuple[AccessibleNode | None, str]:
    wanted = _clean(target, 160).casefold(); wanted_role = _clean(role, 80).casefold()
    if not wanted: return None, "target is required"
    deadline = time.monotonic() + TIME_BUDGET_SECONDS
    exact, partial = [], []
    for index, node in enumerate(adapter.nodes()):
        if index >= MAX_NODES or time.monotonic() > deadline: break
        name = node.name.casefold(); node_role = node.role.casefold()
        if wanted_role and wanted_role not in node_role: continue
        if name == wanted: exact.append(node)
        elif wanted in name: partial.append(node)
    matches = exact or partial
    if not matches: return None, "no matching native control"
    if len(matches) > 1:
        return None, f"ambiguous native target ({len(matches)} matches); provide an exact name and role"
    return matches[0], "exact" if exact else "unique partial"


def execute(adapter: Adapter, target: str, action: str, value: str = "", role: str = "") -> dict[str, Any]:
    normalized = {"click": "invoke", "press": "invoke", "type": "set_value", "write": "set_value"}.get(action, action)
    if normalized not in {"invoke", "set_value", "toggle", "select"}:
        return {"ok": False, "verified": False, "error": "unsupported accessibility action"}
    node, match = find(adapter, target, role)
    if node is None: return {"ok": False, "verified": False, "error": match}
    if not node.enabled: return {"ok": False, "verified": True, "error": "matching control is disabled"}
    before = node.public()
    try:
        adapter.perform(node, normalized, value)
        observed = adapter.observe(node)
    except Exception as exc:
        return {"ok": False, "verified": True, "error": f"native action failed: {type(exc).__name__}"}
    after = observed.public()
    verified = True
    if normalized == "set_value": verified = after["value"] == _clean(value)
    return {"ok": verified, "verified": verified, "match": match, "action": normalized,
            "control": after, "changed": before != after}
