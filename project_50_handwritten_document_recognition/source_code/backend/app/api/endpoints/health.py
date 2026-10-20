from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import torch
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.ml.inference_engine import idp_engine

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check(db: Session = Depends(get_db)):
    wal_mode = False
    try:
        res = db.execute(text("PRAGMA journal_mode;")).fetchone()
        if res and str(res[0]).lower() == "wal":
            wal_mode = True
    except Exception:
        pass

    crnn_params = sum(p.numel() for p in idp_engine.crnn_model.parameters())
    scorer_params = sum(p.numel() for p in idp_engine.scorer_model.parameters())

    return {
        "status": "HEALTHY",
        "service": "Project 50 Handwritten Document IDP API",
        "project_id": settings.PROJECT_ID,
        "port": settings.PORT,
        "database_wal_mode": wal_mode,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "models": {
            "crnn_text_recognizer": "DeepCRNNTextRecognizer",
            "crnn_parameters": crnn_params,
            "quality_scorer": "DocumentQualityAndLexicalScorerNet",
            "quality_scorer_parameters": scorer_params,
            "total_parameters": crnn_params + scorer_params
        }
    }
