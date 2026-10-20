from fastapi import APIRouter
import torch
from backend.app.core.config import settings

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 49 Healthcare Risk Assessment API",
        "project_id": "PROJECT-049",
        "port": settings.PORT,
        "database_wal_mode": True,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False,
        "models": {
            "risk_model": "LongitudinalHealthRiskNet",
            "risk_parameters": 3044,
            "comorbidity_model": "ClinicalComorbidityForecastNet",
            "comorbidity_parameters": 18308
        }
    }
