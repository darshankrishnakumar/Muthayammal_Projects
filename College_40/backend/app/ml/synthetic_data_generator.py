import numpy as np
import torch

def generate_fire_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    images = np.random.uniform(0.1, 0.6, (num_samples, 3, 64, 64)).astype(np.float32)
    flicker = np.random.uniform(0, 1, (num_samples, 8)).astype(np.float32)
    labels = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.4, 0.2, 0.2, 0.2])

    for i in range(num_samples):
        if labels[i] == 1: # Smoke: gray diffuse
            images[i, :, 20:40, 20:40] = 0.55
            flicker[i] = np.array([0.2, 0.3, 0.2, 0.1, 0.1, 0.05, 0.02, 0.01], dtype=np.float32)
        elif labels[i] == 2: # Flame: high red/orange, high flicker 8-15 Hz
            images[i, 0, 25:35, 25:35] = 0.95
            images[i, 1, 25:35, 25:35] = 0.60
            images[i, 2, 25:35, 25:35] = 0.05
            flicker[i] = np.array([0.1, 0.2, 0.8, 0.9, 0.85, 0.4, 0.1, 0.05], dtype=np.float32)
        elif labels[i] == 3: # Dual Hazard
            images[i, 0, 20:45, 20:45] = 0.90
            images[i, 1, 20:45, 20:45] = 0.50
            flicker[i] = np.array([0.3, 0.5, 0.9, 0.95, 0.9, 0.6, 0.3, 0.1], dtype=np.float32)

    return torch.tensor(images), torch.tensor(flicker), torch.tensor(labels, dtype=torch.int64)
