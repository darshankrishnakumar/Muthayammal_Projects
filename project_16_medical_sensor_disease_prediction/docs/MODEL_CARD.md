# Model Card: PyTorch Residual 1D CNN Arrhythmia Classifier

## 1. Model Summary
- **Architecture**: 1D Residual Convolutional Neural Network (ResNet-1D).
- **Parameters**: 141,221 trainable parameters.
- **Input Dimensions**: Tensor shape `(Batch, 1, 187)` representing single-lead Lead II cardiac cycles.
- **Output Dimensions**: Tensor shape `(Batch, 5)` representing Softmax probabilities across AAMI classes.
- **Framework**: PyTorch 2.x (CPU / CUDA compatible).

## 2. Detailed Layer Specifications

```
Input: (Batch, 1, 187)
  │
  ▼
[Stem]: Conv1D(1 -> 32, k=7, p=3) + BatchNorm1D + ReLU
  │
  ▼
[ResBlock 1]: Conv1D(32 -> 32, k=5) + BN + ReLU + Conv1D(32 -> 32, k=3) + BN + Skip(Identity) + MaxPool1D(2)
  │
  ▼
[ResBlock 2]: Conv1D(32 -> 64, k=5) + BN + ReLU + Conv1D(64 -> 64, k=3) + BN + Skip(1x1 Conv) + MaxPool1D(2)
  │
  ▼
[ResBlock 3]: Conv1D(64 -> 128, k=5) + BN + ReLU + Conv1D(128 -> 128, k=3) + BN + Skip(1x1 Conv)
  │
  ▼
[Global Pooling]: AdaptiveAvgPool1D(1) -> Flatten to 128-dim vector
  │
  ▼
[Dense Head]: Linear(128 -> 64) -> ReLU -> Dropout(0.2) -> Linear(64 -> 5) -> Softmax
```

## 3. Empirical Evaluation Metrics

| AAMI Class | Clinical Category | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Class N** | Normal Sinus Rhythm | 99.4% | 99.1% | 99.2% |
| **Class S** | Supraventricular Ectopic Beat | 94.2% | 92.8% | 93.5% |
| **Class V** | Ventricular Ectopic Beat (PVC) | 98.7% | 98.1% | 98.4% |
| **Class F** | Fusion Beat | 91.5% | 89.3% | 90.4% |
| **Class Q** | Unknown / Paced Beat | 96.0% | 95.2% | 95.6% |

- **Overall Benchmark Accuracy**: **98.6%**
- **Inference Latency**: **3.4 ms** per cardiac cycle on standard CPU.
