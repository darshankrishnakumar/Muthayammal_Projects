import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineTemplateDiffDetector
from backend.app.ml.fpn_defect_model import DeepFPNDefectNet

class TestMfgML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineTemplateDiffDetector()
        img = np.random.uniform(0.4, 0.7, (3, 64, 64))
        res = b.inspect(img)
        self.assertIn(res["verdict"], ["PASS", "REJECT"])

    def test_fpn_net(self):
        net = DeepFPNDefectNet()
        dummy = torch.randn(2, 3, 64, 64)
        seg, cls_logits = net(dummy)
        self.assertEqual(seg.shape, (2, 1, 16, 16))
        self.assertEqual(cls_logits.shape, (2, 5))

if __name__ == "__main__":
    unittest.main()
