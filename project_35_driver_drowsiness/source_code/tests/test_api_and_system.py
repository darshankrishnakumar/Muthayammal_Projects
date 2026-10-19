import unittest
import os
import sys
import json
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from database import get_connection, init_db

class TestDriverDrowsinessSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_health_endpoint_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["port"], 5035)

    def test_02_health_endpoint_metadata(self):
        res = self.client.get("/api/health")
        data = res.get_json()
        self.assertIn("classifier_accuracy", data)
        self.assertIn("vigilance_mae", data)
        self.assertIn("microsleep_mae", data)
        self.assertIn("monitored_drivers", data)

    def test_03_driver_profiles_listing(self):
        res = self.client.get("/api/drivers")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 5)
        ids = [d["driver_id"] for d in data["drivers"]]
        self.assertIn("DRV-801", ids)
        self.assertIn("DRV-804", ids)

    def test_04_driver_profile_schema(self):
        res = self.client.get("/api/drivers")
        drivers = res.get_json()["drivers"]
        first = drivers[0]
        for key in ["driver_id", "driver_name", "vehicle_type", "route_corridor", "shift_type"]:
            self.assertIn(key, first)

    def test_05_inference_alert_state(self):
        # Nominal alert driver (high EAR ~0.36, low MAR ~0.15)
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-801",
            "ear": 0.38,
            "mar": 0.15,
            "blink_duration_ms": 140.0,
            "perclos_pct": 3.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["drowsiness_state"], "Alert")
        self.assertFalse(data["alert_required"])
        self.assertGreaterEqual(data["vigilance_score"], 80.0)

    def test_06_inference_severe_drowsiness(self):
        # Severe drowsiness (very low EAR ~0.15, high MAR ~0.65, long blink, high perclos)
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-804",
            "ear": 0.14,
            "mar": 0.68,
            "blink_duration_ms": 780.0,
            "perclos_pct": 55.0,
            "head_pitch_deg": -18.5
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["drowsiness_state"], "Severely Drowsy")
        self.assertTrue(data["alert_required"])
        self.assertEqual(data["severity"], "CRITICAL")
        self.assertIn("EMERGENCY STOP", data["recommended_action"])

    def test_07_audit_contract_ear_mar_compatibility(self):
        # Contract required by test_audit_verification.py
        res = self.client.post("/api/analyze", json={"ear": 0.18, "mar": 0.65})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("drowsiness_state", data)
        self.assertIn(data["drowsiness_state"], ["Alert", "Slightly Drowsy", "Moderately Drowsy", "Severely Drowsy"])

    def test_08_microsleep_risk_range(self):
        res = self.client.post("/api/analyze", json={"ear": 0.15, "mar": 0.60})
        data = res.get_json()
        risk = data["microsleep_risk"]
        self.assertGreaterEqual(risk, 0.0)
        self.assertLessEqual(risk, 1.0)

    def test_09_vigilance_score_range(self):
        res = self.client.post("/api/analyze", json={"ear": 0.35, "mar": 0.18})
        data = res.get_json()
        score = data["vigilance_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_10_softmax_probabilities_sum(self):
        res = self.client.post("/api/analyze", json={"ear": 0.28, "mar": 0.25})
        data = res.get_json()
        probs = data["probabilities"]
        total_p = sum(probs.values())
        self.assertAlmostEqual(total_p, 1.0, places=2)

    def test_11_database_wal_mode(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("PRAGMA journal_mode;")
        mode = c.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_12_telemetry_persistence(self):
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-802",
            "ear": 0.32,
            "mar": 0.20
        })
        tel_id = res.get_json()["id"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM fatigue_telemetry WHERE telemetry_id = ?", (tel_id,))
        row = c.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["driver_id"], "DRV-802")

    def test_13_drowsiness_alert_persistence(self):
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-803",
            "ear": 0.15,
            "mar": 0.60
        })
        alert_id = res.get_json()["alert_id"]
        self.assertIsNotNone(alert_id)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM drowsiness_alerts WHERE alert_id = ?", (alert_id,))
        row = c.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["driver_id"], "DRV-803")

    def test_14_alert_acknowledgment(self):
        # Create alert first
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-805",
            "ear": 0.14,
            "mar": 0.70
        })
        alert_id = res.get_json()["alert_id"]

        # Acknowledge
        ack_res = self.client.post(f"/api/alerts/{alert_id}/acknowledge")
        self.assertEqual(ack_res.status_code, 200)
        self.assertEqual(ack_res.get_json()["status"], "acknowledged")

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT driver_acknowledged FROM drowsiness_alerts WHERE alert_id = ?", (alert_id,))
        ack_val = c.fetchone()[0]
        conn.close()
        self.assertEqual(ack_val, 1)

    def test_15_trips_listing(self):
        res = self.client.get("/api/trips")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 5)
        first = data["trips"][0]
        self.assertIn("safety_grade", first)
        self.assertIn("distance_km", first)

    def test_16_alerts_listing(self):
        res = self.client.get("/api/alerts")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("alerts", data)

    def test_17_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_frames", data)
        self.assertIn("drowsiness_alerts", data)
        self.assertIn("alert_rate", data)
        self.assertIn("average_vigilance_score", data)

    def test_18_legacy_log_endpoint(self):
        res = self.client.get("/api/log")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)

    def test_19_audit_ledger_hashing(self):
        res = self.client.get("/api/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 0)
        latest = data["audit_logs"][0]
        self.assertEqual(len(latest["verification_hash"]), 64) # SHA256 hex length

    def test_20_model_metadata_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["model_name"], "DeepResidualFatigueAndVigilanceNet")
        self.assertIn("classifier_accuracy", data)

    def test_21_empty_payload_fallback(self):
        # API should safely handle empty JSON payload without crashing
        res = self.client.post("/api/analyze", json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("drowsiness_state", data)

    def test_22_head_pose_nodding_fatigue(self):
        # Driver head nodding down (pitch = -24 degrees)
        res = self.client.post("/api/analyze", json={
            "driver_id": "DRV-801",
            "ear": 0.22,
            "mar": 0.35,
            "head_pitch_deg": -24.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data["drowsiness_state"], ["Moderately Drowsy", "Severely Drowsy"])

    def test_23_inference_latency(self):
        start = time.time()
        res = self.client.post("/api/analyze", json={"ear": 0.34, "mar": 0.16})
        dur = (time.time() - start) * 1000.0
        self.assertEqual(res.status_code, 200)
        self.assertLess(dur, 250.0) # Sub-250ms latency

    def test_24_static_file_routing(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"html", res.data.lower())

    def test_25_invalid_route_404(self):
        res = self.client.get("/api/nonexistent_endpoint")
        self.assertEqual(res.status_code, 404)

    def test_26_multiple_driver_attribution(self):
        d1 = self.client.post("/api/analyze", json={"driver_id": "DRV-801", "ear": 0.35}).get_json()
        d2 = self.client.post("/api/analyze", json={"driver_id": "DRV-804", "ear": 0.35}).get_json()
        self.assertEqual(d1["driver_id"], "DRV-801")
        self.assertEqual(d2["driver_id"], "DRV-804")

    def test_27_dataset_file_present(self):
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "driver_fatigue_telemetry_6000.csv"))
        self.assertTrue(os.path.exists(data_path))

    def test_28_model_weights_present(self):
        clf_w = os.path.abspath(os.path.join(backend_dir, "models", "fatigue_classifier_weights.pt"))
        reg_w = os.path.abspath(os.path.join(backend_dir, "models", "vigilance_regressor_weights.pt"))
        self.assertTrue(os.path.exists(clf_w))
        self.assertTrue(os.path.exists(reg_w))

if __name__ == "__main__":
    unittest.main()
