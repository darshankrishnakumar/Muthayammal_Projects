import numpy as np
import torch

def generate_resume_synthetic_dataset(num_samples=150):
    np.random.seed(42)
    c_emb = np.random.normal(0, 1, (num_samples, 128)).astype(np.float32)
    j_emb = np.random.normal(0, 1, (num_samples, 128)).astype(np.float32)
    scores = np.random.uniform(0.4, 0.98, (num_samples, 1)).astype(np.float32)
    return torch.tensor(c_emb), torch.tensor(j_emb), torch.tensor(scores)
