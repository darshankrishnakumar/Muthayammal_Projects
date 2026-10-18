import os
import sys
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["lstm_model_loaded"] is True
    assert data["rf_model_loaded"] is True

def test_options_endpoint():
    res = client.get("/api/options")
    assert res.status_code == 200
    data = res.json()
    assert "airlines" in data
    assert "IndiGo" in data["airlines"]
    assert "sources" in data
    assert "destinations" in data

def test_metrics_endpoint():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "LSTM_Neural_Network" in data["models"]
    assert "Random_Forest_Benchmark" in data["models"]

def test_predict_endpoint_valid():
    payload = {
        "airline": "Vistara",
        "source": "Mumbai",
        "destination": "Delhi",
        "journey_date": "2026-11-25",
        "dep_time": "14:00",
        "arrival_time": "16:15",
        "total_stops": 0
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "recommended_fare" in data
    assert "predicted_price_lstm" in data
    assert "predicted_price_rf" in data
    assert "record_id" in data
    assert data["route"] == "Mumbai → Delhi"
    assert data["duration_mins"] == 135

def test_predict_endpoint_validation_error():
    # Negative stops should fail validation
    payload = {
        "airline": "IndiGo",
        "source": "Delhi",
        "destination": "Cochin",
        "journey_date": "2026-11-25",
        "dep_time": "14:00",
        "arrival_time": "16:15",
        "total_stops": -1
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 422 # Unprocessable Entity

def test_history_endpoint():
    res = client.get("/api/history?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0, "History should contain previously recorded prediction"

def test_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_predictions" in data
    assert "airline_statistics" in data
    assert data["total_predictions"] > 0
