import torch
import torch.nn as nn
import torch.nn.functional as F

class MultimodalEngagementNet(nn.Module):
    """
    Phase 2 Architecture: Multimodal Engagement Fusion Net:
    Input: 12-dimensional multimodal feature vector:
    - 5-D Facial Action Unit activations (Attentive, Neutral, Bored, Distracted, Drowsy)
    - 3-D Head Pose Orientation Vector (Yaw, Pitch, Roll)
    - 4-D Posture & Activity Kinematics (Note-taking, Hand raised, Slumping, Phone use)
    """
    def __init__(self):
        super().__init__()
        self.fusion = nn.Sequential(
            nn.Linear(12, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.LayerNorm(32),
            nn.GELU()
        )
        self.engagement_score_head = nn.Sequential(
            nn.Linear(32, 16),
            nn.GELU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        self.intervention_head = nn.Sequential(
            nn.Linear(32, 16),
            nn.GELU(),
            nn.Linear(16, 4)
        )

    def forward(self, cues):
        h = self.fusion(cues)
        score = self.engagement_score_head(h) * 100.0
        interv_logits = self.intervention_head(h)
        return score, interv_logits
