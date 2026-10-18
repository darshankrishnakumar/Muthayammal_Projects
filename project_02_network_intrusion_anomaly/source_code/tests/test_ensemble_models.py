import os
import pytest
import numpy as np
from ml.inference_engine import NIDSInferenceEngine

@pytest.fixture(scope="module")
def engine():
    eng = NIDSInferenceEngine()
    assert eng.is_ready(), "Inference engine must load all model weights and preprocessors"
    return eng

def test_models_loaded(engine):
    assert engine.rf_model is not None
    assert engine.et_model is not None
    assert engine.iso_forest is not None
    assert engine.preprocessor is not None
    assert engine.label_encoder is not None
    assert len(engine.label_encoder.classes_) == 5

def test_benign_traffic_inference(engine):
    benign_pkt = {
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "duration": 1,
        "src_bytes": 280,
        "dst_bytes": 3520,
        "logged_in": 1,
        "serror_rate": 0.0,
        "rerror_rate": 0.0,
        "count": 2,
        "srv_count": 2
    }
    res = engine.predict_packet(benign_pkt)
    assert res["predicted_category"] == "Normal"
    assert res["confidence"] > 0.85
    assert res["threat_level"] == "BENIGN"
    assert res["is_anomaly"] is False

def test_syn_flood_dos_inference(engine):
    dos_pkt = engine.get_presets()["syn_flood_dos"]["data"]
    res = engine.predict_packet(dos_pkt)
    assert res["predicted_category"] == "DoS"
    assert res["confidence"] > 0.75
    assert res["threat_level"] == "CRITICAL_ATTACK"

def test_zero_day_anomaly_detection(engine):
    anom_pkt = {
        "protocol_type": "udp",
        "service": "other",
        "flag": "OTH",
        "duration": 500,
        "src_bytes": 999999,
        "dst_bytes": 888888,
        "urgent": 10,
        "hot": 20,
        "num_compromised": 50,
        "count": 500,
        "srv_count": 500
    }
    res = engine.predict_packet(anom_pkt)
    assert res["anomaly_score_pct"] > 50.0
    assert res["is_anomaly"] is True
    assert "ANOMALY" in res["threat_level"] or "ATTACK" in res["threat_level"]
