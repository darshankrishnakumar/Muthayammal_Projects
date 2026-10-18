import torch
import torch.nn as nn
import torch.nn.functional as F

class BiLSTMSignAttentionNet(nn.Module):
    """
    Phase 2 Deep Learning Architecture:
    Bidirectional LSTM with Self-Attention for Spatio-Temporal Sign Landmark Sequences.
    Input: (Batch, Sequence_Len=30, Num_Landmarks=54)
    """
    def __init__(self, in_features=54, hidden_dim=128, num_classes=10):
        super().__init__()
        self.fc_in = nn.Linear(in_features, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers=2, bidirectional=True, batch_first=True, dropout=0.2)
        
        # Self-Attention Mechanism
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        h = F.relu(self.fc_in(x)) # (B, T, hidden)
        lstm_out, _ = self.lstm(h) # (B, T, 2*hidden)
        
        # Attention weights over time steps
        attn_weights = F.softmax(self.attn(lstm_out), dim=1) # (B, T, 1)
        context = torch.sum(lstm_out * attn_weights, dim=1) # (B, 2*hidden)
        
        logits = self.classifier(context)
        return logits, attn_weights
