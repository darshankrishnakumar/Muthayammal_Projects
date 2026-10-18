import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineColorDeltaGrader
from backend.app.ml.spectral_freshness_model import SpectralFreshnessCNN

class TestFreshnessML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineColorDeltaGrader()
        img = np.random.uniform(0.3, 0.8, (3, 64, 64))
        res = b.inspect(img)
        self.assertIn("freshness_score", res)

    def test_spectral_net(self):
        net = SpectralFreshnessCNN()
        dummy = torch.randn(2, 3, 64, 64)
        score, shelf, stage = net(dummy)
        self.assertEqual(score.shape, (2, 1))
        self.assertEqual(shelf.shape, (2, 1))
        self.assertEqual(stage.shape, (2, 3))

if __name__ == "__main__":
    unittest.main()
