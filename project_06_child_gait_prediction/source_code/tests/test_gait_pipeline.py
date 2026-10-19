"""
Comprehensive Automated Test Suite for Child Gait Prediction System.
Verifies Data Pipeline, ML Inference Engine, SQLite Database CRUD, and FastAPI REST endpoints.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
ML_DIR = os.path.join(BASE_DIR, "ml-service")

if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)
if ML_DIR not in sys.path:
    sys.path.append(ML_DIR)

from db.database import init_db, get_db_connection
from db.repository import (
    insert_gait_record,
    get_gait_records,
    get_gait_record_by_id,
    delete_gait_record,
    import_csv_to_database,
)
from src.predict import GaitPredictor
from main import app

client = TestClient(app)


# =====================================================================
# 1. DATASET INTEGRITY TESTS
# =====================================================================

def test_real_dataset_exists():
    real_csv = os.path.join(ML_DIR, "data", "real_child_gait_features.csv")
    assert os.path.isfile(real_csv), f"Real C3D dataset missing at {real_csv}"
    assert os.path.getsize(real_csv) > 500, "Dataset file should have non-trivial size"


def test_synthetic_dataset_exists():
    synth_csv = os.path.join(BACKEND_DIR, "data", "synthetic_child_gait.csv")
    assert os.path.isfile(synth_csv), f"Synthetic dataset missing at {synth_csv}"


# =====================================================================
# 2. MACHINE LEARNING MODEL ARTIFACT TESTS
# =====================================================================

def test_model_artifacts_exist():
    models_dir = os.path.join(ML_DIR, "models")
    final_model = os.path.join(models_dir, "gait_final_model.joblib")
    preproc = os.path.join(models_dir, "gait_preprocessor.joblib")
    baseline = os.path.join(models_dir, "gait_random_forest_baseline.joblib")

    assert os.path.isfile(final_model), "Final tuned Random Forest model missing"
    assert os.path.isfile(preproc), "Gait preprocessor pipeline missing"
    assert os.path.isfile(baseline), "Baseline Random Forest model missing"


def test_predictor_initialization():
    predictor = GaitPredictor()
    assert predictor.is_ready is True
    assert predictor.model is not None
    assert predictor.scaler is not None
    assert predictor.label_encoder is not None


# =====================================================================
# 3. ML INFERENCE CLASSIFICATION TESTS
# =====================================================================

def test_normal_gait_prediction():
    predictor = GaitPredictor()
    normal_input = {
        "heel_pressure": 195.5,
        "toe_pressure": 180.2,
        "tilt_angle": 2.1,
        "step_duration": 0.48,
        "stride_length": 82.5,
        "walking_speed": 1.25,
    }
    res = predictor.predict(normal_input)
    assert res["prediction"] in ["Normal", "Diplegic", "Hemiplegic"]
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert "probabilities" in res
    assert "Normal" in res["probabilities"]


def test_diplegic_gait_features():
    predictor = GaitPredictor()
    diplegic_input = {
        "heel_pressure": 115.0,
        "toe_pressure": 220.0,
        "tilt_angle": 14.5,
        "step_duration": 0.78,
        "stride_length": 52.0,
        "walking_speed": 0.65,
    }
    res = predictor.predict(diplegic_input)
    assert "prediction" in res
    assert "probabilities" in res
    assert "Diplegic" in res["probabilities"]
    assert res["features_used"]["stride_length"] == 52.0


def test_hemiplegic_gait_features():
    predictor = GaitPredictor()
    hemiplegic_input = {
        "heel_pressure": 105.0,
        "toe_pressure": 195.0,
        "tilt_angle": 9.2,
        "step_duration": 0.64,
        "stride_length": 62.0,
        "walking_speed": 0.88,
    }
    res = predictor.predict(hemiplegic_input)
    assert "prediction" in res
    assert "Hemiplegic" in res["probabilities"]


def test_derived_biomechanical_features():
    predictor = GaitPredictor()
    input_data = {
        "heel_pressure": 150.0,
        "toe_pressure": 140.0,
        "tilt_angle": 5.0,
        "step_duration": 0.50,
        "stride_length": 70.0,
        "walking_speed": 1.10,
    }
    res = predictor.predict(input_data)
    feats = res["features_used"]
    assert "cadence" in feats
    assert "pelvic_tilt" in feats
    assert "step_asymmetry" in feats
    assert feats["cadence"] == pytest.approx(120.0, rel=1e-2)


# =====================================================================
# 4. DATABASE SUBSYSTEM TESTS (SQLITE CRUD)
# =====================================================================

def test_database_initialization():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gait_records';")
    assert cursor.fetchone() is not None
    conn.close()


def test_database_insert_and_retrieve():
    test_id = "gait-test-record-999"
    test_record = {
        "id": test_id,
        "child_id": "C-TEST-99",
        "age": 9,
        "gender": "Male",
        "heel_pressure": 170.0,
        "toe_pressure": 150.0,
        "tilt_angle": 3.0,
        "step_duration": 0.50,
        "stride_length": 80.0,
        "walking_speed": 1.20,
        "gait_class": "Normal",
        "confidence": 0.94,
        "data_source": "test",
    }
    saved = insert_gait_record(test_record)
    assert saved["id"] == test_id

    fetched = get_gait_record_by_id(test_id)
    assert fetched is not None
    assert fetched["child_id"] == "C-TEST-99"
    assert fetched["age"] == 9
    assert fetched["walking_speed"] == 1.20

    # Clean up
    deleted = delete_gait_record(test_id)
    assert deleted is True


def test_database_filter_by_child():
    records = get_gait_records()
    assert isinstance(records, list)


def test_database_import_csv():
    synth_csv = os.path.join(BACKEND_DIR, "data", "synthetic_child_gait.csv")
    res = import_csv_to_database(synth_csv)
    assert res["status"] == "success"
    assert res["imported_count"] > 0


# =====================================================================
# 5. FASTAPI REST SERVICE ENDPOINT TESTS
# =====================================================================

def test_api_root_html_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "Child Gait" in response.text
    assert "<!DOCTYPE html>" in response.text


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["table"] == "gait_records"


def test_api_root_metadata():
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Child Gait Prediction System API"
    assert "disclaimer" in data


def test_api_predict_endpoint_success():
    payload = {
        "child_id": "C-205",
        "age": 7,
        "gender": "Female",
        "heel_pressure": 185.0,
        "toe_pressure": 170.0,
        "tilt_angle": 2.5,
        "step_duration": 0.50,
        "stride_length": 78.0,
        "walking_speed": 1.15,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "assessmentId" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert data["record"]["child_id"] == "C-205"


def test_api_predict_boundary_validation():
    # Negative heel pressure should trigger 422 Unprocessable Entity
    invalid_payload = {
        "child_id": "C-ERR",
        "age": 6,
        "gender": "Male",
        "heel_pressure": -10.0,
        "toe_pressure": 100.0,
        "tilt_angle": 5.0,
        "step_duration": 0.5,
        "stride_length": 70.0,
        "walking_speed": 1.0,
    }
    response = client.post("/api/predict", json=invalid_payload)
    assert response.status_code == 422


def test_api_records_list_and_delete():
    # Create record
    payload = {
        "child_id": "C-TEMP-DEL",
        "age": 10,
        "gender": "Male",
        "heel_pressure": 160.0,
        "toe_pressure": 150.0,
        "tilt_angle": 4.0,
        "step_duration": 0.52,
        "stride_length": 74.0,
        "walking_speed": 1.12,
    }
    create_res = client.post("/api/predict", json=payload)
    assert create_res.status_code == 200
    rec_id = create_res.json()["assessmentId"]

    # List records
    list_res = client.get("/api/records")
    assert list_res.status_code == 200
    assert any(r["id"] == rec_id for r in list_res.json())

    # Delete record
    del_res = client.delete(f"/api/records/{rec_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"


def test_cors_headers_present():
    response = client.options("/api/records", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ["*", "http://localhost:3000"]


def test_medical_disclaimer_present_in_root():
    response = client.get("/api")
    assert response.status_code == 200
    assert "educational and decision-support purposes" in response.json()["disclaimer"]
