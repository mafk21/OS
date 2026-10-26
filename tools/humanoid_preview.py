"""Read-only HUD visual preview. Never starts AI, microphone, skills or device actions.

Run: python tools/humanoid_preview.py --port 3000
The production desktop app continues to use core.apex_bridge, not this server.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

ROOT = Path(__file__).resolve().parents[1] / "apex_ui" / "static_hud"
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def bootstrap(persona: str = "male") -> dict:
    return {
        "type": "bootstrap", "ready": True, "integrations_ready": True,
        "persona_chosen": True, "persona": persona,
        "assistant_name": "FRIDAY" if persona == "female" else "JARVIS",
        "raw_state": "VISUAL PREVIEW", "muted": True, "paused": False,
        "offline": False, "logs": ["SYS: Visual preview only — AI, microphone and device actions are not running."],
    }


@app.get("/api/hud/bootstrap")
async def get_bootstrap():
    return bootstrap()


@app.post("/api/hud/action")
async def no_actions():
    return JSONResponse({"ok": False, "error": "Read-only visual preview; run main.py for the live assistant."}, status_code=403)


@app.websocket("/ws/hud")
async def websocket(ws: WebSocket):
    await ws.accept()
    await ws.send_json(bootstrap())
    try:
        while True:
            data = await ws.receive_json()
            # Switching the visual edition is connection-local, never persisted.
            if data.get("action") == "set_persona" and data.get("persona") in ("male", "female"):
                await ws.send_json(bootstrap(data["persona"]))
            else:
                await ws.send_json({"type": "log", "line": "SYS: Visual preview only — this action needs the running desktop assistant."})
    except WebSocketDisconnect:
        pass


app.mount("/_next", StaticFiles(directory=ROOT / "_next"), name="next")
app.mount("/hologram", StaticFiles(directory=ROOT / "hologram"), name="hologram")


@app.get("/")
async def index():
    return FileResponse(ROOT / "index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
