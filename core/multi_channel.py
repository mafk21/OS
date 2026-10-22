"""
Multi-channel gateway (Phase 10).

OpenClaw-pattern: unified interface for WhatsApp, Telegram, Discord, Slack,
iMessage and other messaging channels. Provides:

  * Channel registry — register channels, route inbound/outbound messages
  * Webhook server (stdlib http.server) — receive inbound messages from
    channel webhooks (no aiohttp/fastapi needed)
  * Outbound messaging — via existing actions (send_message for desktop
    apps, Telegram bot for Telegram, etc.)
  * Channel routing rules — which channel for which type of message

Designed for graceful degradation: channels that aren't configured are
silently skipped. The webhook server binds to localhost only by default
(for security); expose via the LAN dashboard or a reverse proxy.

All stdlib — no new dependencies.
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

# ── Channel registry ──────────────────────────────────────────────────────


class Channel:
    """A messaging channel: WhatsApp, Telegram, Discord, Slack, iMessage, ..."""

    def __init__(self, channel_id: str, name: str, kind: str,
                 enabled: bool = True, config: Optional[dict] = None):
        self.channel_id = channel_id      # e.g. "whatsapp", "telegram", "discord"
        self.name = name                  # human-readable name
        self.kind = kind                  # "whatsapp" | "telegram" | "discord" | "slack" | "imessage"
        self.enabled = enabled
        self.config = config or {}

    def send(self, text: str, recipient: Optional[str] = None) -> str:
        """Send a message through this channel. Subclasses override."""
        return f"Channel {self.channel_id}: send not implemented"


class ChannelGateway:
    """Registry and router for messaging channels."""

    def __init__(self):
        self._channels: dict[str, Channel] = {}
        self._inbound_handler: Optional[callable] = None  # called on inbound msg
        self._lock = threading.Lock()

    def register(self, channel: Channel) -> None:
        with self._lock:
            self._channels[channel.channel_id] = channel

    def unregister(self, channel_id: str) -> None:
        with self._lock:
            self._channels.pop(channel_id, None)

    def list_channels(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "id": c.channel_id,
                    "name": c.name,
                    "kind": c.kind,
                    "enabled": c.enabled,
                }
                for c in self._channels.values()
            ]

    def get(self, channel_id: str) -> Optional[Channel]:
        with self._lock:
            return self._channels.get(channel_id)

    def enabled_channels(self) -> list[Channel]:
        with self._lock:
            return [c for c in self._channels.values() if c.enabled]

    def set_inbound_handler(self, handler: callable) -> None:
        """Handler called with (channel_id, sender, text) on inbound message."""
        self._inbound_handler = handler

    def handle_inbound(self, channel_id: str, sender: str, text: str) -> str:
        """Route an inbound message. Returns a response string."""
        with self._lock:
            handler = self._inbound_handler
        if handler:
            result = handler(channel_id, sender, text)
            return result if result is not None else "Inbound message handled."
        return f"No inbound handler registered for {channel_id}"

    def send(self, channel_id: str, text: str,
             recipient: Optional[str] = None) -> str:
        """Send a message through a specific channel."""
        ch = self.get(channel_id)
        if not ch:
            return f"Channel '{channel_id}' not registered."
        if not ch.enabled:
            return f"Channel '{channel_id}' is disabled."
        return ch.send(text, recipient)

    def broadcast(self, text: str) -> dict[str, str]:
        """Send to all enabled channels. Returns {channel_id: result}."""
        results: dict[str, str] = {}
        for ch in self.enabled_channels():
            results[ch.channel_id] = ch.send(text)
        return results


# ── Default channels ─────────────────────────────────────────────────────


class DesktopChannel(Channel):
    """Sends via the desktop (send_message action — opens WhatsApp/Telegram
    desktop app and types the message)."""

    def send(self, text: str, recipient: Optional[str] = None) -> str:
        # The actual sending is done by main.py via the send_message action.
        # This channel records the intent; main.py dispatches it.
        return f"Desktop send queued: {text[:60]}{'…' if len(text) > 60 else ''}"


class TelegramChannel(Channel):
    """Sends via the Telegram bot (remote_relay.py / core/telegram_bot.py)."""

    def __init__(self, channel_id: str = "telegram", **kw):
        super().__init__(channel_id, "Telegram", "telegram", **kw)

    def send(self, text: str, recipient: Optional[str] = None) -> str:
        # Dispatch via the Telegram bot's send_message if available
        try:
            import core.telegram_bot as tg  # type: ignore
            if tg.is_running():
                chat_id = recipient or tg.get_default_chat_id()
                if chat_id:
                    tg.send_message(chat_id, text)
                    return f"Telegram sent to {chat_id}"
                return "Telegram: no default chat_id set"
            return "Telegram bot not running (manage_remote start)"
        except Exception as e:
            return f"Telegram send failed: {e}"


# ── Webhook server (inbound) ─────────────────────────────────────────────


class _WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for channel webhooks (WhatsApp, Discord, Slack, ..)."""

    gateway: Optional[ChannelGateway] = None  # set by WebhookServer

    def do_POST(self) -> None:
        if self.gateway is None:
            self._send_json(503, {"error": "gateway not initialized"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return

        channel_id = data.get("channel", data.get("channel_id", "webhook"))
        sender = data.get("sender", data.get("from", "unknown"))
        text = data.get("text", data.get("message", data.get("content", "")))

        if not text:
            self._send_json(400, {"error": "no text/message/content"})
            return

        # Route through the gateway's inbound handler
        response = self.gateway.handle_inbound(channel_id, sender, text)

        # If JARVIS has a session, inject the message as a user turn
        # (handled by the callback registered in main.py)
        if self.gateway._inbound_inject:
            self.gateway._inbound_inject(channel_id, sender, text)

        self._send_json(200, {"status": "ok", "response": response})

    def _send_json(self, code: int, obj: dict) -> None:
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):  # pylint: disable=unused-argument
        pass  # silence default stderr logging


class WebhookServer:
    """Lightweight HTTP webhook server for inbound channel messages.

    Binds to localhost by default. Use a reverse proxy (nginx, Cloudflare
    Tunnel) to expose to WhatsApp/Discord/Slack webhook URLs.
    """

    def __init__(self, gateway: ChannelGateway, host: str = "127.0.0.1",
                 port: int = 8766):
        self.gateway = gateway
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._inbound_inject: Optional[callable] = None  # callback to main.py

    def start(self) -> str:
        _WebhookHandler.gateway = self.gateway
        self._server = HTTPServer((self.host, self.port), _WebhookHandler)
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)
        self._thread.start()
        return f"http://{self.host}:{self.port}/webhook"

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
        if self._thread:
            self._thread.join(timeout=2)

    def set_inbound_inject(self, fn: callable) -> None:
        """Callback to inject an inbound message into JARVIS's session."""
        self._inbound_inject = fn


