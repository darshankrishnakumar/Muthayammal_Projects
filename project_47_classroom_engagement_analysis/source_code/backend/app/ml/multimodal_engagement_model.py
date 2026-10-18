import torch
import torch.nn as nn
import torch.nn.functional as F

class MultimodalEngagementNet(nn.Module):
    """
    Phase 2 Architecture: Privacy-Preserving Multimodal Engagement Fusion Net:
    Stream 1: Anonymized Facial Expression Features (5-D: Attentive, Neutral, Bored, Distracted, Drowsy)
    Stream 2: Head Pose Orientation Vector (3-D: Yaw, Pitch, Roll)
    Stream 3: Posture & Activity Kinematics (4-D: Taking notes, hand raised, slumping, phone)
    """
    def __init__(self):
        super().__init__()
        self.fusion = nn.Sequential(
            nn.Linear(5 + 3 + 4, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.engagement_score_head = nn.Linear(16, 1) # Continuous 0 to 100
        self.intervention_head = nn.Linear(16, 4) # 0: Keep Pace, 1: Ask Question, 2: Interactive Poll, 3: Short Break

    def forward(self, cues):
        h = self.fusion(cues)
        score = torch.sigmoid(self.engagement_score_head(h)) * 100.0
        interv_logits = self.intervention_head(h)
        return score, interv_logits
