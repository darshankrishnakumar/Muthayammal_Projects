import torch
import torch.nn as nn
import torch.nn.functional as F

class SpectralFreshnessCNN(nn.Module):
    """
    Phase 2 Architecture: Multi-cue Spatio-Spectral CNN:
    Stream 1: Color Shift & Oxidation Feature Map (3 x 64 x 64)
    Stream 2: GLCM Texture Entropy & Edge Degradation
    Predicts:
    1. Continuous Freshness Score (0 to 100)
    2. Estimated Remaining Shelf Life in Hours
    3. Deterioration Stage Logits
    """
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2), # 32 x 32
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((2, 2)),
            nn.Flatten()
        )
        self.freshness_head = nn.Linear(64 * 4, 1) # Score
        self.shelflife_head = nn.Linear(64 * 4, 1) # Hours
        self.stage_head = nn.Linear(64 * 4, 3) # Stage 1, 2, 3

    def forward(self, x):
        feat = self.conv(x)
        score = torch.sigmoid(self.freshness_head(feat)) * 100.0
        shelf_life = F.relu(self.shelflife_head(feat)) * 120.0
        stage_logits = self.stage_head(feat)
        return score, shelf_life, stage_logits
