"""
Automated QA Verification Suite for Project 30
AI-Based IoT Device Anomaly Detection for Smart Home Security
28 Comprehensive Unit & Integration Tests (100% Pass Rate Target)
"""

import os
import sys
import json
import unittest
import numpy as np
import torch

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "backend"))
DATA_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "data"))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import get_connection, verify_wal_status, get_all_devices, get_security_stats
from anomaly_engine import get_engine, IoTAnomalyAutoencoder, IoTThreatClassifier

class TestProject30IoTAnomalySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.engine = get_engine()

    def test_01_health_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["port"], 5030)
        self.assertEqual(data["connected_devices"], 6)
        self.assertIn("models", data)
        self.assertIn("database", data)

    def test_02_models_loaded(self):
        self.assertIsNotNone(self.engine.ae_model)
        self.assertIsNotNone(self.engine.clf_model)
        self.assertTrue(os.path.isfile(os.path.join(BACKEND_DIR, "iot_autoencoder_weights.pt")))
        self.assertTrue(os.path.isfile(os.path.join(BACKEND_DIR, "iot_classifier_weights.pt")))

    def test_03_sqlite_wal_mode(self):
        wal = verify_wal_status()
        self.assertEqual(wal["journal_mode"], "WAL")
        self.assertTrue(wal["wal_enabled"])

    def test_04_devices_seed_count(self):
        devices = get_all_devices()
        self.assertEqual(len(devices), 6)
        names = {d["name"] for d in devices}
        self.assertIn("Smart IP Camera", names)
        self.assertIn("Smart Thermostat", names)
        self.assertIn("Smart Lock", names)
        self.assertIn("Smart TV 4K", names)
        self.assertIn("Edge Wi-Fi Router", names)
        self.assertIn("Smart Voice Assistant", names)

    def test_05_devices_endpoint(self):
        res = self.client.get("/api/devices")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 6)

    def test_06_device_metadata_fields(self):
        devices = get_all_devices()
        for d in devices:
            self.assertIn("ip_address", d)
            self.assertIn("protocol", d)
            self.assertIn("norm_packet", d)
            self.assertIn("norm_rate", d)
            self.assertIn("quarantine_status", d)

    def test_07_analyze_normal_scenario(self):
        res = self.client.post("/api/analyze", json={"device": "Smart IP Camera", "scenario": "normal"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["attack_type"], "Normal Baseline Traffic")
        self.assertFalse(data["is_anomaly"])
        self.assertEqual(data["quarantine_status"], "ONLINE")
        self.assertLess(data["anomaly_score"], 40)

    def test_08_analyze_attack_scenario(self):
        res = self.client.post("/api/analyze", json={"device": "Smart IP Camera", "scenario": "attack"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["is_anomaly"])
        self.assertNotEqual(data["attack_type"], "Normal Baseline Traffic")
        self.assertIn("reconstruction_error", data)

    def test_09_analyze_device_selection(self):
        res = self.client.post("/api/analyze", json={"device": "Smart Thermostat", "scenario": "normal"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["device"], "Smart Thermostat")
        self.assertEqual(data["ip_address"], "192.168.1.18")

    def test_10_analyze_all_devices(self):
        devices = get_all_devices()
        for d in devices:
            res = self.client.post("/api/analyze", json={"device": d["name"], "scenario": "normal"})
            self.assertEqual(res.status_code, 200)

    def test_11_threat_signatures_endpoint(self):
        res = self.client.get("/api/signatures")
        self.assertEqual(res.status_code, 200)
        sigs = res.get_json()
        self.assertEqual(len(sigs), 6)
        self.assertIn("Mirai Botnet C&C", sigs)
        self.assertIn("SYN Flood DDoS", sigs)
        self.assertIn("Covert Data Exfiltration", sigs)

    def test_12_critical_threat_isolation(self):
        res = self.client.post("/api/analyze", json={"device": "Smart Lock", "scenario": "attack"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        if data["severity"] == "CRITICAL":
            self.assertEqual(data["quarantine_status"], "ISOLATED")

    def test_13_quarantine_override_endpoint(self):
        res = self.client.post("/api/device/quarantine", json={"device": "Smart TV 4K", "status": "ISOLATED"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["quarantine_status"], "ISOLATED")

        # Reset back
        res2 = self.client.post("/api/device/quarantine", json={"device": "Smart TV 4K", "status": "ONLINE"})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()["quarantine_status"], "ONLINE")

    def test_14_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_inspections", data)
        self.assertIn("anomalies_detected", data)
        self.assertIn("system_security_index", data)

    def test_15_history_retrieval(self):
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_16_history_limit_parameter(self):
        res = self.client.get("/api/history?limit=3")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertLessEqual(len(data), 3)

    def test_17_loss_curve_endpoint(self):
        res = self.client.get("/api/loss-curve")
        self.assertEqual(res.status_code, 200)
        points = res.get_json()
        self.assertIsInstance(points, list)
        if len(points) > 0:
            self.assertIn("reconstruction_error", points[0])
            self.assertIn("threshold", points[0])

    def test_18_raw_features_inference(self):
        raw_feats = [1200.0, 50.0, 0.05, 4.0, 20.0, 60000.0, 0.03, 0.01]
        res = self.client.post("/api/analyze", json={"device": "Smart IP Camera", "features": raw_feats})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("attack_type", data)
        self.assertIn("anomaly_score", data)

    def test_19_audit_logs_endpoint(self):
        res = self.client.get("/api/audit-logs")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)

    def test_20_metrics_endpoint(self):
        res = self.client.get("/api/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("metadata", data)
        self.assertIn("wal_status", data)

    def test_21_autoencoder_tensor_shapes(self):
        t_in = torch.randn(1, 8)
        rec, latent = self.engine.ae_model(t_in)
        self.assertEqual(rec.shape, (1, 8))
        self.assertEqual(latent.shape, (1, 4))

    def test_22_classifier_tensor_shapes(self):
        t_in = torch.randn(1, 9)
        logits = self.engine.clf_model(t_in)
        self.assertEqual(logits.shape, (1, 6))

    def test_23_scalers_file_format(self):
        sc_path = os.path.join(BACKEND_DIR, "iot_scalers.json")
        self.assertTrue(os.path.isfile(sc_path))
        with open(sc_path, "r", encoding="utf-8") as f:
            sc = json.load(f)
        self.assertEqual(len(sc["mean"]), 8)
        self.assertEqual(len(sc["std"]), 8)
        self.assertEqual(len(sc["feature_names"]), 8)

    def test_24_dataset_file_exists(self):
        csv_path = os.path.join(DATA_DIR, "iot_network_telemetry.csv")
        self.assertTrue(os.path.isfile(csv_path))
        import csv
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(len(header), 13) # flow_id, device_name, traffic_type, traffic_idx, is_anomaly + 8 features
            rows = list(reader)
            self.assertEqual(len(rows), 5500)

    def test_25_inference_latency_bounds(self):
        res = self.client.post("/api/analyze", json={"device": "Smart Voice Assistant", "scenario": "normal"})
        self.assertEqual(res.status_code, 200)
        self.assertLess(res.get_json()["latency_ms"], 50)

    def test_26_static_file_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"IoT Sensor Anomaly Detection", res.data)

    def test_27_404_handling(self):
        res = self.client.get("/non_existent_random_endpoint")
        self.assertEqual(res.status_code, 404)

    def test_28_db_persistence_integrity(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anomaly_inspections")
        count_before = cursor.fetchone()[0]
        conn.close()

        self.client.post("/api/analyze", json={"device": "Edge Wi-Fi Router", "scenario": "normal"})

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anomaly_inspections")
        count_after = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count_after, count_before + 1)

if __name__ == "__main__":
    unittest.main()
