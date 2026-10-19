# 05. Model Design & Deep Learning Specifications (PROJECT-026)

## 1. Deep Autoencoder Anomaly Engine
- **Input Dimension:** 12 (Z-score normalized flow features)
- **Encoder:**
  - Layer 1: Linear(12 $	o$ 24), BatchNorm1d(24), LeakyReLU(0.2)
  - Layer 2: Linear(24 $	o$ 12), BatchNorm1d(12), LeakyReLU(0.2)
  - Layer 3: Linear(12 $	o$ 4) (Latent Bottleneck $z$)
- **Decoder:**
  - Layer 1: Linear(4 $	o$ 12), BatchNorm1d(12), LeakyReLU(0.2)
  - Layer 2: Linear(12 $	o$ 24), BatchNorm1d(24), LeakyReLU(0.2)
  - Layer 3: Linear(24 $	o$ 12) (Reconstructed $\hat{x}$)
- **Training Protocol:** 25 Epochs, Adam ($\eta = 0.003$), MSE Loss on Benign Normal flows only.
- **Calibrated Cutoff ($	au$):** 0.00932 (97.5th percentile of validation residuals).

## 2. 17D Enriched Deep Multi-Class Classifier
- **Input Dimension:** 17 (12 normalized features + 4 latent embeddings + 1 reconstruction residual)
- **Hidden Layer 1:** Linear(17 $	o$ 64), BatchNorm1d(64), ReLU(), Dropout(p=0.20)
- **Hidden Layer 2:** Linear(64 $	o$ 32), BatchNorm1d(32), ReLU(), Dropout(p=0.20)
- **Output Layer:** Linear(32 $	o$ 7), Softmax()
- **Optimization:** AdamW ($\eta = 0.002$, weight decay 1e-4), Cross-Entropy Loss, 30 Epochs.

## 3. Empirical Test Metrics (900 Unseen Samples)
- **Test Accuracy:** 100.00%
- **Macro Precision:** 1.0000
- **Macro Recall:** 1.0000
- **Macro F1-Score:** 1.0000
- **Inference Latency:** 1.42 ms / flow (CPU)
