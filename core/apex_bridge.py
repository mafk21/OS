"""
core/apex_bridge.py — Real-time WebSocket + HTTP bridge between JARVIS and APEX-UI.

Serves the pre-built `apex_ui/static_hud` bundle locally (zero Node.js required
at runtime) and streams JARVIS's live states, audio waveform levels, transcripts,
circuit-spoke tool traces, settings, and unforgeable action confirmations to the
APEX-UI desktop HUD.
"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import shutil
import socket
import subprocess
import threading
import time
import urllib.request
import webbrowser
from collections import deque
from pathlib import Path
from typing import Any, Callable

try:
    from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover
    FastAPI = Request = WebSocket = WebSocketDisconnect = None  # type: ignore[assignment,misc]
    FileResponse = HTMLResponse = JSONResponse = StaticFiles = None  # type: ignore[assignment,misc]
from core import (
    audio_devices,
    automations,
    companions,
    dev_workspace,
    mcp_adapter,
    security_vault,
)
from core import confirm as confirm_gate
from memory import accounts
from memory import config_manager as cfg
from memory import memory_manager as mm
from memory import timeline
from memory import config_manager as cfg

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_HUD_DIR = BASE_DIR / "apex_ui" / "static_hud"

# Maps JARVIS built-in actions, plugins, and default skills onto the 18 nodes
# of APEX-UI's ReasoningWeb constellation so live cyan circuit particles stream
# along the exact specialist spokes whenever JARVIS invokes a tool.
TOOL_NODE_MAP: dict[str, list[str]] = {
    "web_search": ["researcher"],
    "youtube_video": ["researcher", "social_media"],
    "memory": ["memory"],
    "brain_control": ["memory", "editor"],
    "smart_notes": ["memory", "editor"],
    "lecture_capture": ["memory", "editor"],
    "code_helper": ["developer", "engineering"],
    "cmd_control": ["ops", "developer"],
    "computer_settings": ["ops", "chief_of_staff"],
    "desktop_control": ["ops", "chief_of_staff"],
    "open_app": ["ops"],
    "system_doctor": ["engineering", "analytics"],
    "system_monitor": ["engineering", "analytics"],
    "printer_control": ["engineering"],
    "home_assistant": ["engineering", "ops"],
    "browser_control": ["social_media", "researcher"],
    "screen_process": ["design", "chief_of_staff"],
    "weather_report": ["design", "chief_of_staff"],
    "pushup_counter": ["design"],
    "clipboard_intelligence": ["editor"],
    "file_processor": ["editor", "drive"],
    "file_controller": ["drive", "ops"],
    "excel_writer": ["finance", "analytics"],
    "morning_briefing": ["chief_of_staff", "strategist"],
    "focus_guardian": ["chief_of_staff", "strategist"],
    "cloud_integrations": ["email", "drive", "calendar"],
    "custom_connector": ["developer", "ops"],
    "manage_accounts": ["chief_of_staff", "email"],
    "gws_pack": ["email", "drive", "calendar"],
    "github_automation": ["developer", "engineering"],
    "remote_relay": ["sales", "ops"],
    "music_selection": ["design", "social_media"],
    "gmail_control": ["email"],
    "calendar_control": ["calendar"],
    "whatsapp": ["sales"],
    "chat_takeover": ["sales"],
    "agent_task": ["strategist", "chief_of_staff"],
}


def map_tool_to_nodes(tool_name: str) -> list[str]:
    """Return 1–2 ReasoningWeb node keys matching a JARVIS tool or skill name."""
    key = (tool_name or "").strip().lower()
    if key in TOOL_NODE_MAP:
        return list(TOOL_NODE_MAP[key])
    for prefix, nodes in TOOL_NODE_MAP.items():
        if prefix in key or key in prefix:
            return list(nodes)
    return ["chief_of_staff", "developer"]


def _pick_port(host: str = "127.0.0.1", preferred: int = 8765) -> int:
    for candidate in (preferred, 8766, 8767, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, candidate))
                return int(s.getsockname()[1])
            except OSError:
                continue
    raise RuntimeError("Could not bind any local port for APEX-UI bridge")


class ApexHudBridge:
    """Thread-safe local HTTP + WebSocket server driving the APEX-UI desktop HUD."""

    def __init__(
        self,
        ui_ref: Any = None,
        *,
        host: str | None = None,
        port: int | None = None,
        on_all_windows_closed: Callable[[], None] | None = None,
        auto_close_on_disconnect: bool = False,
    ) -> None:
        self._ui = ui_ref
        self.host = host or os.environ.get("JARVIS_HUD_HOST", "127.0.0.1")
        env_port = int(os.environ.get("JARVIS_HUD_PORT", "0") or "0")
        self.port = port or (env_port if env_port > 0 else _pick_port(self.host))
        self.url = f"http://127.0.0.1:{self.port}/"

        self._on_all_windows_closed = on_all_windows_closed
        self._auto_close = auto_close_on_disconnect

        self._lock = threading.Lock()
        self._raw_state = "LISTENING"
        self._offline = False
        self._offline_reason = ""
        self._logs: deque[str] = deque(maxlen=140)
        try:
            for seed_ln in timeline.get_console_seed_lines(limit=80):
                self._logs.append(seed_ln)
        except Exception:
            pass
        self._confirm: dict[str, str] | None = None
        self._content: dict[str, str] | None = None
        self._last_level_push = 0.0
        self._tool_tasks: dict[str, dict[str, Any]] = {}
        self._cancelled_task_ids: set[str] = set()

        try:
            from core.subagents import get_subagent_manager
            get_subagent_manager().add_listener(self.push_activity)
        except Exception:
            pass
        try:
            dev_workspace.get_terminal_manager().add_listener(self.push_terminal_session)
        except Exception:
            pass

        self._loop: asyncio.AbstractEventLoop | None = None
        self._clients: set[Any] = set()
        self._had_ws_client = False
        self._close_timer: threading.Timer | None = None
        self._started = threading.Event()
        self._server: Any = None
        self._thread: threading.Thread | None = None

        self._wx_cache: dict[str, Any] | None = None
        self._wx_cached_at = 0.0
        self._auto_scheduler = automations.AutomationScheduler(on_log=self.push_log)

    # ── State inspection helpers ──────────────────────────────────────────────

    def _is_ready(self) -> bool:
        if os.environ.get("JARVIS_HUD_PREVIEW_READY") == "1":
            return True
        win = getattr(self._ui, "_win", None)
        if win is not None and hasattr(win, "_ready"):
            return bool(win._ready)
        return cfg.is_configured()

    def _is_persona_chosen(self) -> bool:
        if os.environ.get("JARVIS_SKIP_PERSONA_PROMPT", "").strip().lower() in (
            "1", "true", "yes",
        ):
            return True
        if self._ui is not None and hasattr(self._ui, "_persona_selected"):
            return bool(self._ui._persona_selected)
        return True

    def _is_integrations_ready(self) -> bool:
        if os.environ.get("JARVIS_HUD_PREVIEW_READY") == "1":
            return True
        if os.environ.get("JARVIS_SKIP_INTEGRATIONS_PROMPT", "").strip().lower() in (
            "1", "true", "yes",
        ):
            return True
        if self._ui is not None and hasattr(self._ui, "_integrations_ready"):
            return bool(self._ui._integrations_ready)
        if self._ui is not None:
            return True
        return cfg.is_integrations_onboarding_done()

    def _is_muted(self) -> bool:
        if self._ui is not None and hasattr(self._ui, "muted"):
            try:
                return bool(self._ui.muted)
            except Exception:
                pass
        return False

    def _is_paused(self) -> bool:
        if self._ui is not None:
            gp_ui = getattr(self._ui, "get_pause_state", None)
            if callable(gp_ui):
                try:
                    return bool(gp_ui())
                except Exception:
                    pass
        win = getattr(self._ui, "_win", None)
        if win is not None:
            gp = getattr(win, "get_pause_state", None)
            if callable(gp):
                try:
                    return bool(gp())
                except Exception:
                    pass
            return bool(getattr(win, "_paused_ui", False))
        return False

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            logs_list = list(self._logs)
            confirm_obj = dict(self._confirm) if self._confirm else None
            content_obj = dict(self._content) if self._content else None
            raw_state = self._raw_state
            offline = self._offline
            offline_reason = self._offline_reason

        try:
            in_devs = audio_devices.list_devices("input")
        except Exception:
            in_devs = [audio_devices.DEFAULT_LABEL]
        try:
            out_devs = audio_devices.list_devices("output")
        except Exception:
            out_devs = [audio_devices.DEFAULT_LABEL]

        try:
            b_counts = timeline.get_brain_snapshot()["counts"]
        except Exception:
            b_counts = {"memories": 0, "files": 0, "outputs": 0, "timeline": 0}

        return {
            "type": "bootstrap",
            "ready": self._is_ready(),
            "integrations_ready": self._is_integrations_ready(),
            "integrations": accounts.get_integrations_status_summary(),
            "privacy": cfg.get_privacy_settings(),
            "brain_counts": b_counts,
            "workers": self.get_activity_snapshot(),
            "active_companion": companions.get_active_companion(),
            "theme_custom": companions.get_theme_customization(),
            "persona": cfg.get_persona(),
            "persona_chosen": self._is_persona_chosen(),
            "assistant_name": cfg.get_assistant_name(),
            "raw_state": raw_state,
            "muted": self._is_muted(),
            "paused": self._is_paused(),
            "offline": offline,
            "offline_reason": offline_reason,
            "voice": cfg.get_voice(),
            "voices": list(cfg.AVAILABLE_VOICES),
            "male_voices": list(cfg.MALE_VOICES),
            "female_voices": list(cfg.FEMALE_VOICES),
            "barge_enabled": cfg.get_barge_in_enabled(),
            "grace_period": cfg.get_grace_period(),
            "inputs": in_devs,
            "outputs": out_devs,
            "current_input": cfg.get_input_device(),
            "current_output": cfg.get_output_device(),
            "logs": logs_list,
            "confirm": confirm_obj,
            "content": content_obj,
        }

    # ── Push methods called from JarvisUI / audio threads ─────────────────────

    def _broadcast_threadsafe(self, payload: dict[str, Any]) -> None:
        loop = self._loop
        if loop is None or loop.is_closed():
            return
        try:
            loop.call_soon_threadsafe(
                asyncio.create_task, self._async_broadcast(payload)
            )
        except RuntimeError:
            pass

    async def _async_broadcast(self, payload: dict[str, Any]) -> None:
        if not self._clients:
            return
        raw = json.dumps(payload)
        stale = []
        for ws in list(self._clients):
            try:
                await ws.send_text(raw)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._clients.discard(ws)

    def push_state(self, state: str) -> None:
        s = (state or "LISTENING").upper()
        with self._lock:
            self._raw_state = s
            offline = self._offline
            offline_reason = self._offline_reason
        self._broadcast_threadsafe(
            {
                "type": "state",
                "raw_state": s,
                "muted": self._is_muted(),
                "paused": self._is_paused(),
                "offline": offline,
                "offline_reason": offline_reason,
            }
        )

    def push_audio_level(self, level: float) -> None:
        now = time.monotonic()
        if now - self._last_level_push < 0.04:  # cap at ~25 Hz
            return
        self._last_level_push = now
        lv = max(0.0, min(1.0, float(level or 0.0)))
        self._broadcast_threadsafe({"type": "level", "level": round(lv, 4)})

    def push_log(self, text: str) -> None:
        line = str(text or "").strip()
        if not line:
            return
        with self._lock:
            self._logs.append(line)
        self._broadcast_threadsafe(
            {
                "type": "log",
                "line": line,
                "ts": time.strftime("%H:%M:%S"),
            }
        )

    def push_tool_trace(self, tool_names: list[str] | str) -> None:
        names = [tool_names] if isinstance(tool_names, str) else list(tool_names or [])
        nodes: list[str] = []
        for name in names:
            for n in map_tool_to_nodes(name):
                if n not in nodes:
                    nodes.append(n)
        if nodes:
            self._broadcast_threadsafe(
                {
                    "type": "trace",
                    "tool": ", ".join(names),
                    "nodes": nodes[:4],
                }
            )

    def get_activity_snapshot(self) -> list[dict[str, Any]]:
        """Unified live worker list combining SubagentManager + running/recent tool tasks."""
        items: list[dict[str, Any]] = []
        try:
            from core.subagents import get_subagent_manager
            items.extend(get_subagent_manager().list_detailed())
        except Exception:
            pass

        now = time.time()
        with self._lock:
            tasks = list(self._tool_tasks.values())
        for t in tasks:
            end_ts = t["updated_at"] if t["status"] in ("completed", "failed", "cancelled") else now
            items.append(
                {
                    **t,
                    "elapsed_s": round(max(0.0, end_ts - float(t["created_at"])), 1),
                }
            )

        # Sort active/pending first, then newest first
        rank = {"in_progress": 0, "pending": 1, "completed": 2, "failed": 2, "cancelled": 2}
        items.sort(key=lambda w: (rank.get(str(w.get("status")), 3), -float(w.get("created_at") or 0)))
        return items[:36]

    def push_activity(self) -> None:
        self._broadcast_threadsafe(
            {"type": "activity", "workers": self.get_activity_snapshot()}
        )

    def push_terminal_session(self, session: dict[str, Any]) -> None:
        self._broadcast_threadsafe({"type": "terminal", "session": session})

    def notify_tool_start(
        self, task_id: str, tool_name: str, args_summary: str = ""
    ) -> None:
        now = time.time()
        tid = str(task_id or f"tool-{int(now * 1000)}")
        label = f"{tool_name}" + (f" · {args_summary[:64]}" if args_summary else "")
        rec: dict[str, Any] = {
            "id": tid,
            "kind": "tool",
            "title": label,
            "goal": label,
            "status": "in_progress",
            "tools": [tool_name],
            "nodes": map_tool_to_nodes(tool_name)[:3],
            "steps": [{"step": 1, "action": tool_name, "result": args_summary[:180] or "Running…", "ts": now}],
            "step_count": 1,
            "max_steps": 1,
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._tool_tasks[tid] = rec
            if len(self._tool_tasks) > 32:
                # Prune oldest finished entries first
                finished = [
                    k for k, v in self._tool_tasks.items()
                    if v.get("status") in ("completed", "failed", "cancelled")
                ]
                for k in finished[:8]:
                    self._tool_tasks.pop(k, None)
        self.push_activity()

    def notify_tool_finish(
        self, task_id: str, result_summary: str = "", status: str = "completed"
    ) -> None:
        now = time.time()
        with self._lock:
            rec = self._tool_tasks.get(str(task_id))
            if rec is None:
                return
            if str(task_id) in self._cancelled_task_ids:
                rec["status"] = "cancelled"
            else:
                rec["status"] = status if status in ("completed", "failed", "cancelled") else "completed"
            rec["updated_at"] = now
            if rec["status"] == "failed":
                rec["error"] = str(result_summary or "")[:300]
            else:
                rec["result"] = str(result_summary or "")[:300]
            if rec.get("steps"):
                rec["steps"][-1]["result"] = str(result_summary or "Done.")[:220]
        self.push_activity()

    def is_task_cancelled(self, task_id: str) -> bool:
        with self._lock:
            return str(task_id) in self._cancelled_task_ids

    def push_confirm(self, title: str, detail: str) -> None:
        obj = {"title": str(title)[:120], "detail": str(detail)[:300]}
        with self._lock:
            self._confirm = obj
        self._broadcast_threadsafe({"type": "confirm", "confirm": obj})

    def hide_confirm(self) -> None:
        with self._lock:
            self._confirm = None
        self._broadcast_threadsafe({"type": "confirm", "confirm": None})

    def push_content(self, title: str, text: str) -> None:
        obj = {"title": str(title)[:64], "text": str(text)[:4000]}
        with self._lock:
            self._content = obj
        try:
            timeline.record_output(str(title)[:120], str(text)[:12000])
        except Exception:
            pass
        self._broadcast_threadsafe({"type": "content", "content": obj})

    def push_offline(self, offline: bool, reason: str = "") -> None:
        with self._lock:
            self._offline = bool(offline)
            self._offline_reason = str(reason or "")
            raw = self._raw_state
        self._broadcast_threadsafe(
            {
                "type": "state",
                "raw_state": raw,
                "muted": self._is_muted(),
                "paused": self._is_paused(),
                "offline": bool(offline),
                "offline_reason": str(reason or ""),
            }
        )

    def push_reconfig(self) -> None:
        self._broadcast_threadsafe({"type": "reconfig"})

    # ── Inbound HUD command execution ─────────────────────────────────────────

    def handle_action(self, data: dict[str, Any]) -> dict[str, Any]:
        action = str(data.get("action") or "").strip()
        ui = self._ui
        win = getattr(ui, "_win", None) if ui is not None else None

        if action == "save_api_key":
            key = str(data.get("key") or "").strip()
            if len(key) < 15:
                return {"ok": False, "error": "Invalid API key"}
            os_name = platform.system()
            cfg.ensure_config_dir()
            existing = cfg.load_api_keys()
            existing["gemini_api_key"] = key
            existing.setdefault("os_system", os_name)
            cfg.CONFIG_FILE.write_text(
                json.dumps(existing, indent=4), encoding="utf-8"
            )
            if win is not None:
                win._ready = True
                self._invoke_qt(lambda: win._on_setup_done(key, os_name))
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True}

        if action == "save_integrations":
            was_live = self._is_persona_chosen()
            payload = data.get("integrations")
            res = accounts.save_onboarding_integrations(
                payload if isinstance(payload, dict) else {}
            )
            if ui is not None:
                setattr(ui, "_integrations_ready", True)
            if win is not None and hasattr(win, "mark_integrations_done"):
                self._invoke_qt(win.mark_integrations_done)
            saved_list = res.get("saved") or []
            if saved_list:
                self.push_log(f"SYS: Connected integrations: {', '.join(saved_list)}.")
            else:
                self.push_log(
                    "SYS: Optional integrations saved (unfilled services ignored)."
                )
            if was_live and ui is not None:
                cb = getattr(ui, "on_integrations_change", None)
                if callable(cb):
                    threading.Thread(target=cb, daemon=True).start()
            self._broadcast_threadsafe(self.snapshot())
            return res

        if action == "skip_integrations":
            cfg.save_integrations_onboarding_done(True)
            if ui is not None:
                setattr(ui, "_integrations_ready", True)
            if win is not None and hasattr(win, "mark_integrations_done"):
                self._invoke_qt(win.mark_integrations_done)
            self.push_log(
                "SYS: Optional integrations skipped — connect any anytime in HUD -> Integrations."
            )
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "summary": accounts.get_integrations_status_summary()}

        if action == "disconnect_integration":
            svc = str(data.get("service") or "").strip().lower()
            if svc == "google":
                for g_svc in ("gmail", "google_drive", "google_calendar"):
                    accounts.disconnect_account(g_svc)
            elif svc:
                accounts.disconnect_account(svc)
            self.push_log(f"SYS: Disconnected {svc or 'integration'}.")
            if self._is_persona_chosen() and ui is not None:
                cb = getattr(ui, "on_integrations_change", None)
                if callable(cb):
                    threading.Thread(target=cb, daemon=True).start()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "summary": accounts.get_integrations_status_summary()}

        if action == "start_google_oauth":
            cid = str(data.get("client_id") or "").strip()
            csec = str(data.get("client_secret") or "").strip()
            if not cid or not csec:
                return {
                    "ok": False,
                    "error": "Enter Google OAuth Client ID and Client Secret first.",
                }
            for g_svc in ("gmail", "google_drive", "google_calendar"):
                accounts.connect_account(
                    g_svc, client_id=cid, client_secret=csec, permission="full"
                )
            redirect_uri = f"http://127.0.0.1:{self.port}/api/oauth/google/callback"
            auth_url = accounts.build_google_oauth_url(cid, redirect_uri)
            return {"ok": True, "auth_url": auth_url, "redirect_uri": redirect_uri}

        if action == "text_command":
            txt = str(data.get("text") or "").strip()
            if txt:
                self.push_log(f"You: {txt}")
                self.push_state("THINKING")
                cb = getattr(ui, "on_text_command", None) if ui else None
                if callable(cb):
                    threading.Thread(target=cb, args=(txt,), daemon=True).start()
                else:
                    try:
                        timeline.append_turn("user", txt, speaker="You", channel="text")
                        companions.detect_and_record_correction(txt)
                    except Exception:
                        pass
            return {"ok": True}

        if action == "orb_tap":
            with self._lock:
                cur = self._raw_state
            if cur == "SPEAKING" and ui is not None and callable(getattr(ui, "on_interrupt", None)):
                ui.on_interrupt()
                self.push_state("LISTENING")
            elif self._is_muted() and ui is not None:
                self._invoke_qt(lambda: setattr(ui, "muted", False))
            elif self._is_paused() and win is not None:
                self._invoke_qt(win._toggle_pause)
                self.push_state("LISTENING")
            else:
                wake_cb = getattr(ui, "on_wake_manual", None) if ui else None
                ptt_cb = getattr(ui, "on_push_to_talk", None) if ui else None
                if callable(wake_cb):
                    threading.Thread(target=wake_cb, daemon=True).start()
                elif callable(ptt_cb):
                    threading.Thread(target=ptt_cb, daemon=True).start()
            return {"ok": True}

        if action == "toggle_mute" and ui is not None:
            new_muted = not self._is_muted()
            self._invoke_qt(lambda: setattr(ui, "muted", new_muted))
            self.push_state("MUTED" if new_muted else "LISTENING")
            return {"ok": True, "muted": new_muted}

        if action == "toggle_pause":
            cb = getattr(ui, "on_pause_toggle", None) if ui is not None else None
            if callable(cb):
                try:
                    paused = bool(cb())
                except Exception:
                    paused = self._is_paused()
            elif win is not None and hasattr(win, "_toggle_pause"):
                self._invoke_qt(win._toggle_pause)
                time.sleep(0.02)
                paused = self._is_paused()
            else:
                paused = False
            self.push_state("PAUSED" if paused else "LISTENING")
            return {"ok": True, "paused": paused}

        if action == "interrupt" and ui is not None:
            cb = getattr(ui, "on_interrupt", None)
            if callable(cb):
                cb()
            self.push_state("LISTENING")
            return {"ok": True}

        if action == "stop_all":
            if ui is not None and callable(getattr(ui, "on_stop_all", None)):
                ui.on_stop_all()
            elif win is not None and hasattr(win, "_do_stop_all"):
                self._invoke_qt(win._do_stop_all)
            self.push_state("LISTENING")
            return {"ok": True}

        if action == "region_capture" and win is not None:
            if ui is not None and getattr(ui, "_on_region_capture", None) and not getattr(win, "_on_region_capture", None):
                win._on_region_capture = ui._on_region_capture
            self._invoke_qt(win._start_region_pick)
            return {"ok": True}

        if action == "remote_qr" and ui is not None:
            cb = getattr(ui, "on_remote_clicked", None)
            if callable(cb):
                threading.Thread(target=cb, daemon=True).start()
            return {"ok": True}

        if action == "set_persona":
            raw_p = str(data.get("persona") or "male").strip().lower()
            req_voice = str(data.get("voice") or "").strip()
            was_chosen = self._is_persona_chosen()
            prev_voice = cfg.get_voice()
            res = cfg.save_persona(raw_p, req_voice or None)
            if ui is not None:
                setattr(ui, "_persona_selected", True)
                if hasattr(ui, "apply_persona_visuals"):
                    self._invoke_qt(
                        lambda p=res["persona"], c=res["ui_color"]: ui.apply_persona_visuals(p, c)
                    )
            if was_chosen and res["voice"] != prev_voice:
                cb = getattr(ui, "on_voice_change", None) if ui else None
                if callable(cb):
                    threading.Thread(target=cb, args=(res["voice"],), daemon=True).start()
            self.push_log(
                f"SYS: {res['persona'].capitalize()} interface activated · Voice: {res['voice']}."
            )
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, **res}

        if action == "set_voice":
            v = str(data.get("voice") or "").strip()
            if v in cfg.AVAILABLE_VOICES:
                cfg.save_voice(v)
                cb = getattr(ui, "on_voice_change", None) if ui else None
                if callable(cb):
                    threading.Thread(target=cb, args=(v,), daemon=True).start()
                self._broadcast_threadsafe(self.snapshot())
            return {"ok": True}

        if action == "set_audio_devices":
            in_dev = str(data.get("input_device") or "")
            out_dev = str(data.get("output_device") or "")
            if in_dev == audio_devices.DEFAULT_LABEL:
                in_dev = ""
            if out_dev == audio_devices.DEFAULT_LABEL:
                out_dev = ""
            prev_in = cfg.get_input_device()
            prev_out = cfg.get_output_device()
            cfg.save_input_device(in_dev)
            cfg.save_output_device(out_dev)
            cb = getattr(ui, "on_audio_device_change", None) if ui else None
            if callable(cb):
                if in_dev != prev_in:
                    threading.Thread(
                        target=cb, args=("input", in_dev), daemon=True
                    ).start()
                if out_dev != prev_out:
                    threading.Thread(
                        target=cb, args=("output", out_dev), daemon=True
                    ).start()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True}

        if action == "set_barge":
            enabled = bool(data.get("enabled", True))
            cfg.save_barge_in_enabled(enabled)
            gb = getattr(ui, "get_barge_state", None) if ui is not None else None
            tb = getattr(ui, "on_barge_toggle", None) if ui is not None else None
            if callable(tb):
                cur = bool(gb()) if callable(gb) else (not enabled)
                if cur != enabled:
                    tb()
            elif win is not None and hasattr(win, "_toggle_barge"):
                self._invoke_qt(win._toggle_barge)
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True}

        if action == "set_grace":
            sec = max(2, min(30, int(data.get("seconds") or 8)))
            cfg.save_grace_period(sec)
            if ui is not None and callable(getattr(ui, "on_grace_change", None)):
                ui.on_grace_change(sec)
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True}

        if action == "confirm_decision":
            approved = bool(data.get("approved", False))
            confirm_gate.resolve(approved)
            self.hide_confirm()
            return {"ok": True}

        if action == "brain_get":
            return {"ok": True, "brain": timeline.get_brain_snapshot()}

        if action == "brain_search":
            q = str(data.get("query") or "").strip()
            return {
                "ok": True,
                "memories": mm.all_entries_for_ui()
                if not q
                else [
                    m
                    for m in mm.all_entries_for_ui()
                    if q.lower() in m["key"].lower()
                    or q.lower() in m["value"].lower()
                    or q.lower() in m["category"].lower()
                ],
                "timeline": timeline.search_timeline(
                    q, limit=40, channel=str(data.get("channel") or "")
                ),
                "files": [
                    f
                    for f in timeline.list_knowledge_files()
                    if not q
                    or q.lower() in f["filename"].lower()
                    or q.lower() in f["preview"].lower()
                ],
                "outputs": timeline.list_outputs(q, limit=40),
            }

        if action == "brain_save_memory":
            cat = str(data.get("category") or "notes").strip().lower()
            key = str(data.get("key") or "").strip()
            val = str(data.get("value") or "").strip()
            if not key or not val:
                return {"ok": False, "error": "Both key and value are required."}
            mm.remember(key, val, category=cat, manual=True)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_forget_memory":
            cat = str(data.get("category") or "notes").strip().lower()
            key = str(data.get("key") or "").strip()
            mm.forget(key, category=cat)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_clear_memories":
            mm.clear_all_memories()
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_upload_file":
            fname = str(data.get("filename") or "note.md").strip()
            content_val = str(data.get("content") or "")
            is_b64 = bool(data.get("is_base64", False))
            if not content_val:
                return {"ok": False, "error": "Empty file content."}
            rec = timeline.ingest_knowledge_file(fname, content_val, is_base64=is_b64)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "file": rec, "brain": snap}

        if action == "brain_read_file":
            fid = int(data.get("file_id") or 0)
            doc = timeline.read_knowledge_file(fid)
            return {"ok": doc is not None, "file": doc}

        if action == "brain_delete_file":
            fid = int(data.get("file_id") or 0)
            timeline.delete_knowledge_file(fid)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_delete_turn":
            mid = int(data.get("id") or 0)
            timeline.delete_timeline_message(mid)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_clear_timeline":
            timeline.clear_timeline()
            with self._lock:
                self._logs.clear()
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_pin_output":
            oid = int(data.get("id") or 0)
            pinned = timeline.toggle_pin_output(oid)
            return {"ok": True, "pinned": pinned, "brain": timeline.get_brain_snapshot()}

        if action == "brain_delete_output":
            oid = int(data.get("id") or 0)
            timeline.delete_output(oid)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "brain": snap}

        if action == "brain_set_privacy":
            if "personalization_enabled" in data:
                cfg.save_personalization_enabled(bool(data["personalization_enabled"]))
            if "adaptive_learning_enabled" in data:
                cfg.save_adaptive_learning_enabled(bool(data["adaptive_learning_enabled"]))
            if "timeline_persistence_enabled" in data:
                cfg.save_timeline_persistence_enabled(bool(data["timeline_persistence_enabled"]))
            if self._is_persona_chosen() and ui is not None:
                cb = getattr(ui, "on_integrations_change", None)
                if callable(cb):
                    threading.Thread(target=cb, daemon=True).start()
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "privacy": cfg.get_privacy_settings(), "brain": snap}

        if action == "brain_import_json":
            payload = data.get("payload")
            if not isinstance(payload, dict):
                return {"ok": False, "error": "Invalid Brain JSON payload."}
            restored = timeline.import_brain_json(payload)
            snap = timeline.get_brain_snapshot()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "restored": restored, "brain": snap}

        # ── 3D World View Worker Orbs & Activity Timeline actions ─────────────

        if action == "activity_get":
            return {"ok": True, "workers": self.get_activity_snapshot()}

        if action == "spawn_worker":
            goal = str(data.get("goal") or "").strip()
            if not goal:
                return {"ok": False, "error": "Worker goal is required."}
            raw_tools = data.get("tools")
            tools = [str(t) for t in raw_tools] if isinstance(raw_tools, list) else []
            auto_start = bool(data.get("auto_start", True))
            from core.subagents import get_subagent_manager
            mgr = get_subagent_manager()
            wid = mgr.spawn(goal=goal, tools=tools, max_steps=int(data.get("max_steps") or 10))
            if auto_start:
                mgr.start(wid)
            self.push_log(f"SYS: Spawned worker {wid} — {goal[:72]}")
            if tools:
                self.push_tool_trace(tools)
            return {"ok": True, "worker_id": wid, "workers": self.get_activity_snapshot()}

        if action == "step_worker":
            wid = str(data.get("worker_id") or "").strip()
            step_act = str(data.get("step_action") or "step").strip()
            step_res = str(data.get("step_result") or "").strip()
            from core.subagents import get_subagent_manager
            ok = get_subagent_manager().add_step(wid, step_act, step_res)
            return {"ok": ok, "workers": self.get_activity_snapshot()}

        if action == "complete_worker":
            wid = str(data.get("worker_id") or "").strip()
            res_txt = str(data.get("result") or "Completed.").strip()
            from core.subagents import get_subagent_manager
            ok = get_subagent_manager().complete(wid, res_txt)
            return {"ok": ok, "workers": self.get_activity_snapshot()}

        if action == "cancel_worker":
            wid = str(data.get("worker_id") or "").strip()
            cancelled = False
            try:
                from core.subagents import get_subagent_manager
                cancelled = get_subagent_manager().cancel(wid)
            except Exception:
                pass
            if not cancelled:
                with self._lock:
                    self._cancelled_task_ids.add(wid)
                    rec = self._tool_tasks.get(wid)
                    if rec and rec.get("status") in ("in_progress", "pending"):
                        rec["status"] = "cancelled"
                        rec["updated_at"] = time.time()
                        cancelled = True
                if cancelled:
                    self.push_activity()
            if cancelled:
                self.push_log(f"SYS: Cancelled worker {wid}.")
            return {"ok": cancelled, "workers": self.get_activity_snapshot()}

        if action == "clear_completed_workers":
            removed = 0
            try:
                from core.subagents import get_subagent_manager
                removed += get_subagent_manager().clear_finished()
            except Exception:
                pass
            with self._lock:
                done_keys = [
                    k for k, v in self._tool_tasks.items()
                    if v.get("status") in ("completed", "failed", "cancelled")
                ]
                for k in done_keys:
                    self._tool_tasks.pop(k, None)
                    removed += 1
            self.push_activity()
            return {"ok": True, "removed": removed, "workers": self.get_activity_snapshot()}

        # ── Behavior Interviews, Companions & Visual Skills/Themes Studio ─────

        if action == "studio_get":
            return {"ok": True, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_save_interview":
            answers = data.get("answers")
            iv = companions.save_behavior_interview(answers if isinstance(answers, dict) else {})
            if self._is_persona_chosen() and ui is not None:
                cb = getattr(ui, "on_integrations_change", None)
                if callable(cb):
                    threading.Thread(target=cb, daemon=True).start()
            return {"ok": True, "interview": iv, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_add_rule":
            rule_txt = str(data.get("rule") or "").strip()
            companions.add_learned_rule(rule_txt)
            return {"ok": True, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_delete_rule":
            rid = str(data.get("rule_id") or "").strip()
            companions.delete_learned_rule(rid)
            return {"ok": True, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_save_companion":
            try:
                comp = companions.save_companion(data.get("companion") if isinstance(data.get("companion"), dict) else data)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "companion": comp, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_delete_companion":
            cid = str(data.get("companion_id") or "").strip()
            companions.delete_companion(cid)
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_activate_companion":
            cid = str(data.get("companion_id") or "default").strip()
            comp = companions.set_active_companion(cid)
            self.push_log(f"SYS: Active companion switched to {comp.get('name')} ({comp.get('role')}).")
            if self._is_persona_chosen() and ui is not None:
                cb = getattr(ui, "on_persona_change", None)
                if callable(cb):
                    threading.Thread(target=cb, args=(comp.get("persona", "male"), comp.get("voice", "")), daemon=True).start()
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "active_companion": comp, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_save_skill":
            try:
                res = companions.save_custom_skill(
                    name=str(data.get("name") or ""),
                    description=str(data.get("description") or ""),
                    body=str(data.get("body") or ""),
                )
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, **res, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_delete_skill":
            sname = str(data.get("name") or "").strip()
            ok = companions.delete_custom_skill(sname)
            return {"ok": ok, "studio": companions.get_studio_snapshot(list(TOOL_NODE_MAP.keys()))}

        if action == "studio_save_theme":
            th = companions.save_theme_customization(
                preset=str(data.get("preset") or "default"),
                custom_primary=str(data.get("custom_primary") or ""),
                custom_secondary=str(data.get("custom_secondary") or ""),
            )
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "theme": th}

        # ── Automations Center, Custom REST/Webhooks & MCP Builder ────────────

        def _auto_state() -> dict[str, Any]:
            return {
                "automations": automations.list_automations(),
                "rest_connectors": mcp_adapter.list_rest_connectors(),
                "mcp_servers": mcp_adapter.list_mcp_servers(),
                "available_tools": sorted(set(TOOL_NODE_MAP.keys())),
            }

        if action == "auto_get":
            return {"ok": True, **_auto_state()}

        if action == "auto_save":
            try:
                rec = automations.save_automation(data.get("automation") if isinstance(data.get("automation"), dict) else data)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "automation": rec, **_auto_state()}

        if action == "auto_toggle":
            aid = str(data.get("id") or "").strip()
            enabled = data.get("enabled") if isinstance(data.get("enabled"), bool) else None
            automations.toggle_automation(aid, enabled=enabled)
            return {"ok": True, **_auto_state()}

        if action == "auto_delete":
            aid = str(data.get("id") or "").strip()
            automations.delete_automation(aid)
            return {"ok": True, **_auto_state()}

        if action == "auto_run_now":
            aid = str(data.get("id") or "").strip()
            try:
                run_rec = automations.run_automation_now(aid, on_log=self.push_log)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            self._broadcast_threadsafe(self.snapshot())
            return {"ok": True, "run": run_rec, **_auto_state()}

        if action == "rest_save":
            try:
                rec = mcp_adapter.save_rest_connector(data.get("connector") if isinstance(data.get("connector"), dict) else data)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "connector": rec, **_auto_state()}

        if action == "rest_delete":
            cid = str(data.get("id") or data.get("name") or "").strip()
            mcp_adapter.delete_rest_connector(cid)
            return {"ok": True, **_auto_state()}

        if action == "rest_test":
            cid = str(data.get("id") or data.get("name") or "").strip()
            params = data.get("params") if isinstance(data.get("params"), dict) else {}
            try:
                out = mcp_adapter.invoke_rest_connector(cid, params)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "output": out, **_auto_state()}

        if action == "mcp_save":
            try:
                srv = mcp_adapter.save_mcp_server(data.get("server") if isinstance(data.get("server"), dict) else data)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "server": srv, **_auto_state()}

        if action == "mcp_delete":
            sid = str(data.get("id") or data.get("name") or "").strip()
            mcp_adapter.delete_mcp_server(sid)
            return {"ok": True, **_auto_state()}

        if action == "mcp_discover":
            sid = str(data.get("id") or data.get("name") or "").strip()
            try:
                tools = mcp_adapter.discover_mcp_tools(sid)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "tools": tools, **_auto_state()}

        if action == "mcp_call":
            sid = str(data.get("server") or "").strip()
            tname = str(data.get("tool_name") or "").strip()
            args = data.get("arguments") if isinstance(data.get("arguments"), dict) else {}
            try:
                out = mcp_adapter.call_mcp_tool(sid, tname, args)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "output": out}

        # ── Live Streaming Dev Terminal, Codebase Map & Diffs ─────────────────

        if action == "dev_run":
            cmd = str(data.get("command") or "").strip()
            cwd = str(data.get("cwd") or "").strip()
            try:
                sess = dev_workspace.get_terminal_manager().start_command(cmd, cwd=cwd)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            self.push_tool_trace(["shell_agent", "dev_agent"])
            return {"ok": True, "session": sess, "sessions": dev_workspace.get_terminal_manager().list_sessions()}

        if action == "dev_stdin":
            sid = str(data.get("session_id") or "").strip()
            txt = str(data.get("text") or "")
            ok = dev_workspace.get_terminal_manager().send_stdin(sid, txt)
            return {"ok": ok}

        if action == "dev_stop":
            sid = str(data.get("session_id") or "").strip()
            ok = dev_workspace.get_terminal_manager().stop_command(sid)
            return {"ok": ok, "sessions": dev_workspace.get_terminal_manager().list_sessions()}

        if action == "dev_tree":
            rdir = str(data.get("root_dir") or "").strip()
            return {"ok": True, "tree": dev_workspace.build_codebase_tree(rdir)}

        if action == "dev_read_file":
            rdir = str(data.get("root_dir") or "").strip()
            fpath = str(data.get("path") or "").strip()
            try:
                fobj = dev_workspace.read_workspace_file(rdir, fpath)
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "file": fobj}

        if action == "dev_diffs":
            rdir = str(data.get("root_dir") or "").strip()
            return {"ok": True, "diffs": dev_workspace.get_workspace_diffs(rdir)}

        # ── Encrypted Vault, Hash-Chained Audit Log & Guest Portals ───────────

        def _sec_snap() -> dict[str, Any]:
            return security_vault.get_security_snapshot(
                accounts.ACCOUNTS_FILE, cfg.CONFIG_FILE
            )

        if action == "security_get":
            return {"ok": True, "security": _sec_snap()}

        if action == "vault_rotate_key":
            res = security_vault.rotate_vault_master_key(
                accounts.ACCOUNTS_FILE, cfg.CONFIG_FILE
            )
            return {**res, "security": _sec_snap()}

        if action == "vault_encrypt_config":
            enabled = bool(data.get("enabled", True))
            ok = cfg.set_strict_config_encryption(enabled)
            security_vault.log_audit_event(
                "hud",
                "vault_encrypt_config",
                {"enabled": enabled},
                f"Strict api_keys.json encryption={'ON' if enabled else 'OFF'}",
            )
            return {"ok": ok, "security": _sec_snap()}

        if action == "audit_verify":
            return {"ok": True, "chain": security_vault.verify_audit_chain(), "security": _sec_snap()}

        if action == "audit_search":
            q = str(data.get("query") or "")
            return {"ok": True, "audit_logs": security_vault.list_audit_events(q, limit=80)}

        if action == "portal_create":
            title = str(data.get("title") or "").strip()
            body = str(data.get("content_body") or "").strip()
            oid = data.get("output_id")
            if not body and oid:
                for o in timeline.list_outputs(limit=100):
                    if int(o["id"]) == int(oid):
                        title = title or o["title"]
                        body = o["body"]
                        break
            try:
                created = security_vault.create_portal(
                    title=title or "Shared Deliverable",
                    content_body=body,
                    scope_type=str(data.get("scope_type") or "output"),
                    expires_hours=float(data.get("expires_hours") or 24.0),
                    max_views=int(data.get("max_views") or 50),
                )
            except Exception as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "portal": created, "security": _sec_snap()}

        if action == "portal_revoke":
            pid = str(data.get("portal_id") or "").strip()
            ok = security_vault.revoke_portal(pid)
            return {"ok": ok, "security": _sec_snap()}

        if action == "portal_revoke_all":
            cnt = security_vault.revoke_all_portals()
            return {"ok": True, "revoked_count": cnt, "security": _sec_snap()}

        return {"ok": False, "error": f"Unknown action: {action}"}

    def _invoke_qt(self, fn: Callable[[], Any]) -> None:
        win = getattr(self._ui, "_win", None) if self._ui is not None else None
        if win is not None and hasattr(win, "_bridge_call_sig"):
            try:
                win._bridge_call_sig.emit(fn)
                return
            except Exception:
                pass
        try:
            fn()
        except Exception:
            pass

    # ── Weather helper ────────────────────────────────────────────────────────

    def _fetch_weather(self) -> dict[str, Any]:
        now = time.monotonic()
        if self._wx_cache is not None and (now - self._wx_cached_at) < 900:
            return self._wx_cache

        city = cfg.get_assistant_name()
        result: dict[str, Any] = {"current": None, "city": city}
        try:
            with urllib.request.urlopen("https://ipapi.co/json/", timeout=2.0) as r:
                geo = json.loads(r.read().decode("utf-8", errors="ignore"))
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            city = geo.get("city") or city
            if lat is not None and lon is not None:
                url = (
                    f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
                )
                with urllib.request.urlopen(url, timeout=2.5) as wr:
                    wd = json.loads(wr.read().decode("utf-8", errors="ignore"))
                result = {"current": wd.get("current"), "city": city}
        except Exception:
            pass

        self._wx_cache = result
        self._wx_cached_at = now
        return result

    # ── FastAPI / Uvicorn lifecycle ───────────────────────────────────────────

    def _build_app(self):
        if FastAPI is None:
            raise RuntimeError("fastapi is required for APEX-UI bridge")

        app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

        @app.get("/api/hud/bootstrap")
        async def _bootstrap():
            return JSONResponse(self.snapshot())

        @app.get("/api/hud/brain")
        async def _brain_get():
            snap = await asyncio.to_thread(timeline.get_brain_snapshot)
            return JSONResponse({"ok": True, "brain": snap})

        @app.get("/api/hud/brain/export")
        async def _brain_export():
            exp = await asyncio.to_thread(timeline.export_brain_json)
            return JSONResponse(exp)

        @app.get("/api/hud/activity")
        async def _activity_get():
            return JSONResponse({"ok": True, "workers": self.get_activity_snapshot()})

        @app.get("/api/hud/studio")
        async def _studio_get():
            st = await asyncio.to_thread(
                companions.get_studio_snapshot, list(TOOL_NODE_MAP.keys())
            )
            return JSONResponse({"ok": True, "studio": st})

        @app.get("/api/hud/automations")
        async def _automations_get():
            return JSONResponse(
                {
                    "ok": True,
                    "automations": automations.list_automations(),
                    "rest_connectors": mcp_adapter.list_rest_connectors(),
                    "mcp_servers": mcp_adapter.list_mcp_servers(),
                    "available_tools": sorted(set(TOOL_NODE_MAP.keys())),
                }
            )

        @app.get("/api/hud/dev")
        async def _dev_get(req: Request):
            rdir = req.query_params.get("root_dir", "")
            tree = await asyncio.to_thread(dev_workspace.build_codebase_tree, rdir)
            diffs = await asyncio.to_thread(dev_workspace.get_workspace_diffs, rdir)
            return JSONResponse(
                {
                    "ok": True,
                    "sessions": dev_workspace.get_terminal_manager().list_sessions(),
                    "tree": tree,
                    "diffs": diffs,
                }
            )

        @app.get("/api/hud/security")
        async def _security_get():
            sec = await asyncio.to_thread(
                security_vault.get_security_snapshot,
                accounts.ACCOUNTS_FILE,
                cfg.CONFIG_FILE,
            )
            return JSONResponse({"ok": True, "security": sec})

        @app.get("/portal/{token}")
        async def _guest_portal(token: str, req: Request):
            ip = (req.client.host if req.client else "127.0.0.1") or "127.0.0.1"
            ua = req.headers.get("user-agent", "")
            status_code, html_doc = await asyncio.to_thread(
                security_vault.access_portal_by_token, token, ip, ua
            )
            return HTMLResponse(content=html_doc, status_code=status_code)

        @app.post("/api/hud/action")
        async def _action(req: Request):
            try:
                body = await req.json()
            except Exception:
                body = {}
            res = await asyncio.to_thread(self.handle_action, body)
            return JSONResponse(res)

        @app.get("/api/weather")
        async def _weather():
            wx = await asyncio.to_thread(self._fetch_weather)
            return JSONResponse(wx)

        @app.get("/api/oauth/google/callback")
        async def _google_oauth_cb(req: Request):
            code = req.query_params.get("code", "")
            err = req.query_params.get("error", "")
            if err or not code:
                return HTMLResponse(
                    f"<html><body style='background:#050b14;color:#ff8090;font-family:sans-serif;padding:40px;text-align:center'>"
                    f"<h2>Google Authorization Cancelled</h2><p>{err or 'No authorization code received.'}</p></body></html>",
                    status_code=400,
                )
            rec = accounts.get_account("gmail") or accounts.get_account("google_drive") or {}
            cid = str(rec.get("client_id") or "")
            csec = str(rec.get("client_secret") or "")
            redirect_uri = f"http://127.0.0.1:{self.port}/api/oauth/google/callback"
            try:
                res = await asyncio.to_thread(
                    accounts.exchange_google_oauth_code, code, cid, csec, redirect_uri
                )
                self.push_log(
                    f"SYS: Google Workspace connected ({res.get('email') or 'Gmail, Drive & Calendar'}) ✓"
                )
                self._broadcast_threadsafe(self.snapshot())
                return HTMLResponse(
                    "<html><body style='background:#050b14;color:#6ef4ff;font-family:sans-serif;padding:48px;text-align:center'>"
                    "<h2>✓ Google Workspace Connected</h2>"
                    "<p style='color:#9ec5d6'>Gmail, Google Drive, and Google Calendar are now linked to JARVIS.<br/>You can close this tab and return to the HUD.</p>"
                    "<script>setTimeout(()=>window.close(),1800)</script></body></html>"
                )
            except Exception as exc:
                return HTMLResponse(
                    f"<html><body style='background:#050b14;color:#ff8090;font-family:sans-serif;padding:40px;text-align:center'>"
                    f"<h2>Google OAuth Error</h2><p>{exc}</p></body></html>",
                    status_code=500,
                )

        @app.websocket("/ws/hud")
        async def _ws_hud(ws: WebSocket):
            if self._loop is None:
                self._loop = asyncio.get_running_loop()
            await ws.accept()
            if self._close_timer is not None:
                self._close_timer.cancel()
                self._close_timer = None
            self._had_ws_client = True
            self._clients.add(ws)
            try:
                await ws.send_text(json.dumps(self.snapshot()))
                while True:
                    raw = await ws.receive_text()
                    try:
                        msg = json.loads(raw)
                        if isinstance(msg, dict) and msg.get("action"):
                            await asyncio.to_thread(self.handle_action, msg)
                    except Exception:
                        pass
            except WebSocketDisconnect:
                pass
            except Exception:
                pass
            finally:
                self._clients.discard(ws)
                if (
                    self._auto_close
                    and self._had_ws_client
                    and len(self._clients) == 0
                    and self._on_all_windows_closed is not None
                ):
                    self._schedule_auto_close()

        index_file = STATIC_HUD_DIR / "index.html"

        @app.get("/")
        async def _root():
            if index_file.exists():
                return FileResponse(
                    index_file,
                    media_type="text/html",
                    headers={"Cache-Control": "no-cache"},
                )
            return JSONResponse(
                {"error": "static_hud bundle missing — run npm run build in apex_ui/"},
                status_code=503,
            )

        if STATIC_HUD_DIR.exists():
            app.mount(
                "/",
                StaticFiles(directory=str(STATIC_HUD_DIR), html=True),
                name="static_hud",
            )

        return app

    def _schedule_auto_close(self) -> None:
        if self._close_timer is not None:
            self._close_timer.cancel()

        def _check():
            if len(self._clients) == 0 and self._on_all_windows_closed is not None:
                try:
                    self._on_all_windows_closed()
                except Exception:
                    pass

        self._close_timer = threading.Timer(3.0, _check)
        self._close_timer.daemon = True
        self._close_timer.start()

    def start(self, timeout: float = 5.0) -> str:
        """Start the local HTTP/WS server in a background daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            return self.url

        import uvicorn

        app = self._build_app()

        def _runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            config = uvicorn.Config(
                app,
                host=self.host,
                port=self.port,
                log_level="warning",
                access_log=False,
            )
            server = uvicorn.Server(config)
            self._server = server

            async def _serve():
                task = asyncio.create_task(server.serve())
                while not server.started and not task.done():
                    await asyncio.sleep(0.02)
                self._started.set()
                await task

            try:
                loop.run_until_complete(_serve())
            except Exception as e:
                print(f"[APEX-HUD] Bridge stopped: {e}")
                self._started.set()

        self._thread = threading.Thread(
            target=_runner, daemon=True, name="jarvis-apex-hud"
        )
        self._thread.start()
        self._auto_scheduler.start()
        self._started.wait(timeout=timeout)
        return self.url

    def stop(self) -> None:
        self._auto_scheduler.stop()
        if self._close_timer is not None:
            self._close_timer.cancel()
        if self._server is not None:
            self._server.should_exit = True


