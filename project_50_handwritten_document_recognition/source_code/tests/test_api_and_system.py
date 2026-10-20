import os
import sys
import unittest
import torch
import numpy as np
from fastapi.testclient import TestClient

# Add source_code to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import ProcessedDocument, AuditLedger
from backend.app.ml.crnn_htr_model import DeepCRNNTextRecognizer, VOCABULARY
from backend.app.ml.quality_scorer_model import DocumentQualityAndLexicalScorerNet
from backend.app.ml.inference_engine import idp_engine

class TestProject50CompleteSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    # 1. Project Deliverables Tests
    def test_01_requirements_file_exists(self):
        req_path = os.path.join(BASE_DIR, "..", "requirements.txt")
        self.assertTrue(os.path.isfile(req_path), "requirements.txt must exist")

    def test_02_env_example_file_exists(self):
        env_path = os.path.join(BASE_DIR, "..", ".env.example")
        self.assertTrue(os.path.isfile(env_path), ".env.example must exist")

    def test_03_walkthrough_script_exists(self):
        wt_path = os.path.join(BASE_DIR, "..", "walkthrough", "walkthrough_script.md")
        self.assertTrue(os.path.isfile(wt_path), "walkthrough_script.md must exist")

    def test_04_dataset_6000_exists(self):
        csv_path = os.path.join(BASE_DIR, "data", "document_telemetry_6000.csv")
        self.assertTrue(os.path.isfile(csv_path), "data/document_telemetry_6000.csv must exist")

    def test_05_weights_crnn_exists(self):
        w_path = os.path.join(BASE_DIR, "backend", "models", "crnn_htr_model_weights.pt")
        self.assertTrue(os.path.isfile(w_path), "crnn_htr_model_weights.pt must exist")

    def test_06_weights_scorer_exists(self):
        w_path = os.path.join(BASE_DIR, "backend", "models", "quality_scorer_weights.pt")
        self.assertTrue(os.path.isfile(w_path), "quality_scorer_weights.pt must exist")

    def test_07_metadata_json_exists(self):
        meta_path = os.path.join(BASE_DIR, "backend", "models", "model_metadata.json")
        self.assertTrue(os.path.isfile(meta_path), "model_metadata.json must exist")

    def test_08_scalers_json_exists(self):
        scalers_path = os.path.join(BASE_DIR, "backend", "models", "idp_scalers.json")
        self.assertTrue(os.path.isfile(scalers_path), "idp_scalers.json must exist")

    # 2. Health & Gateway Tests
    def test_09_health_endpoint_status(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["project_id"], "PROJECT-050")
        self.assertEqual(data["port"], 5050)
        self.assertTrue(data["database_wal_mode"], "Database must be in SQLite WAL mode")

    def test_10_health_models_parameters(self):
        res = self.client.get("/api/health/")
        data = res.json()
        models = data["models"]
        self.assertGreater(models["crnn_parameters"], 300000)
        self.assertGreater(models["quality_scorer_parameters"], 10000)
        self.assertGreater(models["total_parameters"], 320000)

    # 3. Analytics Endpoint Tests
    def test_11_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_documents_processed"], 6000)
        self.assertGreaterEqual(data["human_review_queue_count"], 1)
        self.assertGreater(data["average_transcription_confidence"], 0.70)
        self.assertIn("character_accuracy_cer", data["model_performance"])
        self.assertIn("word_accuracy_wer", data["model_performance"])

    def test_12_analytics_breakdown(self):
        res = self.client.get("/api/analytics/summary")
        data = res.json()
        b_down = data["document_type_breakdown"]
        self.assertIn("HOSPITAL_CLINICAL_INTAKE", b_down)
        self.assertIn("BANK_KYC_LOAN_APPLICATION", b_down)
        self.assertIn("INSURANCE_CLAIM_REIMBURSEMENT", b_down)
        self.assertIn("LEGAL_AFFIDAVIT_ATTESTATION", b_down)

    # 4. Presets Endpoint Tests
    def test_13_presets_availability(self):
        res = self.client.get("/api/idp/presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        presets = data["presets"]
        self.assertEqual(len(presets), 4)
        preset_ids = [p["id"] for p in presets]
        self.assertIn("hayes_intake", preset_ids)
        self.assertIn("global_supplies_invoice", preset_ids)
        self.assertIn("pendelton_claim", preset_ids)
        self.assertIn("anonymous_survey", preset_ids)

    # 5. Documents Retrieval Tests
    def test_14_documents_pagination(self):
        res = self.client.get("/api/idp/documents?skip=0&limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["count"], 10)
        self.assertGreaterEqual(data["total"], 6000)
        self.assertEqual(len(data["documents"]), 10)

    def test_15_documents_filtering_by_type(self):
        res = self.client.get("/api/idp/documents?document_type=HOSPITAL_CLINICAL_INTAKE&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for doc in data["documents"]:
            self.assertEqual(doc["document_type"], "HOSPITAL_CLINICAL_INTAKE")

    def test_16_documents_filtering_by_review_required(self):
        res = self.client.get("/api/idp/documents?review_required=true&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for doc in data["documents"]:
            self.assertTrue(doc["human_review_required"])

    # 6. IDP Process & Dual Model Forward Inference Tests
    def test_17_process_clean_intake_form(self):
        payload = {
            "document_type": "HOSPITAL_CLINICAL_INTAKE",
            "patient_or_client_name": "Dr. Jonathan Hayes",
            "primary_diagnosis_or_purpose": "Acute Bronchitis",
            "date_field": "2026-10-12",
            "id_number": "MED-8842",
            "total_amount": "$350.00",
            "simulate_cursive_unclear": False
        }
        res = self.client.post("/api/idp/process", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertGreaterEqual(m["lexical_confidence"], 0.75)
        self.assertGreaterEqual(m["quality_score"], 65.0)
        self.assertFalse(m["human_review_required"])
        self.assertTrue(m["signature_verified"])
        self.assertEqual(len(m["evidence_hash"]), 64)

    def test_18_process_degraded_survey_form(self):
        payload = {
            "document_type": "LEGAL_AFFIDAVIT_ATTESTATION",
            "patient_or_client_name": "Anonymous Respondent #42",
            "primary_diagnosis_or_purpose": "Property Title Attestation",
            "date_field": "2026-10-08",
            "id_number": "SURV-77",
            "total_amount": "N/A",
            "simulate_cursive_unclear": True
        }
        res = self.client.post("/api/idp/process", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertTrue(m["human_review_required"], "Degraded cursive handwriting must trigger human review")
        self.assertIn("Unclear Cursive", m["patient_or_client_name"])

    def test_19_process_custom_features(self):
        payload = {
            "document_type": "INSURANCE_CLAIM_REIMBURSEMENT",
            "patient_or_client_name": "Arthur Pendelton",
            "primary_diagnosis_or_purpose": "Emergency ER Consultation",
            "date_field": "2026-10-15",
            "id_number": "CLM-4491",
            "total_amount": "$2,850.00",
            "simulate_cursive_unclear": False,
            "custom_features": {
                "contrast_ratio": 0.95,
                "stroke_variance": 0.05,
                "background_snr": 35.0,
                "char_spacing_jitter": 0.04,
                "baseline_slant": 1.0,
                "ink_density": 0.90,
                "occlusion_ratio": 0.01,
                "skew_angle": 0.2,
                "char_mean_logprob": -0.05,
                "dictionary_oov_rate": 0.0,
                "signature_coverage": 95.0,
                "bbox_overlap": 0.98
            }
        }
        res = self.client.post("/api/idp/process", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertGreater(m["quality_score"], 65.0)
        self.assertGreater(m["lexical_confidence"], 0.85)
        self.assertFalse(m["human_review_required"])

    # 7. Cryptographic Audit Ledger Tests
    def test_20_audit_ledger_genesis_block(self):
        res = self.client.get("/api/idp/audit-logs?limit=200")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["chain_valid"], "SHA-256 block hash chain must be 100% valid")
        self.assertGreaterEqual(data["total_blocks"], 150)
        # Genesis block check
        db = SessionLocal()
        genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.event_type, "GENESIS_BLOCK")
        self.assertEqual(genesis.previous_hash, "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(len(genesis.block_hash), 64)
        db.close()

    def test_21_audit_ledger_continuous_chaining(self):
        db = SessionLocal()
        blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).limit(50).all()
        for i in range(1, len(blocks)):
            self.assertEqual(blocks[i].previous_hash, blocks[i-1].block_hash, f"Block {i} previous hash mismatch")
        db.close()

    def test_22_process_appends_audit_block(self):
        res_before = self.client.get("/api/idp/audit-logs?limit=5")
        count_before = res_before.json()["total_blocks"]

        payload = {
            "document_type": "BANK_KYC_LOAN_APPLICATION",
            "patient_or_client_name": "Apex FinCorp",
            "primary_diagnosis_or_purpose": "SBA 7(a) Term Financing",
            "date_field": "2026-10-18",
            "id_number": "BNK-9901",
            "total_amount": "$750,000.00",
            "simulate_cursive_unclear": False
        }
        res = self.client.post("/api/idp/process", json=payload)
        self.assertEqual(res.status_code, 200)
        block = res.json()["audit_block"]
        self.assertGreater(block["block_index"], 0)
        self.assertEqual(len(block["block_hash"]), 64)

        res_after = self.client.get("/api/idp/audit-logs?limit=5")
        self.assertEqual(res_after.json()["total_blocks"], count_before + 1)

    # 8. Frontend Compatibility Endpoints Tests
    def test_23_ocr_records_compat(self):
        res = self.client.get("/api/ocr/records?skip=0&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("records", data)
        self.assertGreater(data["total"], 0)

    def test_24_ocr_extract_compat(self):
        payload = {
            "document_type": "HOSPITAL_CLINICAL_INTAKE",
            "patient_or_client_name": "Dr. Emily Richardson",
            "primary_diagnosis_or_purpose": "Type 2 Diabetes Screening",
            "date_field": "2026-10-11",
            "id_number": "MED-3341",
            "total_amount": "$420.00",
            "simulate_cursive_unclear": False
        }
        res = self.client.post("/api/ocr/extract", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("document", data)
        self.assertIn("metrics", data)

    # 9. DeepCRNNTextRecognizer Unit Tests
    def test_25_crnn_forward_pass_shape(self):
        model = DeepCRNNTextRecognizer()
        dummy = torch.randn(4, 3, 32, 128)
        out = model(dummy)
        self.assertEqual(out.shape, (4, 16, len(VOCABULARY)))

    def test_26_crnn_greedy_decode(self):
        model = DeepCRNNTextRecognizer()
        dummy = torch.randn(2, 3, 32, 128)
        logits = model(dummy)
        decoded = model.decode_greedy(logits)
        self.assertEqual(len(decoded), 2)
        self.assertIn("text", decoded[0])
        self.assertIn("confidence", decoded[0])

    def test_27_crnn_parameter_count(self):
        model = DeepCRNNTextRecognizer()
        p = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertEqual(p, 326569)

    # 10. DocumentQualityAndLexicalScorerNet Unit Tests
    def test_28_scorer_forward_pass_keys(self):
        model = DocumentQualityAndLexicalScorerNet()
        dummy = torch.randn(3, 12)
        out = model(dummy)
        self.assertIn("quality_score", out)
        self.assertIn("lexical_confidence", out)
        self.assertIn("review_risk", out)
        self.assertIn("signature_integrity", out)

    def test_29_scorer_output_ranges(self):
        model = DocumentQualityAndLexicalScorerNet()
        model.eval()
        dummy = torch.randn(5, 12)
        with torch.no_grad():
            out = model(dummy)
            qual = out["quality_score"].squeeze()
            lex = out["lexical_confidence"].squeeze()
            rev = out["review_risk"].squeeze()
            sig = out["signature_integrity"].squeeze()

            self.assertTrue((qual >= 0.0).all() and (qual <= 100.0).all())
            self.assertTrue((lex >= 0.0).all() and (lex <= 1.0).all())
            self.assertTrue((rev >= 0.0).all() and (rev <= 1.0).all())
            self.assertTrue((sig >= 0.0).all() and (sig <= 100.0).all())

    def test_30_scorer_parameter_count(self):
        model = DocumentQualityAndLexicalScorerNet()
        p = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertEqual(p, 12580)

    # 11. Database ACID & Integrity Tests
    def test_31_database_wal_pragma_verified(self):
        from sqlalchemy import text
        db = SessionLocal()
        res = db.execute(text("PRAGMA journal_mode;")).fetchone()
        self.assertEqual(str(res[0]).lower(), "wal")
        db.close()

    def test_32_database_total_rows_at_least_6000(self):
        db = SessionLocal()
        cnt = db.query(ProcessedDocument).count()
        self.assertGreaterEqual(cnt, 6000)
        db.close()

    def test_33_database_no_null_evidence_hashes(self):
        db = SessionLocal()
        null_hashes = db.query(ProcessedDocument).filter(ProcessedDocument.evidence_hash.is_(None)).count()
        self.assertEqual(null_hashes, 0)
        db.close()

    def test_34_inference_engine_synthesizes_valid_image(self):
        t = idp_engine.synthesize_line_image("TEST LINE", degradation_level=0.1)
        self.assertEqual(t.shape, (1, 3, 32, 128))
        self.assertTrue((t >= 0.0).all() and (t <= 1.0).all())

    def test_35_root_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("PROJECT 50: HANDWRITTEN RECOGNITION & EXTRACTION", res.text)

if __name__ == "__main__":
    unittest.main()
