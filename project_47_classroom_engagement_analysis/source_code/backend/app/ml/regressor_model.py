import torch
import torch.nn as nn

class AttentionForecastRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    1. Overall Class Attention Score (0.0 to 100.0%)
    2. Student Drowsiness Risk (0.0 to 100.0%)
    3. Teacher Intervention Urgency Index (0.0 to 100.0%)
    4. Predicted Interactive Participation Rate (0.0 to 100.0%)
    """
    def __init__(self, in_features=10):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.12),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.08)
        )
        self.attention_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.drowsiness_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.intervention_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.participation_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        attention = self.attention_head(h) * 100.0
        drowsiness = self.drowsiness_head(h) * 100.0
        intervention = self.intervention_head(h) * 100.0
        participation = self.participation_head(h) * 100.0
        return attention, drowsiness, intervention, participation
