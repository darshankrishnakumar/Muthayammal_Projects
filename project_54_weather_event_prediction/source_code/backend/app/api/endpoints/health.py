from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 54 AI Weather Event Nowcasting API",
        "cuda_available": torch.cuda.is_available()
    }
