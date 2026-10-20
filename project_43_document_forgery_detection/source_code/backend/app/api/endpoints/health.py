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
        "service": "Project 43 | AI-Based Document Forgery Detection Microservice",
        "port": 5043,
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "database_wal_active": db_exists,
        "models": {
            "dual_domain_forgery_cnn": phase2_exists,
            "forensic_regressor_weights": regressor_exists
        },
        "telemetry_dataset_ready": dataset_exists,
        "architecture": "DualDomainForgeryNet (Spatial ELA + DCT Frequency) + DocumentForensicRiskRegressorNet"
    }
