from fastapi import APIRouter
import torch
import os
from backend.app.core.config import settings

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    mps_available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    cuda_available = torch.cuda.is_available()
    device_name = "mps" if mps_available else ("cuda" if cuda_available else "cpu")
    db_exists = os.path.exists(settings.DATABASE_URL.replace("sqlite:///", ""))

    return {
        "status": "HEALTHY",
        "service": "Project 45 | AI-Powered Skill-Gap Analysis & Career Recommendation Platform",
        "port": 5045,
        "database": {
            "mode": "SQLite WAL",
            "connected": db_exists,
            "url": settings.DATABASE_URL
        },
        "hardware": {
            "device": device_name,
            "cuda_available": cuda_available,
            "mps_available": mps_available
        },
        "models": {
            "competency_embedding_net": "CompetencyEmbeddingNet (64-D Latent Competency Vector Space)",
            "trajectory_forecast_net": "CareerTrajectoryForecastNet (10-in, 4-head Multi-Target Neural Regressor)"
        }
    }