# ── Native App-Mode Window Discovery (Windows / macOS / Linux) ────────────────

def _find_chromium_app_binary() -> str | None:
    system = platform.system()
    candidates: list[str] = []

    if system == "Windows":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")
        candidates.extend(
            [
                os.path.join(pf86, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(pf, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(pf86, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(
                    pf, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"
                ),
            ]
        )
        for name in ("msedge", "chrome", "brave"):
            found = shutil.which(name)
            if found:
                candidates.append(found)
    elif system == "Darwin":
        candidates.extend(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            ]
        )
    else:
        for name in (
            "google-chrome",
            "chromium",
            "chromium-browser",
            "microsoft-edge",
            "brave-browser",
        ):
            found = shutil.which(name)
            if found:
                candidates.append(found)

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def launch_app_window(url: str) -> bool:
    """Open `url` in a standalone frameless desktop app window (Edge/Chrome --app),
    falling back to the default system browser if no Chromium shell is present."""
    exe = _find_chromium_app_binary()
    if exe:
        profile_dir = cfg.CONFIG_DIR / "apex_hud_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        args = [
            exe,
            f"--app={url}",
            "--new-window",
            "--window-size=1440,920",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        popen_cls = getattr(subprocess, "_OrigPopen", subprocess.Popen)
        try:
            popen_cls(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception as e:
            print(f"[APEX-HUD] App-window launch failed ({e}), falling back to browser.")

    try:
        return bool(webbrowser.open(url, new=1))
    except Exception:
        return False
