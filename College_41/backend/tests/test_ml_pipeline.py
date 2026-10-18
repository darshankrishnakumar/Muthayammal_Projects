import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineColorHistogramGrader
from backend.app.ml.multitask_fruit_model import MultiTaskFruitNet

class TestFruitML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineColorHistogramGrader()
        img = np.random.uniform(0.5, 0.9, (3, 64, 64))
        g, d, pct, conf = b.grade(img)
        self.assertIn(g, ["GRADE_A_PREMIUM", "GRADE_B_STANDARD", "GRADE_C_REJECT"])

    def test_multitask_net(self):
        net = MultiTaskFruitNet()
        dummy = torch.randn(2, 3, 64, 64)
        v, g, d = net(dummy)
        self.assertEqual(v.shape, (2, 4))
        self.assertEqual(g.shape, (2, 3))
        self.assertEqual(d.shape, (2, 5))

if __name__ == "__main__":
    unittest.main()
