import torch
import torch.nn as nn

class CandidateCompetencyRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    - Overall Candidate Match Score (0.0 to 100.0%)
    - Semantic Skill Overlap Ratio (0.0 to 1.0)
    - Experience Fit Rating (0.0 to 10.0 pts)
    - Seniority Compatibility Index (0.0 to 100.0%)
    """
    def __init__(self, in_features=10):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.10)
        )
        self.match_score_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.skill_overlap_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.experience_fit_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.seniority_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        # Scaled competency targets
        match_score = self.match_score_head(h) * 100.0         # [0.0, 100.0]%
        skill_overlap = self.skill_overlap_head(h)             # [0.0, 1.0]
        exp_fit = self.experience_fit_head(h) * 10.0           # [0.0, 10.0]
        seniority = self.seniority_head(h) * 100.0             # [0.0, 100.0]%
        return match_score, skill_overlap, exp_fit, seniority
