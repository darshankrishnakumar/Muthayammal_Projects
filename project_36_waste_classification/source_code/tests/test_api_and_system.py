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

class TestWasteClassificationSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_health_endpoint_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["port"], 5036)

    def test_02_health_endpoint_metadata(self):
        res = self.client.get("/api/health")
        data = res.get_json()
        self.assertIn("classifier_accuracy", data)
        self.assertIn("recyclability_mae", data)
        self.assertIn("contamination_mae", data)
        self.assertIn("monitored_conveyors", data)

    def test_03_categories_listing(self):
        res = self.client.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 6)
        names = [c["category_name"] for c in data["categories"]]
        for expected in ["Plastic", "Glass", "Metal", "Paper", "Cardboard", "Organic"]:
            self.assertIn(expected, names)

    def test_04_conveyors_listing(self):
        res = self.client.get("/api/conveyors")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 3)
        ids = [c["conveyor_id"] for c in data["conveyors"]]
        self.assertIn("CONV-A1", ids)
        self.assertIn("CONV-B2", ids)
        self.assertIn("CONV-C3", ids)

    def test_05_classify_plastic_bottle(self):
        res = self.client.post("/api/classify", json={"item_type": "plastic_bottle", "conveyor_id": "CONV-A1"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Plastic")
        self.assertIn("BIN-A", data["diversion_bin"])
        self.assertGreaterEqual(data["confidence_pct"], 90.0)

    def test_06_classify_aluminum_can(self):
        res = self.client.post("/api/classify", json={"item_type": "aluminum_can", "conveyor_id": "CONV-A1"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Metal")
        self.assertIn("BIN-C", data["diversion_bin"])

    def test_07_classify_glass_bottle(self):
        res = self.client.post("/api/classify", json={"item_type": "glass_bottle", "conveyor_id": "CONV-A1"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Glass")
        self.assertIn("BIN-B", data["diversion_bin"])

    def test_08_classify_office_paper(self):
        res = self.client.post("/api/classify", json={"item_type": "office_paper", "conveyor_id": "CONV-B2"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Paper")
        self.assertIn("BIN-D", data["diversion_bin"])

    def test_09_classify_corrugated_box(self):
        res = self.client.post("/api/classify", json={"item_type": "corrugated_box", "conveyor_id": "CONV-B2"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Cardboard")
        self.assertIn("BIN-E", data["diversion_bin"])

    def test_10_classify_food_scrap(self):
        res = self.client.post("/api/classify", json={"item_type": "food_scrap", "conveyor_id": "CONV-C3"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Organic")
        self.assertIn("BIN-F", data["diversion_bin"])

    def test_11_audit_contract_plastic_bottle(self):
        # Strict contract required by test_audit_verification.py
        res = self.client.post("/api/classify", json={"item_type": "plastic_bottle"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("category", data)
        self.assertEqual(data["category"], "Plastic")

    def test_12_softmax_probabilities_sum(self):
        res = self.client.post("/api/classify", json={"item_type": "plastic_bottle"})
        data = res.get_json()
        probs = data["probabilities"]
        total_p = sum(probs.values())
        self.assertAlmostEqual(total_p, 1.0, places=2)

    def test_13_recyclability_score_bounds(self):
        res = self.client.post("/api/classify", json={"item_type": "aluminum_can"})
        data = res.get_json()
        score = data["recyclability_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_14_contamination_risk_bounds(self):
        res = self.client.post("/api/classify", json={"item_type": "food_scrap"})
        data = res.get_json()
        risk = data["contamination_risk"]
        self.assertGreaterEqual(risk, 0.0)
        self.assertLessEqual(risk, 1.0)

    def test_15_database_wal_mode(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("PRAGMA journal_mode;")
        mode = c.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_16_item_persistence(self):
        res = self.client.post("/api/classify", json={"item_type": "pet_clamshell", "conveyor_id": "CONV-A1"})
        item_id = res.get_json()["item_id"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM classified_items WHERE item_id = ?", (item_id,))
        row = c.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["category"], "Plastic")

    def test_17_recycling_batches_listing(self):
        res = self.client.get("/api/batches")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 5)
        first = data["batches"][0]
        self.assertIn("batch_id", first)
        self.assertIn("dispatched_to", first)

    def test_18_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_items_classified", data)
        self.assertIn("average_recyclability_score", data)
        self.assertIn("category_distribution", data)

    def test_19_history_endpoint(self):
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("history", data)

    def test_20_audit_ledger_hashing(self):
        res = self.client.get("/api/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 0)
        latest = data["audit_logs"][0]
        self.assertEqual(len(latest["verification_hash"]), 64)

    def test_21_model_metadata_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["model_name"], "DeepResidualWasteClassificationAndRecyclabilityNet")
        self.assertIn("classifier_accuracy", data)

    def test_22_empty_payload_fallback(self):
        res = self.client.post("/api/classify", json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("category", data)

    def test_23_custom_spectroscopic_features(self):
        # Override with high-density and metal-like features
        res = self.client.post("/api/classify", json={
            "item_type": "unknown_material",
            "features": {
                "density_g_cm3": 7.85,
                "spectral_reflectance_nir": 0.95,
                "magnetic_susceptibility": 0.90,
                "rigidity_modulus_gpa": 120.0
            }
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["category"], "Metal")

    def test_24_static_file_routing(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"html", res.data.lower())

    def test_25_invalid_route_404(self):
        res = self.client.get("/api/nonexistent_route")
        self.assertEqual(res.status_code, 404)

    def test_26_response_latency(self):
        start = time.time()
        res = self.client.post("/api/classify", json={"item_type": "plastic_bottle"})
        dur = (time.time() - start) * 1000.0
        self.assertEqual(res.status_code, 200)
        self.assertLess(dur, 200.0)

    def test_27_dataset_file_present(self):
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "waste_classification_telemetry_6000.csv"))
        self.assertTrue(os.path.exists(data_path))

    def test_28_model_weights_present(self):
        clf_w = os.path.abspath(os.path.join(backend_dir, "models", "waste_classifier_weights.pt"))
        reg_w = os.path.abspath(os.path.join(backend_dir, "models", "recyclability_regressor_weights.pt"))
        self.assertTrue(os.path.exists(clf_w))
        self.assertTrue(os.path.exists(reg_w))

if __name__ == "__main__":
    unittest.main()
