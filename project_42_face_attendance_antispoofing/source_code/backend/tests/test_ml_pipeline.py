import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineEigenFaceRecognizer
from backend.app.ml.antispoof_arcface_model import DeepAntiSpoofFaceNet

class TestAttendanceML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineEigenFaceRecognizer()
        face = np.random.uniform(0, 1, (3, 64, 64))
        res = b.verify(face)
        self.assertIn(res["liveness"], ["REAL", "SPOOF_DETECTED"])

    def test_arcface_net(self):
        net = DeepAntiSpoofFaceNet()
        dummy = torch.randn(2, 3, 64, 64)
        emb, spoof = net(dummy)
        self.assertEqual(emb.shape, (2, 512))
        self.assertEqual(spoof.shape, (2, 2))

if __name__ == "__main__":
    unittest.main()
