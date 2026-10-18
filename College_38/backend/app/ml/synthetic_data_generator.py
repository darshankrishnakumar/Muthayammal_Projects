import numpy as np
import torch

def generate_crack_synthetic_dataset(num_samples=100, img_size=(64, 64)):
    np.random.seed(42)
    images = np.random.uniform(0.3, 0.7, (num_samples, 3, img_size[0], img_size[1])).astype(np.float32)
    masks = np.zeros((num_samples, 1, img_size[0], img_size[1]), dtype=np.float32)

    for i in range(num_samples):
        # Draw synthetic crack line
        x0, y0 = np.random.randint(0, img_size[1]), np.random.randint(0, img_size[0])
        x1, y1 = np.random.randint(0, img_size[1]), np.random.randint(0, img_size[0])
        # Add crack dark trace
        images[i, :, min(y0,y1):max(y0,y1)+1, min(x0,x1):max(x0,x1)+1] = 0.05
        masks[i, 0, min(y0,y1):max(y0,y1)+1, min(x0,x1):max(x0,x1)+1] = 1.0

    return torch.tensor(images), torch.tensor(masks)
