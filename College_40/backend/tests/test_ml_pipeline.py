import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineColorFireDetector
from backend.app.ml.dual_stream_fire_model import DualStreamFireSmokeNet
from backend.app.ml.synthetic_data_generator import generate_fire_synthetic_dataset

class TestFireML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineColorFireDetector()
        img = np.random.uniform(0, 1, (3, 64, 64))
        ht, conf = b.detect(img)
        self.assertIn(ht, ["NONE", "FLAME", "SMOKE", "DUAL_HAZARD"])

    def test_dual_stream_net(self):
        net = DualStreamFireSmokeNet()
        img = torch.randn(2, 3, 64, 64)
        flicker = torch.randn(2, 8)
        out = net(img, flicker)
        self.assertEqual(out.shape, (2, 4))

if __name__ == "__main__":
    unittest.main()
