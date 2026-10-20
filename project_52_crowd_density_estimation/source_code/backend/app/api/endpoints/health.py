from fastapi import APIRouter
import torch
from backend.app.core.config import settings
from backend.app.ml.inference_engine import crowd_engine

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    csr_params = sum(p.numel() for p in crowd_engine.csrnet.parameters())
    risk_params = sum(p.numel() for p in crowd_engine.risk_net.parameters())

    return {
        "status": "HEALTHY",
        "service": "Project 52 AI Crowd Density & Anomaly Analytics API",
        "project_id": settings.PROJECT_ID,
        "port": settings.PORT,
        "database_wal_mode": True,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "models": {
            "csrnet_crowd_model": "CSRNetCrowdDensityNet",
            "csrnet_parameters": csr_params,
            "risk_regressor": "CrowdOpticalFlowRiskRegressorNet",
            "risk_regressor_parameters": risk_params,
            "total_parameters": csr_params + risk_params
        }
    }
