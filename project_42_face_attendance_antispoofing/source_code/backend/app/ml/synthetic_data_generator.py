import numpy as np
import torch

def generate_face_synthetic_dataset(num_samples=160):
    np.random.seed(42)
    faces = np.random.uniform(0.2, 0.8, (num_samples, 3, 64, 64)).astype(np.float32)
    labels = np.random.choice([0, 1], size=num_samples, p=[0.3, 0.7]) # 0: spoof, 1: real

    for i in range(num_samples):
        if labels[i] == 0: # Spoof: flatten high frequency textures
            faces[i] = np.mean(faces[i], axis=0, keepdims=True)

    return torch.tensor(faces), torch.tensor(labels, dtype=torch.int64)
