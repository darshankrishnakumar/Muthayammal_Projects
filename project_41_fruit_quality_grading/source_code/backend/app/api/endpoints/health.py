from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 41 Fruit Quality Grading API",
        "cuda_available": torch.cuda.is_available()
    }
