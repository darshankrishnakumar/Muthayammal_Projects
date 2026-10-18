import numpy as np
import torch

def generate_fruit_synthetic_dataset(num_samples=150):
    np.random.seed(42)
    images = np.random.uniform(0.3, 0.9, (num_samples, 3, 64, 64)).astype(np.float32)
    varieties = np.random.randint(0, 4, size=num_samples)
    grades = np.random.randint(0, 3, size=num_samples)
    defects = np.random.randint(0, 5, size=num_samples)

    for i in range(num_samples):
        if grades[i] == 2: # Reject: inject dark spot
            images[i, :, 25:35, 25:35] = 0.05

    return torch.tensor(images), torch.tensor(varieties), torch.tensor(grades), torch.tensor(defects)
