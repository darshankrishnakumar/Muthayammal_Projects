import torch
import torch.nn as nn

class ManufacturingDefectRiskRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    1. Defect Severity Score (0.0 to 100.0%)
    2. Defect Area Percentage (0.0 to 100.0%)
    3. Surface Roughness Ra (0.1 to 10.0 um)
    4. Pneumatic Ejection Confidence (0.0 to 100.0%)
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
        self.severity_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.area_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.roughness_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.ejection_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        severity = self.severity_head(h) * 100.0          # [0.0, 100.0]%
        area = self.area_head(h) * 100.0                  # [0.0, 100.0]%
        roughness = self.roughness_head(h) * 9.9 + 0.1    # [0.1, 10.0] um
        ejection = self.ejection_head(h) * 100.0          # [0.0, 100.0]%
        return severity, area, roughness, ejection
