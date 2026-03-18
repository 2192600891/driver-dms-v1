import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dms_service import InferenceEngine, SessionStore
import mydetect

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Driver DMS Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = InferenceEngine()
sessions = SessionStore()


class InferRequest(BaseModel):
    image: str
    session_id: Optional[str] = None
    annotated: bool = False


if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="前端页面不存在")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "port": int(os.getenv("PORT", "6006")),
        "runtime_info": mydetect.runtime_info(),
    }


@app.post("/api/infer")
def infer(payload: InferRequest):
    try:
        frame = engine.decode_image(payload.image)
        session = sessions.get(payload.session_id)
        return engine.process_frame(frame, session, include_preview=payload.annotated)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.websocket("/ws/monitor")
async def monitor_socket(websocket: WebSocket):
    await websocket.accept()
    session = sessions.get()
    await websocket.send_json({"type": "ready", "session_id": session.session_id})
    try:
        while True:
            raw_message = await websocket.receive_text()
            payload = json.loads(raw_message)
            if payload.get("type") == "reset":
                session.reset()
                await websocket.send_json({"type": "reset", "session_id": session.session_id})
                continue

            if payload.get("type") != "frame":
                await websocket.send_json({"type": "error", "message": "不支持的消息类型"})
                continue

            frame = engine.decode_image(payload["image"])
            result = engine.process_frame(
                frame,
                session,
                include_preview=bool(payload.get("annotated")),
            )
            result["type"] = "result"
            await websocket.send_json(result)
    except WebSocketDisconnect:
        sessions.drop(session.session_id)
