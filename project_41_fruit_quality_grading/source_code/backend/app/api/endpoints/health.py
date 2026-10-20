from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    mps_avail = torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False
    cuda_avail = torch.cuda.is_available()
    device = "cuda" if cuda_avail else ("mps" if mps_avail else "cpu")
    return {
        "status": "HEALTHY",
        "service": "Project 41 Fruit Quality Grading & Defect Platform API",
        "port": 5041,
        "cuda_available": cuda_avail,
        "mps_available": mps_avail,
        "device": device,
        "models": {
            "multitask_cnn": "MultiTaskFruitNet (Phase 2 SOTA, 391 KB)",
            "freshness_regressor": "FruitFreshnessShelfLifeRegressorNet (83 KB)"
        },
        "database": "fruit_grading.db (SQLite WAL Mode)"
    }
