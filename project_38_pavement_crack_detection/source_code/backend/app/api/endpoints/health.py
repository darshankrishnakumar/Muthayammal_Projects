from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 38 Pavement Crack Analysis API",
        "port": 5038,
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "benchmark": "ASTM D6433 Pavement Condition Index (PCI)",
        "framework": "PyTorch 2.x ResUNet & Dual-Head PCI Regressor"
    }
