from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("", methods=["GET", "HEAD"])
@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    return {
        "status": "HEALTHY",
        "service": "Project 47 Classroom Engagement Analytics API",
        "port": 5047,
        "database": "SQLite (WAL Mode Enabled)",
        "hardware_device": device,
        "models": {
            "multimodal_engagement_net": "MultimodalEngagementNet (Loaded)",
            "attention_forecast_regressor": "AttentionForecastRegressorNet (Loaded)"
        }
    }
