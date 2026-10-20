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
from backend.app.db.models import CareerRole, UpskillingRoadmap, AuditLedger
from backend.app.ml.inference_engine import career_engine, CareerTrajectoryForecastNet

class TestProject45SystemAndAPI(unittest.TestCase):
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

    def test_02_career_roles_count(self):
        count = self.db.query(CareerRole).count()
        self.assertGreaterEqual(count, 4)

    def test_03_roadmaps_seeded(self):
        count = self.db.query(UpskillingRoadmap).count()
        self.assertGreaterEqual(count, 8)

    def test_04_audit_ledger_genesis_block(self):
        genesis = self.db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.action_type, "SYSTEM_INIT")
        self.assertEqual(genesis.previous_hash, "0" * 64)

    def test_05_audit_hash_chain_continuity(self):
        blocks = self.db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
        self.assertGreaterEqual(len(blocks), 2)
        for i in range(1, len(blocks)):
            prev = blocks[i - 1]
            curr = blocks[i]
            self.assertEqual(curr.previous_hash, prev.current_hash)
            expected_hash = compute_block_hash(curr.action_type, curr.details, curr.timestamp, curr.previous_hash)
            self.assertEqual(curr.current_hash, expected_hash)

    def test_06_audit_tamper_detection(self):
        first_block = self.db.query(AuditLedger).filter(AuditLedger.block_index == 1).first()
        if first_block:
            tampered_payload = "TAMPERED_ACTION"
            recalc = compute_block_hash(tampered_payload, first_block.details, first_block.timestamp, first_block.previous_hash)
            self.assertNotEqual(first_block.current_hash, recalc)

    def test_07_telemetry_csv_6000_records(self):
        csv_path = settings.DATASET_PATH
        self.assertTrue(os.path.isfile(csv_path), f"Dataset must exist at {csv_path}")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 6000)

    def test_08_telemetry_csv_columns(self):
        with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
        required = ["roadmap_id", "user_name", "target_role_id", "current_skills", "readiness_score", "gap_score", "estimated_weeks"]
        for col in required:
            self.assertIn(col, header)

    def test_09_telemetry_csv_no_nulls(self):
        with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 100:
                    break
                self.assertTrue(all(v != "" for v in row.values()))

    def test_10_phase2_model_weights_exist(self):
        self.assertTrue(os.path.isfile(settings.MODEL_WEIGHTS_PATH))

    def test_11_regressor_weights_exist(self):
        self.assertTrue(os.path.isfile(settings.REGRESSOR_WEIGHTS_PATH))

    def test_12_career_regressor_forward_pass(self):
        model = CareerTrajectoryForecastNet(in_features=10)
        x = torch.randn(3, 10)
        readiness, gap, weeks, salary = model(x)
        self.assertEqual(readiness.shape, (3, 1))
        self.assertEqual(gap.shape, (3, 1))
        self.assertEqual(weeks.shape, (3, 1))
        self.assertEqual(salary.shape, (3, 1))
        self.assertTrue((readiness >= 0.0).all() and (readiness <= 100.0).all())
        self.assertTrue((gap >= 0.0).all() and (gap <= 100.0).all())
        self.assertTrue((weeks >= 4.0).all() and (weeks <= 40.0).all())

    def test_13_scalers_json_valid(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH))
        with open(settings.SCALERS_PATH, "r") as f:
            sc = json.load(f)
        self.assertIn("mean", sc)
        self.assertIn("std", sc)
        self.assertEqual(len(sc["mean"]), 10)
        self.assertEqual(len(sc["std"]), 10)

    def test_14_model_metadata_valid(self):
        self.assertTrue(os.path.isfile(settings.METADATA_PATH))
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta["dataset_records"], 6000)
        self.assertIn("models", meta)
        self.assertIn("trajectory_forecast_net", meta["models"])

    def test_15_inference_engine_high_readiness(self):
        res = career_engine.analyze_skill_gap(
            user_skills=["Python", "PyTorch", "Deep Learning", "Docker", "MLOps", "Transformers"],
            role_skills=["Python", "PyTorch", "Deep Learning", "MLOps", "Docker", "Transformers", "Kubernetes"],
            target_role_id="ROLE-AI",
            years_experience=5.0
        )
        self.assertGreaterEqual(res["readiness_score"], 70.0)
        self.assertLessEqual(res["gap_score"], 30.0)
        self.assertGreaterEqual(len(res["evidence_hash"]), 32)

    def test_16_inference_engine_career_switcher(self):
        res = career_engine.analyze_skill_gap(
            user_skills=["HTML", "CSS"],
            role_skills=["Python", "PyTorch", "Deep Learning", "MLOps", "Docker", "Transformers", "Kubernetes"],
            target_role_id="ROLE-AI",
            years_experience=0.5
        )
        self.assertLess(res["readiness_score"], 50.0)
        self.assertGreater(res["gap_score"], 50.0)
        self.assertGreaterEqual(res["estimated_weeks"], 10)

    def test_17_inference_engine_curated_courses(self):
        res = career_engine.analyze_skill_gap(
            user_skills=["Python"],
            role_skills=["Python", "Kubernetes", "AWS"],
            target_role_id="ROLE-CLOUD"
        )
        self.assertTrue(len(res["recommended_courses"]) >= 1)
        self.assertTrue(len(res["recommended_projects"]) >= 1)

    def test_18_inference_engine_evidence_hash_deterministic(self):
        r1 = career_engine.analyze_skill_gap(["Python"], ["Python", "SQL"], "ROLE-DATA")
        r2 = career_engine.analyze_skill_gap(["Python"], ["Python", "SQL"], "ROLE-DATA")
        self.assertIsNotNone(r1["evidence_hash"])
        self.assertIsNotNone(r2["evidence_hash"])

    def test_19_api_health_endpoint(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5045)

    def test_20_api_roles_endpoint(self):
        res = self.client.get("/api/career/roles")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 4)

    def test_21_api_roadmaps_endpoint(self):
        res = self.client.get("/api/career/roadmaps")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 8)

    def test_22_api_audit_logs_endpoint(self):
        res = self.client.get("/api/career/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 2)

    def test_23_api_stats_endpoint(self):
        res = self.client.get("/api/career/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ready_ratio_pct", data)
        self.assertIn("audit_ledger_blocks", data)

    def test_24_api_analytics_summary_endpoint(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_generated_roadmaps", data)
        self.assertIn("model_performance", data)

    def test_25_api_analyze_post(self):
        payload = {
            "user_name": "Test Engineer",
            "current_skills": "Python, PyTorch, Deep Learning, Docker",
            "target_role_id": "ROLE-AI",
            "years_experience": 4.5,
            "certifications_count": 2,
            "completed_projects": 5,
            "weekly_hours": 14,
            "learning_budget": 1500.0
        }
        res = self.client.post("/api/career/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["roadmap"]["user_name"], "Test Engineer")
        self.assertIn("readiness_score", data["metrics"])

    def test_26_api_analyze_cloud_architect(self):
        payload = {
            "user_name": "Cloud DevOps Aspirant",
            "current_skills": "Kubernetes, AWS, Terraform, Docker, Linux",
            "target_role_id": "ROLE-CLOUD",
            "years_experience": 4.0
        }
        res = self.client.post("/api/career/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["metrics"]["readiness_score"], 65.0)

    def test_27_frontend_index_exists_and_port_5045(self):
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        self.assertTrue(os.path.isfile(frontend_path))
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("PORT: 5045", content)
        self.assertIn("PROJECT 45", content)

    def test_28_requirements_txt(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        req_path = os.path.join(root_dir, "requirements.txt")
        self.assertTrue(os.path.isfile(req_path))

    def test_29_env_example(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env_path = os.path.join(root_dir, ".env.example")
        self.assertTrue(os.path.isfile(env_path))

    def test_30_walkthrough_script_exists(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        scr_path = os.path.join(root_dir, "walkthrough", "walkthrough_script.md")
        self.assertTrue(os.path.isfile(scr_path))

if __name__ == "__main__":
    unittest.main()
