import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineCannyMorphDefectDetector
from backend.app.ml.resunet_rail_model import ResUNetRailDefectSegmenter

class TestRailML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineCannyMorphDefectDetector()
        dummy = np.random.rand(100, 100)
        res = b.detect_defects(dummy)
        self.assertIn("defect_detected", res)

    def test_resunet(self):
        net = ResUNetRailDefectSegmenter()
        dummy = torch.randn(2, 3, 128, 128)
        out = net(dummy)
        self.assertEqual(out.shape, (2, 6, 128, 128))

if __name__ == "__main__":
    unittest.main()
