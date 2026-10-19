# Project 29: Deep Learning Model Design

## 1. SignSpatialClassifier
- **Architecture**: Deep Residual Landmark Classifier
- **Layers**:
  - `Linear(63, 128)` + `LayerNorm(128)` + `GELU()` + `Dropout(0.1)`
  - `Linear(128, 256)` + `LayerNorm(256)` + `GELU()`
  - `ResidualBlock(256)` (Dual Linear(256, 256) with skip addition)
  - `ResidualBlock(256)`
  - `Linear(256, 128)` + `GELU()` + `Dropout(0.15)`
  - `Linear(128, 38)`
- **Parameters**: 248,358 trainable parameters
- **Loss**: Multi-class Cross-Entropy Loss
- **Optimizer**: AdamW (lr=0.003, weight_decay=1e-4) with Cosine Annealing
- **Metrics**: 92.89% Test Accuracy on held-out test set.

## 2. SignSequenceBiLSTM
- **Architecture**: 2-Layer Bidirectional LSTM with Temporal Self-Attention
- **Input**: $(B, T=16, D=63)$
- **Hidden Dim**: 64 (128 effective bidirectional features)
- **Attention**: Dense projection with Tanh activation yielding temporal importance weights
- **Multi-Head Heads**:
  - Class Logits: Linear(128, 128) -> GELU -> Linear(128, 38)
  - Transition Probability: Linear(128, 32) -> ReLU -> Linear(32, 1) -> Sigmoid
- **Metrics**: 89.39% Sequence Accuracy.
