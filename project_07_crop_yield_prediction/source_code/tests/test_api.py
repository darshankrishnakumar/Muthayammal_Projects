"""
Automated Integration and API Tests for CropAI Flask REST API
==============================================================
Tests all REST endpoints, validation rules, farm-size calculations,
crop recommendation engine, and database history.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path

import backend_api
import database


@pytest.fixture
def test_db(tmp_path):
    """Sets up an isolated temporary SQLite database for test execution."""
    db_file = tmp_path / "test_history.db"
    orig_db = database.DEFAULT_DB_PATH
    database.DEFAULT_DB_PATH = db_file
    database.init_db(db_file)
    yield db_file
    database.DEFAULT_DB_PATH = orig_db


@pytest.fixture
def client(test_db):
    """Provides a Flask test client configured with test database."""
    backend_api.app.config["TESTING"] = True
    with backend_api.app.test_client() as client:
        yield client


# ============================================================
# A. EXISTING API ENDPOINTS
# ============================================================
def test_api_stats(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "records" in data
    assert data["records"] == 28242
    assert data["countries"] == 101
    assert data["crops"] == 10
    assert data["yearMin"] == 1990
    assert data["yearMax"] == 2013


def test_api_options(client):
    res = client.get("/api/options")
    assert res.status_code == 200
    data = res.get_json()
    assert "countries" in data
    assert "crops" in data
    assert len(data["countries"]) == 101
    assert len(data["crops"]) == 10
    assert "Albania" in data["countries"]
    assert "Maize" in data["crops"]


def test_api_models_regression(client):
    res = client.get("/api/models/regression")
    assert res.status_code == 200
    models = res.get_json()
    assert isinstance(models, list)
    assert len(models) >= 6
    names = [m["name"] for m in models]
    assert "Random Forest" in names
    assert "Linear Regression" in names
    assert "Decision Tree" in names


def test_api_classification_binary(client):
    res = client.get("/api/classification?type=binary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "binary"
    assert "labels" in data
    assert "models" in data
    assert "threshold" in data
    assert len(data["models"]) >= 4


def test_api_classification_3class(client):
    res = client.get("/api/classification?type=3class")
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "3class"
    assert data["labels"] == ["Low", "Medium", "High"]
    assert "q33" in data
    assert "q67" in data
    assert len(data["models"]) >= 4


# ============================================================
# B. PREDICTION API & INPUT VALIDATION
# ============================================================
def test_predict_valid_scenario(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "model": "Random Forest"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "yield" in data
    assert data["yield"] > 0
    assert data["unit"] == "hg/ha"
    assert "confidence" in data
    assert "id" in data
    assert data["id"] is not None


def test_predict_missing_parameter(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        # missing rain, pest, temp
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert "Missing required parameter" in data["error"]


def test_predict_negative_rainfall(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": -50.0,
        "pest": 100.0,
        "temp": 20.0,
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "cannot be negative" in data["error"]


def test_predict_negative_pesticides(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 800.0,
        "pest": -10.0,
        "temp": 20.0,
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "cannot be negative" in data["error"]


def test_predict_out_of_bounds_temperature(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 800.0,
        "pest": 100.0,
        "temp": 100.0,  # 100°C is outside realistic agronomic bounds
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "realistic agricultural limits" in data["error"]


def test_predict_unsupported_country(client):
    payload = {
        "country": "Atlantis",
        "crop": "Maize",
        "year": 2010,
        "rain": 800.0,
        "pest": 100.0,
        "temp": 20.0,
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "Unsupported country" in data["error"]


def test_predict_unsupported_crop(client):
    payload = {
        "country": "Albania",
        "crop": "Dragonfruit",
        "year": 2010,
        "rain": 800.0,
        "pest": 100.0,
        "temp": 20.0,
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "Unsupported crop" in data["error"]


def test_predict_invalid_year_range(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 1820,
        "rain": 800.0,
        "pest": 100.0,
        "temp": 20.0,
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "between 1900 and 2100" in data["error"]


# ============================================================
# C. CLASSIFICATION API
# ============================================================
def test_classify_binary_valid(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "type": "binary"
    }
    res = client.post("/api/classify", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "binary"
    assert data["class"] in [0, 1]
    assert data["label"] in ["Above Average", "Below Average"]
    assert "threshold" in data
    assert "id" in data


def test_classify_3class_valid(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "type": "3class"
    }
    res = client.post("/api/classify", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "3class"
    assert data["class"] in [0, 1, 2]
    assert data["label"] in ["Low", "Medium", "High"]
    assert "q33" in data
    assert "q67" in data


def test_classify_invalid_classifier(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "model": "NonExistentClassifier"
    }
    res = client.post("/api/classify", json=payload)
    assert res.status_code == 400


# ============================================================
# D. FARM-SIZE AND TOTAL HARVEST CALCULATOR
# ============================================================
def test_predict_with_hectares(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "farm_area": 10.0,
        "farm_area_unit": "ha"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["farm_area"] == 10.0
    assert data["farm_area_unit"] == "ha"
    assert data["farm_area_ha"] == 10.0
    expected_yield_t_ha = data["yield"] / 10000000.0
    expected_harvest = round(expected_yield_t_ha * 10.0, 4)
    assert abs(data["total_harvest_tonnes"] - expected_harvest) < 0.001
    assert data["harvest_calculation_note"] is not None


def test_predict_with_acres_conversion(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "farm_area": 24.7105,
        "farm_area_unit": "acres"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    # 24.7105 acres / 2.47105 = 10.0 hectares
    assert abs(data["farm_area_ha"] - 10.0) < 0.01
    expected_yield_t_ha = data["yield"] / 10000000.0
    expected_harvest = round(expected_yield_t_ha * 10.0, 4)
    assert abs(data["total_harvest_tonnes"] - expected_harvest) < 0.01


def test_predict_zero_or_negative_farm_size(client):
    payload = {
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "farm_area": -5.0,
        "farm_area_unit": "ha"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "must be greater than 0" in data["error"]


# ============================================================
# E. CROP RECOMMENDATION ENGINE
# ============================================================
def test_recommend_crops_valid(client):
    payload = {
        "country": "Albania",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "farm_area": 5.0,
        "farm_area_unit": "ha"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 3
    assert "all_ranked" in data
    assert len(data["all_ranked"]) == 10

    # Ensure ranking order is descending by predicted yield
    yields = [item["predicted_yield"] for item in data["all_ranked"]]
    assert yields == sorted(yields, reverse=True)
    assert data["recommendations"][0]["rank"] == 1
    assert data["recommendations"][0]["predicted_yield"] >= data["recommendations"][1]["predicted_yield"]
    assert "disclaimer" in data


def test_recommend_missing_parameters(client):
    payload = {"country": "Albania"}
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 400


# ============================================================
# F. DATABASE & PERSISTENT HISTORY
# ============================================================
def test_history_persistence_and_retrieval(client):
    # Perform prediction
    pred_res = client.post("/api/predict", json={
        "country": "Albania",
        "crop": "Maize",
        "year": 2010,
        "rain": 1485.0,
        "pest": 121.0,
        "temp": 16.4,
        "farm_area": 2.0,
        "farm_area_unit": "ha"
    })
    assert pred_res.status_code == 200
    pred_id = pred_res.get_json()["id"]
    assert pred_id is not None

    # Retrieve history
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.get_json()
    assert "records" in hist_data
    assert len(hist_data["records"]) >= 1
    record = hist_data["records"][0]
    assert record["id"] == pred_id
    assert record["country"] == "Albania"
    assert record["crop"] == "Maize"
    assert record["farm_area"] == 2.0

    # Retrieve specific record
    item_res = client.get(f"/api/history/{pred_id}")
    assert item_res.status_code == 200
    assert item_res.get_json()["id"] == pred_id

    # Export CSV
    csv_res = client.get("/api/history/export")
    assert csv_res.status_code == 200
    assert csv_res.mimetype == "text/csv"
    assert "Albania" in csv_res.get_data(as_text=True)

    # Delete single record
    del_res = client.delete(f"/api/history/{pred_id}")
    assert del_res.status_code == 200
    assert client.get(f"/api/history/{pred_id}").status_code == 404

    # Clear history
    client.post("/api/predict", json={
        "country": "Albania", "crop": "Potatoes", "year": 2011,
        "rain": 1000.0, "pest": 50.0, "temp": 15.0
    })
    assert len(client.get("/api/history").get_json()["records"]) >= 1
    clear_res = client.delete("/api/history")
    assert clear_res.status_code == 200
    assert len(client.get("/api/history").get_json()["records"]) == 0
