import os
import sys
import unittest
import sqlite3
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PKG_DIR = os.path.join(SOURCE_DIR, "personalized_outfit_recommendation_system")
sys.path.insert(0, SOURCE_DIR)
sys.path.insert(0, PKG_DIR)

from server import app
import config
from backend.profile_manager import ProfileManager
from backend.recommendation_engine import HybridRecommendationEngine

class TestProject18APIAndSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.profile_mgr = ProfileManager(config.DB_PATH)
        cls.engine = HybridRecommendationEngine()

    def test_health_endpoint(self):
        """Verify /health returns status ok, port 5018, and loaded models."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["port"], 5018)
        self.assertIn("gbm_pipeline", data["models"])
        self.assertGreater(data["catalogue_items_count"], 0)

    def test_catalogue_endpoint(self):
        """Verify /api/catalogue returns clothing items list."""
        resp = self.client.get("/api/catalogue")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["count"], 20)
        first_item = data["data"][0]
        self.assertIn("outfit_id", first_item)
        self.assertIn("outfit_name", first_item)
        self.assertIn("price", first_item)

    def test_models_evaluation_endpoint(self):
        """Verify /api/models returns GBM metrics."""
        resp = self.client.get("/api/models")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        metrics = data["metrics"]
        self.assertIn("accuracy", metrics)
        self.assertIn("classes", metrics)
        self.assertIn("confusion_matrix", metrics)
        self.assertEqual(len(metrics["classes"]), 11)

    def test_history_endpoint(self):
        """Verify /api/history returns recorded SQLite logs."""
        resp = self.client.get("/api/history?user_id=user_default")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["data"], list)

    def test_recommendation_endpoint_valid_run(self):
        """Verify /api/recommend returns ranked outfit recommendations with scores."""
        payload = {
            "skin_tone": "Medium",
            "undertone": "Warm",
            "body_shape": "Hourglass",
            "preferred_styles": "Classic",
            "preferred_occasions": "Formal",
            "preferred_colours": "Navy Blue",
            "preferred_categories": "All",
            "budget_max": "7000",
            "query_text": "crisp white oxford shirt"
        }
        resp = self.client.post("/api/recommend", data=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["recommendations"]), 0)
        self.assertGreater(data["latency_ms"], 0.0)

        top_rec = data["recommendations"][0]
        self.assertIn("outfit_id", top_rec)
        self.assertIn("final_score", top_rec)
        self.assertGreaterEqual(top_rec["final_score"], 0.0)
        self.assertLessEqual(top_rec["final_score"], 1.0)
        self.assertIn("component_scores", top_rec)

    def test_sqlite_transaction_logging(self):
        """Verify recommendation execution writes entry into SQLite RECOMMENDATION_HISTORY."""
        payload = {
            "skin_tone": "Olive",
            "undertone": "Warm",
            "body_shape": "Pear",
            "preferred_styles": "Classic",
            "preferred_occasions": "Ethnic",
            "preferred_colours": "Crimson",
            "preferred_categories": "All",
            "budget_max": "12000",
            "query_text": "silk saree"
        }
        resp = self.client.post("/api/recommend", data=payload)
        self.assertEqual(resp.status_code, 200)

        # Check SQLite
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT outfit_id, outfit_name, match_score FROM RECOMMENDATION_HISTORY ORDER BY recommendation_id DESC LIMIT 1;")
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertGreater(len(row[0]), 0)

    def test_attribute_compatibility_bounds(self):
        """Verify attribute compatibility score is bounded in [0, 1]."""
        dummy_row = {
            "suitable_skin_tones": "fair, medium, olive",
            "suitable_undertones": "warm, neutral",
            "compatible_body_shapes": "hourglass, pear"
        }
        import pandas as pd
        series = pd.Series(dummy_row)
        score = self.engine.calculate_attribute_compatibility(
            series,
            skin_tone="Fair",
            undertone="Warm",
            body_shape="Hourglass"
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertAlmostEqual(score, 1.0, places=1)

    def test_profile_manager_validation_limits(self):
        """Verify human measurement validation logic in profile manager."""
        valid, msg = self.profile_mgr.validate_measurements(
            height_cm=170,
            shoulder_cm=42,
            chest_cm=95,
            waist_cm=75,
            hip_cm=98
        )
        self.assertTrue(valid)
        self.assertIsNone(msg)

        invalid, err_msg = self.profile_mgr.validate_measurements(height_cm=350)
        self.assertFalse(invalid)
        self.assertIn("Height", err_msg)

if __name__ == "__main__":
    unittest.main()
