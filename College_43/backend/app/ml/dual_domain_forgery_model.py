import torch
import torch.nn as nn
import torch.nn.functional as F

class DualDomainForgeryNet(nn.Module):
    """
    Phase 2 Architecture: Multi-Domain Forensic CNN:
    Stream 1: Spatial ELA Residual Stream (3 x 64 x 64)
    Stream 2: Frequency DCT / Noise Variance Stream (3 x 64 x 64)
    Generates pixel-wise tampering heatmap and forgery verdict logits.
    """
    def __init__(self):
        super().__init__()
        self.spatial_stream = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2), # 32 x 32
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten()
        )
        self.freq_stream = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten()
        )
        # Fusion Classifier (0: Authentic, 1: Copy-Move, 2: Splicing, 3: Text Erasure)
        self.classifier = nn.Sequential(
            nn.Linear(64 * 16 * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 4)
        )

    def forward(self, img_spatial, img_freq):
        s_feat = self.spatial_stream(img_spatial)
        f_feat = self.freq_stream(img_freq)
        fused = torch.cat([s_feat, f_feat], dim=-1)
        logits = self.classifier(fused)
        return logits
