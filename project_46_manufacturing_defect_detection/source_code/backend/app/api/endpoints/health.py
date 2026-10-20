from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("", methods=["GET", "HEAD"])
@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    return {
        "status": "HEALTHY",
        "service": "Project 46 Product Defect Detection API",
        "port": 5046,
        "database": "SQLite (WAL Mode Enabled)",
        "hardware_device": device,
        "models": {
            "fpn_defect_segmenter": "DeepFPNDefectNet (Loaded)",
            "defect_risk_regressor": "ManufacturingDefectRiskRegressorNet (Loaded)"
        }
    }
