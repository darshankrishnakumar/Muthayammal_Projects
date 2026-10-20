import unittest
import os
import sys
import json
import sqlite3
import hashlib
import torch
import numpy as np

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import CrackIncident, MaintenanceWorkOrder, AuditLedger
from backend.app.ml.inference_engine import pavement_engine
from backend.app.ml.unet_crack_model import ResUNetCrackSegmenter
from backend.app.ml.severity_evaluator import PavementSeverityEvaluator
from backend.app.core.config import settings

class PavementCrackSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    # 1. Health with trailing slash
    def test_01_health_with_slash(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["port"], 5038)
        self.assertIn("Pavement Crack", data["service"])

    # 2. Health without trailing slash
    def test_02_health_no_slash(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")

    # 3. Model Information Endpoint
    def test_03_model_info(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["project_id"], "PROJECT-038")
        self.assertEqual(data["dataset_records"], 6000)
        self.assertIn("ASTM D6433", data["benchmark_standards"])

    # 4. Analytics Summary Endpoint
    def test_04_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_distress_records", data)
        self.assertIn("network_average_pci", data)
        self.assertIn("model_performance", data)
        self.assertEqual(data["model_performance"]["unet_mean_iou"], 0.884)

    # 5. Analyze Crack - Default
    def test_05_analyze_crack_default(self):
        payload = {"road_name": "State Route 17 Westbound", "chainage_km": 34.5}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("incident", data)
        self.assertIn("pci_score", data["metrics"])
        self.assertGreaterEqual(data["metrics"]["pci_score"], 0.0)
        self.assertLessEqual(data["metrics"]["pci_score"], 100.0)

    # 6. Analyze Crack - Alligator Fatigue
    def test_06_analyze_alligator_crack(self):
        payload = {"road_name": "Interstate 80 Westbound", "chainage_km": 112.4, "crack_type": "ALLIGATOR", "severity": "HIGH"}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["crack_type"], "ALLIGATOR")
        self.assertEqual(data["metrics"]["severity_level"], "HIGH")
        self.assertIsNotNone(data["work_order"])
        self.assertEqual(data["work_order"]["priority_tier"], "URGENT")

    # 7. Analyze Crack - Transverse Thermal
    def test_07_analyze_transverse_crack(self):
        payload = {"road_name": "Broadway Boulevard", "chainage_km": 18.2, "crack_type": "TRANSVERSE"}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["crack_type"], "TRANSVERSE")

    # 8. Analyze Crack - Pothole Distress
    def test_08_analyze_pothole_distress(self):
        payload = {"road_name": "El Camino Real Sector 4", "chainage_km": 24.6, "crack_type": "POTHOLE", "severity": "HIGH"}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["metrics"]["crack_type"], "POTHOLE")
        self.assertEqual(data["metrics"]["severity_level"], "HIGH")

    # 9. List Incidents Endpoint
    def test_09_list_incidents(self):
        res = self.client.get("/api/cracks/?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("count", data)
        self.assertIn("incidents", data)
        self.assertGreater(data["count"], 0)

    # 10. List Work Orders Endpoint
    def test_10_list_work_orders(self):
        res = self.client.get("/api/cracks/work-orders?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("count", data)
        self.assertIn("work_orders", data)
        self.assertGreater(data["count"], 0)

    # 11. Audit Ledger Endpoint
    def test_11_audit_ledger_endpoint(self):
        res = self.client.get("/api/audit-logs?limit=15")
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 2)
        for l in logs:
            self.assertEqual(len(l["record_hash"]), 64)
            self.assertEqual(len(l["prev_hash"]), 64)

    # 12. Cryptographic Hash Tamper Detection
    def test_12_crypto_hash_tamper_detection(self):
        db = SessionLocal()
        logs = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()
        db.close()

        self.assertGreaterEqual(len(logs), 2)
        for i in range(1, len(logs)):
            curr = logs[i]
            prev = logs[i - 1]
            self.assertEqual(curr.prev_hash, prev.record_hash)
            raw = f"{curr.action}|{curr.details}|{curr.timestamp}|{curr.prev_hash}"
            expected_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            self.assertEqual(curr.record_hash, expected_hash)

    # 13. SQLite WAL Mode
    def test_13_sqlite_wal_mode(self):
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    # 14. Direct ResUNet Forward Pass
    def test_14_direct_unet_forward_pass(self):
        dummy_in = torch.randn(2, 3, 64, 64).to(pavement_engine.device)
        model = pavement_engine.model
        with torch.no_grad():
            mask_logits, sev_logits = model(dummy_in)
        self.assertEqual(mask_logits.shape, (2, 1, 64, 64))
        self.assertEqual(sev_logits.shape, (2, 3))

    # 15. Direct Severity Evaluator Zero Crack
    def test_15_evaluator_zero_crack(self):
        zero_mask = np.zeros((64, 64), dtype=np.float32)
        metrics = PavementSeverityEvaluator.calculate_metrics(zero_mask)
        self.assertEqual(metrics["crack_type"], "NONE")
        self.assertEqual(metrics["severity_level"], "NONE")
        self.assertEqual(metrics["pci_score"], 100.0)

    # 16. Direct Severity Evaluator High Crack
    def test_16_evaluator_high_crack(self):
        dense_mask = np.ones((64, 64), dtype=np.float32)
        metrics = PavementSeverityEvaluator.calculate_metrics(dense_mask)
        self.assertEqual(metrics["severity_level"], "HIGH")
        self.assertLessEqual(metrics["pci_score"], 40.0)

    # 17. Dataset 6,000 Records Verification
    def test_17_dataset_file_verification(self):
        csv_path = os.path.join(BACKEND_DIR, "data", "pavement_crack_telemetry_6000.csv")
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 6001) # header + 6000 records

    # 18. Model Weights Files Verification
    def test_18_weights_files_verification(self):
        p2_weights = os.path.join(BACKEND_DIR, "experiments", "phase2_model.pt")
        pci_weights = os.path.join(BACKEND_DIR, "backend", "models", "pci_regressor_weights.pt")
        meta_json = os.path.join(BACKEND_DIR, "backend", "models", "model_metadata.json")
        self.assertTrue(os.path.exists(p2_weights))
        self.assertTrue(os.path.exists(pci_weights))
        self.assertTrue(os.path.exists(meta_json))

    # 19. Static Frontend Serving
    def test_19_serve_frontend(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    # 20. 404 Route Handling
    def test_20_not_found(self):
        res = self.client.get("/api/cracks/invalid_non_existent_route")
        self.assertEqual(res.status_code, 404)

    # 21. Multi-Segment Inspection - Pacific Coast Highway
    def test_21_pacific_coast_inspection(self):
        payload = {"road_name": "Pacific Coast Highway", "chainage_km": 42.8}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["incident"]["road_name"], "Pacific Coast Highway")

    # 22. Multi-Segment Inspection - Tech Corridor
    def test_22_tech_corridor_inspection(self):
        payload = {"road_name": "Tech Corridor Expressway", "chainage_km": 78.5}
        res = self.client.post("/api/cracks/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["incident"]["road_name"], "Tech Corridor Expressway")

    # 23. Manual Audit Log Addition
    def test_23_manual_audit_entry(self):
        from backend.app.db.session import log_audit_entry
        db = SessionLocal()
        h = log_audit_entry(db, "TEST_MAINTENANCE_AUDIT", "Testing manual audit entry chaining")
        db.close()
        self.assertEqual(len(h), 64)

    # 24. Pavement Recommendations Mapping
    def test_24_recommendation_mapping(self):
        mask_low = np.zeros((64, 64), dtype=np.float32)
        mask_low[30, 20:25] = 1.0 # Minimal crack
        metrics_low = PavementSeverityEvaluator.calculate_metrics(mask_low)
        self.assertIn("ROUTINE", metrics_low["recommendation"])

    # 25. PCI Bounded Range Check
    def test_25_pci_range_bounds(self):
        payload = {"road_name": "Test Highway", "chainage_km": 1.0}
        res = self.client.post("/api/cracks/analyze", json=payload)
        pci = res.json()["metrics"]["pci_score"]
        self.assertGreaterEqual(pci, 0.0)
        self.assertLessEqual(pci, 100.0)

    # 26. High Severity Mill and Fill Recommendation
    def test_26_mill_and_fill_recommendation(self):
        mask_dense = np.ones((64, 64), dtype=np.float32)
        metrics = PavementSeverityEvaluator.calculate_metrics(mask_dense)
        self.assertEqual(metrics["recommendation"], "MILL_AND_FILL")

    # 27. Model Performance Comparison File Verification
    def test_27_comparison_matrix_verification(self):
        matrix_path = os.path.join(BACKEND_DIR, "experiments", "comparative_evaluation_matrix.json")
        self.assertTrue(os.path.exists(matrix_path))
        with open(matrix_path, "r", encoding="utf-8") as f:
            mat = json.load(f)
        self.assertIn("mean_iou", mat["comparison"])
        self.assertGreater(mat["comparison"]["mean_iou"]["phase2"], mat["comparison"]["mean_iou"]["baseline"])

    # 28. Incident Count Query Integrity
    def test_28_incident_count_query(self):
        db = SessionLocal()
        count = db.query(CrackIncident).count()
        db.close()
        self.assertGreaterEqual(count, 15)

    # 29. Work Order Dispatch Integrity
    def test_29_work_order_dispatch_integrity(self):
        db = SessionLocal()
        orders = db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.status == "DISPATCHED").all()
        db.close()
        self.assertGreater(len(orders), 0)

    # 30. Scalers Feature Columns Verification
    def test_30_scalers_feature_columns(self):
        sc_path = os.path.join(BACKEND_DIR, "backend", "models", "pavement_scalers.json")
        self.assertTrue(os.path.exists(sc_path))
        with open(sc_path, "r", encoding="utf-8") as f:
            sc = json.load(f)
        self.assertEqual(len(sc["feature_cols"]), 5)
        self.assertIn("roughness_iri", sc["feature_cols"])

if __name__ == "__main__":
    unittest.main()
