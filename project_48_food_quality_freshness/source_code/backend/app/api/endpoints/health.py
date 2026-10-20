from fastapi import APIRouter
import torch
from backend.app.core.config import settings

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 48 Food Quality & Freshness Detection API",
        "project_id": "PROJECT-048",
        "port": settings.PORT,
        "database_wal_mode": True,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False,
        "models": {
            "cnn_model": "SpectralFreshnessCNN",
            "cnn_parameters": 20869,
            "regressor_model": "ShelfLifeForecastRegressorNet",
            "regressor_parameters": 18052
        }
    }
