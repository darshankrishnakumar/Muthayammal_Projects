import torch

def generate_weather_synthetic_dataset(num_samples: int = 160):
    torch.manual_seed(42)
    # 12 time steps, 7 meteorological parameters
    X = torch.randn(num_samples, 12, 7)
    y = torch.randint(0, 5, (num_samples,))
    return X, y
