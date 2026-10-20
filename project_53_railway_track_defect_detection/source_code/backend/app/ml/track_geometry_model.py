import torch
import torch.nn as nn

class RailTrackGeometryAndDegradationRegressorNet(nn.Module):
    """
    Model 2: Deep Multi-Task Track Geometry & Mechanical Degradation Regressor.
    Ingests 12-dimensional physical track geometry, dynamic vibration, and thermal telemetry.
    Predicts Track Quality Index (TQI), speed restriction, derailment risk score,
    and 3-class defect severity classification (Minor, Moderate, Critical).
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
        self.head_tqi = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_speed = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_derailment = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_severity = nn.Linear(32, 3) # Minor, Moderate, Critical

    def forward(self, x: torch.Tensor):
        feat = self.feature_net(x)
        tqi = self.head_tqi(feat) * 100.0 # 0-100 scale
        speed = self.head_speed(feat) * 160.0 # 0-160 km/h speed limit
        derail = self.head_derailment(feat) # 0.0 - 1.0 probability
        severity_logits = self.head_severity(feat)
        return {
            "track_quality_index": tqi,
            "speed_restriction_kmh": speed,
            "derailment_risk": derail,
            "severity_logits": severity_logits
        }
