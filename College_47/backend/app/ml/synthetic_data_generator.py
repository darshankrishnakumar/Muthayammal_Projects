import numpy as np
import torch

def generate_classroom_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    cues = np.random.uniform(0, 1, (num_samples, 12)).astype(np.float32)
    scores = np.random.uniform(40, 95, (num_samples, 1)).astype(np.float32)
    return torch.tensor(cues), torch.tensor(scores)
