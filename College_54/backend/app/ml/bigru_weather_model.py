import torch
import torch.nn as nn

class BiGRUWeatherNowcastingNet(nn.Module):
    """
    Phase 2 SOTA: Multi-Sensor Spatio-Temporal Bidirectional GRU with Temporal Attention.
    Inputs: Sequence of 12 hourly observations across 7 meteorological channels:
    [Temperature, Barometric Pressure, Wind Speed, Humidity, Dew Point, Solar Irradiance, Radar Reflectivity].
    Outputs: 5 severe weather event class logits:
    0: Normal Transition, 1: Heavy Rainfall, 2: Severe Thunderstorm, 3: Gale Wind Storm, 4: Heatwave Spike.
    """
    def __init__(self, input_dim=7, hidden_dim=64, num_classes=5):
        super().__init__()
        self.gru = nn.GRU(
            input_dim,
            hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.Tanh(),
            nn.Linear(32, 1)
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x: (B, seq_len=12, input_dim=7)
        gru_out, _ = self.gru(x) # (B, 12, 128)
        attn_w = torch.softmax(self.attn(gru_out), dim=1) # (B, 12, 1)
        context = torch.sum(gru_out * attn_w, dim=1) # (B, 128)
        logits = self.classifier(context) # (B, 5)
        return logits
