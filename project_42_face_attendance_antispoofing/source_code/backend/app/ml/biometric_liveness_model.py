import torch
import torch.nn as nn

class BiometricLivenessQualityRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    - Presentation Attack Risk Score (0.0 to 100.0%)
    - Micro-Tremor Optical Flow Index (0.0 to 1.0)
    - Facial Illumination Homogeneity Entropy (0.0 to 10.0)
    - Biometric Verification Match Score (0.0 to 100.0%)
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
        self.spoof_risk_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.micro_tremor_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.entropy_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.match_score_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        # Scaled physical and forensic biometric targets
        spoof_risk = self.spoof_risk_head(h) * 100.0           # [0.0, 100.0]%
        micro_tremor = self.micro_tremor_head(h)               # [0.0, 1.0]
        illum_entropy = self.entropy_head(h) * 10.0            # [0.0, 10.0]
        match_score = self.match_score_head(h) * 100.0         # [0.0, 100.0]%
        return spoof_risk, micro_tremor, illum_entropy, match_score
