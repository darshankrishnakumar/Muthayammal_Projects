import unittest
import torch
from backend.app.ml.baseline_model import BaselineTFIDFMatcher
from backend.app.ml.transformer_matching_model import TransformerSemanticMatcherNet

class TestScreeningML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineTFIDFMatcher()
        res = b.match(["Python", "SQL"], ["Python", "PyTorch", "Docker"])
        self.assertIn("keyword_overlap_score", res)

    def test_transformer_matcher(self):
        net = TransformerSemanticMatcherNet()
        c = torch.randn(2, 128)
        j = torch.randn(2, 128)
        out = net(c, j)
        self.assertEqual(out.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
