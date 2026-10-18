import numpy as np
import torch

def generate_forgery_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    spatial = np.random.uniform(0.3, 0.8, (num_samples, 3, 64, 64)).astype(np.float32)
    freq = np.random.uniform(0.1, 0.5, (num_samples, 3, 64, 64)).astype(np.float32)
    labels = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.4, 0.2, 0.2, 0.2])

    for i in range(num_samples):
        if labels[i] != 0: # Forged: inject high frequency boundary noise
            spatial[i, :, 20:35, 20:35] = 0.95
            freq[i, :, 20:35, 20:35] = 0.90

    return torch.tensor(spatial), torch.tensor(freq), torch.tensor(labels, dtype=torch.int64)
