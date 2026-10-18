import torch

def generate_rail_synthetic_dataset(num_samples: int = 140):
    torch.manual_seed(42)
    images = torch.randn(num_samples, 3, 128, 128)
    masks = torch.randint(0, 6, (num_samples, 128, 128))
    return images, masks
