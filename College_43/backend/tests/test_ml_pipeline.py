import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineELADetector
from backend.app.ml.dual_domain_forgery_model import DualDomainForgeryNet

class TestForgeryML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineELADetector()
        img = np.random.uniform(0, 1, (3, 64, 64))
        res = b.detect_tampering(img)
        self.assertIn(res["verdict"], ["FORGED", "AUTHENTIC"])

    def test_dual_domain_net(self):
        net = DualDomainForgeryNet()
        s = torch.randn(2, 3, 64, 64)
        f = torch.randn(2, 3, 64, 64)
        out = net(s, f)
        self.assertEqual(out.shape, (2, 4))

if __name__ == "__main__":
    unittest.main()
