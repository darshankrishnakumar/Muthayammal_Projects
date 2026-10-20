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
from backend.app.db.models import FruitItem, SortingLane, AuditLedger
from backend.app.ml.multitask_fruit_model import MultiTaskFruitNet
from backend.app.ml.fruit_freshness_model import FruitFreshnessShelfLifeRegressorNet
from backend.app.ml.inference_engine import fruit_engine, VARIETIES, GRADES, DEFECTS

class TestP41FruitQualitySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "fruit_grading.db"))
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "fruit_quality_telemetry_6000.csv"))

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
        self.assertIn("fruit_items", tables)
        self.assertIn("sorting_lanes", tables)
        self.assertIn("audit_ledger", tables)

    def test_04_sorting_lanes_count(self):
        db = SessionLocal()
        count = db.query(SortingLane).count()
        db.close()
        self.assertGreaterEqual(count, 4)

    def test_05_initial_fruit_records(self):
        db = SessionLocal()
        count = db.query(FruitItem).count()
        db.close()
        self.assertGreaterEqual(count, 8)

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
            "record_id", "batch_lot", "conveyor_lane", "fruit_variety", "variety_id",
            "quality_grade", "grade_id", "defect_type", "defect_id", "sorting_chute",
            "weight_grams", "diameter_mm", "mean_chroma_r", "mean_chroma_g", "mean_chroma_b",
            "surface_defect_ratio", "skin_reflectance_index", "harvest_days_elapsed",
            "cold_storage_temp_c", "storage_humidity_pct", "firmness_n", "sugar_brix",
            "shelf_life_days", "batch_economic_index"
        ]
        for col in expected_cols:
            self.assertIn(col, header, f"Expected column {col} missing from CSV header")

    def test_12_dataset_variety_balance(self):
        with open(self.csv_path, "r", encoding="utf-8") as f:
            rows = [l.strip().split(",") for l in f][1:]
        var_counts = {}
        for r in rows:
            v = r[3]
            var_counts[v] = var_counts.get(v, 0) + 1
        for var_name in ["APPLE", "ORANGE", "BANANA", "MANGO"]:
            self.assertEqual(var_counts.get(var_name), 1500, f"Variety {var_name} should have 1,500 samples")

    # ─────────────────────────────────────────────────────────────────────────
    # PyTorch Model Architecture & Weight Serialization
    # ─────────────────────────────────────────────────────────────────────────
    def test_13_multitask_cnn_weights_exist(self):
        phase2_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments", "phase2_model.pt"))
        self.assertTrue(os.path.exists(phase2_path), f"Phase 2 weights must exist at {phase2_path}")
        self.assertGreater(os.path.getsize(phase2_path), 300000)

    def test_14_freshness_regressor_weights_exist(self):
        reg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models", "fruit_freshness_regressor_weights.pt"))
        self.assertTrue(os.path.exists(reg_path), f"Freshness regressor weights must exist at {reg_path}")
        self.assertGreater(os.path.getsize(reg_path), 50000)

    def test_15_multitask_cnn_forward_shape(self):
        model = MultiTaskFruitNet(num_varieties=4, num_grades=3, num_defects=5)
        x = torch.randn(2, 3, 64, 64)
        v_out, g_out, d_out = model(x)
        self.assertEqual(v_out.shape, (2, 4))
        self.assertEqual(g_out.shape, (2, 3))
        self.assertEqual(d_out.shape, (2, 5))

    def test_16_freshness_regressor_forward_shape(self):
        model = FruitFreshnessShelfLifeRegressorNet(in_features=10)
        x = torch.randn(4, 10)
        p_firm, p_brix, p_shelf, p_econ = model(x)
        self.assertEqual(p_firm.shape, (4, 1))
        self.assertEqual(p_brix.shape, (4, 1))
        self.assertEqual(p_shelf.shape, (4, 1))
        self.assertEqual(p_econ.shape, (4, 1))

    def test_17_model_metadata_valid(self):
        meta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models", "model_metadata.json"))
        self.assertTrue(os.path.exists(meta_path))
        with open(meta_path, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta.get("status"), "TRAINED_SERIALIZED")
        self.assertEqual(meta.get("dataset_records"), 6000)
        self.assertIn("multitask_cnn", meta)
        self.assertIn("freshness_regressor", meta)

    # ─────────────────────────────────────────────────────────────────────────
    # Inference Engine & Physics Bounds
    # ─────────────────────────────────────────────────────────────────────────
    def test_18_inference_engine_grade_a_export(self):
        res = fruit_engine.analyze(
            conveyor_lane=1,
            variety="APPLE",
            simulate_defect="NONE"
        )
        self.assertEqual(res["grade"], "GRADE_A_PREMIUM")
        self.assertEqual(res["sorting_chute"], "BIN_1_EXPORT")
        self.assertGreaterEqual(res["firmness_n"], 50.0)
        self.assertGreaterEqual(res["sugar_brix"], 12.0)
        self.assertIn("evidence_hash", res)
        self.assertEqual(len(res["evidence_hash"]), 64)

    def test_19_inference_engine_grade_c_reject(self):
        res = fruit_engine.analyze(
            conveyor_lane=2,
            variety="ORANGE",
            simulate_defect="SKIN_ROT"
        )
        self.assertEqual(res["grade"], "GRADE_C_REJECT")
        self.assertEqual(res["sorting_chute"], "BIN_3_DISCARD")
        self.assertEqual(res["defect"], "SKIN_ROT")
        self.assertLessEqual(res["shelf_life_days"], 5.0)

    def test_20_inference_engine_banana_varieties(self):
        res = fruit_engine.analyze(
            conveyor_lane=3,
            variety="BANANA",
            simulate_defect="NONE"
        )
        self.assertEqual(res["variety"], "BANANA")
        self.assertIn(res["grade"], GRADES)

    def test_21_inference_engine_mango_quality(self):
        res = fruit_engine.analyze(
            conveyor_lane=4,
            variety="MANGO",
            simulate_defect="NONE"
        )
        self.assertEqual(res["variety"], "MANGO")
        self.assertGreaterEqual(res["weight_grams"], 200.0)

    # ─────────────────────────────────────────────────────────────────────────
    # REST API Endpoints
    # ─────────────────────────────────────────────────────────────────────────
    def test_22_api_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"].lower(), "healthy")
        self.assertEqual(data["port"], 5041)
        self.assertTrue("device" in data or "hardware_device" in data)

    def test_23_api_health_trailing_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"].lower(), "healthy")

    def test_24_api_lanes_list(self):
        res = self.client.get("/api/grading/lanes")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        lanes = data["lanes"] if isinstance(data, dict) and "lanes" in data else data
        self.assertIsInstance(lanes, list)
        self.assertGreaterEqual(len(lanes), 4)

    def test_25_api_items_list(self):
        res = self.client.get("/api/grading/items")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        items = data["items"] if isinstance(data, dict) and "items" in data else data
        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 8)

    def test_26_api_audit_logs(self):
        res = self.client.get("/api/grading/audit-logs")
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 2)
        self.assertEqual(logs[-1]["block_index"], 0)

    def test_27_api_stats(self):
        res = self.client.get("/api/grading/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("total_graded", stats)
        self.assertIn("export_grade_a", stats)
        self.assertIn("audit_blocks_sealed", stats)

    def test_28_api_inspect_fruit(self):
        payload = {
            "conveyor_lane": 1,
            "variety": "APPLE",
            "defect_sim": "NONE"
        }
        res = self.client.post("/api/grading/inspect", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("item", data)
        self.assertIn("metrics", data)
        self.assertEqual(data["metrics"]["grade"], "GRADE_A_PREMIUM")

    def test_29_api_chute_override(self):
        list_res = self.client.get("/api/grading/items")
        data = list_res.json()
        items = data["items"] if isinstance(data, dict) and "items" in data else data
        target_id = items[0]["item_id"]
        res = self.client.post(f"/api/grading/chute-override/{target_id}?chute=BIN_2_DOMESTIC")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["sorting_chute"], "BIN_2_DOMESTIC")

    def test_30_api_defect_classification_contract(self):
        payload = {
            "conveyor_lane": 2,
            "variety": "ORANGE",
            "defect_sim": "BRUISE"
        }
        res = self.client.post("/api/grading/inspect", json=payload)
        self.assertEqual(res.status_code, 200)
        metrics = res.json()["metrics"]
        self.assertEqual(metrics["defect"], "BRUISE")

if __name__ == "__main__":
    unittest.main()
