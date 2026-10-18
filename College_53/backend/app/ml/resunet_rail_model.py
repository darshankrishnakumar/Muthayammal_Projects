import torch
import torch.nn as nn

class ResUNetRailDefectSegmenter(nn.Module):
    """
    Phase 2 SOTA: Multi-Class Semantic Segmentation ResUNet for Rail Tracks.
    Predicts pixel-level defect masks across 6 classes:
    0: Clean Rail, 1: Surface Crack, 2: Missing Fastener, 3: Abnormal Joint,
    4: Surface Deterioration, 5: Foreign Obstacle.
    """
    def __init__(self, in_channels=3, num_classes=6):
        super().__init__()
        # Encoder
        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1)

        # Bottleneck
        self.bridge = nn.Conv2d(128, 128, kernel_size=3, padding=1)

        # Decoder with Skip Connections
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.up2 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec2 = nn.Conv2d(64, 32, kernel_size=3, padding=1)

        self.classifier = nn.Conv2d(32, num_classes, kernel_size=1)

    def forward(self, x):
        e1 = torch.relu(self.conv1(x))
        e2 = torch.relu(self.conv2(e1))
        e3 = torch.relu(self.conv3(e2))

        b = torch.relu(self.bridge(e3))

        d1 = self.up1(b)
        d1 = torch.relu(self.dec1(torch.cat([d1, e2], dim=1)))

        d2 = self.up2(d1)
        d2 = torch.relu(self.dec2(torch.cat([d2, e1], dim=1)))

        out = self.classifier(d2)
        return out
