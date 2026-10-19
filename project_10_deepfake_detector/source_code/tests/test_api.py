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

class TestDeepfakeAPI:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["port"] == 5010
        assert data["models_loaded"] is True

    def test_root_serves_frontend(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "MesoInception-4" in resp.text or "Deepfake" in resp.text

    def test_api_stats(self):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_audited_scans" in data
        assert "deepfakes_intercepted" in data
        assert "authentic_rate_pct" in data
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
        assert "filename" in first
        assert "prediction" in first
        assert "confidence" in first

    def test_api_samples_list(self):
        resp = client.get("/api/samples")
        assert resp.status_code == 200
        samples = resp.json()
        assert isinstance(samples, list)
        assert len(samples) >= 4
        assert "real_person_01.jpg" in samples

    def test_api_sample_image_endpoint(self):
        resp = client.get("/api/sample-image/real_person_01.jpg")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("image/")

    def test_api_sample_image_not_found(self):
        resp = client.get("/api/sample-image/non_existent_image_123.jpg")
        assert resp.status_code == 404

    def test_analyze_real_person(self):
        resp = client.post("/api/analyze", json={"sample_name": "real_person_01.jpg"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "REAL"
        assert data["is_deepfake"] is False
        assert data["confidence"] > 0.80
        assert "AUTHENTIC" in data["moderation_verdict"]

    def test_analyze_deepfake_faceswap(self):
        resp = client.post("/api/analyze", json={"sample_name": "deepfake_faceswap_01.jpg"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "DEEPFAKE"
        assert data["is_deepfake"] is True
        assert data["confidence"] > 0.80
        assert "QUARANTINED" in data["moderation_verdict"]

    def test_analyze_deepfake_stylegan(self):
        resp = client.post("/api/analyze", json={"sample_name": "deepfake_stylegan_01.jpg"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "DEEPFAKE"
        assert data["is_deepfake"] is True

    def test_analyze_deepfake_diffusion(self):
        resp = client.post("/api/analyze", json={"sample_name": "deepfake_diffusion_01.jpg"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prediction"] == "DEEPFAKE"
        assert data["is_deepfake"] is True

    def test_analyze_forensic_indicators_structure(self):
        resp = client.post("/api/analyze", json={"sample_name": "real_person_02.jpg"})
        assert resp.status_code == 200
        data = resp.json()
        inds = data["forensic_indicators"]
        assert "fft_anomaly_score" in inds
        assert "boundary_discontinuity" in inds
        assert "color_chroma_variance" in inds
        assert "laplacian_sharpness" in inds
        assert "eye_asymmetry_index" in inds
        assert data["latency_ms"] >= 0

    def test_analyze_database_persistence(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM forensic_scans")
        before = cur.fetchone()[0]
        conn.close()

        resp = client.post("/api/analyze", json={"sample_name": "real_person_01.jpg"})
        assert resp.status_code == 200

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM forensic_scans")
        after = cur.fetchone()[0]
        conn.close()

        assert after == before + 1

    def test_batch_analyze(self):
        resp = client.post("/api/batch", json=["real_person_01.jpg", "deepfake_faceswap_01.jpg"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_processed"] == 2
        assert len(data["results"]) == 2
