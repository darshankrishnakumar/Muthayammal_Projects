import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiHorizonEnergyLSTM(nn.Module):
    """
    Phase 2 Architecture: Multi-Horizon Deep Bi-LSTM Demand Forecaster:
    Ingests 24 past hourly readings (kWh, Temp, Humidity, Occupancy, Tariff) -> Predicts next 24 hours kWh.
    """
    def __init__(self, in_features=5, hidden_dim=64, horizon=24):
        super().__init__()
        self.lstm = nn.LSTM(in_features, hidden_dim, num_layers=2, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Linear(64, horizon)
        )

    def forward(self, x):
        out, _ = self.lstm(x) # (B, T, 2*hidden)
        pooled = out[:, -1, :] # Last hidden
        forecast = self.fc(pooled) # (B, 24)
        return forecast
