import unittest
import os
import sys
import torch
import numpy as np
import sqlite3
import hashlib
import json

# Ensure source_code is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal, compute_block_hash
from backend.app.db.models import FireIncident, HazardZone, AuditLedger
from backend.app.ml.dual_stream_fire_model import DualStreamFireSmokeNet
from backend.app.ml.thermal_risk_model import FirePropagationThermalRiskRegressorNet
from backend.app.ml.inference_engine import fire_engine, HAZARD_CLASSES

class TestP40FireSmokeSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "fire_smoke.db"))
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "fire_smoke_telemetry_6000.csv"))

    # ─────────────────────────────────────────────────────────────────────────
    # Database & Schema Integrity
    # ─────────────────────────────────────────────────────────────────────────
    def test_01_sqlite_database_exists(self):
        self.assertTrue(os.path.exists(self.db_path), f"Database must exist at {self.db_path}")

    def test_02_sqlite_wal_mode_enabled(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal", f"Journal mode must be WAL, got {mode}")

    def test_03_database_tables_exist(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        conn.close()
        self.assertIn("fire_incidents", tables)
        self.assertIn("hazard_zones", tables)
        self.assertIn("audit_ledger", tables)

    def test_04_hazard_zones_count(self):
        db = SessionLocal()
        count = db.query(HazardZone).count()
        db.close()
        self.assertGreaterEqual(count, 5)

    def test_05_fire_incidents_initial_records(self):
        db = SessionLocal()
        count = db.query(FireIncident).count()
        db.close()
        self.assertGreaterEqual(count, 6)

    # ─────────────────────────────────────────────────────────────────────────
    # Cryptographic Audit Ledger & Chain of Custody
    # ─────────────────────────────────────────────────────────────────────────
    def test_06_audit_ledger_genesis_block(self):
        db = SessionLocal()
        genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        db.close()
        self.assertIsNotNone(genesis, "Genesis block (block 0) must exist")
        self.assertEqual(genesis.previous_hash, "0" * 64, "Genesis previous_hash must be 64 zeros")
        expected_hash = compute_block_hash(genesis.action_type, genesis.details, genesis.timestamp, genesis.previous_hash)
        self.assertEqual(genesis.current_hash, expected_hash, "Genesis current_hash must match SHA-256 calculation")

    def test_07_audit_ledger_hash_chain_continuity(self):
        db = SessionLocal()
        blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
        db.close()
        self.assertGreaterEqual(len(blocks), 2, "Must have at least 2 blocks in audit ledger")
        for i in range(1, len(blocks)):
            prev = blocks[i - 1]
            curr = blocks[i]
            self.assertEqual(curr.previous_hash, prev.current_hash, f"Block {curr.block_index} previous_hash broken")
            calc_hash = compute_block_hash(curr.action_type, curr.details, curr.timestamp, curr.previous_hash)
            self.assertEqual(curr.current_hash, calc_hash, f"Block {curr.block_index} hash recalculation mismatch")

    def test_08_audit_ledger_tamper_detection(self):
        db = SessionLocal()
        block = db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
        db.close()
        self.assertIsNotNone(block)
        tampered_details = block.details + " [MALICIOUS_TAMPER]"
        tampered_hash = compute_block_hash(block.action_type, tampered_details, block.timestamp, block.previous_hash)
        self.assertNotEqual(tampered_hash, block.current_hash, "Tamper simulation must invalidate SHA-256 hash")

    # ─────────────────────────────────────────────────────────────────────────
    # Dataset Integrity (6,000 Physical Telemetry Records)
    # ─────────────────────────────────────────────────────────────────────────
    def test_09_dataset_file_exists(self):
        self.assertTrue(os.path.exists(self.csv_path), f"Dataset CSV must exist at {self.csv_path}")

    def test_10_dataset_record_count(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        header = lines[0]
        rows = lines[1:]
        self.assertEqual(len(rows), 6000, f"Dataset must contain exactly 6,000 records, found {len(rows)}")

    def test_11_dataset_columns(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            header = f.readline().strip().split(",")
        expected_cols = [
            "record_id", "zone_name", "camera_id", "hazard_type", "class_id",
            "ambient_temp_c", "ir_thermal_radiation_kw_m2", "smoke_obscuration_pct_m",
            "flicker_frequency_hz", "flame_pixel_area_ratio", "plume_expansion_m_s",
            "co_concentration_ppm", "airflow_velocity_m_s", "zone_occupancy_persons",
            "structural_thermal_strain", "evacuation_urgency_index"
        ]
        for col in expected_cols:
            self.assertIn(col, header, f"Expected column {col} missing from CSV header")

    def test_12_dataset_class_balance(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            rows = [l.strip().split(",") for l in f][1:]
        class_counts = {}
        for r in rows:
            c = r[3]
            class_counts[c] = class_counts.get(c, 0) + 1
        for cls_name in ["NORMAL", "SMOKE_DETECTED", "FLAME_DETECTED", "DUAL_FIRE_SMOKE_HAZARD"]:
            self.assertEqual(class_counts.get(cls_name), 1500, f"Class {cls_name} should have 1,500 samples")

    # ─────────────────────────────────────────────────────────────────────────
    # PyTorch Model Architecture & Weight Serialization
    # ─────────────────────────────────────────────────────────────────────────
    def test_13_dual_stream_model_weights_exist(self):
        phase2_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments", "phase2_model.pt"))
        self.assertTrue(os.path.exists(phase2_path), f"Phase 2 weights must exist at {phase2_path}")
        self.assertGreater(os.path.getsize(phase2_path), 500000, "Weight file size must be substantial")

    def test_14_thermal_regressor_weights_exist(self):
        thermal_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models", "thermal_risk_regressor_weights.pt"))
        self.assertTrue(os.path.exists(thermal_path), f"Thermal regressor weights must exist at {thermal_path}")
        self.assertGreater(os.path.getsize(thermal_path), 50000)

    def test_15_dual_stream_forward_shape(self):
        from backend.app.ml.dual_stream_fire_model import DualStreamFireSmokeNet
        model = DualStreamFireSmokeNet(num_classes=4)
        x_img = torch.randn(2, 3, 64, 64)
        x_flicker = torch.randn(2, 8)
        out = model(x_img, x_flicker)
        self.assertEqual(out.shape, (2, 4), f"Expected shape (2, 4), got {out.shape}")

    def test_16_thermal_regressor_forward_shape(self):
        from backend.app.ml.thermal_risk_model import FirePropagationThermalRiskRegressorNet
        model = FirePropagationThermalRiskRegressorNet(in_features=10)
        x = torch.randn(4, 10)
        p_temp, p_plume, p_urg, p_co = model(x)
        self.assertEqual(p_temp.shape, (4, 1), f"Expected shape (4, 1), got {p_temp.shape}")
        self.assertEqual(p_plume.shape, (4, 1), f"Expected shape (4, 1), got {p_plume.shape}")
        self.assertEqual(p_urg.shape, (4, 1), f"Expected shape (4, 1), got {p_urg.shape}")
        self.assertEqual(p_co.shape, (4, 1), f"Expected shape (4, 1), got {p_co.shape}")

    def test_17_model_metadata_valid(self):
        meta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models", "model_metadata.json"))
        self.assertTrue(os.path.exists(meta_path))
        with open(meta_path, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta.get("status"), "TRAINED_SERIALIZED")
        self.assertEqual(meta.get("dataset_records"), 6000)
        self.assertEqual(meta.get("target_hazard_classes"), 4)
        self.assertIn("test_mae", meta)

    # ─────────────────────────────────────────────────────────────────────────
    # Inference Engine & Physics Bounds
    # ─────────────────────────────────────────────────────────────────────────
    def test_18_inference_engine_flame_detection(self):
        res = fire_engine.analyze(
            zone_name="Industrial Plant Boiler Room",
            simulate_flame=True,
            simulate_smoke=False
        )
        self.assertEqual(res["hazard_type"], "FLAME_DETECTED")
        self.assertGreater(res["flame_temp_c"], 200.0)
        self.assertIn("confidence", res)
        self.assertIn("evidence_hash", res)
        self.assertEqual(len(res["evidence_hash"]), 64)

    def test_19_inference_engine_smoke_detection(self):
        res = fire_engine.analyze(
            zone_name="Warehouse Sector B Chemical Storage",
            simulate_flame=False,
            simulate_smoke=True
        )
        self.assertEqual(res["hazard_type"], "SMOKE_DETECTED")
        self.assertGreater(res["plume_expansion_rate"], 1.5)
        self.assertGreater(res["co_ppm"], 50.0)

    def test_20_inference_engine_dual_hazard(self):
        res = fire_engine.analyze(
            zone_name="Warehouse Sector B Chemical Storage",
            simulate_flame=True,
            simulate_smoke=True
        )
        self.assertEqual(res["hazard_type"], "DUAL_FIRE_SMOKE_HAZARD")
        self.assertEqual(res["severity_tier"], "TIER_3_CRITICAL")
        self.assertGreater(res["evacuation_urgency"], 75.0)

    def test_21_inference_engine_normal_condition(self):
        res = fire_engine.analyze(
            zone_name="Data Center Server Hall 3",
            simulate_flame=False,
            simulate_smoke=False
        )
        self.assertEqual(res["hazard_type"], "NORMAL")
        self.assertEqual(res["severity_tier"], "NONE")
        self.assertLess(res["flame_temp_c"], 60.0)

    # ─────────────────────────────────────────────────────────────────────────
    # REST API Endpoints
    # ─────────────────────────────────────────────────────────────────────────
    def test_22_api_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"].lower(), "healthy")
        self.assertEqual(data["port"], 5040)
        self.assertTrue("device" in data or "hardware_device" in data)

    def test_23_api_health_trailing_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"].lower(), "healthy")

    def test_24_api_zones_list(self):
        res = self.client.get("/api/incidents/zones")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        zones = data["zones"] if isinstance(data, dict) and "zones" in data else data
        self.assertIsInstance(zones, list)
        self.assertGreaterEqual(len(zones), 5)
        self.assertIn("zone_name", zones[0])

    def test_25_api_incidents_list(self):
        res = self.client.get("/api/incidents/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        incidents = data["incidents"] if isinstance(data, dict) and "incidents" in data else data
        self.assertIsInstance(incidents, list)
        self.assertGreaterEqual(len(incidents), 6)

    def test_26_api_audit_logs(self):
        res = self.client.get("/api/incidents/audit-logs")
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 2)
        self.assertEqual(logs[-1]["block_index"], 0)

    def test_27_api_stats(self):
        res = self.client.get("/api/incidents/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("total_scans", stats)
        self.assertIn("active_alarms", stats)
        self.assertIn("audit_blocks", stats)

    def test_28_api_analyze_incident(self):
        payload = {
            "zone_name": "Commercial Mall Kitchen",
            "simulate_flame": True,
            "simulate_smoke": False
        }
        res = self.client.post("/api/incidents/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["hazard_type"], "FLAME_DETECTED")
        self.assertIn("incident_id", data)
        self.assertIn("evidence_hash", data)

    def test_29_api_acknowledge_incident(self):
        list_res = self.client.get("/api/incidents/")
        data = list_res.json()
        incidents = data["incidents"] if isinstance(data, dict) and "incidents" in data else data
        target_id = incidents[0]["incident_id"]
        res = self.client.post(f"/api/incidents/acknowledge/{target_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["dispatch_status"], "ACKNOWLEDGED")

    def test_30_api_dispatch_suppression(self):
        list_res = self.client.get("/api/incidents/")
        data = list_res.json()
        incidents = data["incidents"] if isinstance(data, dict) and "incidents" in data else data
        target_id = incidents[-1]["incident_id"]
        res = self.client.post(f"/api/incidents/dispatch-suppression/{target_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["dispatch_status"], "SUPPRESSED")

if __name__ == "__main__":
    unittest.main()
