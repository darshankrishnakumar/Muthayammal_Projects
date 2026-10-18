from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 52 AI Crowd Density & Anomaly Analytics API",
        "cuda_available": torch.cuda.is_available()
    }
