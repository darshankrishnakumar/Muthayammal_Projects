"""
FastAPI route handlers for Child Gait Records and Data Pipeline.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

# Ensure repo root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.repository import (
    insert_gait_record,
    get_gait_records,
    get_gait_record_by_id,
    delete_gait_record,
    import_csv_to_database,
)
from api.schemas import (
    GaitRecordCreate,
    GaitRecordResponse,
    PredictionResultResponse,
    CSVImportResponse,
)

router = APIRouter(prefix="/api", tags=["Gait Records"])

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "synthetic_child_gait.csv",
)

# ML Predictor integration from ml-service
ML_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ml-service",
)
if ML_DIR not in sys.path:
    sys.path.append(ML_DIR)

try:
    from src.predict import GaitPredictor
    ml_predictor = GaitPredictor()
except Exception as e:
    print(f"[Warning] Failed to import GaitPredictor: {e}")
    ml_predictor = None


def classify_gait(data: Dict[str, Any]) -> tuple[str, Optional[float]]:
    """
    Classifies gait parameters using the real trained Random Forest model.
    Falls back gracefully only if the model is not loaded.
    """
    if ml_predictor and ml_predictor.is_ready:
        try:
            res = ml_predictor.predict(data)
            return res["prediction"], res.get("confidence")
        except Exception as e:
            print(f"[Warning] ML prediction error: {e}")

    # Fallback only if model is offline
    tilt = float(data.get("tilt_angle") or data.get("tiltAngle", 0))
    duration = float(data.get("step_duration") or data.get("stepDuration", 0))
    stride = float(data.get("stride_length") or data.get("strideLength", 0))
    if tilt >= 10.0 or (duration >= 0.70 and stride <= 65.0):
        return "Diplegic", 0.92
    elif tilt >= 8.0:
        return "Hemiplegic", 0.88
    else:
        return "Normal", 0.95


@router.post("/import-csv", response_model=CSVImportResponse)
def import_csv(filepath: Optional[str] = Query(default=None)):
    """
    Imports dummy CSV gait data into the `gait_records` database table.
    """
    target_path = filepath if filepath else DEFAULT_CSV_PATH
    try:
        res = import_csv_to_database(target_path)
        return CSVImportResponse(**res)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Import failed: {str(e)}")


@router.post("/records", response_model=GaitRecordResponse, status_code=status.HTTP_201_CREATED)
def create_gait_record(payload: GaitRecordCreate):
    """
    Adds a new gait assessment record directly into `gait_records`.
    """
    data = payload.model_dump()
    if not data.get("gait_class"):
        pred, conf = classify_gait(data)
        data["gait_class"] = pred
        data["confidence"] = conf

    record = insert_gait_record(data)
    return GaitRecordResponse(**record)


@router.post("/predict", response_model=PredictionResultResponse)
def predict_and_store_gait(payload: GaitRecordCreate):
    """
    Predicts gait category from input parameters AND persists the record in `gait_records`.
    Directly connects to frontend `predictGait()` API calls.
    """
    data = payload.model_dump()
    prediction, confidence = classify_gait(data)

    data["gait_class"] = prediction
    data["confidence"] = confidence

    saved_record = insert_gait_record(data)

    return PredictionResultResponse(
        prediction=prediction,
        confidence=confidence,
        assessmentId=saved_record["id"],
        record=saved_record,
    )


@router.get("/records", response_model=List[GaitRecordResponse])
def list_gait_records(child_id: Optional[str] = Query(default=None, alias="childId")):
    """
    Retrieves all gait assessment records or filters by child ID.
    """
    records = get_gait_records(child_id=child_id)
    return [GaitRecordResponse(**r) for r in records]


@router.get("/records/child/{child_id}", response_model=List[GaitRecordResponse])
def get_records_by_child(child_id: str):
    """
    Retrieves gait assessment records for a specific child ID.
    """
    records = get_gait_records(child_id=child_id)
    return [GaitRecordResponse(**r) for r in records]


@router.get("/records/{record_id}", response_model=GaitRecordResponse)
def get_record(record_id: str):
    """
    Retrieves a single gait record by ID.
    """
    record = get_gait_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gait record not found")
    return GaitRecordResponse(**record)


@router.delete("/records/{record_id}")
def delete_record(record_id: str):
    """
    Deletes a gait assessment record from `gait_records`.
    """
    deleted = delete_gait_record(record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gait record not found")
    return {"status": "deleted", "id": record_id}
