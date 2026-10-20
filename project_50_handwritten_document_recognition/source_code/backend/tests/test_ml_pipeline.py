import os
import sys
import unittest
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.ml.baseline_model import BaselineOtsuOCR
from backend.app.ml.crnn_htr_model import DeepCRNNTextRecognizer, VOCABULARY

class TestIDPML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineOtsuOCR()
        res = b.transcribe("NAME")
        self.assertIn("text", res)

    def test_crnn_net(self):
        net = DeepCRNNTextRecognizer()
        dummy = torch.randn(2, 3, 32, 128)
        out = net(dummy)
        self.assertEqual(out.shape, (2, 16, len(VOCABULARY)))

if __name__ == "__main__":
    unittest.main()
