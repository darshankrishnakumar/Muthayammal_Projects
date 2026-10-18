import numpy as np
import torch

def generate_manufacturing_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    images = np.random.uniform(0.4, 0.7, (num_samples, 3, 64, 64)).astype(np.float32)
    labels = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=[0.5, 0.15, 0.15, 0.1, 0.1])

    for i in range(num_samples):
        if labels[i] != 0:
            images[i, :, 25:35, 25:35] = 0.05 # Defect dark spot/scratch

    return torch.tensor(images), torch.tensor(labels, dtype=torch.int64)
