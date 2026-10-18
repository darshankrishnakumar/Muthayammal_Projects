import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepFPNDefectNet(nn.Module):
    """
    Phase 2 Architecture: Feature Pyramid Network (FPN) Defect Segmenter & Multi-Class Anomaly Head:
    Extracts multi-scale representations to detect micro-scratches and structural dents.
    """
    def __init__(self, num_defect_classes=5): # 0: None, 1: Scratch, 2: Crack, 3: Dent, 4: Missing Component
        super().__init__()
        self.stage1 = nn.Sequential(nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2)) # 32 x 32
        self.stage2 = nn.Sequential(nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2)) # 16 x 16
        self.stage3 = nn.Sequential(nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2)) # 8 x 8

        # FPN Lateral & Smoothing Layers
        self.lat3 = nn.Conv2d(128, 64, 1)
        self.lat2 = nn.Conv2d(64, 64, 1)
        self.smooth = nn.Conv2d(64, 64, 3, padding=1)

        # Defect Segmentation Head
        self.seg_head = nn.Conv2d(64, 1, 1)

        # Defect Category Classifier Head
        self.cls_head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(64, num_defect_classes)
        )

    def forward(self, x):
        c1 = self.stage1(x)
        c2 = self.stage2(c1)
        c3 = self.stage3(c2)

        p3 = self.lat3(c3)
        p2 = self.lat2(c2) + F.interpolate(p3, size=c2.shape[-2:], mode="nearest")
        p2_smooth = self.smooth(p2)

        seg_mask = self.seg_head(p2_smooth)
        defect_logits = self.cls_head(p2_smooth)

        return seg_mask, defect_logits
