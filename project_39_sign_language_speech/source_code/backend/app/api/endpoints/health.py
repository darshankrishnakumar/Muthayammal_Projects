from fastapi import APIRouter
import torch

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Project 39 Sign Language Recognition & Speech API",
        "port": 5039,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "device": "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"),
        "models": {
            "gesture_classifier": "BiLSTMSignAttentionNet (700,107 params)",
            "prosody_regressor": "SpeechProsodyAcousticRegressorNet (83 KB)"
        },
        "database": "sign_speech.db (SQLite WAL Mode)"
    }
