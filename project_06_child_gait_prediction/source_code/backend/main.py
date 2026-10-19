"""
Main FastAPI server for Child Gait Prediction System.
Unifies ML inference, SQLite data persistence, and interactive frontend dashboard.
Runs on Port 5006.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure package directory is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from db.database import init_db
from db.repository import get_gait_records, import_csv_to_database
from api.routes import router

HTML_FILE = os.path.abspath(os.path.join(os.path.dirname(CURRENT_DIR), "public", "index.html"))

MEDICAL_DISCLAIMER = (
    "This application is a college-level machine learning prototype intended for "
    "educational and decision-support purposes. It does not replace professional "
    "medical diagnosis, clinical assessment, or treatment."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and gait_records table on startup
    init_db()
    print("[Backend] SQLite database initialized. Table `gait_records` ready.")
    
    # Auto-seed initial dataset if table is empty
    records = get_gait_records()
    if len(records) == 0:
        csv_path = os.path.join(CURRENT_DIR, "data", "synthetic_child_gait.csv")
        if os.path.exists(csv_path):
            import_csv_to_database(csv_path)
            print(f"[Backend] Auto-seeded initial dataset from {csv_path}")
            
    yield


app = FastAPI(
    title="Child Gait Prediction System",
    description="Full-stack AI system for pediatric abnormal gait detection and longitudinal biomechanical tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def serve_frontend():
    if os.path.exists(HTML_FILE):
        return FileResponse(HTML_FILE, media_type="text/html")
    return HTMLResponse("<h2>Child Gait Prediction Portal Loaded</h2><p>API is active.</p>")


@app.get("/api")
def api_root():
    records = get_gait_records()
    return {
        "service": "Child Gait Prediction System API",
        "status": "online",
        "database": "SQLite (gait_records)",
        "total_records": len(records),
        "disclaimer": MEDICAL_DISCLAIMER,
    }


@app.get("/api/health")
def health_check():
    records = get_gait_records()
    return {
        "status": "healthy",
        "service": "Child Gait Prediction AI",
        "database": "connected",
        "table": "gait_records",
        "total_records": len(records),
        "port": int(os.environ.get("PORT", 5006)),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5006))
    print(f"[Backend] Launching Child Gait Prediction Server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
