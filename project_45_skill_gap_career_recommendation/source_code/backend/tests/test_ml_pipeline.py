import unittest
import torch
from backend.app.ml.baseline_model import BaselineSkillOverlapMatcher
from backend.app.ml.collaborative_gap_model import CompetencyGapRecommenderNet

class TestCareerML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineSkillOverlapMatcher()
        res = b.evaluate(["Python", "SQL"], ["Python", "SQL", "Tableau"])
        self.assertIn("readiness_pct", res)

    def test_collaborative_net(self):
        net = CompetencyGapRecommenderNet()
        c = torch.randn(2, 64)
        r = torch.randn(2, 64)
        gap, weeks = net(c, r)
        self.assertEqual(gap.shape, (2, 1))
        self.assertEqual(weeks.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
