from fastapi import APIRouter
import torch
import sqlite3
from backend.app.core.config import settings

router = APIRouter()

@router.api_route("/", methods=["GET", "HEAD"])
def health_check():
    wal_mode = False
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        row = cur.fetchone()
        wal_mode = (row[0].lower() == "wal") if row else False
        conn.close()
    except Exception:
        wal_mode = False

    return {
        "status": "HEALTHY",
        "service": "Project 54 AI Weather Event Nowcasting & Prediction API",
        "project_id": "PROJECT-054",
        "port": 5054,
        "database_wal_mode": wal_mode,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available(),
        "models": {
            "bigru_weather_model": "BiGRUWeatherNowcastingNet",
            "bigru_parameters": 115270,
            "radar_precip_regressor": "RadarPrecipitationAndExtremeWeatherRegressorNet",
            "radar_regressor_parameters": 12615,
            "total_parameters": 127885
        }
    }
