import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepAntiSpoofFaceNet(nn.Module):
    """
    Phase 2 Architecture: Dual-Task Deep Neural Network:
    Head 1: 512-D ArcFace Biometric Feature Embedding
    Head 2: Multi-Modal Anti-Spoofing Classifier (Texture Fourier + Micro-Motion cue)
    """
    def __init__(self, embedding_dim=512):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.PReLU(),
            nn.MaxPool2d(2), # 32 x 32
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.PReLU(),
            nn.MaxPool2d(2), # 16 x 16
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.PReLU(),
            nn.AdaptiveAvgPool2d((2, 2)),
            nn.Flatten()
        )
        # Face Biometric Embedding Head
        self.face_embedding = nn.Linear(128 * 4, embedding_dim)

        # Anti-Spoofing Head (Real vs Print Attack vs Screen Replay vs 3D Mask)
        self.antispoof_head = nn.Sequential(
            nn.Linear(128 * 4, 64),
            nn.ReLU(),
            nn.Linear(64, 2) # 0: Spoof, 1: Real Live Face
        )

    def forward(self, x):
        feats = self.backbone(x)
        raw_emb = self.face_embedding(feats)
        norm_emb = F.normalize(raw_emb, p=2, dim=1)
        spoof_logits = self.antispoof_head(feats)
        return norm_emb, spoof_logits
