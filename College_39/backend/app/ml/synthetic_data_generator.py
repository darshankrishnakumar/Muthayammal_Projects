import numpy as np
import torch

def generate_sign_synthetic_dataset(num_samples=150, seq_len=30, num_features=54):
    np.random.seed(42)
    X = np.random.normal(0.0, 0.5, (num_samples, seq_len, num_features)).astype(np.float32)
    y = np.random.randint(0, 10, size=(num_samples,), dtype=np.int64)

    # Inject distinctive gesture trajectory pattern
    for i in range(num_samples):
        cls = y[i]
        X[i, :, cls*5:(cls+1)*5] += np.sin(np.linspace(0, 3.14, seq_len))[:, None] * 2.5

    return torch.tensor(X), torch.tensor(y)
