import numpy as np
import torch

def generate_idp_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    images = np.random.uniform(0.1, 0.9, (num_samples, 3, 32, 128)).astype(np.float32)
    labels = np.random.randint(0, 36, size=(num_samples, 16), dtype=np.int64)
    return torch.tensor(images), torch.tensor(labels)
