import torch
import torch.nn as nn
import torch.nn.functional as F

class DualStreamFireSmokeNet(nn.Module):
    """
    Phase 2 Deep Learning Architecture:
    Dual-Stream Spatio-Temporal ConvNet with Flame Flicker Gating & Smoke Diffusion Tracking.
    Stream 1: Spatial Chromatic & Texture Feature Map (3 x 64 x 64)
    Stream 2: Temporal Flicker FFT Oscillation & Flow Dynamics (8 temporal bins)
    """
    def __init__(self, num_classes=4): # 0: None, 1: Smoke, 2: Flame, 3: Dual Hazard
        super().__init__()
        # Spatial Stream
        self.spatial_stream = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2), # 32 x 32
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten(),
            nn.Linear(64 * 16, 128),
            nn.ReLU()
        )
        # Temporal Flicker Stream
        self.temporal_stream = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU()
        )
        # Cross-Attention / Fusion Classifier
        self.fusion_head = nn.Sequential(
            nn.Linear(128 + 64, 64),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(64, num_classes)
        )

    def forward(self, images, temporal_flicker):
        s_feat = self.spatial_stream(images) # (B, 128)
        t_feat = self.temporal_stream(temporal_flicker) # (B, 64)
        fused = torch.cat([s_feat, t_feat], dim=-1)
        logits = self.fusion_head(fused)
        return logits
