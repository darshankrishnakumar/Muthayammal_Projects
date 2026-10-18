"""
Senior ML Engineer Automated Test Suite for Car Price Prediction System.

Validates:
1. Model file loading (joblib, pickle, and individual model artifacts).
2. Data preprocessing & leak-free train/test evaluation metrics.
3. Random Forest, Decision Tree, and Linear Regression pipeline inference.
4. FastAPI endpoints (/api/health, /api/info, /api/predict, /api/history, /api/dataset/sample).
5. Input validation and boundary error conditions.
6. SQLite prediction history persistence and CRUD operations.
"""

import json
import os
import pickle
import sqlite3
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

from app.main import app, DB_FILE
from scripts.train_model import preprocess_data, extract_brand

client = TestClient(app)


def test_model_loading_artifacts():
    """1. Verify all saved model files exist and can be loaded successfully."""
    # Test Joblib model
    joblib_path = os.path.join("models", "best_car_price_model.joblib")
    assert os.path.exists(joblib_path), "best_car_price_model.joblib missing"
    model_joblib = joblib.load(joblib_path)
    assert hasattr(model_joblib, "predict"), "Loaded joblib object lacks predict method"
    assert "preprocessor" in model_joblib.named_steps
    assert "regressor" in model_joblib.named_steps

    # Test Pickle model
    pkl_path = os.path.join("models", "best_car_price_model.pkl")
    assert os.path.exists(pkl_path), "best_car_price_model.pkl missing"
    with open(pkl_path, "rb") as f:
        model_pkl = pickle.load(f)
    assert hasattr(model_pkl, "predict"), "Loaded pickle object lacks predict method"

    # Test individual candidate models
    for name in ["random_forest_regression.joblib", "decision_tree_regression.joblib", "linear_regression.joblib"]:
        path = os.path.join("models", name)
        assert os.path.exists(path), f"Candidate model {name} missing"
        cand = joblib.load(path)
        assert hasattr(cand, "predict"), f"{name} lacks predict method"


def test_random_forest_is_trained():
    """2. Verify that Random Forest Regressor is fitted with actual decision trees."""
    joblib_path = os.path.join("models", "best_car_price_model.joblib")
    model = joblib.load(joblib_path)
    rf = model.named_steps["regressor"]
    assert hasattr(rf, "estimators_"), "Random Forest has no estimators_ (not fitted)"
    assert len(rf.estimators_) == 150, f"Expected 150 trees, found {len(rf.estimators_)}"
    assert hasattr(rf, "feature_importances_"), "Random Forest lacks feature_importances_"
    assert len(rf.feature_importances_) > 0, "Empty feature importances"
    assert rf.estimators_[0].tree_.node_count > 10, "Tree appears trivial/unfitted"


