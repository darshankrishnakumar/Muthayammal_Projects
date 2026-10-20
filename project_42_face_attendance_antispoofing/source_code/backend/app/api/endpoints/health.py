from fastapi import APIRouter
import torch
import os
from backend.app.core.config import settings

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    db_exists = os.path.exists(settings.DATABASE_URL.replace("sqlite:///", ""))
    phase2_exists = os.path.exists(settings.MODEL_WEIGHTS_PATH)
    regressor_exists = os.path.exists(settings.REGRESSOR_WEIGHTS_PATH)
    dataset_exists = os.path.exists(settings.DATASET_PATH)

    return {
        "status": "HEALTHY",
        "service": "Project 42 | AI-Driven Face Attendance & Anti-Spoofing Microservice",
        "port": 5042,
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "database_wal_active": db_exists,
        "models": {
            "arcface_antispoof_weights": phase2_exists,
            "biometric_regressor_weights": regressor_exists
        },
        "telemetry_dataset_ready": dataset_exists,
        "architecture": "DeepAntiSpoofFaceNet + BiometricLivenessQualityRegressorNet"
    }
