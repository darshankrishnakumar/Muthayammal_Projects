import unittest
import os
import sys
import json
import sqlite3
import torch
import numpy as np

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import get_connection, log_audit_entry, DB_PATH
from violation_engine import get_engine, TrafficViolationClassifierNet, TrafficSafetySeverityRegressorNet

class TrafficEnforcementSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.engine = get_engine()

    # 1. Health & Status
    def test_01_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["port"], 5037)
        self.assertIn("AI Traffic Violation Detection", data["service"])
        self.assertIn("100.00%", data["classifier_accuracy"])

    # 2. Intersections Endpoint
    def test_02_intersections_endpoint(self):
        res = self.client.get("/api/intersections")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 4)
        ids = [i["id"] for i in data]
        self.assertIn("INT-01", ids)
        self.assertIn("INT-02", ids)

    # 3. Cameras Endpoint
    def test_03_cameras_endpoint(self):
        res = self.client.get("/api/cameras")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 6)
        cams = [c["camera_id"] for c in data]
        self.assertIn("CAM-101", cams)

    # 4. Model Metadata Endpoint
    def test_04_model_info_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["project_id"], "PROJECT-037")
        self.assertEqual(data["dataset_records"], 6000)
        self.assertEqual(len(data["classes"]), 8)

    # 5. Speeding Violation Inference
    def test_05_speeding_violation(self):
        payload = {"vehicle_type": "Car", "speed_kmh": 98.0, "speed_limit": 60.0}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 1)
        det = data["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Speeding")
        self.assertEqual(det["fine_amount"], 2000)
        self.assertIn("MVA Sec 183(1)", det["mva_section"])
        self.assertGreaterEqual(det["severity_index"], 40.0)

    # 6. Red Light Violation Inference
    def test_06_red_light_violation(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 52.0,
            "speed_limit": 60.0,
            "traffic_light_state": 0, # Red
            "distance_to_stop_line_m": -3.5 # Past stop line
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 1)
        det = data["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Red Light Violation")
        self.assertEqual(det["fine_amount"], 1000)
        self.assertIn("MVA Sec 184", det["mva_section"])

    # 7. Wrong Way Driving Inference
    def test_07_wrong_way_violation(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 45.0,
            "speed_limit": 60.0,
            "heading_degrees": 178.0
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 1)
        det = data["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Wrong Way Driving")
        self.assertEqual(det["fine_amount"], 5000)

    # 8. No Helmet Violation Inference
    def test_08_no_helmet_violation(self):
        payload = {
            "vehicle_type": "Motorcycle",
            "speed_kmh": 42.0,
            "speed_limit": 60.0,
            "helmet_detected": 0
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 1)
        det = data["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "No Helmet / Two-Wheeler")
        self.assertEqual(det["fine_amount"], 1000)
        self.assertIn("MVA Sec 194D", det["mva_section"])

    # 9. Mobile Phone Usage Violation Inference
    def test_09_mobile_phone_violation(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 45.0,
            "speed_limit": 60.0,
            "mobile_phone_detected": 1
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 1)
        det = data["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Mobile Phone Usage")
        self.assertEqual(det["fine_amount"], 1500)

    # 10. Normal Compliant Vehicle
    def test_10_normal_compliant_vehicle(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 45.0,
            "speed_limit": 60.0,
            "traffic_light_state": 2, # Green
            "distance_to_stop_line_m": 25.0,
            "lane_offset_m": 0.05,
            "seatbelt_detected": 1,
            "mobile_phone_detected": 0,
            "heading_degrees": 2.0
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["violations_found"], 0)
        det = data["detections"][0]
        self.assertFalse(det["violation_detected"])
        self.assertEqual(det["fine_amount"], 0)

    # 11. Multi-Vehicle Scene Synthesis
    def test_11_multi_vehicle_scene(self):
        payload = {"location": "INT-02 North Highway", "camera_id": "CAM-103"}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["vehicles_detected"], 2)
        self.assertEqual(data["location"], "INT-02 North Highway")
        self.assertEqual(data["camera_id"], "CAM-103")

    # 12. Violations History Endpoint
    def test_12_violations_history(self):
        res = self.client.get("/api/violations?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    # 13. Challans History Endpoint
    def test_13_challans_history(self):
        res = self.client.get("/api/challans?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        chl = data[0]
        self.assertTrue(chl["challan_id"].startswith("CHL-"))
        self.assertIn("evidence_hash", chl)

    # 14. Aggregate Stats Endpoint
    def test_14_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_vehicles_scanned", data)
        self.assertIn("total_violations", data)
        self.assertIn("total_fine_revenue", data)
        self.assertIn("compliance_rate", data)
        self.assertGreater(data["total_vehicles_scanned"], 0)

    # 15. Audit Ledger Cryptographic Chaining
    def test_15_audit_ledger_integrity(self):
        res = self.client.get("/api/audit-logs?limit=20")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertGreaterEqual(len(logs), 2)
        for entry in logs:
            self.assertIn("record_hash", entry)
            self.assertIn("prev_hash", entry)
            self.assertEqual(len(entry["record_hash"]), 64)

    # 16. Database WAL Mode Verification
    def test_16_db_wal_mode(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    # 17. PyTorch Forward Pass Directly
    def test_17_direct_classifier_forward_pass(self):
        engine = self.engine
        dummy_in = torch.randn(2, 13)
        with torch.no_grad():
            out = engine.classifier(dummy_in)
        self.assertEqual(out.shape, (2, 8))

    # 18. PyTorch Regressor Directly
    def test_18_direct_regressor_forward_pass(self):
        engine = self.engine
        dummy_in = torch.randn(2, 13)
        with torch.no_grad():
            sev, risk = engine.regressor(dummy_in)
        self.assertEqual(sev.shape, (2, 1))
        self.assertEqual(risk.shape, (2, 1))
        self.assertTrue((sev >= 0.0).all() and (sev <= 100.0).all())
        self.assertTrue((risk >= 0.0).all() and (risk <= 1.0).all())

    # 19. Static Frontend Serving
    def test_19_serve_frontend(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Traffic Violation Detection", res.data)

    # 20. 404 Endpoint Handling
    def test_20_not_found(self):
        res = self.client.get("/api/non_existent_route")
        self.assertEqual(res.status_code, 404)

    # 21. Seatbelt Violation Inference
    def test_21_seatbelt_violation(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 50.0,
            "speed_limit": 60.0,
            "seatbelt_detected": 0
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        det = res.get_json()["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Seatbelt Non-Compliance")
        self.assertEqual(det["fine_amount"], 1000)

    # 22. Stop Line Intrusion Inference
    def test_22_stop_line_intrusion(self):
        payload = {
            "vehicle_type": "Car",
            "speed_kmh": 40.0,
            "speed_limit": 60.0,
            "lane_offset_m": 1.45
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        det = res.get_json()["detections"][0]
        self.assertTrue(det["violation_detected"])
        self.assertEqual(det["violation_type"], "Lane Intrusion / Stop Line Cross")
        self.assertEqual(det["fine_amount"], 500)

    # 23. Manual Audit Logging
    def test_23_manual_audit_logging(self):
        h = log_audit_entry("MANUAL_TEST_EVENT", "Testing cryptographic audit logger")
        self.assertEqual(len(h), 64)

    # 24. Dataset File Verification
    def test_24_dataset_file(self):
        data_path = os.path.join(BACKEND_DIR, "..", "data", "traffic_violation_telemetry_6000.csv")
        self.assertTrue(os.path.exists(data_path))
        with open(data_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 6001) # header + 6000 rows

    # 25. Serialized Model Files Verification
    def test_25_model_files_exist(self):
        m_dir = os.path.join(BACKEND_DIR, "models")
        self.assertTrue(os.path.isfile(os.path.join(m_dir, "violation_classifier_weights.pt")))
        self.assertTrue(os.path.isfile(os.path.join(m_dir, "safety_regressor_weights.pt")))
        self.assertTrue(os.path.isfile(os.path.join(m_dir, "traffic_scalers.json")))
        self.assertTrue(os.path.isfile(os.path.join(m_dir, "model_metadata.json")))

    # 26. MVA Fine Table Compliance
    def test_26_mva_fine_structure(self):
        engine = self.engine
        self.assertEqual(engine.fine_map["Speeding"], 2000)
        self.assertEqual(engine.fine_map["Red Light Violation"], 1000)
        self.assertEqual(engine.fine_map["Wrong Way Driving"], 5000)
        self.assertEqual(engine.fine_map["No Helmet / Two-Wheeler"], 1000)
        self.assertEqual(engine.fine_map["Mobile Phone Usage"], 1500)
        self.assertEqual(engine.fine_map["Lane Intrusion / Stop Line Cross"], 500)
        self.assertEqual(engine.fine_map["Seatbelt Non-Compliance"], 1000)

    # 27. Confidence Score Normalization
    def test_27_confidence_score_normalization(self):
        payload = {"vehicle_type": "Car", "speed_kmh": 85.0, "speed_limit": 60.0}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        conf = res.get_json()["detections"][0]["confidence"]
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)

    # 28. Cryptographic Hash Tamper Verification
    def test_28_crypto_hash_tamper_detection(self):
        import hashlib
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, timestamp, action, details, prev_hash, record_hash FROM audit_ledger ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()

        for i in range(1, len(rows)):
            curr = rows[i]
            prev = rows[i - 1]
            self.assertEqual(curr["prev_hash"], prev["record_hash"])
            expected_raw = f"{curr['action']}|{curr['details']}|{curr['timestamp']}|{curr['prev_hash']}"
            expected_hash = hashlib.sha256(expected_raw.encode("utf-8")).hexdigest()
            self.assertEqual(curr["record_hash"], expected_hash)

    # 29. Delivery Van Vehicle Class Handling
    def test_29_delivery_van_analysis(self):
        payload = {"vehicle_type": "Delivery Van", "speed_kmh": 105.0, "speed_limit": 60.0}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        det = res.get_json()["detections"][0]
        self.assertEqual(det["vehicle_type"], "Delivery Van")
        self.assertTrue(det["violation_detected"])

    # 30. Bus Vehicle Class Handling
    def test_30_bus_analysis(self):
        payload = {"vehicle_type": "Bus", "speed_kmh": 50.0, "speed_limit": 60.0}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        det = res.get_json()["detections"][0]
        self.assertEqual(det["vehicle_type"], "Bus")

    # 31. Auto Rickshaw Vehicle Class Handling
    def test_31_auto_rickshaw_analysis(self):
        payload = {"vehicle_type": "Auto Rickshaw", "speed_kmh": 40.0, "speed_limit": 50.0}
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        det = res.get_json()["detections"][0]
        self.assertEqual(det["vehicle_type"], "Auto Rickshaw")

    # 32. Empty Payload Safe Fallback
    def test_32_empty_payload_fallback(self):
        res = self.client.post("/api/analyze", json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("vehicles_detected", data)
        self.assertGreater(data["vehicles_detected"], 0)

if __name__ == "__main__":
    unittest.main()
