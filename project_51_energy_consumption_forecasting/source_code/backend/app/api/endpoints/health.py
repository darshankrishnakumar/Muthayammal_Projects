from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import torch
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.ml.inference_engine import energy_engine

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

    lstm_params = sum(p.numel() for p in energy_engine.lstm_model.parameters())
    reg_params = sum(p.numel() for p in energy_engine.reg_model.parameters())

    return {
        "status": "HEALTHY",
        "service": "Project 51 Smart Energy Forecasting & Peak Shaving API",
        "project_id": settings.PROJECT_ID,
        "port": settings.PORT,
        "database_wal_mode": wal_mode,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "models": {
            "multi_horizon_lstm": "MultiHorizonEnergyLSTM",
            "lstm_parameters": lstm_params,
            "grid_regressor": "GridPeakAndCarbonEmissionRegressorNet",
            "grid_regressor_parameters": reg_params,
            "total_parameters": lstm_params + reg_params
        }
    }
