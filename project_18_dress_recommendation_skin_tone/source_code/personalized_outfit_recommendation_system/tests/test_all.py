"""Comprehensive Automated Test Suite for AI Outfit Recommendation System.

Covers:
- TF-IDF text matching & ranking
- Gradient Boosting training, prediction, and edge cases
- SQLite Database & ProfileManager CRUD and Cascade
- Body shape & Skin tone CV analysis edge cases
- Hybrid Recommendation Engine filtering & scoring
- Graceful fallbacks for missing files & invalid inputs
"""

import os
import sys
import tempfile
import unittest
import cv2
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.dataset_loader import load_catalogue
from backend.tfidf_recommender import TFIDFRecommender
from backend.gbm_recommender import (
    train_model,
    load_model,
    validate_input_features,
    predict_preferred_category,
    return_prediction_results,
)
from backend.database import init_db, get_db_connection
from backend.profile_manager import ProfileManager
from backend.skin_tone_analysis import analyze_skin_tone
from backend.body_shape_analysis import analyze_body_shape, estimate_silhouette_ratio
from backend.recommendation_engine import HybridRecommendationEngine


class TestTFIDFRecommender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue()
        cls.recommender = TFIDFRecommender(cls.catalogue)

    def test_corpus_and_matrix_built(self):
        self.assertGreater(len(self.recommender.corpus), 0)
        self.assertIsNotNone(self.recommender.tfidf_matrix)
        self.assertEqual(self.recommender.tfidf_matrix.shape[0], len(self.catalogue))

    def test_query_construction(self):
        q = self.recommender.build_query_string(
            user_query_text="cotton shirt",
            preferred_styles="Classic",
            preferred_colours="White",
            preferred_occasions="Formal",
        )
        self.assertIn("cotton shirt", q)
        self.assertIn("style classic", q)
        self.assertIn("colour white", q)
        self.assertIn("occasion formal", q)

    def test_recommendation_ranking_and_filters(self):
        q = self.recommender.build_query_string(user_query_text="wedding silk saree")
        recs = self.recommender.recommend(q, occasion_filter="Wedding", top_k=5)
        self.assertGreater(len(recs), 0)
        # Should be sorted descending by similarity score
        scores = [r["tfidf_similarity_score"] for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))
        # Hard filter check
        for r in recs:
            self.assertEqual(r["occasion"], "Wedding")

    def test_empty_query_fallback(self):
        sims = self.recommender.compute_similarity("")
        self.assertEqual(len(sims), len(self.catalogue))
        self.assertTrue(np.all(sims == 0.0))


class TestGradientBoosting(unittest.TestCase):
    def test_validate_input_features(self):
        # Valid features
        valid_dict = {
            "body_shape": "Triangle (Pear)",
            "skin_tone": "Fair",
            "undertone": "Warm",
            "preferred_style": "Classic",
            "preferred_occasion": "Formal",
            "preferred_colour": "Blue",
            "budget_max": 5000.0,
        }
        ok, err = validate_input_features(valid_dict)
        self.assertTrue(ok)
        self.assertIsNone(err)

        # Missing feature
        invalid_dict = valid_dict.copy()
        del invalid_dict["budget_max"]
        ok, err = validate_input_features(invalid_dict)
        self.assertFalse(ok)
        self.assertIn("Missing required feature", err)

        # Invalid budget
        invalid_budget = valid_dict.copy()
        invalid_budget["budget_max"] = -100
        ok, err = validate_input_features(invalid_budget)
        self.assertFalse(ok)

    def test_training_and_prediction(self):
        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tf_mod:
            m_path = tf_mod.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf_eval:
            e_path = tf_eval.name

        try:
            eval_res = train_model(save_path=m_path, eval_save_path=e_path)
            self.assertIn("accuracy", eval_res)
            self.assertIn("f1_weighted", eval_res)
            self.assertGreater(eval_res["test_samples"], 0)

            # Test inference
            pipeline = load_model(m_path)
            self.assertIsNotNone(pipeline)

            sample_input = {
                "body_shape": "Rectangle / Hourglass",
                "skin_tone": "Fair",
                "undertone": "Cool",
                "preferred_style": "Traditional",
                "preferred_occasion": "Wedding",
                "preferred_colour": "Red",
                "budget_max": 9000.0,
            }
            pred, conf = predict_preferred_category(sample_input, model=pipeline)
            self.assertIsNotNone(pred)
            self.assertGreater(conf, 0.0)

            full_res = return_prediction_results(sample_input, model=pipeline)
            self.assertTrue(full_res["success"])
            self.assertEqual(full_res["predicted_category"], pred)
            self.assertIn("disclaimer", full_res)
        finally:
            if os.path.exists(m_path):
                os.remove(m_path)
            if os.path.exists(e_path):
                os.remove(e_path)


