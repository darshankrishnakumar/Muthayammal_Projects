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
from backend.app.db.models import InspectedPart, InspectionTemplate, AuditLedger
from backend.app.ml.inference_engine import mfg_engine
from backend.app.ml.fpn_defect_model import DeepFPNDefectNet
from backend.app.ml.regressor_model import ManufacturingDefectRiskRegressorNet

class TestProject46SystemAndAPI(unittest.TestCase):
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

    def test_03_inspection_templates_count(self):
        count = self.db.query(InspectionTemplate).count()
        self.assertGreaterEqual(count, 4)

    def test_04_inspection_templates_content(self):
        pcb = self.db.query(InspectionTemplate).filter(InspectionTemplate.template_id == "TEMPL-PCB").first()
        self.assertIsNotNone(pcb)
        self.assertEqual(pcb.part_type, "PCB_BOARD")
        self.assertTrue(pcb.is_active)
        self.assertGreater(pcb.ejection_air_pressure_bar, 5.0)

    def test_05_inspected_parts_seeded(self):
        count = self.db.query(InspectedPart).count()
        self.assertGreaterEqual(count, 8)

    def test_06_inspected_parts_verdicts(self):
        passes = self.db.query(InspectedPart).filter(InspectedPart.inspection_verdict == "PASS").count()
        rejects = self.db.query(InspectedPart).filter(InspectedPart.inspection_verdict == "REJECT").count()
        self.assertGreater(passes, 0)
        self.assertGreater(rejects, 0)

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
            tampered_details = first_block.details + " [MALICIOUS INJECTION]"
            recalculated = compute_block_hash(
                first_block.action_type,
                tampered_details,
                first_block.timestamp,
                first_block.previous_hash
            )
            self.assertNotEqual(first_block.current_hash, recalculated)

    def test_10_evidence_hash_integrity(self):
        sample = self.db.query(InspectedPart).first()
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
            expected = ["part_id", "assembly_line", "part_type", "inspection_verdict", "defect_type", "severity_score"]
            for h in expected:
                self.assertIn(h, headers)

    def test_13_model_metadata_validity(self):
        self.assertTrue(os.path.exists(settings.METADATA_PATH))
        with open(settings.METADATA_PATH, "r") as f:
            meta = json.load(f)
            self.assertEqual(meta["dataset_records"], 6000)
            self.assertIn("fpn_defect_net", meta["models"])
            self.assertIn("defect_risk_regressor", meta["models"])

    def test_14_scalers_file_validity(self):
        self.assertTrue(os.path.exists(settings.SCALERS_PATH))
        with open(settings.SCALERS_PATH, "r") as f:
            scalers = json.load(f)
            self.assertEqual(len(scalers["mean"]), 10)
            self.assertEqual(len(scalers["std"]), 10)

    def test_15_fpn_model_weights_exist(self):
        self.assertTrue(os.path.exists(settings.MODEL_WEIGHTS_PATH))

    def test_16_regressor_weights_exist(self):
        self.assertTrue(os.path.exists(settings.REGRESSOR_WEIGHTS_PATH))

    def test_17_fpn_model_forward_pass(self):
        model = DeepFPNDefectNet(num_defect_classes=5)
        dummy_in = torch.randn(2, 3, 64, 64)
        seg, logits = model(dummy_in)
        self.assertEqual(seg.shape, (2, 1, 16, 16))
        self.assertEqual(logits.shape, (2, 5))

    def test_18_regressor_forward_pass(self):
        model = ManufacturingDefectRiskRegressorNet(in_features=10)
        dummy_in = torch.randn(3, 10)
        sev, area, rough, eject = model(dummy_in)
        self.assertEqual(sev.shape, (3, 1))
        self.assertEqual(area.shape, (3, 1))
        self.assertEqual(rough.shape, (3, 1))
        self.assertEqual(eject.shape, (3, 1))

    def test_19_inference_nominal_part(self):
        dummy_img = np.random.uniform(0.4, 0.6, (3, 64, 64)).astype(np.float32)
        res = mfg_engine.inspect_part(dummy_img, part_type="PCB_BOARD", simulate_defect="NONE")
        self.assertEqual(res["inspection_verdict"], "PASS")
        self.assertEqual(res["defect_type"], "NONE")
        self.assertEqual(res["actuator_action"], "ROUTE_CONVEYOR")
        self.assertLess(res["severity_score"], 50.0)

    def test_20_inference_defect_part(self):
        dummy_img = np.random.uniform(0.4, 0.6, (3, 64, 64)).astype(np.float32)
        res = mfg_engine.inspect_part(dummy_img, part_type="MACHINED_GEAR", simulate_defect="CRACK")
        self.assertEqual(res["inspection_verdict"], "REJECT")
        self.assertEqual(res["defect_type"], "CRACK")
        self.assertEqual(res["actuator_action"], "TRIGGER_PNEUMATIC_EJECT")
        self.assertGreater(res["pneumatic_ejection_confidence"], 50.0)

    def test_21_evidence_hash_determinism(self):
        dummy_img = np.zeros((3, 64, 64), dtype=np.float32)
        res1 = mfg_engine.inspect_part(dummy_img, "PCB_BOARD", "NONE")
        res2 = mfg_engine.inspect_part(dummy_img, "PCB_BOARD", "NONE")
        self.assertEqual(res1["evidence_hash"], res2["evidence_hash"])

    def test_22_api_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5046)

    def test_23_api_health_trailing_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "HEALTHY")

    def test_24_api_parts_endpoint(self):
        res = self.client.get("/api/inspection/parts")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("parts", data)
        self.assertGreaterEqual(data["count"], 1)

    def test_25_api_templates_endpoint(self):
        res = self.client.get("/api/inspection/templates")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("templates", data)
        self.assertEqual(data["count"], 4)

    def test_26_api_audit_logs_endpoint(self):
        res = self.client.get("/api/inspection/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("audit_logs", data)
        self.assertGreaterEqual(data["count"], 2)

    def test_27_api_stats_endpoint(self):
        res = self.client.get("/api/inspection/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_parts_inspected", data)
        self.assertIn("yield_rate_pct", data)

    def test_28_api_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("line_yield_pct", data)
        self.assertIn("defect_distribution", data)

    def test_29_api_scan_pass(self):
        payload = {
            "assembly_line": "Line-1 SMT PCB Assembly",
            "part_type": "PCB_BOARD",
            "simulate_defect": "NONE"
        }
        res = self.client.post("/api/inspection/scan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["part"]["inspection_verdict"], "PASS")
        self.assertEqual(data["part"]["actuator_action"], "ROUTE_CONVEYOR")

    def test_30_api_scan_reject(self):
        payload = {
            "assembly_line": "Line-2 CNC Gear Milling",
            "part_type": "MACHINED_GEAR",
            "simulate_defect": "SCRATCH"
        }
        res = self.client.post("/api/inspection/scan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["part"]["inspection_verdict"], "REJECT")
        self.assertEqual(data["part"]["actuator_action"], "TRIGGER_PNEUMATIC_EJECT")

    def test_31_audit_block_increments_on_scan(self):
        pre_count = self.db.query(AuditLedger).count()
        payload = {
            "assembly_line": "Line-4 Precision Aerospace",
            "part_type": "TURBINE_BLADE",
            "simulate_defect": "DENT"
        }
        res = self.client.post("/api/inspection/scan", json=payload)
        self.assertEqual(res.status_code, 200)
        post_count = self.db.query(AuditLedger).count()
        self.assertEqual(post_count, pre_count + 1)

    def test_32_root_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))

if __name__ == "__main__":
    unittest.main()
