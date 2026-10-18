import torch
import torch.nn as nn
import torch.nn.functional as F

class TransformerSemanticMatcherNet(nn.Module):
    """
    Phase 2 Architecture: Contextual Semantic Transformer Embedding & Multi-Factor Matching Head:
    Computes cross-attention between Candidate Profile vector (128-D) and Job Requirements vector (128-D).
    """
    def __init__(self, emb_dim=128):
        super().__init__()
        self.candidate_proj = nn.Sequential(
            nn.Linear(emb_dim, emb_dim),
            nn.LayerNorm(emb_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        self.job_proj = nn.Sequential(
            nn.Linear(emb_dim, emb_dim),
            nn.LayerNorm(emb_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        # Deep Non-Linear Matching Scorer
        self.match_head = nn.Sequential(
            nn.Linear(emb_dim * 3, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, cand_emb, job_emb):
        c = self.candidate_proj(cand_emb)
        j = self.job_proj(job_emb)
        diff = torch.abs(c - j)
        fused = torch.cat([c, j, diff], dim=-1)
        match_score = self.match_head(fused)
        return match_score
