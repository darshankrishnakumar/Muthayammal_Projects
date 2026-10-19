import os
import sys
import pytest
from fastapi.testclient import TestClient

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(SRC_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from main import app, get_db

client = TestClient(app)

class TestParkinsonsAPI:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["port"] == 5011
        assert data["models_loaded"] is True

    def test_root_serves_frontend(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Inception-RNN" in resp.text or "Parkinson" in resp.text

    def test_api_stats(self):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_patients_screened" in data
        assert "parkinsons_detected" in data
        assert "healthy_controls_rate_pct" in data
        assert data["model_accuracy_pct"] >= 95.0

    def test_api_metrics(self):
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "accuracy" in data
        assert "f1_score" in data
        assert "confusion_matrix" in data

    def test_api_history(self):
        resp = client.get("/api/history?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "patient_id" in first
        assert "diagnosis" in first
        assert "predicted_updrs" in first

    def test_api_presets_list(self):
        resp = client.get("/api/presets")
        assert resp.status_code == 200
        presets = resp.json()
        assert isinstance(presets, list)
        assert len(presets) >= 3
        assert "patient_healthy_control.json" in presets

    def test_api_preset_data_endpoint(self):
        resp = client.get("/api/preset/patient_healthy_control.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "patient_id" in data
        assert "features" in data
        assert "MDVP:Fo(Hz)" in data["features"]

    def test_api_preset_data_not_found(self):
        resp = client.get("/api/preset/non_existent_preset_999.json")
        assert resp.status_code == 404

    def test_diagnose_healthy_control(self):
        payload = {
            "patient_id": "HC-0192",
            "features": {
                "MDVP:Fo(Hz)": 197.1,
                "MDVP:Fhi(Hz)": 206.9,
                "MDVP:Flo(Hz)": 192.1,
                "MDVP:Jitter(%)": 0.00289,
                "MDVP:Shimmer": 0.01689,
                "NHR": 0.008,
                "HNR": 26.88,
                "RPDE": 0.428,
                "DFA": 0.697,
                "spread1": -7.15,
                "spread2": 0.175,
                "PPE": 0.115
            }
        }
        resp = client.post("/api/diagnose", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagnosis"] == "HEALTHY_CONTROL"
        assert data["is_parkinsons"] is False
        assert data["confidence"] > 0.80
        assert data["predicted_updrs_score"] < 15.0
        assert "NORMAL" in data["clinical_recommendation"]

    def test_diagnose_parkinsons_early_stage(self):
        payload = {
            "patient_id": "PD-3041",
            "features": {
                "MDVP:Fo(Hz)": 152.8,
                "MDVP:Fhi(Hz)": 163.3,
                "MDVP:Flo(Hz)": 129.4,
                "MDVP:Jitter(%)": 0.00582,
                "MDVP:Shimmer": 0.0285,
                "NHR": 0.021,
                "HNR": 21.43,
                "RPDE": 0.512,
                "DFA": 0.724,
                "spread1": -5.62,
                "spread2": 0.224,
                "PPE": 0.198
            }
        }
        resp = client.post("/api/diagnose", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagnosis"] == "PARKINSONS_DIAGNOSED"
        assert data["is_parkinsons"] is True
        assert data["confidence"] > 0.80
        assert data["predicted_updrs_score"] >= 15.0

    def test_diagnose_parkinsons_advanced(self):
        payload = {
            "patient_id": "PD-8820",
            "features": {
                "MDVP:Fo(Hz)": 116.6,
                "MDVP:Fhi(Hz)": 131.1,
                "MDVP:Flo(Hz)": 95.2,
                "MDVP:Jitter(%)": 0.00994,
                "MDVP:Shimmer": 0.0543,
                "NHR": 0.048,
                "HNR": 17.20,
                "RPDE": 0.643,
                "DFA": 0.789,
                "spread1": -4.12,
                "spread2": 0.345,
                "PPE": 0.312
            }
        }
        resp = client.post("/api/diagnose", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagnosis"] == "PARKINSONS_DIAGNOSED"
        assert data["predicted_updrs_score"] >= 35.0

    def test_diagnose_database_persistence(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clinical_diagnoses")
        before = cur.fetchone()[0]
        conn.close()

        payload = {
            "patient_id": "TEST-PERSISTENCE",
            "features": {"MDVP:Fo(Hz)": 180.0, "MDVP:Jitter(%)": 0.003, "HNR": 25.0}
        }
        resp = client.post("/api/diagnose", json=payload)
        assert resp.status_code == 200

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clinical_diagnoses")
        after = cur.fetchone()[0]
        conn.close()

        assert after == before + 1

    def test_batch_diagnose(self):
        batch_req = [
            {"patient_id": "P1", "features": {"MDVP:Fo(Hz)": 200.0, "MDVP:Jitter(%)": 0.002}},
            {"patient_id": "P2", "features": {"MDVP:Fo(Hz)": 120.0, "MDVP:Jitter(%)": 0.009}}
        ]
        resp = client.post("/api/batch", json=batch_req)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_processed"] == 2
        assert len(data["results"]) == 2
