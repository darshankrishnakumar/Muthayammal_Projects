from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 40 Industrial Fire & Smoke Vision Surveillance API",
        "port": 5040,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "device": "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"),
        "models": {
            "dual_stream_convnet": "DualStreamFireSmokeNet (Phase 2 SOTA, 672 KB)",
            "thermal_risk_regressor": "FirePropagationThermalRiskRegressorNet (83 KB)"
        },
        "database": "fire_smoke.db (SQLite WAL Mode)"
    }