def test_evaluation_metrics_and_reproducibility():
    """3. Verify 80:20 split and reproduction of test R2, MAE, and RMSE on held-out data."""
    raw_df = pd.read_csv(os.path.join("data", "car_data.csv"))
    assert len(raw_df) == 450, f"Expected 450 rows in dataset, got {len(raw_df)}"

    clean_df = preprocess_data(raw_df)
    numerical_cols = ["Car_Age", "Present_Price", "Kms_Driven", "Owner"]
    categorical_cols = ["Fuel_Type", "Seller_Type", "Transmission", "Brand"]
    feature_cols = numerical_cols + categorical_cols

    X = clean_df[feature_cols]
    y = clean_df["Selling_Price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    assert len(X_train) == 360, f"Expected 360 train samples, got {len(X_train)}"
    assert len(X_test) == 90, f"Expected 90 test samples, got {len(X_test)}"
    assert len(set(X_train.index).intersection(set(X_test.index))) == 0, "Train and test overlap!"

    # Load saved model and evaluate on test set
    model = joblib.load(os.path.join("models", "best_car_price_model.joblib"))
    y_pred = model.predict(X_test)

    r2 = float(r2_score(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    # Verify metrics meet reported performance thresholds
    assert r2 >= 0.95, f"Expected test R2 >= 0.95, got {r2:.4f}"
    assert 0.5 <= mae <= 1.5, f"MAE out of expected bounds: {mae:.4f}"
    assert 0.8 <= rmse <= 2.2, f"RMSE out of expected bounds: {rmse:.4f}"


def test_health_check_endpoint():
    """4. Verify health endpoint responds with healthy status and models list."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data


def test_model_metadata_endpoint():
    """5. Verify model info returns valid metrics, feature importances, and options."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["best_model"] == "Random Forest Regression"
    assert "metrics" in data
    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0

    # Verify importance weights sum close to 100%
    total_pct = sum(f["importance_pct"] for f in data["feature_importances"])
    assert 95.0 <= total_pct <= 105.0


def test_predict_endpoint_all_algorithms():
    """6. Verify prediction endpoint with all supported algorithms and bounds."""
    for algo in ["Random Forest Regression", "Decision Tree Regression", "Linear Regression", None]:
        payload = {
            "brand": "Toyota",
            "car_model": "Fortuner",
            "year": 2019,
            "present_price": 35.5,
            "kms_driven": 60000.0,
            "fuel_type": "Diesel",
            "seller_type": "Dealer",
            "transmission": "Automatic",
            "owner": 0,
            "algorithm": algo
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200, f"Failed for algo={algo}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["predicted_price_lakhs"] > 0
        assert data["predicted_price_lakhs"] <= payload["present_price"] * 1.05
        assert data["confidence_range"]["lower_lakhs"] <= data["predicted_price_lakhs"]
        assert data["confidence_range"]["upper_lakhs"] >= data["predicted_price_lakhs"]
        assert data["retention_rating"] in ["Excellent", "Good", "Moderate", "High Depreciation"]


def test_predict_input_validation_boundary_conditions():
    """7. Verify Pydantic input validation rejects boundary and invalid inputs."""
    base = {
        "brand": "Honda", "car_model": "City", "year": 2018,
        "present_price": 12.0, "kms_driven": 40000.0, "fuel_type": "Petrol",
        "seller_type": "Dealer", "transmission": "Manual", "owner": 0
    }

    invalid_cases = [
        ("Year too old (< 1990)", {**base, "year": 1980}),
        ("Year in future (> 2025)", {**base, "year": 2030}),
        ("Negative present price", {**base, "present_price": -5.0}),
        ("Zero present price", {**base, "present_price": 0.0}),
        ("Exorbitant present price", {**base, "present_price": 500.0}),
        ("Odometer below 100 km", {**base, "kms_driven": 50.0}),
        ("Odometer above 500,000 km", {**base, "kms_driven": 600000.0}),
        ("Invalid fuel type", {**base, "fuel_type": "Hydrogen"}),
        ("Invalid seller channel", {**base, "seller_type": "Auction"}),
        ("Invalid transmission", {**base, "transmission": "DualClutch"}),
        ("Negative owner count", {**base, "owner": -1}),
        ("Excessive owner count (> 5)", {**base, "owner": 9}),
    ]

    for label, payload in invalid_cases:
        res = client.post("/api/predict", json=payload)
        assert res.status_code == 422, f"Expected 422 for '{label}', got {res.status_code}"


def test_sqlite_database_crud_persistence():
    """8. Verify SQLite prediction history insertion, querying, and deletion."""
    # 1. Clear history
    del_res = client.delete("/api/history")
    assert del_res.status_code == 200

    # 2. Insert via predict
    payload = {
        "brand": "Hyundai",
        "car_model": "Creta",
        "year": 2021,
        "present_price": 15.0,
        "kms_driven": 30000.0,
        "fuel_type": "Diesel",
        "seller_type": "Dealer",
        "transmission": "Automatic",
        "owner": 0
    }
    pred_res = client.post("/api/predict", json=payload)
    assert pred_res.status_code == 200
    created_id = pred_res.json().get("history_id")
    assert created_id is not None

    # 3. Verify in SQLite directly
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, brand, predicted_price_lakhs FROM prediction_history WHERE id = ?", (created_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == created_id
        assert row[1] == "Hyundai"

    # 4. Verify via /api/history endpoint
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    records = hist_res.json()
    assert any(r["id"] == created_id for r in records)

    # 5. Delete specific record
    del_one = client.delete(f"/api/history/{created_id}")
    assert del_one.status_code == 200

    # 6. Verify record is removed
    hist_after = client.get("/api/history").json()
    assert not any(r["id"] == created_id for r in hist_after)


def test_dataset_sample_endpoint():
    """9. Verify dataset sample endpoint returns valid records from car_data.csv."""
    response = client.get("/api/dataset/sample?limit=5")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) == 5
    first = samples[0]
    for key in ["Car_Name", "Year", "Selling_Price", "Present_Price", "Kms_Driven"]:
        assert key in first


if __name__ == "__main__":
    test_suite = [
        ("1. Model Artifact Loading (Joblib, Pickle, Candidates)", test_model_loading_artifacts),
        ("2. Random Forest Regressor Training Verification", test_random_forest_is_trained),
        ("3. 80:20 Train-Test Split & Metric Reproducibility", test_evaluation_metrics_and_reproducibility),
        ("4. FastAPI Health Check Endpoint", test_health_check_endpoint),
        ("5. Model Metadata & Feature Importance", test_model_metadata_endpoint),
        ("6. Multi-Algorithm Inference via /api/predict", test_predict_endpoint_all_algorithms),
        ("7. Pydantic Boundary & Error Input Validation", test_predict_input_validation_boundary_conditions),
        ("8. SQLite Persistence & History CRUD", test_sqlite_database_crud_persistence),
        ("9. Dataset Sample Endpoint Integrity", test_dataset_sample_endpoint),
    ]

    print("==================================================================")
    print(" SENIOR ML ENGINEER AUDIT: EXECUTING AUTOMATED TEST SUITE        ")
    print("==================================================================")
    passed = 0
    failed = 0
    for name, test_func in test_suite:
        try:
            test_func()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")
            failed += 1

    print("==================================================================")
    print(f" RESULTS: {passed} PASSED, {failed} FAILED (TOTAL: {len(test_suite)})")
    print("==================================================================")
    if failed > 0:
        exit(1)
