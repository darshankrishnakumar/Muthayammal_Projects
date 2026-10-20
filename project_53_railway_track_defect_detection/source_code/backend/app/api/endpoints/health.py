from fastapi import APIRouter
import torch
from backend.app.core.config import settings
from backend.app.ml.inference_engine import rail_engine

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    res_params = sum(p.numel() for p in rail_engine.resunet.parameters())
    geo_params = sum(p.numel() for p in rail_engine.geo_net.parameters())

    return {
        "status": "HEALTHY",
        "service": "Project 53 Intelligent Railway Track Defect Detection API",
        "project_id": settings.PROJECT_ID,
        "port": settings.PORT,
        "database_wal_mode": True,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "models": {
            "resunet_segmenter": "ResUNetRailDefectSegmenter",
            "resunet_parameters": res_params,
            "geometry_regressor": "RailTrackGeometryAndDegradationRegressorNet",
            "geometry_regressor_parameters": geo_params,
            "total_parameters": res_params + geo_params
        }
    }
