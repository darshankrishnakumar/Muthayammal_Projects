import unittest
import torch
import numpy as np
from backend.app.ml.baseline_model import BaselinePersistenceEnergyForecaster
from backend.app.ml.lstm_energy_model import MultiHorizonEnergyLSTM

class TestEnergyML(unittest.TestCase):
    def test_baseline(self):
        b = BaselinePersistenceEnergyForecaster()
        dummy = np.ones(24) * 400.0
        out = b.forecast_24h(dummy)
        self.assertEqual(len(out), 24)

    def test_lstm_net(self):
        net = MultiHorizonEnergyLSTM()
        dummy = torch.randn(2, 24, 5)
        out = net(dummy)
        self.assertEqual(out.shape, (2, 24))

if __name__ == "__main__":
    unittest.main()
