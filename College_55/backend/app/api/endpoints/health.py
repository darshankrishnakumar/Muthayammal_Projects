"""
System Health and Diagnostics API Endpoint.
"""

import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.db.session import get_db
from backend.app.core.config import settings

router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"])
def health_check(db: Session = Depends(get_db)):
    # Check DB
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    device_name = "Apple Silicon MPS" if torch.backends.mps.is_available() else ("NVIDIA CUDA" if torch.cuda.is_available() else "CPU")

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "environment": settings.ENVIRONMENT,
        "database_connected": db_ok,
        "inference_hardware": {
            "device": device_name,
            "mps_available": torch.backends.mps.is_available(),
            "cuda_available": torch.cuda.is_available(),
            "torch_version": torch.__version__
        },
        "models_loaded": {
            "phase2_model": settings.MODEL_WEIGHTS_PATH,
            "baseline_model": settings.BASELINE_WEIGHTS_PATH
        },
        "version": "2.1.0-enterprise"
    }
