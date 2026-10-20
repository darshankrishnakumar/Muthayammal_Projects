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
from backend.app.db.models import PatientProfile, PatientRiskAssessment, AuditLedger
from backend.app.ml.longitudinal_risk_model import LongitudinalHealthRiskNet
from backend.app.ml.comorbidity_model import ClinicalComorbidityForecastNet
from backend.app.ml.inference_engine import health_engine

class TestProject049ComprehensiveSuite(unittest.TestCase):
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
        self.assertEqual(data["project_id"], "PROJECT-049")
        self.assertEqual(data["port"], 5049)
        self.assertTrue(data["database_wal_mode"])
        self.assertIn("models", data)
        self.assertEqual(data["models"]["risk_parameters"], 3044)
        self.assertEqual(data["models"]["comorbidity_parameters"], 18308)

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
        test_index = 999
        test_prev = "b" * 64
        test_time = "2026-10-21T01:30:00"
        test_event = "CLINICAL_ASSESSMENT"
        valid_details = json.dumps({"patient": "valid", "cvd": 45.0})
        tampered_details = json.dumps({"patient": "tampered", "cvd": 95.0})
        evidence = hashlib.sha256(b"tamper_proof_test_p49").hexdigest()
        
        valid_hash = compute_block_hash(test_index, test_prev, test_time, test_event, valid_details, evidence)
        tampered_hash = compute_block_hash(test_index, test_prev, test_time, test_event, tampered_details, evidence)
        self.assertNotEqual(valid_hash, tampered_hash, "Tampered details must yield divergent SHA-256 block hash")

    def test_07_assessments_list_api(self):
        res = self.client.get("/api/patients/assessments")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("assessments", data)
        self.assertGreaterEqual(len(data["assessments"]), 4)
        first = data["assessments"][0]
        self.assertIn("assessment_id", first)
        self.assertIn("patient_id", first)
        self.assertIn("cardiovascular_risk_pct", first)
        self.assertIn("composite_risk_tier", first)

    def test_08_records_alias_api(self):
        res = self.client.get("/api/patients/records")
        self.assertEqual(res.status_code, 200)
        self.assertIn("records", res.json())
        res_hr = self.client.get("/api/health-risk/records")
        self.assertEqual(res_hr.status_code, 200)
        self.assertIn("records", res_hr.json())

    def test_09_patient_profiles_api(self):
        res = self.client.get("/api/patients/profiles")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("profiles", data)
        self.assertGreaterEqual(len(data["profiles"]), 4)
        first = data["profiles"][0]
        self.assertIn("patient_id", first)
        self.assertIn("cohort", first)

    def test_10_audit_logs_api(self):
        res = self.client.get("/api/patients/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["chain_verified"], "Cryptographic chain must be verified")
        self.assertFalse(data["tamper_detected"], "No tampering should be detected")
        self.assertGreaterEqual(data["total_blocks"], 5)

    def test_11_analytics_summary_api(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_assessments", data)
        self.assertIn("high_cardiovascular_risk_pct", data)
        self.assertIn("model_performance", data)
        self.assertEqual(data["discriminative_roc_auc"], 0.945)
        self.assertEqual(data["model_performance"]["r2_score"], 0.993)

    def test_12_stats_api(self):
        res = self.client.get("/api/patients/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_assessments", data)
        self.assertIn("mean_cardiovascular_risk_pct", data)
        self.assertIn("tier_distribution", data)

    def test_13_assess_hypertensive_patient_pipeline(self):
        res = self.client.post("/api/patients/assess", json={
            "full_name": "Arthur Pendelton",
            "patient_id": "PAT-903",
            "age": 67,
            "gender": "Male",
            "systolic_bp": 162.0,
            "diastolic_bp": 98.0,
            "hba1c": 7.8,
            "fasting_glucose": 175.0,
            "cholesterol": 245.0,
            "hdl": 34.0,
            "ldl": 168.0,
            "egfr": 32.0,
            "bmi": 29.5
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        m = data["metrics"]
        self.assertIn(m["composite_risk_tier"], ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(m["cardiovascular_risk_pct"], 60.0)
        self.assertGreaterEqual(m["ckd_risk_pct"], 60.0)
        self.assertEqual(len(m["evidence_hash"]), 64)

    def test_14_assess_normal_control_patient(self):
        res = self.client.post("/api/patients/assess", json={
            "full_name": "Linda Sterling",
            "patient_id": "PAT-902",
            "age": 42,
            "gender": "Female",
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "hba1c": 5.2,
            "fasting_glucose": 92.0,
            "cholesterol": 175.0,
            "hdl": 58.0,
            "ldl": 98.0,
            "egfr": 104.0,
            "bmi": 23.2
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertEqual(m["composite_risk_tier"], "LOW")
        self.assertLess(m["cardiovascular_risk_pct"], 35.0)
        self.assertLess(m["type2_diabetes_risk_pct"], 35.0)

    def test_15_evaluate_alias_endpoint(self):
        res = self.client.post("/api/patients/evaluate", json={
            "full_name": "Jennifer Montgomery",
            "systolic_bp": 136.0,
            "glucose_mg_dl": 188.0,
            "hba1c": 8.9,
            "bmi": 34.8
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertGreaterEqual(data["metrics"]["type2_diabetes_risk_pct"], 60.0)

    def test_16_risk_net_forward_shapes(self):
        net = LongitudinalHealthRiskNet(in_features=10)
        dummy_in = torch.randn(4, 10)
        cvd, t2d, htn, ckd = net(dummy_in)
        self.assertEqual(cvd.shape, (4, 1))
        self.assertEqual(t2d.shape, (4, 1))
        self.assertEqual(htn.shape, (4, 1))
        self.assertEqual(ckd.shape, (4, 1))
        for t in [cvd, t2d, htn, ckd]:
            self.assertTrue(torch.all((t >= 0.0) & (t <= 100.0)))

    def test_17_comorbidity_net_forward_shapes(self):
        net = ClinicalComorbidityForecastNet(input_dim=14, hidden_dim=64)
        dummy_in = torch.randn(5, 14)
        out = net(dummy_in)
        self.assertEqual(out.shape, (5, 4))
        self.assertTrue(torch.all((out >= 0.0) & (out <= 100.0)))

    def test_18_real_telemetry_dataset_integrity(self):
        csv_path = settings.DATASET_PATH
        self.assertTrue(os.path.isfile(csv_path), f"Telemetry CSV must exist at {csv_path}")
        df = pd.read_csv(csv_path)
        self.assertEqual(len(df), 6000, "Dataset must contain exactly 6,000 physical patient records")
        required_cols = [
            "assessment_id", "patient_id", "full_name", "cohort", "age", "gender",
            "systolic_bp", "diastolic_bp", "hba1c", "fasting_glucose", "total_cholesterol",
            "hdl_cholesterol", "ldl_cholesterol", "egfr", "bmi",
            "cardiovascular_risk_pct", "type2_diabetes_risk_pct", "hypertension_risk_pct", "ckd_risk_pct",
            "composite_risk_tier", "primary_biomarker_drivers", "preventive_recommendations",
            "ten_year_mortality_risk_pct", "hospital_readmission_risk_pct",
            "polypharmacy_complexity_index", "renal_progression_hazard_pct"
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required patient telemetry column: {col}")
        self.assertEqual(df.isnull().sum().sum(), 0, "Patient telemetry CSV must have zero null values")
        self.assertTrue(df["age"].between(18, 100).all())
        self.assertTrue(df["systolic_bp"].between(80.0, 240.0).all())

    def test_19_serialized_model_weights_on_disk(self):
        self.assertTrue(os.path.isfile(settings.RISK_MODEL_WEIGHTS_PATH), "Risk net weights must exist on disk")
        self.assertTrue(os.path.isfile(settings.COMORBIDITY_WEIGHTS_PATH), "Comorbidity regressor weights must exist on disk")
        risk_sd = torch.load(settings.RISK_MODEL_WEIGHTS_PATH, map_location="cpu")
        self.assertIn("cvd_head.weight", risk_sd)
        comb_sd = torch.load(settings.COMORBIDITY_WEIGHTS_PATH, map_location="cpu")
        self.assertIn("out_mortality.weight", comb_sd)

    def test_20_scalers_and_metadata_files(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH), "Scalers JSON must exist")
        self.assertTrue(os.path.isfile(settings.METADATA_PATH), "Metadata JSON must exist")
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta["project"], "PROJECT-049")
        self.assertEqual(meta["port"], 5049)
        self.assertIn("risk_model", meta)
        self.assertIn("comorbidity_model", meta)

    def test_21_evidence_hashes_deterministic_and_unique(self):
        db = SessionLocal()
        try:
            hashes = [a.evidence_hash for a in db.query(PatientRiskAssessment.evidence_hash).all()]
            self.assertEqual(len(hashes), len(set(hashes)), "Assessment evidence hashes must be unique")
        finally:
            db.close()

    def test_22_frontend_index_file_valid(self):
        frontend_path = os.path.join(SOURCE_CODE_DIR, "frontend/index.html")
        self.assertTrue(os.path.isfile(frontend_path), "Frontend index.html must exist")
        with open(frontend_path, "r") as f:
            html = f.read()
        self.assertIn("5049", html, "Frontend must reference Port 5049")
        self.assertIn("shapChart", html, "Frontend must include SHAP chart canvas")
        self.assertIn("records-body", html, "Frontend must include records table")
        self.assertIn("audit-body", html, "Frontend must include audit ledger table")

    def test_23_cohort_distribution(self):
        df = pd.read_csv(settings.DATASET_PATH)
        cohorts = set(df["cohort"].unique())
        expected = {"DIABETIC_METABOLIC", "HYPERTENSIVE_CVD", "RENAL_CKD", "NORMOTENSIVE_CONTROL"}
        self.assertTrue(expected.issubset(cohorts), f"Expected cohorts {expected}, got {cohorts}")

    def test_24_systolic_bp_hypertension_correlation(self):
        df = pd.read_csv(settings.DATASET_PATH)
        corr = df["systolic_bp"].corr(df["hypertension_risk_pct"])
        self.assertGreater(corr, 0.75, "Systolic BP must correlate strongly with hypertension risk (> 0.75)")

    def test_25_hba1c_diabetes_correlation(self):
        df = pd.read_csv(settings.DATASET_PATH)
        corr = df["hba1c"].corr(df["type2_diabetes_risk_pct"])
        self.assertGreater(corr, 0.75, "HbA1c must correlate strongly with type 2 diabetes risk (> 0.75)")

    def test_26_egfr_ckd_inverse_correlation(self):
        df = pd.read_csv(settings.DATASET_PATH)
        corr = df["egfr"].corr(df["ckd_risk_pct"])
        self.assertLess(corr, -0.75, "eGFR must negatively correlate strongly with CKD risk (< -0.75)")

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
