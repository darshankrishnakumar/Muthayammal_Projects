import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiTaskFruitNet(nn.Module):
    """
    Phase 2 Architecture: Multi-task CNN for Variety, Quality Grade, and Defect Type.
    """
    def __init__(self, num_varieties=4, num_grades=3, num_defects=5):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2), # 32 x 32
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2), # 16 x 16
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
        self.variety_head = nn.Linear(128, num_varieties)
        self.grade_head = nn.Linear(128, num_grades)
        self.defect_head = nn.Linear(128, num_defects)

    def forward(self, x):
        feats = self.backbone(x)
        var_logits = self.variety_head(feats)
        grade_logits = self.grade_head(feats)
        defect_logits = self.defect_head(feats)
        return var_logits, grade_logits, defect_logits
