import os
import sys
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import database as db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["port"] == 5014
    assert "PassiveAggressiveClassifier" in data["model"]["classifier"]
    assert data["database"]["status"] == "connected"

def test_home_route(client):
    res = client.get("/")
    assert res.status_code == 200

def test_predict_get_page(client):
    res = client.get("/predict")
    assert res.status_code == 200

def test_api_predict_fake(client):
    payload = {
        "news": "SHOCKING BOMBSHELL: Banned scientists publish forbidden conspiracy cure that doctors tried to destroy!",
        "pure_language_mode": True
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_fake"] is True
    assert "Fake" in data["verdict_title"]
    assert data["confidence"] > 50.0
    assert "sensational_score" in data

def test_api_predict_real(client):
    payload = {
        "news": "United States Supreme Court justices issued an official written opinion concerning environmental regulation authority",
        "pure_language_mode": False
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_fake"] is False
    assert "Real" in data["verdict_title"]
    assert data["real_pct"] > 50.0

def test_api_predict_missing_text(client):
    res = client.post("/api/predict", json={"news": ""})
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_api_experiments(client):
    res = client.get("/api/experiments")
    assert res.status_code == 200

def test_api_history(client):
    res = client.get("/api/history?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "records" in data
    assert len(data["records"]) <= 10

def test_api_stats(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "stats" in data
    assert data["stats"]["total_verifications"] > 0
