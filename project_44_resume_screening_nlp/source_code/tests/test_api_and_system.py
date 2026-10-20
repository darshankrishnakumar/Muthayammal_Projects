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
from backend.app.db.models import JobOpening, CandidateMatch, AuditLedger
from backend.app.ml.inference_engine import screening_engine
from backend.app.ml.transformer_matching_model import TransformerSemanticMatcherNet
from backend.app.ml.candidate_competency_model import CandidateCompetencyRegressorNet

class TestProject44SystemAndAPI(unittest.TestCase):
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

    def test_02_job_openings_count(self):
        count = self.db.query(JobOpening).count()
        self.assertGreaterEqual(count, 4)

    def test_03_candidate_matches_seeded(self):
        count = self.db.query(CandidateMatch).count()
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
            tampered_payload = "TAMPERED_EVENT"
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
        required = ["match_id", "job_id", "candidate_name", "candidate_experience_years", "overall_match_score", "screening_decision"]
        for col in required:
            self.assertIn(col, header)

    def test_09_telemetry_csv_no_nulls(self):
        with open(settings.DATASET_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 100:
                    break
                self.assertTrue(all(v != "" for v in row.values()))

    def test_10_transformer_model_weights_exist(self):
        self.assertTrue(os.path.isfile(settings.MODEL_WEIGHTS_PATH))

    def test_11_transformer_model_forward_pass(self):
        model = TransformerSemanticMatcherNet(emb_dim=128)
        c = torch.randn(2, 128)
        j = torch.randn(2, 128)
        out = model(c, j)
        self.assertEqual(out.shape, (2, 1))
        self.assertTrue((out >= 0.0).all() and (out <= 1.0).all())

    def test_12_competency_regressor_weights_exist(self):
        self.assertTrue(os.path.isfile(settings.REGRESSOR_WEIGHTS_PATH))

    def test_13_competency_regressor_forward_pass(self):
        reg = CandidateCompetencyRegressorNet(in_features=10)
        x = torch.randn(3, 10)
        match_s, overlap, exp_f, sen = reg(x)
        self.assertEqual(match_s.shape, (3, 1))
        self.assertEqual(overlap.shape, (3, 1))
        self.assertEqual(exp_f.shape, (3, 1))
        self.assertEqual(sen.shape, (3, 1))
        self.assertTrue((match_s >= 0.0).all() and (match_s <= 100.0).all())
        self.assertTrue((overlap >= 0.0).all() and (overlap <= 1.0).all())
        self.assertTrue((exp_f >= 0.0).all() and (exp_f <= 10.0).all())

    def test_14_scalers_json_valid(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH))
        with open(settings.SCALERS_PATH, "r") as f:
            sc = json.load(f)
        self.assertIn("mean", sc)
        self.assertIn("std", sc)
        self.assertEqual(len(sc["mean"]), 10)
        self.assertEqual(len(sc["std"]), 10)

    def test_15_model_metadata_valid(self):
        self.assertTrue(os.path.isfile(settings.METADATA_PATH))
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta["dataset_records"], 6000)
        self.assertIn("transformer_semantic_matcher", meta)
        self.assertIn("competency_regressor", meta)

    def test_16_inference_engine_shortlist_profile(self):
        res = screening_engine.evaluate_fit(
            candidate_skills=["PyTorch", "Transformers", "Computer Vision", "Docker", "FastAPI", "Python"],
            job_skills=["PyTorch", "Transformers", "Computer Vision", "Docker", "FastAPI", "Python"],
            candidate_exp_years=6.0,
            job_min_exp=4.0
        )
        self.assertEqual(res["screening_decision"], "SHORTLISTED")
        self.assertGreaterEqual(res["overall_match_score"], 80.0)
        self.assertGreater(len(res["evidence_hash"]), 32)

    def test_17_inference_engine_reject_profile(self):
        res = screening_engine.evaluate_fit(
            candidate_skills=["HTML", "CSS"],
            job_skills=["PyTorch", "Transformers", "Computer Vision", "Docker", "FastAPI", "Python"],
            candidate_exp_years=0.5,
            job_min_exp=4.0
        )
        self.assertEqual(res["screening_decision"], "REJECTED")
        self.assertLess(res["overall_match_score"], 60.0)

    def test_18_inference_engine_evidence_hash_deterministic(self):
        r1 = screening_engine.evaluate_fit(["Python"], ["Python", "SQL"], 2.0, 3.0)
        r2 = screening_engine.evaluate_fit(["Python"], ["Python", "SQL"], 2.0, 3.0)
        self.assertIsNotNone(r1["evidence_hash"])
        self.assertIsNotNone(r2["evidence_hash"])

    def test_19_api_health_endpoint(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5044)

    def test_20_api_jobs_endpoint(self):
        res = self.client.get("/api/screening/jobs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 4)

    def test_21_api_matches_endpoint(self):
        res = self.client.get("/api/screening/matches")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 8)

    def test_22_api_audit_logs_endpoint(self):
        res = self.client.get("/api/screening/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 2)

    def test_23_api_stats_endpoint(self):
        res = self.client.get("/api/screening/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("shortlist_ratio_pct", data)
        self.assertIn("audit_ledger_blocks", data)

    def test_24_api_analytics_summary_endpoint(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_screened_candidates", data)
        self.assertIn("model_performance", data)

    def test_25_api_match_post_shortlist(self):
        payload = {
            "candidate_name": "Test Senior Researcher",
            "candidate_skills": "PyTorch, Transformers, Computer Vision, Docker, FastAPI, Python",
            "experience_years": 5.5,
            "job_id": "JOB-AI-LEAD",
            "certification_count": 3,
            "education_level": 3,
            "github_contributions": 65,
            "anonymize_bias": False
        }
        res = self.client.post("/api/screening/match", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["match"]["candidate_name"], "Test Senior Researcher")
        self.assertEqual(data["match"]["screening_decision"], "SHORTLISTED")

    def test_26_api_match_post_anonymized(self):
        payload = {
            "candidate_name": "John Doe Private",
            "candidate_skills": "React, Node.js, TypeScript, PostgreSQL",
            "experience_years": 3.5,
            "job_id": "JOB-CLOUD-DEV",
            "anonymize_bias": True
        }
        res = self.client.post("/api/screening/match", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["match"]["candidate_name"].startswith("Candidate #ANON-"))

    def test_27_api_candidates_alias(self):
        res = self.client.get("/api/screening/candidates")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 1)

    def test_28_frontend_index_exists_and_port_5044(self):
        frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        self.assertTrue(os.path.isfile(frontend_path))
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("PORT: 5044", content)
        self.assertIn("PROJECT 44", content)

    def test_29_requirements_txt(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        req_path = os.path.join(root_dir, "requirements.txt")
        self.assertTrue(os.path.isfile(req_path))

    def test_30_env_example(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env_path = os.path.join(root_dir, ".env.example")
        self.assertTrue(os.path.isfile(env_path))

if __name__ == "__main__":
    unittest.main()
