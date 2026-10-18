import numpy as np
import torch

def generate_health_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    # 10 clinical features
    vitals = np.random.uniform(0.1, 1.0, (num_samples, 10)).astype(np.float32)
    targets = np.random.uniform(10, 90, (num_samples, 4)).astype(np.float32)
    return torch.tensor(vitals), torch.tensor(targets)
