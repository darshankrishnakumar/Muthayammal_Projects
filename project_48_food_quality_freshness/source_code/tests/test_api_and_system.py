import os
import sys
import json
import sqlite3
import hashlib
import unittest
import torch
import pandas as pd
from fastapi.testclient import TestClient

# Path resolution
SOURCE_CODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SOURCE_CODE_DIR)

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal, compute_block_hash
from backend.app.db.models import FoodBatch, FreshnessAssessment, AuditLedger
from backend.app.ml.spectral_freshness_model import SpectralFreshnessCNN
from backend.app.ml.regressor_model import ShelfLifeForecastRegressorNet
from backend.app.ml.inference_engine import freshness_engine

class TestProject048ComprehensiveSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    def test_01_static_deliverables_exist(self):
        root = os.path.abspath(os.path.join(SOURCE_CODE_DIR, ".."))
        self.assertTrue(os.path.isfile(os.path.join(root, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(root, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(root, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")
        self.assertTrue(os.path.isfile(os.path.join(root, "walkthrough", "walkthrough_timestamps.md")), "walkthrough_timestamps.md must exist")

    def test_02_system_health_endpoint(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["project_id"], "PROJECT-048")
        self.assertEqual(data["port"], 5048)
        self.assertTrue(data["database_wal_mode"])
        self.assertIn("models", data)
        self.assertEqual(data["models"]["cnn_parameters"], 20869)
        self.assertEqual(data["models"]["regressor_parameters"], 18052)

    def test_03_sqlite_wal_mode_active(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal", "SQLite database must operate in Write-Ahead Logging (WAL) mode")

    def test_04_genesis_block_integrity(self):
        db = SessionLocal()
        try:
            genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
            self.assertIsNotNone(genesis, "Genesis block #0 must be seeded")
            self.assertEqual(genesis.previous_hash, "0" * 64, "Genesis previous hash must be 64 zeros")
            self.assertEqual(genesis.event_type, "GENESIS_SEED")
            self.assertEqual(len(genesis.block_hash), 64, "Genesis block hash must be 64-char SHA-256")
            self.assertEqual(len(genesis.evidence_hash), 64, "Genesis evidence hash must be 64-char SHA-256")
        finally:
            db.close()

    def test_05_audit_hash_chain_continuity(self):
        db = SessionLocal()
        try:
            blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
            self.assertGreaterEqual(len(blocks), 5, "Must have at least 5 audit ledger blocks seeded")
            for i in range(1, len(blocks)):
                curr = blocks[i]
                prev = blocks[i - 1]
                self.assertEqual(curr.previous_hash, prev.block_hash, f"Block #{curr.block_index} previous_hash mismatch with Block #{prev.block_index}")
        finally:
            db.close()

    def test_06_audit_tamper_detection(self):
        # Tamper test: simulate altered block data and assert mismatch
        test_index = 999
        test_prev = "a" * 64
        test_time = "2026-10-21T01:00:00"
        test_event = "QUALITY_EVALUATION"
        valid_details = json.dumps({"test": "valid"})
        tampered_details = json.dumps({"test": "tampered"})
        evidence = hashlib.sha256(b"tamper_proof_test").hexdigest()
        
        valid_hash = compute_block_hash(test_index, test_prev, test_time, test_event, valid_details, evidence)
        tampered_hash = compute_block_hash(test_index, test_prev, test_time, test_event, tampered_details, evidence)
        self.assertNotEqual(valid_hash, tampered_hash, "Tampered details must yield divergent SHA-256 block hash")

    def test_07_batches_list_api(self):
        res = self.client.get("/api/freshness/batches")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("batches", data)
        self.assertGreaterEqual(len(data["batches"]), 4)
        first = data["batches"][0]
        self.assertIn("batch_id", first)
        self.assertIn("freshness_score", first)
        self.assertIn("remaining_shelf_life_days", first)
        self.assertIn("deterioration_stage", first)

    def test_08_records_alias_api(self):
        res = self.client.get("/api/freshness/records")
        self.assertEqual(res.status_code, 200)
        self.assertIn("records", res.json())
        res_food = self.client.get("/api/food/records")
        self.assertEqual(res_food.status_code, 200)
        self.assertIn("records", res_food.json())

    def test_09_assessments_list_api(self):
        res = self.client.get("/api/freshness/assessments")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("assessments", data)
        self.assertGreaterEqual(len(data["assessments"]), 4)
        first = data["assessments"][0]
        self.assertIn("evidence_hash", first)
        self.assertEqual(len(first["evidence_hash"]), 64)

    def test_10_audit_logs_api(self):
        res = self.client.get("/api/freshness/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["chain_verified"], "Cryptographic chain must be verified")
        self.assertFalse(data["tamper_detected"], "No tampering should be detected")
        self.assertGreaterEqual(data["total_blocks"], 5)

    def test_11_analytics_summary_api(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_scans", data)
        self.assertIn("average_freshness_index", data)
        self.assertIn("model_performance", data)
        self.assertEqual(data["model_performance"]["freshness_mae"], 1.24)
        self.assertEqual(data["model_performance"]["shelf_life_r2"], 0.978)

    def test_12_stats_api(self):
        res = self.client.get("/api/freshness/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_batches", data)
        self.assertIn("mean_freshness_index", data)
        self.assertIn("stage_breakdown", data)

    def test_13_evaluate_fresh_batch_pipeline(self):
        res = self.client.post("/api/freshness/evaluate", json={
            "product_name": "Organic Prime Ribeye",
            "food_category": "MEAT_POULTRY",
            "simulate_spoilage": False,
            "storage_temp_c": 2.8,
            "relative_humidity_pct": 84.0,
            "browning_index": 1.1,
            "tvbn_mg_per_100g": 7.5
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        m = data["metrics"]
        self.assertGreaterEqual(m["freshness_score"], 70.0)
        self.assertEqual(m["deterioration_stage"], "STAGE_1_FRESH")
        self.assertGreater(m["remaining_shelf_life_days"], 2.0)
        self.assertEqual(len(m["evidence_hash"]), 64)

    def test_14_evaluate_spoiled_batch_pipeline(self):
        res = self.client.post("/api/freshness/evaluate", json={
            "product_name": "Artisan Sourdough Loaves",
            "food_category": "BAKERY",
            "simulate_spoilage": True,
            "storage_temp_c": 14.2,
            "browning_index": 22.0,
            "tvbn_mg_per_100g": 38.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertLess(m["freshness_score"], 50.0)
        self.assertEqual(m["deterioration_stage"], "STAGE_3_DETERIORATED")
        self.assertEqual(m["recommendation"], "DISCARD_COMPOSTING")

    def test_15_food_inspect_alias_endpoint(self):
        res = self.client.post("/api/food/inspect", json={
            "food_name": "Fresh Atlantic Salmon",
            "simulated_spoilage": "fresh"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("freshness_score", data)
        self.assertIn("safety_status", data)
        self.assertIn("remaining_shelf_life_days", data)

    def test_16_cnn_forward_shapes(self):
        net = SpectralFreshnessCNN()
        dummy_in = torch.randn(3, 3, 64, 64)
        score, shelf, stage = net(dummy_in)
        self.assertEqual(score.shape, (3, 1))
        self.assertEqual(shelf.shape, (3, 1))
        self.assertEqual(stage.shape, (3, 3))

    def test_17_regressor_forward_shapes(self):
        net = ShelfLifeForecastRegressorNet(input_dim=10, hidden_dim=64)
        dummy_in = torch.randn(5, 10)
        out = net(dummy_in)
        self.assertEqual(out.shape, (5, 4))
        self.assertTrue(torch.all(out[:, 0] >= 0.0), "Shelf life days must be non-negative")
        self.assertTrue(torch.all((out[:, 1:] >= 0.0) & (out[:, 1:] <= 100.0)), "Percentages must be within [0, 100]")

    def test_18_real_telemetry_dataset_integrity(self):
        csv_path = settings.DATASET_PATH
        self.assertTrue(os.path.isfile(csv_path), f"Telemetry CSV must exist at {csv_path}")
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 6000, "Dataset must contain exactly 6,000 physical telemetry records")
        required_cols = [
            "sample_id", "food_category", "product_name", "storage_temp_c",
            "relative_humidity_pct", "storage_duration_hours", "browning_index",
            "tvbn_mg_per_100g", "ph_level", "ethylene_concentration_ppm",
            "moisture_content_pct", "bacterial_log_cfu_g", "reflectance_ratio_650_850",
            "freshness_score", "deterioration_stage", "remaining_shelf_life_days",
            "spoilage_risk_pct", "microbial_risk_pct", "cold_chain_compliance_score"
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required telemetry column: {col}")
        self.assertEqual(df.isnull().sum().sum(), 0, "Telemetry CSV must have zero null values")
        self.assertTrue(df["storage_temp_c"].between(-2.0, 16.0).all())
        self.assertTrue(df["freshness_score"].between(0.0, 100.0).all())

    def test_19_serialized_model_weights_on_disk(self):
        self.assertTrue(os.path.isfile(settings.CNN_MODEL_WEIGHTS_PATH), "CNN weights must exist on disk")
        self.assertTrue(os.path.isfile(settings.REGRESSOR_WEIGHTS_PATH), "Regressor weights must exist on disk")
        cnn_sd = torch.load(settings.CNN_MODEL_WEIGHTS_PATH, map_location="cpu")
        self.assertIn("freshness_head.weight", cnn_sd)
        reg_sd = torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location="cpu")
        self.assertIn("out_shelf_life.weight", reg_sd)

    def test_20_scalers_and_metadata_files(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH), "Scalers JSON must exist")
        self.assertTrue(os.path.isfile(settings.METADATA_PATH), "Metadata JSON must exist")
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta["project"], "PROJECT-048")
        self.assertEqual(meta["port"], 5048)
        self.assertIn("cnn_model", meta)
        self.assertIn("regressor_model", meta)

    def test_21_evidence_hashes_deterministic_and_unique(self):
        db = SessionLocal()
        try:
            hashes = [a.evidence_hash for a in db.query(FreshnessAssessment.evidence_hash).all()]
            self.assertEqual(len(hashes), len(set(hashes)), "Assessment evidence hashes must be unique")
        finally:
            db.close()

    def test_22_frontend_index_file_valid(self):
        frontend_path = os.path.join(SOURCE_CODE_DIR, "frontend/index.html")
        self.assertTrue(os.path.isfile(frontend_path), "Frontend index.html must exist")
        with open(frontend_path, "r") as f:
            html = f.read()
        self.assertIn("5048", html, "Frontend must reference Port 5048")
        self.assertIn("specChart", html, "Frontend must include spectral canvas")
        self.assertIn("records-body", html, "Frontend must include records table")
        self.assertIn("audit-body", html, "Frontend must include audit ledger table")

    def test_23_category_distribution(self):
        df = pd.read_csv(settings.DATASET_PATH)
        categories = set(df["food_category"].unique())
        expected = {"MEAT_POULTRY", "FRESH_PRODUCE", "DAIRY", "BAKERY"}
        self.assertTrue(expected.issubset(categories), f"Expected categories {expected}, got {categories}")

    def test_24_microbial_decay_correlation(self):
        df = pd.read_csv(settings.DATASET_PATH)
        corr = df["bacterial_log_cfu_g"].corr(df["spoilage_risk_pct"])
        self.assertGreater(corr, 0.70, "Bacterial count must strongly correlate with spoilage risk (> 0.70)")

    def test_25_cold_chain_compliance_range(self):
        df = pd.read_csv(settings.DATASET_PATH)
        self.assertTrue(df["cold_chain_compliance_score"].between(0.0, 100.0).all())

    def test_26_arrhenius_temperature_effect(self):
        df = pd.read_csv(settings.DATASET_PATH)
        cold_shelf = df[df["storage_temp_c"] <= 4.0]["remaining_shelf_life_days"].mean()
        warm_shelf = df[df["storage_temp_c"] >= 10.0]["remaining_shelf_life_days"].mean()
        self.assertGreater(cold_shelf, warm_shelf, "Cold stored food must exhibit greater shelf life than warm stored food")

    def test_27_audit_block_hash_recomputation(self):
        db = SessionLocal()
        try:
            b1 = db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
            self.assertIsNotNone(b1)
            recomputed = compute_block_hash(
                b1.block_index,
                b1.previous_hash,
                b1.timestamp.isoformat(),
                b1.event_type,
                b1.details_json,
                b1.evidence_hash
            )
            self.assertEqual(recomputed, b1.block_hash, "Block #1 hash must match cryptographic recomputation")
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
