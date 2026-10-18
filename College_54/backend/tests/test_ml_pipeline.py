import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselineWeatherMLP
from backend.app.ml.bigru_weather_model import BiGRUWeatherNowcastingNet

class TestWeatherML(unittest.TestCase):
    def test_baseline(self):
        b = BaselineWeatherMLP()
        dummy = np.ones(7) * 20.0
        res = b.predict(dummy)
        self.assertIn("predicted_class", res)

    def test_bigru(self):
        net = BiGRUWeatherNowcastingNet()
        dummy = torch.randn(2, 12, 7)
        out = net(dummy)
        self.assertEqual(out.shape, (2, 5))

if __name__ == "__main__":
    unittest.main()
