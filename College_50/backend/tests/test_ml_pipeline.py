import unittest
import torch
from backend.app.ml.baseline_model import BaselineOtsuOCR
from backend.app.ml.crnn_htr_model import DeepCRNNTextRecognizer

class TestIDPML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineOtsuOCR()
        res = b.transcribe("NAME")
        self.assertIn("text", res)

    def test_crnn_net(self):
        net = DeepCRNNTextRecognizer()
        dummy = torch.randn(2, 3, 32, 128)
        out = net(dummy)
        self.assertEqual(out.shape, (2, 16, 36))

if __name__ == "__main__":
    unittest.main()
