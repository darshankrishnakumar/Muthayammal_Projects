"""Unit and integration tests for data validation, search, scoring, and filters."""

import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_validation import validate_catalogue_schema, validate_image_files
from src.text_recommender import TFIDFSearchEngine
from src.attribute_rules import calculate_attribute_compatibility_score
from src.hybrid_recommender import HybridOutfitRecommender
from src.skin_analysis import analyze_skin_tone_cv
from src.body_measurement import analyze_body_proportions_cv


class TestDressRecommenderAcademicSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.recommender = HybridOutfitRecommender()
        cls.text_engine = TFIDFSearchEngine()

    def test_catalogue_schema_validation(self):
        """Tests that catalogue contains all required 18 schema fields."""
        df = pd.read_csv(config.CATALOGUE_PATH)
        is_valid, errors = validate_catalogue_schema(df)
        self.assertTrue(is_valid, f"Schema validation failed: {errors}")
        self.assertGreaterEqual(len(df), 20)

    def test_budget_hard_filter(self):
        """Tests that budget constraint strictly caps prices."""
        res = self.recommender.recommend(
            query_text="casual shirt",
            budget_max=1500.0,
            top_k=10,
        )
        for it in res["recommendations"]:
            self.assertLessEqual(it["price"], 1500.0)

    def test_category_hard_filter(self):
        """Tests that category filter strictly limits output items."""
        res = self.recommender.recommend(
            preferred_category="T-shirts",
            top_k=10,
        )
        for it in res["recommendations"]:
            self.assertEqual(it["category"], "T-shirts")

    def test_empty_query_fallback(self):
        """Tests that empty text queries return graceful valid suggestions."""
        res = self.text_engine.search(query="", top_k=5)
        self.assertGreater(len(res), 0)

    def test_skin_tone_empty_image(self):
        """Tests computer vision safe handling of None/empty image arrays."""
        res = analyze_skin_tone_cv(None)
        self.assertIn("skin_tone", res)
        self.assertIn("undertone", res)

    def test_body_measurement_manual_override(self):
        """Tests that user-supplied manual measurements override camera approximations."""
        res = analyze_body_proportions_cv(None, manual_shape="Hourglass", manual_ratio=1.0)
        self.assertEqual(res["body_shape"], "Hourglass")
        self.assertFalse(res["is_camera_estimate"])

    def test_attribute_rule_scoring(self):
        """Tests attribute compatibility score produces numeric bounds [0.0, 1.0]."""
        dummy_item = {
            "price": 1200.0,
            "primary_color": "Blue",
            "category": "Shirts",
            "occasion": "Casual",
            "fit": "Regular Fit",
        }
        score, reasons = calculate_attribute_compatibility_score(
            dummy_item,
            skin_tone="Fair",
            undertone="Cool",
            body_shape="Rectangle / Hourglass",
            preferred_colors=["Blue"],
            preferred_occasion="Casual",
            budget_max=2000.0,
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(len(reasons), 0)

    def test_hybrid_ensemble_scoring(self):
        """Tests hybrid multi-modal ensemble output format and components."""
        res = self.recommender.recommend(
            query_text="linen casual shirt",
            skin_tone="Medium",
            undertone="Warm",
            top_k=5,
        )
        self.assertIn("recommendations", res)
        self.assertIn("weights_used", res)
        self.assertGreater(len(res["recommendations"]), 0)
        top_item = res["recommendations"][0]
        self.assertIn("final_score", top_item)
        self.assertIn("component_scores", top_item)
        self.assertIn("summary_reason", top_item)


if __name__ == "__main__":
    unittest.main()
