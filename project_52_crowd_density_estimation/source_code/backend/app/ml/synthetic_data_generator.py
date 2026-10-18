import torch
import numpy as np

def generate_crowd_synthetic_dataset(num_samples: int = 150):
    """
    Generates synthetic multi-scale crowd scene tensors and ground truth headcounts.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    images = torch.randn(num_samples, 3, 128, 128)
    headcounts = []

    for i in range(num_samples):
        # Vary crowd intensity
        c = int(np.random.randint(15, 450))
        headcounts.append(c)

    return images, torch.tensor(headcounts, dtype=torch.float32)
