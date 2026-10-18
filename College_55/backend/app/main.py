"""
Enterprise FastAPI Application Entrypoint for Project 55.
AI-Based Accident Detection and Emergency Alert System Using Computer Vision.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.websocket_manager import ws_manager
from backend.app.db.session import init_db
from backend.app.api.endpoints import incidents, streams, analytics, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and models
    print(f"Starting {settings.PROJECT_NAME}...")
    init_db()
    os.makedirs(settings.EVIDENCE_OUTPUT_DIR, exist_ok=True)
    yield
    print("Shutting down Project 55 Enterprise API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.1.0",
    description="Enterprise-grade AI Road Accident Detection & Automated Emergency Dispatch Platform.",
    lifespan=lifespan
)

# CORS configuration for enterprise operator clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents & Dispatch"])
app.include_router(streams.router, prefix="/api/streams", tags=["Cameras & Live Streams"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["System Analytics"])
app.include_router(health.router, prefix="/api/health", tags=["Health & Diagnostics"])

# Static evidence snapshots
os.makedirs(settings.EVIDENCE_OUTPUT_DIR, exist_ok=True)
app.mount("/static/evidence", StaticFiles(directory=settings.EVIDENCE_OUTPUT_DIR), name="evidence")


# Real-time WebSocket Endpoint
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# Mount Frontend Dashboard Assets if built, or serve single-page dashboard
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("static/"):
            return None
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_path)
else:
    # Fallback dashboard template
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
    index_html = os.path.join(FRONTEND_DIR, "index.html")

    @app.api_route("/", methods=["GET", "HEAD"])
    async def serve_root():
        if os.path.exists(index_html):
            return FileResponse(index_html)
        return {"message": "Project 55 Enterprise API is running. Access /docs for Swagger UI."}
