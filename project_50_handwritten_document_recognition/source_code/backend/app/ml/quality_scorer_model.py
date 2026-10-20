import torch
import torch.nn as nn
import torch.nn.functional as F

class DocumentQualityAndLexicalScorerNet(nn.Module):
    """
    Phase 2 Architecture: Deep Multi-Task Regressor & Classifier for Document Quality,
    Pen Stroke Degradation, Lexical Confidence, Signature Integrity, and Human Review Escalation.
    Input: 12-dimensional document & handwriting degradation feature vector.
    """
    def __init__(self, input_dim: int = 12, hidden_dim: int = 128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.dropout1 = nn.Dropout(0.15)

        self.fc2 = nn.Linear(hidden_dim, 64)
        self.ln2 = nn.LayerNorm(64)
        self.dropout2 = nn.Dropout(0.10)

        self.fc3 = nn.Linear(64, 32)
        self.ln3 = nn.LayerNorm(32)

        # Multi-task output heads
        self.head_quality = nn.Linear(32, 1)          # Quality Score (0-100)
        self.head_lexical = nn.Linear(32, 1)          # Lexical Confidence (0.0 - 1.0)
        self.head_review_risk = nn.Linear(32, 1)      # Human Review Escalation Probability (0.0 - 1.0)
        self.head_signature = nn.Linear(32, 1)        # Signature Integrity Score (0-100)

    def forward(self, x: torch.Tensor):
        h = F.relu(self.ln1(self.fc1(x)))
        h = self.dropout1(h)
        h = F.relu(self.ln2(self.fc2(h)))
        h = self.dropout2(h)
        h = F.relu(self.ln3(self.fc3(h)))

        quality = torch.sigmoid(self.head_quality(h)) * 100.0
        lexical = torch.sigmoid(self.head_lexical(h))
        review_risk = torch.sigmoid(self.head_review_risk(h))
        signature = torch.sigmoid(self.head_signature(h)) * 100.0

        return {
            "quality_score": quality,
            "lexical_confidence": lexical,
            "review_risk": review_risk,
            "signature_integrity": signature
        }