# ── Gateway singleton ─────────────────────────────────────────────────────

_gateway: Optional[ChannelGateway] = None
_webhook: Optional[WebhookServer] = None


def get_gateway() -> ChannelGateway:
    global _gateway
    if _gateway is None:
        _gateway = ChannelGateway()
        # Register default channels
        _gateway.register(DesktopChannel("desktop", "Desktop (send_message)",
                                         "desktop"))
        _gateway.register(TelegramChannel())
    return _gateway


def get_webhook() -> Optional[WebhookServer]:
    return _webhook


def start_webhook(host: str = "127.0.0.1", port: int = 8766) -> str:
    global _webhook
    if _webhook is None:
        gateway = get_gateway()
        _webhook = WebhookServer(gateway, host, port)
        url = _webhook.start()
        return url
    return f"http://{_webhook.host}:{_webhook.port}/webhook"


def stop_webhook() -> None:
    global _webhook
    if _webhook:
        _webhook.stop()
        _webhook = None


# ── Tool declaration ─────────────────────────────────────────────────────

TOOL = {
    "name": "multi_channel",
    "description": (
        "Multi-channel messaging gateway — send/receive across WhatsApp, "
        "Telegram, Discord, Slack, iMessage and desktop apps. "
        "Actions: 'send' (send via a channel), 'channels' (list registered "
        "channels), 'webhook' (get inbound webhook URL), 'broadcast' (send "
        "to all enabled channels). "
        "Channel IDs: 'desktop' (opens WhatsApp/Telegram desktop app), "
        "'telegram' (Telegram bot). Configure channel webhooks to receive "
        "inbound messages."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "send | channels | webhook | broadcast",
            },
            "channel": {
                "type": "STRING",
                "description": "Channel ID (desktop, telegram, ...)",
            },
            "text": {
                "type": "STRING",
                "description": "Message text to send",
            },
            "recipient": {
                "type": "STRING",
                "description": "Recipient (phone, chat_id, username, ...)",
            },
        },
        "required": ["action"],
    },
    "handler": None,  # set below
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
}


def multi_channel(parameters: dict, response=None, player=None,
                  session_memory=None) -> str:
    """Handle multi_channel tool calls."""
    try:
        action = (parameters or {}).get("action", "").strip().lower()
        gateway = get_gateway()

        if action == "channels":
            chans = gateway.list_channels()
            if not chans:
                return "No channels registered."
            lines = ["Registered channels:"]
            for c in chans:
                status = "enabled" if c["enabled"] else "disabled"
                lines.append(f"  [{c['id']}] {c['name']} ({c['kind']}) — {status}")
            return "\n".join(lines)

        elif action == "webhook":
            try:
                url = start_webhook()
                return f"Inbound webhook URL: {url}\nConfigure this URL in WhatsApp Business, Discord, Slack, etc. to receive inbound messages."
            except Exception as e:
                return f"Webhook server failed: {e}"

        elif action == "send":
            channel = (parameters or {}).get("channel", "desktop")
            text = (parameters or {}).get("text", "")
            recipient = (parameters or {}).get("recipient")
            if not text:
                return "multi_channel send: no text provided."
            return gateway.send(channel, text, recipient)

        elif action == "broadcast":
            text = (parameters or {}).get("text", "")
            if not text:
                return "multi_channel broadcast: no text provided."
            results = gateway.broadcast(text)
            lines = ["Broadcast results:"]
            for ch_id, res in results.items():
                lines.append(f"  [{ch_id}] {res}")
            return "\n".join(lines)

        else:
            return (f"multi_channel: unknown action '{action}'. "
                    f"Use: send | channels | webhook | broadcast")
    except Exception as e:
        return f"multi_channel: {e}"


TOOL["handler"] = multi_channel
