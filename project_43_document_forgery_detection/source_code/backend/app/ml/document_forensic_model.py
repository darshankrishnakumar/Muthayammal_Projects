import torch
import torch.nn as nn

class DocumentForensicRiskRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    - Document Forgery Risk Score (0.0 to 100.0%)
    - Tampered Bounding Area Percentage (0.0 to 50.0%)
    - ELA Compression Discrepancy Index (0.0 to 10.0)
    - Spectral 2D-DCT Noise Energy (0.0 to 1.0)
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
        self.forgery_risk_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.tampered_area_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.ela_discrepancy_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.dct_noise_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        # Scaled forensic targets
        forgery_risk = self.forgery_risk_head(h) * 100.0        # [0.0, 100.0]%
        tampered_area = self.tampered_area_head(h) * 50.0       # [0.0, 50.0]%
        ela_disc = self.ela_discrepancy_head(h) * 10.0          # [0.0, 10.0]
        dct_noise = self.dct_noise_head(h)                      # [0.0, 1.0]
        return forgery_risk, tampered_area, ela_disc, dct_noise
