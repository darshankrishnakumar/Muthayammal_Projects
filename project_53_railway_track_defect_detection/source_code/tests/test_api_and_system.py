import os
import sys
import pytest
import sqlite3
import torch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.ml.resunet_rail_model import ResUNetRailDefectSegmenter
from backend.app.ml.track_geometry_model import RailTrackGeometryAndDegradationRegressorNet

client = TestClient(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

class TestProject53CompleteSystem:
    # 1. Deliverables Verification
    def test_01_requirements_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "requirements.txt"))

    def test_02_env_example_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, ".env.example"))

    def test_03_walkthrough_script_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "walkthrough", "walkthrough_script.md"))

    def test_04_dataset_6000_exists(self):
        csv_path = os.path.join(BASE_DIR, "data", "railway_telemetry_6000.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 6001  # header + 6000 records

    def test_05_weights_resunet_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "resunet_rail_weights.pt"))
        assert os.path.isfile(os.path.join(BASE_DIR, "experiments", "phase2_model.pt"))

    def test_06_weights_geometry_regressor_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "rail_geometry_weights.pt"))

    def test_07_metadata_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "model_metadata.json"))

    def test_08_scalers_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "rail_scalers.json"))

    # 2. Health & Gateway Verification
    def test_09_health_endpoint_status(self):
        res = client.get("/api/health/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert data["project_id"] == "PROJECT-053"
        assert data["port"] == 5053
        assert data["database_wal_mode"] is True

    def test_10_health_models_parameters(self):
        res = client.get("/api/health/")
        data = res.json()
        assert "models" in data
        models = data["models"]
        assert models["resunet_parameters"] == 374342
        assert models["geometry_regressor_parameters"] == 12582
        assert models["total_parameters"] == 386924

    # 3. Analytics & KPI Aggregations
    def test_11_analytics_summary(self):
        res = client.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_inspected_defects"] >= 6000
        assert data["critical_priority_defects"] > 0
        assert data["mean_track_quality_index"] > 30.0
        assert data["model_performance"]["mIoU_accuracy"] == 0.862
        assert data["model_performance"]["f1_score"] == 0.952

    def test_12_analytics_breakdown(self):
        res = client.get("/api/analytics/breakdown")
        assert res.status_code == 200
        data = res.json()
        assert "breakdown" in data
        assert len(data["breakdown"]) >= 4

    # 4. Presets & Pagination Queries
    def test_13_presets_availability(self):
        res = client.get("/api/rail/presets")
        assert res.status_code == 200
        data = res.json()
        assert len(data["presets"]) == 4

    def test_14_defects_pagination(self):
        res = client.get("/api/rail/defects?skip=0&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 6000
        assert len(data["records"]) == 10

    def test_15_defects_filtering_by_corridor(self):
        segment = "High-Speed Line 1 Westbound"
        res = client.get(f"/api/rail/defects?track_segment={segment}&limit=5")
        assert res.status_code == 200
        data = res.json()
        for r in data["records"]:
            assert r["track_segment"] == segment

    # 5. Track Inspection & Defect Inference
    def test_16_inspect_high_speed_clean_track(self):
        payload = {
            "chainage_km": "KM 144.200",
            "track_segment": "Line 1 Main Westbound",
            "simulated_condition": "nominal"
        }
        res = client.post("/api/rail/inspect", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "record" in data
        assert "metrics" in data
        m = data["metrics"]
        assert m["track_segment"] == "Line 1 Main Westbound"
        assert m["defect_type"] == "Clean Rail Head"
        assert m["severity"] == "None"
        assert m["derailment_risk"] < 0.20

    def test_17_inspect_heavy_freight_crack(self):
        payload = {
            "chainage_km": "KM 082.450",
            "track_segment": "Line 2 Freight Northbound",
            "simulated_condition": "crack"
        }
        res = client.post("/api/rail/inspect", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["track_segment"] == "Line 2 Freight Northbound"
        assert m["severity"] in ["Moderate", "Critical"]
        assert "Crack" in m["defect_type"]
        assert m["derailment_risk"] >= 0.50

    def test_18_inspect_mountain_pass_missing_fastener(self):
        payload = {
            "chainage_km": "KM 210.800",
            "track_segment": "Mountain Switch & Turnout",
            "simulated_condition": "fastener"
        }
        res = client.post("/api/rail/inspect", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["severity"] in ["Moderate", "Critical"]
        assert "Fastener" in m["defect_type"]

    # 6. Cryptographic Audit Ledger
    def test_19_audit_ledger_genesis_block(self):
        res = client.get("/api/rail/audit-logs?limit=5")
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

        assert rows[0][0] == 0  # Genesis
        for i in range(1, len(rows)):
            assert rows[i][1] == rows[i-1][2], f"Hash break at block {rows[i][0]}"

    def test_21_inspect_appends_audit_block(self):
        res_before = client.get("/api/rail/audit-logs?limit=1")
        total_before = res_before.json()["total_blocks"]

        payload = {"chainage_km": "KM 018.150", "track_segment": "Metro Suburban Southbound", "simulated_condition": "nominal"}
        res_inspect = client.post("/api/rail/inspect", json=payload)
        assert res_inspect.status_code == 200

        res_after = client.get("/api/rail/audit-logs?limit=1")
        total_after = res_after.json()["total_blocks"]
        assert total_after == total_before + 1

    # 7. PyTorch Neural Engine Unit Tests
    def test_22_resunet_forward_pass_shape(self):
        model = ResUNetRailDefectSegmenter(in_channels=3, num_classes=6)
        model.eval()
        dummy_in = torch.randn(2, 3, 128, 128)
        with torch.no_grad():
            mask_logits = model(dummy_in)
        assert mask_logits.shape == (2, 6, 128, 128)

    def test_23_resunet_parameter_count(self):
        model = ResUNetRailDefectSegmenter(in_channels=3, num_classes=6)
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 374342

    def test_24_geometry_regressor_forward_pass_keys(self):
        model = RailTrackGeometryAndDegradationRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert "track_quality_index" in out
        assert "speed_restriction_kmh" in out
        assert "derailment_risk" in out
        assert "severity_logits" in out

    def test_25_geometry_regressor_output_ranges(self):
        model = RailTrackGeometryAndDegradationRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert torch.all(out["derailment_risk"] >= 0.0) and torch.all(out["derailment_risk"] <= 1.0)
        assert torch.all(out["speed_restriction_kmh"] >= 0.0)

    def test_26_geometry_regressor_parameter_count(self):
        model = RailTrackGeometryAndDegradationRegressorNet(input_dim=12)
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 12582

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
        cur.execute("SELECT count(*) FROM railway_defect_records;")
        cnt = cur.fetchone()[0]
        conn.close()
        assert cnt >= 6000

    def test_29_database_no_null_evidence_hashes(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM railway_defect_records WHERE evidence_hash IS NULL OR length(evidence_hash) != 64;")
        bad_cnt = cur.fetchone()[0]
        conn.close()
        assert bad_cnt == 0

    def test_30_root_serves_html(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert "PROJECT 53" in res.text
        assert "Port: 5053" in res.text

    def test_31_root_contains_segmentation_container(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "vis-box" in res.text
        assert "audit-body" in res.text