class TestDatabaseAndProfileManager(unittest.TestCase):
    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        self.pm = ProfileManager(self.temp_db_path)

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_user_creation_and_update(self):
        u = self.pm.get_or_create_user("user_123", "John Doe")
        self.assertEqual(u["user_id"], "user_123")
        self.assertEqual(u["display_name"], "John Doe")

        self.pm.update_profile("user_123", "Johnny")
        u_updated = self.pm.get_or_create_user("user_123")
        self.assertEqual(u_updated["display_name"], "Johnny")

    def test_measurements_manual_vs_estimate(self):
        # Save manual
        ok, err = self.pm.save_measurements("user_123", height_cm=180.0, waist_cm=85.0, source="manual")
        self.assertTrue(ok)
        latest_manual = self.pm.get_latest_measurements("user_123", source="manual")
        self.assertEqual(latest_manual["height_cm"], 180.0)
        self.assertEqual(latest_manual["measurement_source"], "manual")

        # Save estimate without overwriting manual
        ok, err = self.pm.save_measurements("user_123", height_cm=178.0, waist_cm=88.0, source="image_estimate")
        self.assertTrue(ok)
        latest_est = self.pm.get_latest_measurements("user_123", source="image_estimate")
        self.assertEqual(latest_est["height_cm"], 178.0)
        self.assertEqual(latest_est["measurement_source"], "image_estimate")

        # Re-verify manual record remained distinct
        latest_manual_again = self.pm.get_latest_measurements("user_123", source="manual")
        self.assertEqual(latest_manual_again["height_cm"], 180.0)

    def test_measurement_range_validation(self):
        # Height out of range
        ok, err = self.pm.save_measurements("user_123", height_cm=350.0)
        self.assertFalse(ok)
        self.assertIn("Height must be between", err)

        # Negative waist
        ok, err = self.pm.save_measurements("user_123", waist_cm=-10.0)
        self.assertFalse(ok)

    def test_preferences_and_cascade_delete(self):
        self.pm.save_preferences(
            "user_123",
            preferred_styles="Modern",
            preferred_colours="Black",
            preferred_occasions="Party",
            preferred_categories="Dresses",
            budget_min=2000.0,
            budget_max=8000.0,
        )
        prefs = self.pm.get_preferences("user_123")
        self.assertEqual(prefs["preferred_styles"], "Modern")
        self.assertEqual(prefs["budget_max"], 8000.0)

        # Record recommendation
        self.pm.record_recommendation("user_123", "OUTFIT_007", "Emerald Dress", "Dresses", 0.92, "Party wear")
        self.assertEqual(len(self.pm.get_recommendation_history("user_123")), 1)

        # Cascade deletion
        self.pm.delete_profile("user_123")
        self.assertIsNone(self.pm.get_preferences("user_123"))
        self.assertIsNone(self.pm.get_latest_measurements("user_123"))
        self.assertEqual(len(self.pm.get_recommendation_history("user_123")), 0)


class TestComputerVisionEdgeCases(unittest.TestCase):
    def test_skin_tone_empty_image(self):
        res = analyze_skin_tone(None)
        self.assertEqual(res["skin_tone"], "Unknown")
        self.assertFalse(res["face_detected"])

    def test_skin_tone_synthetic_face(self):
        # Create synthetic warm peach square image
        img = np.full((300, 300, 3), (160, 190, 235), dtype=np.uint8)
        res = analyze_skin_tone(img)
        self.assertIn(res["skin_tone"], ["Fair", "Medium/Wheatish", "Dusky/Dark"])
        self.assertIn(res["undertone"], ["Warm", "Cool", "Neutral"])

    def test_body_shape_empty_image(self):
        res = analyze_body_shape(None)
        self.assertEqual(res["body_shape"], "Unknown")
        self.assertFalse(res["is_calibrated_cm"])

    def test_body_shape_synthetic_silhouette(self):
        # Create synthetic silhouette image (white person silhouette on black background)
        img = np.zeros((400, 300, 3), dtype=np.uint8)
        # Shoulders
        cv2.rectangle(img, (90, 80), (210, 150), (255, 255, 255), -1)
        # Hips
        cv2.rectangle(img, (100, 180), (200, 270), (255, 255, 255), -1)
        res = analyze_body_shape(img)
        self.assertIn(res["body_shape"], ["Triangle (Pear)", "Rectangle / Hourglass", "Inverted Triangle"])
        self.assertFalse(res["is_calibrated_cm"])


class TestHybridRecommendationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HybridRecommendationEngine()

    def test_recommendation_with_text_only(self):
        res = self.engine.recommend(
            query_text="sharp corporate business suit",
            preferred_styles="Formal",
            preferred_occasions="Formal",
            budget_max=10000.0,
            top_k=3,
        )
        self.assertIn("recommendations", res)
        recs = res["recommendations"]
        self.assertGreater(len(recs), 0)
        # Clip weight should have reallocated cleanly since user_img is None
        self.assertEqual(res["applied_weights"]["clip"], 0.0)
        self.assertAlmostEqual(sum(res["applied_weights"].values()), 1.0, places=2)

    def test_recommendation_hard_constraints(self):
        # Budget constraint test
        res = self.engine.recommend(
            preferred_occasions="Casual",
            budget_max=1000.0,  # Only items <= 1000 INR
            top_k=10,
        )
        for r in res["recommendations"]:
            self.assertLessEqual(r["price"], 1000.0)

    def test_recommendation_with_image(self):
        # Create a sample synthetic user image
        dummy_img = np.full((300, 300, 3), (180, 160, 140), dtype=np.uint8)
        res = self.engine.recommend(
            user_img_bgr=dummy_img,
            query_text="evening dress",
            preferred_occasions="Party",
            top_k=3,
        )
        recs = res["recommendations"]
        self.assertGreater(len(recs), 0)
        self.assertGreater(res["applied_weights"]["clip"], 0.0)
        for r in recs:
            self.assertIn("final_score", r)
            self.assertGreaterEqual(r["final_score"], 0.0)
            self.assertLessEqual(r["final_score"], 1.0)
            self.assertIn("summary_reason", r)


if __name__ == "__main__":
    unittest.main()
