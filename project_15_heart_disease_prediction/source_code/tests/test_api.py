import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["port"] == 5015
    assert "RandomForestClassifier" in data["model"]["classifier"]
    assert data["model"]["features_count"] == 11
    assert data["database"]["status"] == "connected"

def test_health_alias(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_home_route(client):
    res = client.get("/")
    assert res.status_code == 200

def test_api_predict_low_risk(client):
    payload = {
        "Age": 35,
        "Sex": 0,
        "ChestPainType": 1,
        "RestingBP": 115,
        "Cholesterol": 180,
        "FastingBS": 0,
        "RestingECG": 0,
        "MaxHR": 175,
        "ExerciseAngina": 0,
        "Oldpeak": 0.0,
        "ST_Slope": 0
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"] == 0
    assert "No Heart Disease" in data["result_text"]
    assert data["healthy_probability"] > data["disease_probability"]
    assert "assessment_id" in data

def test_api_predict_high_risk(client):
    payload = {
        "Age": 62,
        "Sex": 1,
        "ChestPainType": 0,
        "RestingBP": 155,
        "Cholesterol": 290,
        "FastingBS": 1,
        "RestingECG": 2,
        "MaxHR": 110,
        "ExerciseAngina": 1,
        "Oldpeak": 3.5,
        "ST_Slope": 2
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"] == 1
    assert "Heart Disease Detected" in data["result_text"]
    assert data["disease_probability"] > 50.0
    assert data["risk_tier"] in ["High", "Elevated"]

def test_api_predict_invalid_data(client):
    payload = {
        "Age": "invalid_age_string",
        "Sex": 1
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_api_download_report_pdf(client):
    payload = {
        "prediction_result": "🚨 Heart Disease Detected!",
        "input_data": [62, 1, 0, 155, 290, 1, 2, 110, 1, 3.5, 2]
    }
    res = client.post("/api/download-report", json=payload)
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert len(res.data) > 1000  # Non-trivial PDF size

def test_api_history(client):
    res = client.get("/api/history?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["records"], list)
    assert len(data["records"]) <= 10

def test_api_stats(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    stats = data["stats"]
    assert stats["status"] == "connected"
    assert stats["total_assessments"] > 0
    assert "disease_percentage" in stats
