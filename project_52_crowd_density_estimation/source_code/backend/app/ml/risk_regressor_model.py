import torch
import torch.nn as nn

class CrowdOpticalFlowRiskRegressorNet(nn.Module):
    """
    Model 2: Deep Multi-Task Optical Flow Turbulence & Stampede Risk Regressor.
    Ingests 12-dimensional physical optical flow & spatial crowding telemetry.
    Predicts multi-task crowd risk score, optical flow turbulence index,
    headcount correction, and 5-class anomaly classification.
    """
    def __init__(self, input_dim: int = 12):
        super().__init__()
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.10),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True)
        )
        self.head_risk = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_turbulence = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_correction = nn.Linear(32, 1)
        self.head_anomaly = nn.Linear(32, 5)

    def forward(self, x: torch.Tensor):
        feat = self.feature_net(x)
        risk = self.head_risk(feat)
        turb = self.head_turbulence(feat)
        correction = self.head_correction(feat)
        anomaly_logits = self.head_anomaly(feat)
        return {
            "risk_score": risk,
            "turbulence": turb,
            "correction": correction,
            "anomaly_logits": anomaly_logits
        }
