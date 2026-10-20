import unittest
import os
import sys
import torch
import numpy as np
import sqlite3
import hashlib

# Ensure source_code is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal, compute_block_hash
from backend.app.db.models import TranslationLog, GestureVocabulary, AuditLedger
from backend.app.ml.temporal_sign_model import BiLSTMSignAttentionNet
from backend.app.ml.prosody_model import SpeechProsodyAcousticRegressorNet
from backend.app.ml.inference_engine import sign_engine, VOCAB_LIST, SENTENCE_MAP

class TestP39SignLanguageSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sign_speech.db"))

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
        self.assertIn("translation_logs", tables)
        self.assertIn("vocabulary", tables)
        self.assertIn("audit_ledger", tables)

    def test_04_vocabulary_has_ten_classes(self):
        db = SessionLocal()
        count = db.query(GestureVocabulary).count()
        db.close()
        self.assertGreaterEqual(count, 10)

    # ─────────────────────────────────────────────────────────────────────────
    # Cryptographic Audit Ledger & Chain of Custody
    # ─────────────────────────────────────────────────────────────────────────
    def test_05_audit_ledger_genesis_block(self):
        db = SessionLocal()
        genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        db.close()
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.previous_hash, "0" * 64)
        self.assertEqual(len(genesis.current_hash), 64)

    def test_06_audit_ledger_hash_continuity(self):
        db = SessionLocal()
        blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
        db.close()
        self.assertGreaterEqual(len(blocks), 2)
        for i in range(1, len(blocks)):
            self.assertEqual(blocks[i].previous_hash, blocks[i-1].current_hash,
                             f"Chain broken between block {i-1} and {i}")
            expected = compute_block_hash(
                blocks[i].action_type,
                blocks[i].details,
                blocks[i].timestamp,
                blocks[i].previous_hash
            )
            self.assertEqual(blocks[i].current_hash, expected)

    def test_07_tamper_detection(self):
        db = SessionLocal()
        block = db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
        db.close()
        if block:
            tampered_hash = compute_block_hash(
                block.action_type,
                "TAMPERED_MALICIOUS_RECORD",
                block.timestamp,
                block.previous_hash
            )
            self.assertNotEqual(tampered_hash, block.current_hash, "Tampered details must alter the SHA-256 hash")

    # ─────────────────────────────────────────────────────────────────────────
    # PyTorch Deep Learning Invariance Tests
    # ─────────────────────────────────────────────────────────────────────────
    def test_08_bilstm_model_instantiation(self):
        model = BiLSTMSignAttentionNet(in_features=54, hidden_dim=128, num_classes=10)
        self.assertEqual(sum(p.numel() for p in model.parameters()), 700107)

    def test_09_bilstm_forward_pass_dimensions(self):
        dummy_in = torch.randn(2, 30, 54).to(sign_engine.device)
        logits, attn = sign_engine.model(dummy_in)
        self.assertEqual(logits.shape, (2, 10))
        self.assertEqual(attn.shape, (2, 30, 1))

    def test_10_bilstm_attention_normalization(self):
        dummy_in = torch.randn(1, 30, 54).to(sign_engine.device)
        _, attn = sign_engine.model(dummy_in)
        attn_sum = float(torch.sum(attn).item())
        self.assertAlmostEqual(attn_sum, 1.0, places=4)

    def test_11_prosody_regressor_forward_pass(self):
        dummy_kin = torch.randn(2, 10).to(sign_engine.device)
        pitch, dur, energy, qual = sign_engine.prosody_model(dummy_kin)
        self.assertEqual(pitch.shape, (2, 1))
        self.assertEqual(dur.shape, (2, 1))
        self.assertEqual(energy.shape, (2, 1))
        self.assertEqual(qual.shape, (2, 1))

    def test_12_prosody_physical_bounds(self):
        dummy_kin = torch.randn(5, 10).to(sign_engine.device)
        pitch, dur, energy, qual = sign_engine.prosody_model(dummy_kin)
        for i in range(5):
            p = float(pitch[i].item())
            d = float(dur[i].item())
            e = float(energy[i].item())
            q = float(qual[i].item())
            self.assertTrue(80.0 <= p <= 280.0, f"Pitch {p} out of bounds")
            self.assertTrue(0.4 <= d <= 3.0, f"Duration {d} out of bounds")
            self.assertTrue(40.0 <= e <= 85.0, f"Energy {e} out of bounds")
            self.assertTrue(0.0 <= q <= 100.0, f"Quality {q} out of bounds")

    # ─────────────────────────────────────────────────────────────────────────
    # Benchmark Dataset Quality
    # ─────────────────────────────────────────────────────────────────────────
    def test_13_dataset_file_exists(self):
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sign_language_telemetry_6000.csv"))
        self.assertTrue(os.path.exists(csv_path))

    def test_14_dataset_has_6000_records(self):
        import pandas as pd
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sign_language_telemetry_6000.csv"))
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 6000)

    def test_15_dataset_balanced_classes(self):
        import pandas as pd
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sign_language_telemetry_6000.csv"))
        df = pd.read_csv(csv_path)
        counts = df["gloss"].value_counts().to_dict()
        for gloss in VOCAB_LIST:
            self.assertEqual(counts.get(gloss, 0), 600)

    # ─────────────────────────────────────────────────────────────────────────
    # REST API Contracts
    # ─────────────────────────────────────────────────────────────────────────
    def test_16_health_endpoint_trailing_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "HEALTHY")
        self.assertEqual(data.get("port"), 5039)

    def test_17_health_endpoint_no_slash(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "HEALTHY")

    def test_18_predict_hello_gesture(self):
        res = self.client.post("/api/translation/predict", json={"gesture_index": 0})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gloss", data)
        self.assertIn("spoken_sentence", data)
        self.assertIn("confidence", data)
        self.assertIn("prosody", data)
        self.assertGreater(data["confidence"], 0.5)

    def test_19_predict_emergency_gesture(self):
        res = self.client.post("/api/translation/predict", json={"gesture_index": 4})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gloss", data)
        self.assertIn("prosody", data)

    def test_20_predict_doctor_gesture(self):
        res = self.client.post("/api/translation/predict", json={"gesture_index": 5})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gloss", data)

    def test_21_predict_water_gesture(self):
        res = self.client.post("/api/translation/predict", json={"gesture_index": 6})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gloss", data)

    def test_22_translation_logs_endpoint(self):
        res = self.client.get("/api/translation/logs?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("count", data)
        self.assertIn("logs", data)

    def test_23_translation_vocabulary_endpoint(self):
        res = self.client.get("/api/translation/vocabulary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 10)

    def test_24_translation_audit_logs_endpoint(self):
        res = self.client.get("/api/translation/audit-logs?limit=5")
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)
        self.assertIn("record_hash", logs[0])

    def test_25_analytics_summary_endpoint(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_translations", data)
        self.assertIn("model_performance", data)
        self.assertAlmostEqual(data["model_performance"]["top1_accuracy"], 0.966, places=2)

    def test_26_translation_stats_endpoint(self):
        res = self.client.get("/api/translation/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_translations", data)
        self.assertIn("vocabulary_count", data)

    def test_27_frontend_index_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("PROJECT 39: AI SIGN LANGUAGE TO SPEECH PLATFORM", res.text)
        self.assertIn("Port: 5039", res.text)

    def test_28_evidence_hash_reproducibility(self):
        gloss = "TEST_GLOSS"
        sentence = "Test Sentence"
        conf = 0.95
        pitch = 180.0
        dur = 1.0
        expected = hashlib.sha256(f"{gloss}|{sentence}|{conf}|{pitch}|{dur}".encode()).hexdigest()
        self.assertEqual(len(expected), 64)

    def test_29_session_id_propagation(self):
        custom_session = "SPECIAL-EMERGENCY-CALL-911"
        res = self.client.post("/api/translation/predict", json={"gesture_index": 4, "session_id": custom_session})
        self.assertEqual(res.status_code, 200)
        db = SessionLocal()
        log = db.query(TranslationLog).filter(TranslationLog.session_id == custom_session).first()
        db.close()
        self.assertIsNotNone(log)
        self.assertEqual(log.session_id, custom_session)

    def test_30_vocabulary_sentence_mapping_coverage(self):
        for gloss in VOCAB_LIST:
            self.assertIn(gloss, SENTENCE_MAP)
            self.assertGreater(len(SENTENCE_MAP[gloss]), 5)

if __name__ == "__main__":
    unittest.main()
