import os
import sys
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json() if hasattr(res, "get_json") else res.json()
    assert data["status"] == "healthy"
    assert data["port"] == 5013
    assert data["database"]["status"] == "connected"

def test_districts_endpoint(client):
    res = client.get("/api/districts")
    assert res.status_code == 200
    data = res.json()
    assert "districts" in data
    assert len(data["districts"]) >= 8

def test_metrics_endpoint(client):
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "project_id" in data
    assert data["project_id"] == "PROJECT-013"

def test_stats_endpoint(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_incidents" in data
    assert data["total_incidents"] > 0
    assert "risk_distribution" in data

def test_history_endpoint(client):
    res = client.get("/api/history?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
    assert len(data["records"]) <= 10

def test_dispatches_endpoint(client):
    res = client.get("/api/dispatches?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "dispatches" in data
    assert len(data["dispatches"]) <= 5

def test_predict_risk_critical(client):
    payload = {
        "hour": 23,
        "day_of_week": 5,
        "month": 10,
        "is_weekend": 1,
        "district": "Central Downtown",
        "location_type": "Nightclub / Bar",
        "historical_density": 9.2,
        "ambient_light": 1,
        "patrol_score": 1,
        "latitude": 41.8825,
        "longitude": -87.6285
    }
    res = client.post("/api/predict_risk", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "predicted_risk" in data
    assert "predicted_crime_type" in data
    assert "risk_probabilities" in data
    assert data["patrol_dispatched"] is True

def test_predict_risk_low(client):
    payload = {
        "hour": 10,
        "day_of_week": 1,
        "month": 4,
        "is_weekend": 0,
        "district": "Tech Corridor",
        "location_type": "Commercial Store / Mall",
        "historical_density": 1.5,
        "ambient_light": 5,
        "patrol_score": 4,
        "latitude": 41.925,
        "longitude": -87.682
    }
    res = client.post("/api/predict_risk", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

def test_predict_risk_validation_error(client):
    # Invalid hour > 23
    res = client.post("/api/predict_risk", json={"hour": 99})
    assert res.status_code == 422

def test_forecast_hourly(client):
    payload = {
        "district": "Central Downtown",
        "day_of_week": 5,
        "month": 10,
        "location_type": "Nightclub / Bar"
    }
    res = client.post("/api/forecast_hourly", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["hourly_forecast"]) == 24
    assert "peak_hour" in data

def test_dispatch_unit(client):
    payload = {
        "unit_callsign": "BRAVO-99",
        "assigned_district": "Central Downtown",
        "priority_level": "URGENT - CODE 3",
        "incident_type": "ROBBERY",
        "eta_minutes": 3
    }
    res = client.post("/api/dispatch_unit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "DISPATCHED"
