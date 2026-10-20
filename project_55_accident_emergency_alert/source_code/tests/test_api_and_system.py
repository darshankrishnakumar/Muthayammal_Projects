"""
Comprehensive Verification and QA Test Suite for Project 55:
AI-Based Accident Detection and Emergency Alert System Using Computer Vision.
Covers:
- Physical Deliverables Integrity
- Health Gateway & Enterprise Port 5055 Diagnostics
- SQLite Database ACID & WAL Journal Mode Verification
- Dual Real PyTorch Models (198,638 Trainable Parameters)
- 6,000 Record Telemetry Dataset (Zero Nulls)
- Presets & On-Demand Multi-Cue Temporal Fusion Inference
- Cryptographic Audit Ledger SHA-256 Hash Chaining (Genesis Block #0 + continuous chain)
- Operator Triage Flow & Status Lifecycle
- False Alarm Suppression & Hard Braking Robustness
"""

import os
import sys
import json
import sqlite3
import hashlib
import unittest
import pandas as pd
import torch
from fastapi.testclient import TestClient

# Path resolution
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db
from backend.app.ml.temporal_fusion_model import MultiCueTemporalFusionModel
from backend.app.ml.severity_estimator import CrashSeverityAndDispatchNeuralNet


class TestProject55EnterpriseSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    # 1. Deliverables Verification
    def test_01_deliverables_exist(self):
        self.assertTrue(os.path.isfile(os.path.join(ROOT_DIR, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(ROOT_DIR, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isdir(os.path.join(ROOT_DIR, "docs")), "docs/ dir must exist")
        self.assertTrue(os.path.isdir(os.path.join(ROOT_DIR, "presentations")), "presentations/ dir must exist")
        self.assertTrue(os.path.isdir(os.path.join(ROOT_DIR, "walkthrough")), "walkthrough/ dir must exist")

    # 2. Health Endpoint
    def test_02_health_endpoint(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "HEALTHY")
        self.assertEqual(data.get("project_id"), "PROJECT-055")
        self.assertEqual(data.get("port"), 5055)
        self.assertTrue(data.get("database_connected"))

    # 3. Database Counts in Health
    def test_03_health_database_counts(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        counts = res.json().get("database_counts", {})
        self.assertEqual(counts.get("cameras"), 4)
        self.assertGreaterEqual(counts.get("incidents"), 6000)
        self.assertGreaterEqual(counts.get("dispatches"), 1000)
        self.assertGreaterEqual(counts.get("audit_blocks"), 6001)

    # 4. Dual Model Parameters in Health
    def test_04_health_dual_model_parameters(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        models = res.json().get("models", {})
        self.assertEqual(models.get("temporal_fusion_model", {}).get("parameters"), 185990)
        self.assertEqual(models.get("crash_severity_regressor", {}).get("parameters"), 12648)
        self.assertEqual(models.get("total_parameters"), 198638)

    # 5. Database WAL Mode
    def test_05_database_sqlite_wal_mode(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal", "Database must operate in SQLite Write-Ahead Logging (WAL) mode")

    # 6. Analytics Summary
    def test_06_analytics_summary_kpis(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        kpis = data.get("kpis", {})
        self.assertGreaterEqual(kpis.get("total_incidents_recorded"), 6000)
        self.assertEqual(kpis.get("mean_time_to_detect_sec"), 1.15)
        self.assertEqual(kpis.get("false_alarm_rate_pct"), 0.0)

    # 7. Analytics Severity Distribution
    def test_07_analytics_severity_distribution(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        sev = res.json().get("severity_distribution", {})
        for cat in ["Critical", "Severe", "Moderate", "Minor"]:
            self.assertIn(cat, sev)
            self.assertGreater(sev[cat], 0)

    # 8. Cameras Listing
    def test_08_cameras_listing(self):
        res = self.client.get("/api/streams/cameras")
        self.assertEqual(res.status_code, 200)
        cams = res.json().get("cameras", [])
        self.assertEqual(len(cams), 4)
        for c in cams:
            self.assertIn("camera_id", c)
            self.assertIn("latitude", c)
            self.assertIn("longitude", c)
            self.assertIn("stream_endpoint", c)

    # 9. Incidents Listing Default
    def test_09_incidents_listing_default(self):
        res = self.client.get("/api/incidents/?limit=50")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("count"), 50)
        self.assertEqual(len(data.get("incidents")), 50)

    # 10. Incidents Filter By Severity
    def test_10_incidents_filter_by_severity(self):
        res = self.client.get("/api/incidents/?severity=Critical&limit=10")
        self.assertEqual(res.status_code, 200)
        for inc in res.json().get("incidents"):
            self.assertEqual(inc.get("severity"), "Critical")

    # 11. Incident Details By UUID
    def test_11_incident_details_by_uuid(self):
        list_res = self.client.get("/api/incidents/?limit=1")
        self.assertEqual(list_res.status_code, 200)
        uuid_str = list_res.json()["incidents"][0]["incident_uuid"]

        res = self.client.get(f"/api/incidents/{uuid_str}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("incident_uuid"), uuid_str)
        self.assertIn("camera", data)
        self.assertIn("dispatches", data)
        self.assertIn("evidence_hash", data)

    # 12. Presets Scenarios Endpoint
    def test_12_preset_scenarios_endpoint(self):
        res = self.client.get("/api/incidents/presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("count"), 4)
        preset_ids = [p["id"] for p in data.get("presets", [])]
        self.assertIn("PRESET-HWY101-ROLLOVER", preset_ids)
        self.assertIn("PRESET-URBAN-TBONE", preset_ids)
        self.assertIn("PRESET-RURAL-GUARDRAIL", preset_ids)
        self.assertIn("PRESET-SAFE-BRAKING", preset_ids)

    # 13. Audit Ledger Genesis Block
    def test_13_audit_ledger_genesis_block(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT block_index, event_type, previous_hash, block_hash FROM audit_ledger WHERE block_index = 0;")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 0)
        self.assertEqual(row[1], "GENESIS_BLOCK")
        self.assertEqual(row[2], "0" * 64)
        self.assertEqual(len(row[3]), 64)

    # 14. Audit Ledger Continuous Chaining
    def test_14_audit_ledger_continuous_chaining(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT block_index, previous_hash, block_hash FROM audit_ledger ORDER BY block_index ASC LIMIT 25;")
        rows = cur.fetchall()
        conn.close()
        self.assertGreaterEqual(len(rows), 25)
        for i in range(1, len(rows)):
            self.assertEqual(rows[i][1], rows[i - 1][2], f"Block #{rows[i][0]} previous_hash must match block #{rows[i-1][0]} block_hash")

    # 15. Audit Ledger API Integrity Status
    def test_15_audit_ledger_integrity_status(self):
        res = self.client.get("/api/incidents/audit-ledger?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("chain_integrity"), "VALID")
        self.assertGreaterEqual(data.get("total_blocks"), 6001)

    # 16. Dual-Model Inference: Critical Rollover Crash
    def test_16_inference_critical_rollover_scenario(self):
        payload = {
            "camera_id": "CAM-HWY-101-NORTH",
            "deceleration_g": 5.2,
            "orientation_yaw_deg": 180.0,
            "trajectory_deviation_m": 15.0,
            "impact_force_kn": 380.0,
            "delta_v_kph": 88.0,
            "post_impact_immobility_sec": 50.0,
            "actual_speed_kph": 120.0,
            "speed_limit_kph": 110.0,
            "vehicles_involved": 2,
            "road_friction_coeff": 0.70,
            "visibility_m": 800.0,
            "ambient_lux": 400.0,
            "rollover_detected": True
        }
        res = self.client.post("/api/incidents/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertEqual(d.get("severity"), "Critical")
        self.assertEqual(d.get("priority"), "P1-Critical")
        self.assertGreaterEqual(d.get("confidence"), 0.90)
        self.assertIn("audit_block", d)
        self.assertEqual(len(d["audit_block"]["block_hash"]), 64)

    # 17. Dual-Model Inference: Urban T-Bone Collision
    def test_17_inference_urban_tbone_scenario(self):
        payload = {
            "camera_id": "CAM-URBAN-MAIN-5TH",
            "deceleration_g": 4.0,
            "orientation_yaw_deg": 90.0,
            "trajectory_deviation_m": 8.0,
            "impact_force_kn": 270.0,
            "delta_v_kph": 55.0,
            "post_impact_immobility_sec": 35.0,
            "actual_speed_kph": 58.0,
            "speed_limit_kph": 50.0,
            "vehicles_involved": 3,
            "road_friction_coeff": 0.65,
            "visibility_m": 600.0,
            "ambient_lux": 850.0,
            "rollover_detected": False
        }
        res = self.client.post("/api/incidents/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertIn(d.get("severity"), ["Severe", "Critical"])
        self.assertEqual(d.get("vehicles_involved"), 3)

    # 18. False Alarm Suppression: Safe Hard Braking Non-Crash
    def test_18_inference_safe_braking_false_alarm_suppression(self):
        payload = {
            "camera_id": "CAM-PORT-LOGISTICS-WAY",
            "deceleration_g": 1.6,
            "orientation_yaw_deg": 3.0,
            "trajectory_deviation_m": 0.4,
            "impact_force_kn": 10.0,
            "delta_v_kph": 12.0,
            "post_impact_immobility_sec": 0.0,
            "actual_speed_kph": 40.0,
            "speed_limit_kph": 45.0,
            "vehicles_involved": 1,
            "road_friction_coeff": 0.55,
            "visibility_m": 400.0,
            "ambient_lux": 250.0,
            "rollover_detected": False
        }
        res = self.client.post("/api/incidents/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertEqual(d.get("severity"), "Minor")
        self.assertEqual(d.get("priority"), "P4-Low")
        self.assertLessEqual(d.get("confidence"), 0.50)
        self.assertEqual(d.get("status"), "Resolved")

    # 19. Dynamic Cue Weights Output
    def test_19_inference_dynamic_cue_weights(self):
        payload = {
            "camera_id": "CAM-RURAL-PASS-RT9",
            "deceleration_g": 3.0,
            "orientation_yaw_deg": 120.0,
            "trajectory_deviation_m": 9.0,
            "impact_force_kn": 180.0,
            "delta_v_kph": 45.0,
            "post_impact_immobility_sec": 25.0,
            "actual_speed_kph": 65.0,
            "speed_limit_kph": 65.0,
            "vehicles_involved": 1,
            "road_friction_coeff": 0.50,
            "visibility_m": 300.0,
            "ambient_lux": 150.0,
            "rollover_detected": False
        }
        res = self.client.post("/api/incidents/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        weights = res.json().get("dynamic_cue_weights", {})
        self.assertIn("trajectory_deviation_weight", weights)
        self.assertIn("sudden_deceleration_weight", weights)
        self.assertIn("abnormal_orientation_weight", weights)
        self.assertIn("collision_proximity_weight", weights)
        self.assertIn("immobility_weight", weights)

    # 20. Chained Block Persistence on Live Analyze
    def test_20_inference_creates_audit_block(self):
        before_res = self.client.get("/api/incidents/audit-ledger?limit=1")
        before_total = before_res.json()["total_blocks"]

        payload = {
            "camera_id": "CAM-HWY-101-NORTH",
            "deceleration_g": 4.5,
            "orientation_yaw_deg": 45.0,
            "trajectory_deviation_m": 12.0,
            "impact_force_kn": 310.0,
            "delta_v_kph": 75.0,
            "post_impact_immobility_sec": 40.0,
            "actual_speed_kph": 115.0,
            "speed_limit_kph": 110.0,
            "vehicles_involved": 2,
            "road_friction_coeff": 0.70,
            "visibility_m": 800.0,
            "ambient_lux": 400.0,
            "rollover_detected": True
        }
        self.client.post("/api/incidents/analyze", json=payload)

        after_res = self.client.get("/api/incidents/audit-ledger?limit=1")
        after_total = after_res.json()["total_blocks"]
        self.assertEqual(after_total, before_total + 1)

    # 21. Incident Operator Triage Flow
    def test_21_incident_operator_triage_flow(self):
        list_res = self.client.get("/api/incidents/?limit=1")
        uuid_str = list_res.json()["incidents"][0]["incident_uuid"]

        triage_payload = {
            "action": "DISPATCH",
            "operator_id": "OPERATOR_COMMAND_09",
            "notes": "Emergency units en route"
        }
        res = self.client.post(f"/api/incidents/{uuid_str}/triage", json=triage_payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("new_status"), "Dispatched")

    # 22. Triage Invalid Action Handling
    def test_22_incident_operator_triage_invalid_action(self):
        list_res = self.client.get("/api/incidents/?limit=1")
        uuid_str = list_res.json()["incidents"][0]["incident_uuid"]

        res = self.client.post(f"/api/incidents/{uuid_str}/triage", json={"action": "INVALID_STATE"})
        self.assertEqual(res.status_code, 400)

    # 23. Incident 404 Handling
    def test_23_incident_details_404_not_found(self):
        res = self.client.get("/api/incidents/NON_EXISTENT_UUID_99999")
        self.assertEqual(res.status_code, 404)

    # 24. PyTorch Model 1 Parameter Count Check
    def test_24_pytorch_model1_parameter_count(self):
        m1 = MultiCueTemporalFusionModel(spatial_dim=128, temporal_dim=64, kinematic_dim=5, fusion_dim=64)
        p1 = sum(p.numel() for p in m1.parameters() if p.requires_grad)
        self.assertEqual(p1, 185990, "MultiCueTemporalFusionModel must contain exactly 185,990 parameters")

    # 25. PyTorch Model 2 Parameter Count Check
    def test_25_pytorch_model2_parameter_count(self):
        m2 = CrashSeverityAndDispatchNeuralNet(input_dim=12)
        p2 = sum(p.numel() for p in m2.parameters() if p.requires_grad)
        self.assertEqual(p2, 12648, "CrashSeverityAndDispatchNeuralNet must contain exactly 12,648 parameters")

    # 26. PyTorch Model 1 Forward Tensor Shapes
    def test_26_pytorch_model1_forward_tensor_shapes(self):
        m1 = MultiCueTemporalFusionModel()
        m1.eval()
        dummy_frames = torch.randn(2, 16, 3, 64, 64)
        dummy_kine = torch.randn(2, 5)
        with torch.no_grad():
            out = m1(dummy_frames, dummy_kine)
        self.assertIn("confidence", out)
        self.assertIn("cue_weights", out)
        self.assertIn("fused_features", out)
        self.assertEqual(out["confidence"].shape, (2, 1))
        self.assertEqual(out["cue_weights"].shape, (2, 5))

    # 27. PyTorch Model 2 Forward Tensor Shapes
    def test_27_pytorch_model2_forward_tensor_shapes(self):
        m2 = CrashSeverityAndDispatchNeuralNet(input_dim=12)
        m2.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = m2(dummy_in)
        self.assertEqual(out["severity_score"].shape, (4, 1))
        self.assertEqual(out["delta_v_kph"].shape, (4, 1))
        self.assertEqual(out["casualty_risk"].shape, (4, 1))
        self.assertEqual(out["required_ems_units"].shape, (4, 1))
        self.assertEqual(out["priority_logits"].shape, (4, 4))

    # 28. Model Weights Files on Disk
    def test_28_model_weights_files_on_disk(self):
        m1_file = os.path.join(BASE_DIR, "backend", "models", "temporal_fusion_weights.pt")
        m2_file = os.path.join(BASE_DIR, "backend", "models", "crash_severity_weights.pt")
        self.assertTrue(os.path.isfile(m1_file), f"{m1_file} must exist")
        self.assertTrue(os.path.isfile(m2_file), f"{m2_file} must exist")
        self.assertGreater(os.path.getsize(m1_file), 100000)
        self.assertGreater(os.path.getsize(m2_file), 10000)

    # 29. Metadata & Scalers JSON
    def test_29_model_scalers_and_metadata_json(self):
        meta_file = os.path.join(BASE_DIR, "backend", "models", "model_metadata.json")
        scaler_file = os.path.join(BASE_DIR, "backend", "models", "accident_scalers.json")
        self.assertTrue(os.path.isfile(meta_file), "model_metadata.json must exist")
        self.assertTrue(os.path.isfile(scaler_file), "accident_scalers.json must exist")
        with open(meta_file, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta.get("project_id"), "PROJECT-055")
        self.assertEqual(meta.get("models", {}).get("total_parameters"), 198638)

    # 30. CSV Telemetry Dataset Validity
    def test_30_csv_dataset_telemetry_validity(self):
        csv_file = os.path.join(BASE_DIR, "data", "accident_telemetry_6000.csv")
        self.assertTrue(os.path.isfile(csv_file), "accident_telemetry_6000.csv must exist")
        df = pd.read_csv(csv_file)
        self.assertEqual(len(df), 6000, "Dataset must have exactly 6,000 rows")
        self.assertEqual(df.isnull().sum().sum(), 0, "Dataset must have 0 null values")
        self.assertIn("incident_uuid", df.columns)
        self.assertIn("evidence_hash", df.columns)

    # 31. Root Frontend Dashboard Accessible
    def test_31_root_frontend_dashboard_accessible(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("PROJECT 55", res.text)


if __name__ == "__main__":
    unittest.main()
