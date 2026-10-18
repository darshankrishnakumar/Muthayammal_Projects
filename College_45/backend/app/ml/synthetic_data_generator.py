import numpy as np
import torch

def generate_career_synthetic_dataset(num_samples=150):
    np.random.seed(42)
    cand = np.random.uniform(0, 1, (num_samples, 64)).astype(np.float32)
    role = np.random.uniform(0, 1, (num_samples, 64)).astype(np.float32)
    gaps = np.random.uniform(10, 80, (num_samples, 1)).astype(np.float32)
    return torch.tensor(cand), torch.tensor(role), torch.tensor(gaps)
