import unittest
import os
import sys
import json
import csv
import hashlib
import torch
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal, engine, compute_block_hash
from backend.app.db.models import ClassroomSession, EngagementSnapshot, AuditLedger
from backend.app.ml.inference_engine import classroom_engine
from backend.app.ml.multimodal_engagement_model import MultimodalEngagementNet
from backend.app.ml.regressor_model import AttentionForecastRegressorNet

class TestProject47SystemAndAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_database_wal_mode(self):
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode;")).scalar()
            self.assertEqual(result.lower(), "wal")

    def test_02_database_foreign_keys(self):
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys;")).scalar()
            self.assertEqual(result, 1)

    def test_03_classroom_sessions_count(self):
        count = self.db.query(ClassroomSession).count()
        self.assertGreaterEqual(count, 4)

    def test_04_classroom_sessions_content(self):
        cs = self.db.query(ClassroomSession).filter(ClassroomSession.course_code == "CS-301").first()
        self.assertIsNotNone(cs)
        self.assertEqual(cs.instructor_name, "Dr. Alan Turing")
        self.assertTrue(cs.is_active)

    def test_05_engagement_snapshots_seeded(self):
        count = self.db.query(EngagementSnapshot).count()
        self.assertGreaterEqual(count, 8)

    def test_06_engagement_snapshots_diversity(self):
        actions = self.db.query(EngagementSnapshot.pedagogical_recommendation).distinct().all()
        act_names = [a[0] for a in actions]
        self.assertIn("MAINTAIN_CURRENT_PACE", act_names)
        self.assertIn("ASK_CHECKPOINT_QUESTION", act_names)

    def test_07_audit_ledger_genesis_block(self):
        genesis = self.db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.action_type, "SYSTEM_INIT")
        self.assertEqual(genesis.previous_hash, "0" * 64)

    def test_08_audit_hash_chain_continuity(self):
        blocks = self.db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
        self.assertGreaterEqual(len(blocks), 2)
        for i in range(1, len(blocks)):
            prev = blocks[i - 1]
            curr = blocks[i]
            self.assertEqual(curr.previous_hash, prev.current_hash)
            expected_hash = compute_block_hash(curr.action_type, curr.details, curr.timestamp, curr.previous_hash)
            self.assertEqual(curr.current_hash, expected_hash)

    def test_09_audit_tamper_detection(self):
        first_block = self.db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
        if first_block:
            tampered_details = first_block.details + " [MALICIOUS ATTACK]"
            recalculated = compute_block_hash(
                first_block.action_type,
                tampered_details,
                first_block.timestamp,
                first_block.previous_hash
            )
            self.assertNotEqual(first_block.current_hash, recalculated)

    def test_10_evidence_hash_integrity(self):
        sample = self.db.query(EngagementSnapshot).first()
        self.assertIsNotNone(sample.evidence_hash)
        self.assertEqual(len(sample.evidence_hash), 64)

    def test_11_dataset_exists_and_row_count(self):
        self.assertTrue(os.path.exists(settings.DATASET_PATH))
        with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 6000)

    def test_12_dataset_columns(self):
        with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["snapshot_id", "course_code", "course_name", "student_count", "mean_engagement_score", "attentive_pct"]
            for h in expected:
                self.assertIn(h, headers)

    def test_13_model_metadata_validity(self):
        self.assertTrue(os.path.exists(settings.METADATA_PATH))
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
            self.assertEqual(meta["dataset_records"], 6000)
            self.assertIn("multimodal_engagement_net", meta["models"])
            self.assertIn("attention_forecast_regressor", meta["models"])

    def test_14_scalers_file_validity(self):
        self.assertTrue(os.path.exists(settings.SCALERS_PATH))
        with open(settings.SCALERS_PATH, "r") as f:
            scalers = json.load(f)
            self.assertEqual(len(scalers["mean"]), 10)
            self.assertEqual(len(scalers["std"]), 10)

    def test_15_multimodal_weights_exist(self):
        self.assertTrue(os.path.exists(settings.MODEL_WEIGHTS_PATH))

    def test_16_regressor_weights_exist(self):
        self.assertTrue(os.path.exists(settings.REGRESSOR_WEIGHTS_PATH))

    def test_17_multimodal_model_forward_pass(self):
        model = MultimodalEngagementNet()
        dummy_in = torch.randn(2, 12)
        score, logits = model(dummy_in)
        self.assertEqual(score.shape, (2, 1))
        self.assertEqual(logits.shape, (2, 4))

    def test_18_regressor_forward_pass(self):
        model = AttentionForecastRegressorNet(in_features=10)
        dummy_in = torch.randn(3, 10)
        att, drowsy, interv, part = model(dummy_in)
        self.assertEqual(att.shape, (3, 1))
        self.assertEqual(drowsy.shape, (3, 1))
        self.assertEqual(interv.shape, (3, 1))
        self.assertEqual(part.shape, (3, 1))

    def test_19_inference_high_focus_lecture(self):
        res = classroom_engine.evaluate_classroom(
            course_code="CS-301",
            student_count=32,
            attentive_pct=88.0,
            bored_pct=4.0,
            distracted_pct=5.0,
            drowsy_pct=3.0,
            head_pose_board_focus_pct=90.0,
            hand_raise_count=6
        )
        self.assertGreater(res["mean_engagement_score"], 70.0)
        self.assertEqual(res["pedagogical_recommendation"], "MAINTAIN_CURRENT_PACE")

    def test_20_inference_fatigue_intervention(self):
        res = classroom_engine.evaluate_classroom(
            course_code="AI-405",
            student_count=40,
            attentive_pct=25.0,
            bored_pct=35.0,
            distracted_pct=20.0,
            drowsy_pct=20.0,
            head_pose_board_focus_pct=30.0,
            hand_raise_count=0
        )
        self.assertLess(res["mean_engagement_score"], 50.0)
        self.assertEqual(res["pedagogical_recommendation"], "TAKE_2_MIN_REFRESHER_BREAK")

    def test_21_evidence_hash_determinism(self):
        res1 = classroom_engine.evaluate_classroom(course_code="CS-301", student_count=30, attentive_pct=80.0)
        res2 = classroom_engine.evaluate_classroom(course_code="CS-301", student_count=30, attentive_pct=80.0)
        self.assertEqual(res1["evidence_hash"], res2["evidence_hash"])

    def test_22_api_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5047)

    def test_23_api_health_trailing_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "HEALTHY")

    def test_24_api_sessions_endpoint(self):
        res = self.client.get("/api/engagement/sessions")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sessions", data)
        self.assertEqual(data["count"], 4)

    def test_25_api_timeline_endpoint(self):
        res = self.client.get("/api/engagement/timeline")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("snapshots", data)
        self.assertGreaterEqual(data["count"], 8)

    def test_26_api_audit_logs_endpoint(self):
        res = self.client.get("/api/engagement/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("audit_logs", data)
        self.assertGreaterEqual(data["count"], 2)

    def test_27_api_stats_endpoint(self):
        res = self.client.get("/api/engagement/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_monitored_snapshots", data)
        self.assertIn("mean_engagement_index", data)

    def test_28_api_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_lecture_snapshots", data)
        self.assertIn("action_distribution", data)

    def test_29_api_analyze_high_focus(self):
        payload = {
            "course_code": "CS-301",
            "lecture_title": "Distributed Systems: Consensus Protocols",
            "student_count": 32,
            "attentive_pct": 88.0,
            "bored_pct": 5.0,
            "distracted_pct": 5.0,
            "drowsy_pct": 2.0,
            "head_pose_board_focus_pct": 90.0,
            "hand_raise_count": 6
        }
        res = self.client.post("/api/engagement/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["snapshot"]["pedagogical_recommendation"], "MAINTAIN_CURRENT_PACE")

    def test_30_api_analyze_fatigue(self):
        payload = {
            "course_code": "AI-405",
            "lecture_title": "Backprop Through Time",
            "student_count": 40,
            "attentive_pct": 28.0,
            "bored_pct": 32.0,
            "distracted_pct": 22.0,
            "drowsy_pct": 18.0,
            "head_pose_board_focus_pct": 32.0,
            "hand_raise_count": 0
        }
        res = self.client.post("/api/engagement/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["snapshot"]["pedagogical_recommendation"], "TAKE_2_MIN_REFRESHER_BREAK")

    def test_31_audit_block_increments_on_analyze(self):
        pre_count = self.db.query(AuditLedger).count()
        payload = {
            "course_code": "MATH-210",
            "lecture_title": "Stokes Theorem",
            "student_count": 28,
            "attentive_pct": 75.0,
            "bored_pct": 10.0,
            "distracted_pct": 10.0,
            "drowsy_pct": 5.0,
            "head_pose_board_focus_pct": 80.0,
            "hand_raise_count": 3
        }
        res = self.client.post("/api/engagement/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        post_count = self.db.query(AuditLedger).count()
        self.assertEqual(post_count, pre_count + 1)

    def test_32_root_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))

if __name__ == "__main__":
    unittest.main()
