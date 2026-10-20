import torch
import torch.nn as nn

class FirePropagationThermalRiskRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    - Flame Core Temperature (deg C) [150.0 to 950.0]
    - Smoke Plume Expansion Velocity (m/s) [0.2 to 8.5]
    - Evacuation Urgency Index (0.0 to 100.0)
    - Carbon Monoxide (CO) Toxicity Index (ppm) [10.0 to 800.0]
    """
    def __init__(self, in_features=10):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.10)
        )
        self.temp_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.plume_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.urgency_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.co_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        flame_temp = 150.0 + self.temp_head(h) * 800.0
        plume_vel = 0.2 + self.plume_head(h) * 8.3
        urgency = self.urgency_head(h) * 100.0
        co_ppm = 10.0 + self.co_head(h) * 790.0
        return flame_temp, plume_vel, urgency, co_ppm
