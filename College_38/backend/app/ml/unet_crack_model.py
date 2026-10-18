import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )
    def forward(self, x):
        return self.net(x)

class ResUNetCrackSegmenter(nn.Module):
    """
    Phase 2 SOTA Architecture:
    Residual U-Net for pixel-wise road crack segmentation & multi-head severity regression.
    """
    def __init__(self, in_channels=3):
        super().__init__()
        self.inc = DoubleConv(in_channels, 16)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(16, 32))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(32, 64))
        self.up1 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.conv_up1 = DoubleConv(64, 32)
        self.up2 = nn.ConvTranspose2d(32, 16, 2, stride=2)
        self.conv_up2 = DoubleConv(32, 16)
        self.outc = nn.Conv2d(16, 1, 1)

        # Global Severity Head
        self.severity_head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3) # Low, Medium, High severity logits
        )

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)

        # Segmentation branch
        u1 = self.up1(x3)
        u1 = torch.cat([u1, x2], dim=1)
        u1 = self.conv_up1(u1)
        u2 = self.up2(u1)
        u2 = torch.cat([u2, x1], dim=1)
        u2 = self.conv_up2(u2)
        mask_logits = self.outc(u2)

        # Severity classification branch
        sev_logits = self.severity_head(x3)

        return mask_logits, sev_logits
