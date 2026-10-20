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
from backend.app.db.models import DocumentAudit, InspectionTemplate, AuditLedger
from backend.app.ml.dual_domain_forgery_model import DualDomainForgeryNet
from backend.app.ml.document_forensic_model import DocumentForensicRiskRegressorNet
from backend.app.ml.inference_engine import forgery_engine

class TestProject43DocumentForgery(unittest.TestCase):
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
            self.assertIn("document_audits", names)
            self.assertIn("inspection_templates", names)
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
                tampered_details = block.details + " [UNAUTHORIZED_FORGERY_MODIFICATION]"
                tampered_hash = compute_block_hash(block.action_type, tampered_details, block.timestamp, block.previous_hash)
                self.assertNotEqual(tampered_hash, block.current_hash, "Tampered details must produce mismatched hash")
        finally:
            db.close()

    # 3. TEMPLATES & DATASET
    def test_06_inspection_templates_roster(self):
        db = SessionLocal()
        try:
            templates = db.query(InspectionTemplate).all()
            self.assertGreaterEqual(len(templates), 4)
            codes = [t.template_code for t in templates]
            self.assertIn("TMPL-INV-01", codes)
            self.assertIn("TMPL-ID-02", codes)
        finally:
            db.close()

    def test_07_telemetry_dataset_file(self):
        csv_file = settings.DATASET_PATH
        self.assertTrue(os.path.isfile(csv_file), f"Dataset must exist at {csv_file}")
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 6000, "Dataset must contain exactly 6,000 forensic telemetry records")
            first = rows[0]
            self.assertIn("audit_id", first)
            self.assertIn("forgery_risk_pct", first)
            self.assertIn("tampered_area_pct", first)
            self.assertIn("ela_discrepancy_score", first)

    def test_08_scalers_and_metadata_files(self):
        self.assertTrue(os.path.isfile(settings.SCALERS_PATH), "forgery_scalers.json must exist")
        self.assertTrue(os.path.isfile(settings.METADATA_PATH), "model_metadata.json must exist")
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
            self.assertEqual(meta["dataset_records"], 6000)
            self.assertEqual(meta["status"], "TRAINED_SERIALIZED")

    # 4. PYTORCH NEURAL MODELS
    def test_09_dual_domain_model_weights_and_shape(self):
        self.assertTrue(os.path.isfile(settings.MODEL_WEIGHTS_PATH), "phase2_model.pt must exist")
        model = DualDomainForgeryNet()
        weights = torch.load(settings.MODEL_WEIGHTS_PATH, map_location="cpu")
        model.load_state_dict(weights)
        model.eval()

        dummy_s = torch.randn(2, 3, 64, 64)
        dummy_f = torch.randn(2, 3, 64, 64)
        with torch.no_grad():
            logits = model(dummy_s, dummy_f)
            self.assertEqual(logits.shape, (2, 4), "DualDomain logits must be 4 classes (batch, 4)")

    def test_10_regressor_model_weights_and_heads(self):
        self.assertTrue(os.path.isfile(settings.REGRESSOR_WEIGHTS_PATH), "document_forensic_regressor_weights.pt must exist")
        reg = DocumentForensicRiskRegressorNet(in_features=10)
        weights = torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location="cpu")
        reg.load_state_dict(weights)
        reg.eval()

        dummy_x = torch.randn(3, 10)
        with torch.no_grad():
            p_risk, p_area, p_ela, p_dct = reg(dummy_x)
            self.assertEqual(p_risk.shape, (3, 1))
            self.assertEqual(p_area.shape, (3, 1))
            self.assertEqual(p_ela.shape, (3, 1))
            self.assertEqual(p_dct.shape, (3, 1))
            self.assertTrue(torch.all(p_risk >= 0.0) and torch.all(p_risk <= 100.0))
            self.assertTrue(torch.all(p_area >= 0.0) and torch.all(p_area <= 50.0))

    # 5. INFERENCE ENGINE
    def test_11_inference_authentic_document(self):
        res = forgery_engine.audit_document(simulate_tamper=False)
        self.assertEqual(res["forgery_verdict"], "AUTHENTIC")
        self.assertEqual(res["forgery_type"], "NONE")
        self.assertLess(res["forgery_probability"], 0.20)
        self.assertEqual(res["tampered_area_pct"], 0.0)
        self.assertIn("evidence_hash", res)
        self.assertEqual(len(res["evidence_hash"]), 64)

    def test_12_inference_copy_move_detection(self):
        res = forgery_engine.audit_document(simulate_tamper=True, forgery_type="COPY_MOVE")
        self.assertEqual(res["forgery_verdict"], "FORGED")
        self.assertEqual(res["forgery_type"], "COPY_MOVE")
        self.assertGreater(res["forgery_probability"], 0.80)
        self.assertGreater(res["tampered_area_pct"], 0.0)

    def test_13_inference_splicing_detection(self):
        res = forgery_engine.audit_document(simulate_tamper=True, forgery_type="SPLICING")
        self.assertEqual(res["forgery_verdict"], "FORGED")
        self.assertEqual(res["forgery_type"], "SPLICING")
        self.assertGreater(res["forgery_probability"], 0.85)

    def test_14_inference_text_erasure_detection(self):
        res = forgery_engine.audit_document(simulate_tamper=True, forgery_type="TEXT_ERASURE")
        self.assertEqual(res["forgery_verdict"], "FORGED")
        self.assertEqual(res["forgery_type"], "TEXT_ERASURE")

    # 6. REST API ENDPOINTS
    def test_15_api_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5043)
        self.assertTrue(data["database_wal_active"])

    def test_16_api_audits(self):
        res = self.client.get("/api/forensics/audits")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 1)
        self.assertIn("audits", data)

    def test_17_api_audit_logs(self):
        res = self.client.get("/api/forensics/audit-logs?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ledger", data)
        self.assertGreaterEqual(data["count"], 1)

    def test_18_api_templates(self):
        res = self.client.get("/api/forensics/templates")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 4)

    def test_19_api_stats(self):
        res = self.client.get("/api/forensics/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_audits", data)
        self.assertIn("authentic_documents", data)
        self.assertIn("forged_intercepted", data)

    def test_20_api_analyze_authentic(self):
        payload = {
            "document_title": "Verified Medical Claim #881",
            "document_type": "INVOICE",
            "simulate_forgery": False
        }
        res = self.client.post("/api/forensics/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["forgery_verdict"], "AUTHENTIC")
        self.assertEqual(data["record"]["document_type"] if "record" in data else data["audit"]["document_type"], "INVOICE")

    def test_21_api_analyze_forged(self):
        payload = {
            "document_title": "Forged Contract Escrow #410",
            "document_type": "CONTRACT",
            "simulate_forgery": True,
            "forgery_type": "SPLICING"
        }
        res = self.client.post("/api/forensics/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["forgery_verdict"], "FORGED")
        self.assertEqual(data["metrics"]["forgery_type"], "SPLICING")

    def test_22_api_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_documents_audited", data)
        self.assertIn("model_performance", data)

    def test_23_root_index_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("PROJECT 43", res.text)
        self.assertIn("PORT: 5043", res.text)

    def test_24_evidence_hash_uniqueness(self):
        res1 = forgery_engine.audit_document(simulate_tamper=False, document_title="Doc A")
        res2 = forgery_engine.audit_document(simulate_tamper=True, document_title="Doc B")
        self.assertNotEqual(res1["evidence_hash"], res2["evidence_hash"])

    def test_25_model_latency_benchmark(self):
        res = forgery_engine.audit_document(simulate_tamper=False)
        self.assertLess(res["latency_ms"], 100.0, "Forensic audit latency must be under 100ms")

    def test_26_custom_document_category(self):
        res = forgery_engine.audit_document(document_type="PASSPORT_ID")
        self.assertEqual(res["document_type"], "PASSPORT_ID")

    def test_27_genesis_block_tamper_fails(self):
        db = SessionLocal()
        try:
            genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
            if genesis:
                tampered = compute_block_hash("MALICIOUS_GENESIS", genesis.details, genesis.timestamp, genesis.previous_hash)
                self.assertNotEqual(tampered, genesis.current_hash)
        finally:
            db.close()

    def test_28_regressor_batch_inference(self):
        reg = DocumentForensicRiskRegressorNet(in_features=10)
        weights = torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location="cpu")
        reg.load_state_dict(weights)
        reg.eval()
        batch_input = torch.randn(16, 10)
        with torch.no_grad():
            r, a, e, d = reg(batch_input)
            self.assertEqual(r.shape, (16, 1))
            self.assertEqual(a.shape, (16, 1))

    def test_29_tampered_area_bounds(self):
        res = forgery_engine.audit_document(simulate_tamper=True)
        self.assertGreaterEqual(res["tampered_area_pct"], 0.0)
        self.assertLessEqual(res["tampered_area_pct"], 50.0)

    def test_30_sequential_block_index(self):
        db = SessionLocal()
        try:
            initial_count = db.query(AuditLedger).count()
            entry = append_audit_block(db, "TEST_ACTION", "Testing sequential block incrementation")
            self.assertEqual(entry.block_index, initial_count)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
