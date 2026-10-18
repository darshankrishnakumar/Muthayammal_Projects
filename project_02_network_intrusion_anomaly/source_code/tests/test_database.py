import os
import pytest
import tempfile
from database.database import NIDSDatabase

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name
    db = NIDSDatabase(db_path=temp_path)
    yield db
    if os.path.exists(temp_path):
        os.remove(temp_path)

def test_database_init(temp_db):
    assert os.path.exists(temp_db.db_path)
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='security_events'")
        table = cursor.fetchone()
        assert table is not None

def test_log_and_fetch_event(temp_db):
    event = {
        "source_ip": "10.0.0.99",
        "destination_ip": "10.0.0.1",
        "protocol": "tcp",
        "service": "http",
        "flag": "SF",
        "src_bytes": 450,
        "dst_bytes": 3200,
        "predicted_category": "Normal",
        "confidence": 0.985,
        "threat_level": "BENIGN",
        "anomaly_score_pct": 12.5,
        "is_anomaly": False,
        "recommended_action": "ALLOW",
        "latency_ms": 42.1
    }
    event_id = temp_db.log_event(event)
    assert event_id > 0

    recent = temp_db.get_recent_events(limit=5)
    assert len(recent) == 1
    row = recent[0]
    assert row["source_ip"] == "10.0.0.99"
    assert row["predicted_category"] == "Normal"
    assert row["threat_level"] == "BENIGN"

def test_threat_analytics(temp_db):
    # Log 1 Normal, 1 DoS, 1 Probe
    temp_db.log_event({"predicted_category": "Normal", "threat_level": "BENIGN", "is_anomaly": False, "latency_ms": 30.0})
    temp_db.log_event({"predicted_category": "DoS", "threat_level": "CRITICAL_ATTACK", "is_anomaly": False, "latency_ms": 40.0})
    temp_db.log_event({"predicted_category": "Probe", "threat_level": "HIGH_ALERT", "is_anomaly": True, "latency_ms": 50.0})

    analytics = temp_db.get_threat_analytics()
    assert analytics["total_inspected_packets"] == 3
    assert analytics["malicious_intrusions"] == 2
    assert analytics["benign_packets"] == 1
    assert analytics["anomalies_detected"] == 1
    assert analytics["avg_latency_ms"] == 40.0
