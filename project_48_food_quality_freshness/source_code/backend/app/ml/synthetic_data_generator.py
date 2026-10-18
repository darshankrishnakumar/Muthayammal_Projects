import numpy as np
import torch

def generate_food_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    images = np.random.uniform(0.3, 0.8, (num_samples, 3, 64, 64)).astype(np.float32)
    scores = np.random.uniform(20, 98, (num_samples, 1)).astype(np.float32)
    return torch.tensor(images), torch.tensor(scores)
