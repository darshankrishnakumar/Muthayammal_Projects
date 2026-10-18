import torch
import torch.nn as nn
import torch.nn.functional as F

class CompetencyGapRecommenderNet(nn.Module):
    """
    Phase 2 Architecture: Multi-Task Competency Vector Space Embedding:
    Maps 64-D candidate skill profile and 64-D target role profile into latent competency space.
    Predicts:
    1. Quantified Skill-Gap Score (0 - 100)
    2. Estimated Weeks to Role Readiness
    3. Trajectory Relevance Probability
    """
    def __init__(self, skill_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(skill_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        self.gap_head = nn.Linear(32, 1) # Gap score
        self.weeks_head = nn.Linear(32, 1) # Estimated weeks

    def forward(self, cand_profile, role_profile):
        fused = torch.cat([cand_profile, role_profile], dim=-1)
        latent = self.encoder(fused)
        gap = torch.sigmoid(self.gap_head(latent)) * 100.0
        weeks = F.relu(self.weeks_head(latent)) * 16.0 + 4.0
        return gap, weeks
