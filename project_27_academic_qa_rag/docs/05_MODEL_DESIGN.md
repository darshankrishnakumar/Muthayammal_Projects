# 05. Deep Neural Model Design: PyTorch Bi-Encoder (PROJECT-027)

## Neural Network Specification
```python
class AcademicDenseEncoder(nn.Module):
    def __init__(self, vocab_size=1142, embed_dim=64, hidden_dim=128, out_dim=128):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, mode='mean')
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.10)
        self.fc2 = nn.Linear(hidden_dim, out_dim)

    def forward(self, x):
        h = self.embedding(x)
        h = self.dropout(self.relu(self.fc1(h)))
        out = self.fc2(h)
        return F.normalize(out, p=2, dim=-1)
```

## Loss Function & Optimization
- **Loss:** Triplet Contrastive Margin Loss: $L(q, d^+, d^-) = \max(0, m - \cos(e_q, e_{d^+}) + \cos(e_q, e_{d^-}))$ with margin $m = 0.35$.
- **Optimizer:** Adam ($	ext{lr} = 0.003, eta_1=0.9, eta_2=0.999$).
- **Epochs:** 25 with early convergence monitoring.
- **Weights File:** `source_code/backend/rag_embedding_weights.pt` (under 2.6 MB).
