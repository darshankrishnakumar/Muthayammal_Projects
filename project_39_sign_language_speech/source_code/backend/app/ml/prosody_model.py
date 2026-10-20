import torch
import torch.nn as nn

class SpeechProsodyAcousticRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting Speech Acoustic Prosody:
    - Pitch F0 (Hz) [80.0 to 280.0]
    - Utterance Duration (seconds) [0.4 to 3.0]
    - Speech Energy (dB) [40.0 to 85.0]
    - Synthesis Prosody Quality Score (0 to 100)
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
        self.pitch_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.dur_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.energy_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.quality_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        pitch = 80.0 + self.pitch_head(h) * 200.0
        dur = 0.4 + self.dur_head(h) * 2.6
        energy = 40.0 + self.energy_head(h) * 45.0
        quality = self.quality_head(h) * 100.0
        return pitch, dur, energy, quality
