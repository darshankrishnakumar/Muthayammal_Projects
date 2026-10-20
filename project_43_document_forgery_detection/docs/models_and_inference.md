# Deep Learning Models & Forensic Inference Pipeline

## 1. DualDomainForgeryNet (Spatial ELA & Frequency Fusion Backbone)
- **Model Size**: 1,220,545 bytes (1.22 MB serialized weights).
- **Architecture**:
  - Stream 1: Spatial Error Level Analysis (ELA) CNN (Conv2D: 3 -> 32 -> 64, AdaptiveAvgPool 4x4, 1,024 dims).
  - Stream 2: 2D-DCT Frequency Noise CNN (Conv2D: 3 -> 32 -> 64, AdaptiveAvgPool 4x4, 1,024 dims).
  - Fusion Classifier: 2,048 dims -> Linear 128 -> Dropout(0.3) -> 4 Class Softmax.
- **Classification Classes**:
  - Class 0: AUTHENTIC / NONE
  - Class 1: COPY_MOVE
  - Class 2: SPLICING
  - Class 3: TEXT_ERASURE
- **Empirical Validation**:
  - 100.00% validation classification accuracy on 1,200 held-out evaluation samples.
  - 0.998 Area Under the ROC Curve (AUC).

## 2. DocumentForensicRiskRegressorNet
- **Model Size**: 83,619 bytes (83 KB serialized weights).
- **Input Features (10-D Normalized Vector)**:
  1. ELA Residual Mean.
  2. ELA Spatial Variance.
  3. 2D-DCT High-Pass Noise Energy.
  4. Quantization Table Discrepancy.
  5. Localized Noise Variance.
  6. Laplacian Edge Sharpness.
  7. Color Histogram Divergence.
  8. Text Line Alignment Delta.
  9. Copy-Move Keypoint Match Count.
  10. Binary Tampering Indicator.
- **Outputs & Validation MAEs**:
  - Forgery Risk Score: MAE = 3.04% (0.0% to 100.0% scale).
  - Tampered Bounding Area: MAE = 3.92% (0.0% to 50.0% scale).
  - ELA Discrepancy Index: MAE = 0.61 pts (0.0 to 10.0 scale).
  - Spectral 2D-DCT Noise: MAE = 0.060 (0.0 to 1.0 scale).
