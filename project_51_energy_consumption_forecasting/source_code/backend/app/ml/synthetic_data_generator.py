import numpy as np
import torch

def generate_energy_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    X = np.random.uniform(0.2, 0.9, (num_samples, 24, 5)).astype(np.float32)
    y = np.random.uniform(300, 600, (num_samples, 24)).astype(np.float32)
    return torch.tensor(X), torch.tensor(y)
