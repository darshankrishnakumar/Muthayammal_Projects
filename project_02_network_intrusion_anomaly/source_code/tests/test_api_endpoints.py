import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["models_ready"] is True
    assert data["database_connected"] is True

def test_presets_endpoint(client):
    res = client.get("/api/presets")
    assert res.status_code == 200
    presets = res.json()
    assert "syn_flood_dos" in presets
    assert "normal_http_session" in presets
    assert "zero_day_anomaly" in presets

def test_inspect_packet_benign(client):
    payload = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "duration": 1,
        "src_bytes": 300,
        "dst_bytes": 2500,
        "count": 2,
        "srv_count": 2,
        "serror_rate": 0.0,
        "rerror_rate": 0.0
    }
    res = client.post("/api/inspect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_category"] == "Normal"
    assert data["threat_level"] == "BENIGN"
    assert "event_id" in data
    assert data["source_ip"] == "192.168.1.100"

def test_inspect_packet_attack(client):
    payload = {
        "source_ip": "185.220.101.5",
        "destination_ip": "10.0.0.1",
        "protocol_type": "tcp",
        "service": "private",
        "flag": "S0",
        "duration": 0,
        "src_bytes": 0,
        "dst_bytes": 0,
        "count": 250,
        "srv_count": 25,
        "serror_rate": 1.0,
        "srv_serror_rate": 1.0
    }
    res = client.post("/api/inspect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_category"] == "DoS"
    assert data["threat_level"] == "CRITICAL_ATTACK"
    assert "BLOCK" in data["recommended_action"]

def test_legacy_predict_endpoint(client):
    res = client.post("/predict", json={"features": [1.0, 2.0, 3.0]})
    assert res.status_code == 200
    data = res.json()
    assert "predicted_category" in data
    assert "threat_level" in data

def test_events_endpoint(client):
    res = client.get("/api/events?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert isinstance(data["events"], list)

def test_analytics_endpoint(client):
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_inspected_packets" in data
    assert "malicious_intrusions" in data
    assert "category_distribution" in data

def test_metrics_endpoint(client):
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "random_forest" in data
    assert data["random_forest"]["accuracy"] > 0.95
