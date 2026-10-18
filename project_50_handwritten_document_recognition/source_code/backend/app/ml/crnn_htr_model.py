import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepCRNNTextRecognizer(nn.Module):
    """
    Phase 2 Architecture: Deep CRNN-CTC Text Recognizer & Layout Analysis Head:
    Convolutional Map -> Bi-GRU Sequence Modeling -> CTC Logits.
    """
    def __init__(self, num_chars=36, hidden_dim=128):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2), # 32 x 16 x 64
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2), # 64 x 8 x 32
            nn.AdaptiveAvgPool2d((4, 16))
        )
        self.rnn = nn.GRU(64 * 4, hidden_dim, bidirectional=True, batch_first=True)
        self.char_head = nn.Linear(hidden_dim * 2, num_chars)

    def forward(self, x):
        b = x.size(0)
        feats = self.cnn(x) # (B, 64, 4, 16)
        feats = feats.permute(0, 3, 1, 2).contiguous().view(b, 16, -1) # (B, 16, 256)
        out, _ = self.rnn(feats) # (B, 16, 256)
        logits = self.char_head(out) # (B, 16, 36)
        return logits
