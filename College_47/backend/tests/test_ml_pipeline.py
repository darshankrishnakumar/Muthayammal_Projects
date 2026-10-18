import unittest
import torch
from backend.app.ml.baseline_model import BaselineFacialCountEngagement
from backend.app.ml.multimodal_engagement_model import MultimodalEngagementNet

class TestEngagementML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineFacialCountEngagement()
        res = b.estimate(28, 30, 0.1)
        self.assertIn("engagement_score", res)

    def test_multimodal_net(self):
        net = MultimodalEngagementNet()
        dummy = torch.randn(2, 12)
        score, interv = net(dummy)
        self.assertEqual(score.shape, (2, 1))
        self.assertEqual(interv.shape, (2, 4))

if __name__ == "__main__":
    unittest.main()
