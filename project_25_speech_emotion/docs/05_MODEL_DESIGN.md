# 05. Model Architecture & Mathematical Design

## DeepSERNet Architecture
The neural network integrates convolutional, recurrent, and attention mechanisms:

1. **1D-CNN Stage:**
   - Input: $(B, 1, 40)$
   - Conv1D(1 $\to$ 64, kernel=5, pad=2) + BatchNorm1d + ReLU + MaxPool1d(2) $\to (B, 64, 20)$
   - Conv1D(64 $\to$ 128, kernel=3, pad=1) + BatchNorm1d + ReLU + MaxPool1d(2) $\to (B, 128, 10)$

2. **Bidirectional LSTM Stage:**
   - Permute to temporal sequence: $(B, 10, 128)$
   - 2-layer Bi-LSTM with hidden size 64: output $(B, 10, 128)$

3. **Self-Attention Pooling:**
   - Scores: $e_t = w^T h_t + b$
   - Weights: $\alpha_t = \text{Softmax}(e_t)$
   - Context Vector: $c = \sum_{t=1}^{10} \alpha_t h_t \in \mathbb{R}^{128}$

4. **Dual Output Heads:**
   - Shared Representation: Linear(128 $\to$ 64) + ReLU
   - Emotion Classification: Linear(64 $\to$ 7) $\to$ Softmax probabilities
   - Valence-Arousal Regression: Linear(64 $\to$ 2) $\to$ Tanh coordinates $[-1, 1]$

## Empirical Test Metrics
- **Classification Accuracy:** 98.80%
- **Macro Precision:** 98.80%
- **Macro Recall:** 98.68%
- **Macro F1-Score:** 0.9872
- **Valence-Arousal MSE:** 0.0076\n