import unittest
import torch
import numpy as np
from backend.app.ml.temporal_sign_model import BiLSTMSignAttentionNet
from backend.app.ml.synthetic_data_generator import generate_sign_synthetic_dataset

class TestSignML(unittest.TestCase):
    def test_synthetic(self):
        X, y = generate_sign_synthetic_dataset(num_samples=20)
        self.assertEqual(X.shape, (20, 30, 54))
        self.assertEqual(y.shape, (20,))

    def test_bilstm_forward(self):
        net = BiLSTMSignAttentionNet()
        dummy = torch.randn(2, 30, 54)
        logits, attn = net(dummy)
        self.assertEqual(logits.shape, (2, 10))
        self.assertEqual(attn.shape, (2, 30, 1))

if __name__ == "__main__":
    unittest.main()
