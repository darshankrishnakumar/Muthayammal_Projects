import os
import sys
import pytest
import sqlite3
import torch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.ml.csrnet_crowd_model import CSRNetCrowdDensityNet
from backend.app.ml.risk_regressor_model import CrowdOpticalFlowRiskRegressorNet

client = TestClient(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

class TestProject52CompleteSystem:
    # 1. Deliverables Verification
    def test_01_requirements_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "requirements.txt"))

    def test_02_env_example_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, ".env.example"))

    def test_03_walkthrough_script_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "walkthrough", "walkthrough_script.md"))

    def test_04_dataset_6000_exists(self):
        csv_path = os.path.join(BASE_DIR, "data", "crowd_telemetry_6000.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 6001 # header + 6000 records

    def test_05_weights_csrnet_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "csrnet_crowd_weights.pt"))
        assert os.path.isfile(os.path.join(BASE_DIR, "experiments", "phase2_model.pt"))

    def test_06_weights_risk_regressor_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "crowd_risk_weights.pt"))

    def test_07_metadata_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "model_metadata.json"))

    def test_08_scalers_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "crowd_scalers.json"))

    # 2. Health & Gateway Verification
    def test_09_health_endpoint_status(self):
        res = client.get("/api/health/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert data["project_id"] == "PROJECT-052"
        assert data["port"] == 5052
        assert data["database_wal_mode"] is True

    def test_10_health_models_parameters(self):
        res = client.get("/api/health/")
        data = res.json()
        assert "models" in data
        models = data["models"]
        assert models["csrnet_parameters"] == 350950
        assert models["risk_regressor_parameters"] == 12648
        assert models["total_parameters"] == 363598

    # 3. Analytics & KPI Aggregations
    def test_11_analytics_summary(self):
        res = client.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_monitored_scans"] >= 6000
        assert data["active_anomaly_alerts"] > 0
        assert data["mean_zonal_headcount"] > 50
        assert data["model_performance"]["density_mae_people"] == 4.8
        assert data["model_performance"]["anomaly_f1_score"] == 0.942

    def test_12_analytics_breakdown(self):
        res = client.get("/api/analytics/breakdown")
        assert res.status_code == 200
        data = res.json()
        assert "breakdown" in data
        assert len(data["breakdown"]) == 4

    # 4. Presets & Pagination Queries
    def test_13_presets_availability(self):
        res = client.get("/api/crowd/presets")
        assert res.status_code == 200
        data = res.json()
        assert len(data["presets"]) == 4

    def test_14_events_pagination(self):
        res = client.get("/api/crowd/events?skip=0&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 6000
        assert len(data["events"]) == 10

    def test_15_events_filtering_by_zone(self):
        res = client.get("/api/crowd/events?zone_name=Central Plaza Concourse&limit=5")
        assert res.status_code == 200
        data = res.json()
        for e in data["events"]:
            assert e["zone_name"] == "Central Plaza Concourse"

    # 5. Scene Analysis & Anomaly Detection
    def test_16_analyze_central_plaza_high_surge(self):
        payload = {
            "zone_name": "Central Plaza Concourse",
            "simulation_level": "high"
        }
        res = client.post("/api/crowd/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "event" in data
        assert "metrics" in data
        m = data["metrics"]
        assert m["zone_name"] == "Central Plaza Concourse"
        assert m["estimated_headcount"] >= 300
        assert m["anomaly_detected"] is True
        assert len(m["density_map_preview"]) == 16
        assert len(m["density_map_preview"][0]) == 16

    def test_17_analyze_north_gate_turnstiles(self):
        payload = {
            "zone_name": "North Gate Turnstiles",
            "simulation_level": "moderate"
        }
        res = client.post("/api/crowd/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["zone_name"] == "North Gate Turnstiles"
        assert m["archetype"] == "VENUE_BOTTLENECK"
        assert len(m["evidence_hash"]) == 64

    def test_18_analyze_stadium_emergency_exit(self):
        payload = {
            "zone_name": "Stadium Emergency Exit Corridor",
            "simulation_level": "high"
        }
        res = client.post("/api/crowd/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["anomaly_detected"] is True
        assert m["risk_score"] >= 0.70

    # 6. Cryptographic Audit Ledger
    def test_19_audit_ledger_genesis_block(self):
        res = client.get("/api/crowd/audit-logs?limit=5")
        assert res.status_code == 200
        data = res.json()
        assert data["chain_valid"] is True
        assert data["total_blocks"] >= 6001
        assert data["genesis_block_hash"] is not None

    def test_20_audit_ledger_continuous_chaining(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT block_index, previous_hash, block_hash FROM audit_ledger ORDER BY block_index ASC LIMIT 50;")
        rows = cur.fetchall()
        conn.close()

        assert rows[0][0] == 0 # Genesis
        for i in range(1, len(rows)):
            assert rows[i][1] == rows[i-1][2], f"Hash break at block {rows[i][0]}"

    def test_21_analyze_appends_audit_block(self):
        res_before = client.get("/api/crowd/audit-logs?limit=1")
        total_before = res_before.json()["total_blocks"]

        payload = {"zone_name": "Transit Station Platform 2", "simulation_level": "low"}
        res_scan = client.post("/api/crowd/analyze", json=payload)
        assert res_scan.status_code == 200

        res_after = client.get("/api/crowd/audit-logs?limit=1")
        total_after = res_after.json()["total_blocks"]
        assert total_after == total_before + 1

    # 7. PyTorch Neural Engine Unit Tests
    def test_22_csrnet_forward_pass_shape(self):
        model = CSRNetCrowdDensityNet()
        model.eval()
        dummy_in = torch.randn(2, 3, 128, 128)
        with torch.no_grad():
            d_map, a_logits = model(dummy_in)
        assert d_map.shape == (2, 1, 16, 16)
        assert a_logits.shape == (2, 5)

    def test_23_csrnet_parameter_count(self):
        model = CSRNetCrowdDensityNet()
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 350950

    def test_24_risk_regressor_forward_pass_keys(self):
        model = CrowdOpticalFlowRiskRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert "risk_score" in out
        assert "turbulence" in out
        assert "correction" in out
        assert "anomaly_logits" in out

    def test_25_risk_regressor_output_ranges(self):
        model = CrowdOpticalFlowRiskRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert torch.all(out["risk_score"] >= 0.0) and torch.all(out["risk_score"] <= 1.0)
        assert torch.all(out["turbulence"] >= 0.0) and torch.all(out["turbulence"] <= 1.0)

    def test_26_risk_regressor_parameter_count(self):
        model = CrowdOpticalFlowRiskRegressorNet(input_dim=12)
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 12648

    # 8. Database ACID & Web Serving Tests
    def test_27_database_wal_pragma_verified(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        assert mode.lower() == "wal"

    def test_28_database_total_rows_at_least_6000(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM crowd_monitoring_events;")
        cnt = cur.fetchone()[0]
        conn.close()
        assert cnt >= 6000

    def test_29_database_no_null_evidence_hashes(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM crowd_monitoring_events WHERE evidence_hash IS NULL OR length(evidence_hash) != 64;")
        bad_cnt = cur.fetchone()[0]
        conn.close()
        assert bad_cnt == 0

    def test_30_root_serves_html(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert "PROJECT 52" in res.text
        assert "Port: 5052" in res.text

    def test_31_root_contains_heatmap_container(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "heatmap-grid" in res.text
        assert "audit-body" in res.text
