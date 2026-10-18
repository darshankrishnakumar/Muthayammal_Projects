"""
ML Pipeline and Computer Vision Unit Tests for Project 55.
Tests quality checks, multi-cue extractor, baseline model, and Phase 2 fusion model.
"""

import os
import unittest
import numpy as np
import torch

from backend.app.ml.dataset import VideoQualityChecker, preprocess_frame
from backend.app.ml.multi_cue_extractor import MultiCueFeatureExtractor
from backend.app.ml.baseline_model import BaselineTemporalCNNGRU
from backend.app.ml.temporal_fusion_model import MultiCueTemporalFusionModel, FocalLoss
from backend.app.ml.severity_estimator import SeverityEstimator


class TestMLPipeline(unittest.TestCase):

    def test_video_quality_checker_valid_and_blur(self):
        sharp_frame = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        res_sharp = VideoQualityChecker.assess_frame_quality(sharp_frame)
        self.assertIn("accepted", res_sharp)
        self.assertIn("blur_metric", res_sharp)

        flat_frame = np.ones((240, 320, 3), dtype=np.uint8) * 100
        res_flat = VideoQualityChecker.assess_frame_quality(flat_frame)
        self.assertFalse(res_flat["accepted"])
        self.assertEqual(res_flat["reason"], "Blurry")

    def test_preprocess_frame_shape_and_norm(self):
        raw_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        tensor = preprocess_frame(raw_frame, target_size=(224, 224))
        self.assertEqual(tensor.shape, (3, 224, 224))
        self.assertEqual(tensor.dtype, np.float32)

    def test_multi_cue_feature_extractor(self):
        extractor = MultiCueFeatureExtractor(fps=25.0)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        det1 = [
            {"vehicle_id": 1, "box": [100, 200, 140, 260], "speed": 100.0, "angle": 0.0},
            {"vehicle_id": 2, "box": [105, 205, 145, 265], "speed": 10.0, "angle": 85.0}
        ]
        cues = extractor.extract_cues(frame, det1)

        self.assertIn("trajectory_score", cues)
        self.assertIn("deceleration_score", cues)
        self.assertIn("orientation_score", cues)
        self.assertIn("collision_score", cues)
        self.assertIn("immobility_score", cues)
        self.assertEqual(len(cues["cues_vector"]), 5)

    def test_baseline_model_forward(self):
        model = BaselineTemporalCNNGRU(feature_dim=128, hidden_dim=64)
        model.eval()
        dummy_input = torch.randn(2, 16, 3, 224, 224)
        with torch.no_grad():
            out = model(dummy_input)
        self.assertEqual(out.shape, (2, 1))
        self.assertTrue((out >= 0.0).all() and (out <= 1.0).all())

    def test_phase2_model_forward(self):
        model = MultiCueTemporalFusionModel()
        model.eval()
        dummy_frames = torch.randn(2, 16, 3, 224, 224)
        dummy_kinematics = torch.tensor([
            [0.8, 0.9, 0.7, 0.9, 0.8],
            [0.1, 0.1, 0.0, 0.0, 0.0]
        ], dtype=torch.float32)

        with torch.no_grad():
            out = model(dummy_frames, dummy_kinematics)

        self.assertIn("confidence", out)
        self.assertIn("cue_weights", out)
        self.assertEqual(out["confidence"].shape, (2, 1))
        self.assertEqual(out["cue_weights"].shape, (2, 5))

    def test_severity_estimator(self):
        multi_cues = {
            "trajectory_score": 0.85,
            "deceleration_score": 0.92,
            "orientation_score": 0.78,
            "collision_score": 0.95,
            "immobility_score": 0.90
        }
        camera_meta = {
            "camera_id": "CAM-TEST",
            "roadway": "Interstate 80",
            "lat": 37.8,
            "lon": -122.3,
            "zone": "Fast Lane"
        }
        sev = SeverityEstimator.estimate_severity(
            multi_cues=multi_cues,
            vehicles_count=2,
            camera_meta=camera_meta,
            confidence=0.96
        )

        self.assertIn(sev["severity"], ["Severe", "Critical"])
        self.assertIn(sev["priority"], ["P1-Critical", "P2-High"])
        self.assertTrue(sev["rollover_detected"])
        self.assertGreater(len(sev["recommended_dispatch"]), 0)


if __name__ == "__main__":
    unittest.main()
