import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.websocket_manager import ws_manager
from backend.app.db.session import init_db
from backend.app.api.endpoints import grading, analytics, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.PROJECT_NAME, version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grading.router, prefix="/api/grading", tags=["Fruit Grading"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["System Analytics"])
app.include_router(health.router, prefix="/api/health", tags=["System Health"])

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

FRONTEND_INDEX = os.path.join(os.path.dirname(__file__), "../../frontend/index.html")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    if os.path.exists(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX)
    return {"message": "Project 41 API Active"}
