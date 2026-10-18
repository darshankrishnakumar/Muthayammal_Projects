import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineBlobCrowdCounter
from backend.app.ml.csrnet_crowd_model import CSRNetCrowdDensityNet

class TestCrowdML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineBlobCrowdCounter()
        dummy = np.random.rand(100, 100)
        count = b.estimate_count(dummy)
        res = b.detect_anomaly(count, 0.4)
        self.assertIn("baseline_count", res)

    def test_csrnet(self):
        net = CSRNetCrowdDensityNet()
        dummy = torch.randn(2, 3, 128, 128)
        dmap, logits = net(dummy)
        self.assertEqual(dmap.shape, (2, 1, 16, 16))
        self.assertEqual(logits.shape, (2, 5))

if __name__ == "__main__":
    unittest.main()
