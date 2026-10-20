import unittest
import os
import sys
import csv
import json
import hashlib
import torch
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal, engine, compute_block_hash, append_audit_block
from backend.app.db.models import Student, AttendanceRecord, AuditLedger
from backend.app.ml.antispoof_arcface_model import DeepAntiSpoofFaceNet
from backend.app.ml.biometric_liveness_model import BiometricLivenessQualityRegressorNet
from backend.app.ml.inference_engine import attendance_engine

class TestProject42FaceAttendance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    # 1. DATABASE & WAL MODE
    def test_01_wal_mode_active(self):
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode;")).scalar()
            self.assertEqual(result.lower(), "wal", "Database must operate in Write-Ahead Logging (WAL) mode")

    def test_02_database_tables_exist(self):
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
            names = [t[0] for t in tables]
            self.assertIn("students", names)
            self.assertIn("attendance_records", names)
            self.assertIn("audit_ledger", names)

    # 2. CRYPTOGRAPHIC AUDIT LEDGER
    def test_03_audit_genesis_block(self):
        db = SessionLocal()
        try:
            genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
            self.assertIsNotNone(genesis, "Genesis block (index 0) must exist")
            self.assertEqual(genesis.action_type, "SYSTEM_INIT")
            self.assertEqual(genesis.previous_hash, "0" * 64)
            self.assertEqual(len(genesis.current_hash), 64)
        finally:
            db.close()

    def test_04_audit_ledger_hash_continuity(self):
        db = SessionLocal()
        try:
            blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
            self.assertGreaterEqual(len(blocks), 2)
            for i in range(1, len(blocks)):
                prev = blocks[i-1]
                curr = blocks[i]
                self.assertEqual(curr.previous_hash, prev.current_hash, f"Hash break at block {curr.block_index}")
                recomputed = compute_block_hash(curr.action_type, curr.details, curr.timestamp, curr.previous_hash)
                self.assertEqual(curr.current_hash, recomputed, f"Invalid SHA-256 hash in block {curr.block_index}")
        finally:
            db.close()

    def test_05_audit_tamper_detection(self):
        db = SessionLocal()
        try:
            block = db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
            if block:
                tampered_details = block.details + " [MALICIOUS_MODIFICATION]"
                tampered_hash = compute_block_hash(block.action_type, tampered_details, block.timestamp, block.previous_hash)
                self.assertNotEqual(tampered_hash, block.current_hash, "Tampered details must produce mismatched hash")
        finally:
            db.close()

    # 3. ENROLLED STUDENTS & DATA
    def test_06_enrolled_students_roster(self):
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            self.assertGreaterEqual(len(students), 5)
            sids = [s.student_id for s in students]
            self.assertIn("STU-101", sids)
            self.assertIn("STU-102", sids)
            self.assertIn("STU-103", sids)
        finally:
            db.close()

    def test_07_telemetry_dataset_file(self):
        csv_file = settings.DATASET_PATH
        self.assertTrue(os.path.isfile(csv_file), f"Dataset must exist at {csv_file}")
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 6000, "Dataset must contain exactly 6,000 physical telemetry records")
            first = rows[0]
            self.assertIn("record_id", first)
            self.assertIn("student_id", first)
            self.assertIn("spoof_risk_pct", first)
            self.assertIn("micro_tremor_score", first)
            self.assertIn("illumination_entropy", first)

    def test_08_scalers_and_metadata_files(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH), "face_scalers.json must exist")
        self.assertTrue(os.path.isfile(settings.METADATA_PATH), "model_metadata.json must exist")
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
            self.assertEqual(meta["dataset_records"], 6000)
            self.assertEqual(meta["status"], "TRAINED_SERIALIZED")

    # 4. PYTORCH NEURAL MODELS
    def test_09_arcface_model_weights_and_shape(self):
        self.assertTrue(os.path.isfile(settings.MODEL_WEIGHTS_PATH), "phase2_model.pt must exist")
        model = DeepAntiSpoofFaceNet()
        weights = torch.load(settings.MODEL_WEIGHTS_PATH, map_location="cpu")
        model.load_state_dict(weights)
        model.eval()

        dummy = torch.randn(2, 3, 64, 64)
        with torch.no_grad():
            emb, logits = model(dummy)
            self.assertEqual(emb.shape, (2, 512), "ArcFace embedding must be 512-D")
            self.assertEqual(logits.shape, (2, 2), "Anti-spoof logits must be binary (batch, 2)")

    def test_10_regressor_model_weights_and_heads(self):
        self.assertTrue(os.path.isfile(settings.REGRESSOR_WEIGHTS_PATH), "biometric_liveness_regressor_weights.pt must exist")
        reg = BiometricLivenessQualityRegressorNet(in_features=10)
        weights = torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location="cpu")
        reg.load_state_dict(weights)
        reg.eval()

        dummy_x = torch.randn(3, 10)
        with torch.no_grad():
            p_risk, p_tremor, p_ent, p_match = reg(dummy_x)
            self.assertEqual(p_risk.shape, (3, 1))
            self.assertEqual(p_tremor.shape, (3, 1))
            self.assertEqual(p_ent.shape, (3, 1))
            self.assertEqual(p_match.shape, (3, 1))
            self.assertTrue(torch.all(p_risk >= 0.0) and torch.all(p_risk <= 100.0))
            self.assertTrue(torch.all(p_tremor >= 0.0) and torch.all(p_tremor <= 1.0))

    # 5. INFERENCE ENGINE
    def test_11_inference_genuine_face(self):
        res = attendance_engine.verify_face(student_idx=0, is_spoof_attack=False)
        self.assertEqual(res["student_id"], "STU-101")
        self.assertEqual(res["full_name"], "Alex Chen")
        self.assertEqual(res["liveness_status"], "REAL")
        self.assertEqual(res["status"], "PRESENT")
        self.assertLess(res["spoof_risk_pct"], 50.0)
        self.assertGreater(res["micro_tremor_score"], 0.5)
        self.assertIn("evidence_hash", res)
        self.assertEqual(len(res["evidence_hash"]), 64)

    def test_12_inference_print_attack_blocked(self):
        res = attendance_engine.verify_face(student_idx=1, is_spoof_attack=True, attack_type="PRINT_ATTACK_2D")
        self.assertEqual(res["student_id"], "STU-102")
        self.assertEqual(res["liveness_status"], "SPOOF_DETECTED")
        self.assertEqual(res["status"], "REJECTED_SPOOF")
        self.assertGreater(res["spoof_risk_pct"], 50.0)
        self.assertLess(res["micro_tremor_score"], 0.4)

    def test_13_inference_screen_replay_attack_blocked(self):
        res = attendance_engine.verify_face(student_idx=2, is_spoof_attack=True, attack_type="SCREEN_REPLAY_ATTACK")
        self.assertEqual(res["student_id"], "STU-103")
        self.assertEqual(res["liveness_status"], "SPOOF_DETECTED")
        self.assertEqual(res["status"], "REJECTED_SPOOF")

    def test_14_inference_silicone_mask_attack_blocked(self):
        res = attendance_engine.verify_face(student_idx=3, is_spoof_attack=True, attack_type="SILICONE_3D_MASK")
        self.assertEqual(res["student_id"], "STU-104")
        self.assertEqual(res["liveness_status"], "SPOOF_DETECTED")
        self.assertEqual(res["status"], "REJECTED_SPOOF")

    # 6. REST API ENDPOINTS
    def test_15_api_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5042)
        self.assertTrue(data["database_wal_active"])

    def test_16_api_students_roster(self):
        res = self.client.get("/api/attendance/students")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 5)
        self.assertIsInstance(data["students"], list)

    def test_17_api_logs(self):
        res = self.client.get("/api/attendance/logs?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("records", data)
        self.assertGreaterEqual(data["count"], 1)

    def test_18_api_audit_logs(self):
        res = self.client.get("/api/attendance/audit-logs?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ledger", data)
        self.assertGreaterEqual(data["count"], 1)

    def test_19_api_stats(self):
        res = self.client.get("/api/attendance/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_records", data)
        self.assertIn("present_count", data)
        self.assertIn("spoof_attacks_blocked", data)

    def test_20_api_verify_genuine(self):
        payload = {
            "student_index": 0,
            "simulate_spoof_attack": False,
            "course_code": "CS-401",
            "classroom_id": "HALL-A1"
        }
        res = self.client.post("/api/attendance/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["status"], "PRESENT")
        self.assertEqual(data["record"]["student_id"], "STU-101")
        self.assertEqual(len(data["record"]["evidence_hash"]), 64)

    def test_21_api_verify_spoof(self):
        payload = {
            "student_index": 4,
            "simulate_spoof_attack": True,
            "attack_type": "SCREEN_REPLAY_ATTACK",
            "course_code": "CYB-408",
            "classroom_id": "HALL-C3"
        }
        res = self.client.post("/api/attendance/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["status"], "REJECTED_SPOOF")
        self.assertEqual(data["record"]["attack_type"], "SCREEN_REPLAY_ATTACK")

    def test_22_api_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_attendance_scans", data)
        self.assertIn("model_performance", data)

    def test_23_root_index_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("PROJECT 42", res.text)
        self.assertIn("PORT: 5042", res.text)

    def test_24_evidence_hash_uniqueness(self):
        res1 = attendance_engine.verify_face(student_idx=0, is_spoof_attack=False)
        res2 = attendance_engine.verify_face(student_idx=1, is_spoof_attack=False)
        self.assertNotEqual(res1["evidence_hash"], res2["evidence_hash"])

    def test_25_model_latency_benchmark(self):
        res = attendance_engine.verify_face(student_idx=0, is_spoof_attack=False)
        self.assertLess(res["latency_ms"], 100.0, "Verification latency must be under 100ms for edge turnstile operation")

    def test_26_student_index_wrapping(self):
        res = attendance_engine.verify_face(student_idx=10, is_spoof_attack=False)
        self.assertEqual(res["student_id"], "STU-101", "Student index 10 modulo 5 must map to STU-101")

    def test_27_custom_course_and_hall(self):
        res = attendance_engine.verify_face(student_idx=1, is_spoof_attack=False, course_code="AI-999")
        self.assertEqual(res["course_code"], "AI-999")

    def test_28_arcface_embedding_norm(self):
        res = attendance_engine.verify_face(student_idx=0, is_spoof_attack=False)
        self.assertAlmostEqual(res["embedding_norm"], 1.0, places=2, msg="ArcFace embeddings must be normalized to unit hypersphere")

    def test_29_genesis_block_tamper_fails(self):
        db = SessionLocal()
        try:
            genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
            if genesis:
                tampered = compute_block_hash("MALICIOUS_GENESIS", genesis.details, genesis.timestamp, genesis.previous_hash)
                self.assertNotEqual(tampered, genesis.current_hash)
        finally:
            db.close()

    def test_30_regressor_batch_inference(self):
        reg = BiometricLivenessQualityRegressorNet(in_features=10)
        weights = torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location="cpu")
        reg.load_state_dict(weights)
        reg.eval()
        batch_input = torch.randn(16, 10)
        with torch.no_grad():
            r, t, e, m = reg(batch_input)
            self.assertEqual(r.shape, (16, 1))
            self.assertEqual(t.shape, (16, 1))

if __name__ == "__main__":
    unittest.main()
