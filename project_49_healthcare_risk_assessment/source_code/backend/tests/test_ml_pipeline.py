import unittest
import torch
from backend.app.ml.baseline_model import BaselineFraminghamRiskScorer
from backend.app.ml.longitudinal_risk_model import LongitudinalHealthRiskNet

class TestHealthML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineFraminghamRiskScorer()
        res = b.evaluate(58, 148.0, 7.2, 158.0)
        self.assertIn("cardio_risk_pct", res)

    def test_longitudinal_net(self):
        net = LongitudinalHealthRiskNet()
        dummy = torch.randn(2, 10)
        cvd, t2d, htn, ckd = net(dummy)
        self.assertEqual(cvd.shape, (2, 1))
        self.assertEqual(t2d.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
