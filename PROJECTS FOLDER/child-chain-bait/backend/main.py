"""
Main FastAPI server for Child Gait Prediction Backend & Data Pipeline.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure package directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import init_db
from api.routes import router

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
    yield


app = FastAPI(
    title="Child Gait Prediction Backend API",
    description="Data pipeline and persistence service for pediatric gait assessments.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for the React/TanStack frontend running at localhost:8080
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Child Gait Prediction Backend API",
        "status": "online",
        "database": "SQLite (gait_records)",
        "disclaimer": MEDICAL_DISCLAIMER,
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "table": "gait_records",
    }


if __name__ == "__main__":
    import uvicorn
    # Default backend port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
