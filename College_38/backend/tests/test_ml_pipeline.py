import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineCrackDetector
from backend.app.ml.unet_crack_model import ResUNetCrackSegmenter
from backend.app.ml.severity_evaluator import PavementSeverityEvaluator

class TestCrackML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineCrackDetector(threshold=0.3)
        dummy = np.random.uniform(0, 1, (3, 64, 64))
        m = b.predict_mask(dummy)
        self.assertEqual(m.shape, (64, 64))

    def test_unet(self):
        net = ResUNetCrackSegmenter()
        x = torch.randn(2, 3, 64, 64)
        mask_out, sev_out = net(x)
        self.assertEqual(mask_out.shape, (2, 1, 64, 64))
        self.assertEqual(sev_out.shape, (2, 3))

    def test_evaluator(self):
        mask = np.zeros((100, 100))
        mask[40:50, 40:60] = 1.0
        metrics = PavementSeverityEvaluator.calculate_metrics(mask)
        self.assertIn("pci_score", metrics)
        self.assertIn("severity_level", metrics)

if __name__ == "__main__":
    unittest.main()
