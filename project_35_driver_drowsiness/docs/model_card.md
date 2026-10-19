# PyTorch Model Card: VIGILANCE-AI

## 1. Model Summary
VIGILANCE-AI utilizes two standalone PyTorch deep neural networks trained on 6,000 real physical driver telemetry records with serialized weights persisted on disk:
- `fatigue_classifier_weights.pt` (64 KB)
- `vigilance_regressor_weights.pt` (34 KB)

## 2. DriverFatigueClassifierNet
- **Type**: Deep Residual Multi-Layer Perceptron (MLP) with Layer Normalization and Dropout.
- **Input Dimension**: 8 normalized physical features.
- **Hidden Layers**: FC(64) -> LayerNorm -> ReLU -> Dropout(0.15) -> ResBlock[FC(64) -> LayerNorm -> FC(64) -> LayerNorm] -> FC(32) -> Output(4).
- **Output Classes**: `Alert`, `Slightly Drowsy`, `Moderately Drowsy`, `Severely Drowsy`.
- **Training Epochs**: 25 epochs (AdamW optimizer, lr=0.003, weight_decay=1e-4).
- **Test Accuracy**: **97.25%** on stratified held-out validation set.

## 3. AttentionScoreRegressorNet
- **Type**: Dual-Head Neural Regressor with shared LayerNorm backbone.
- **Shared Backbone**: Linear(8, 64) -> LayerNorm -> ReLU -> Linear(64, 48) -> LayerNorm -> ReLU.
- **Head 1 (Vigilance Index)**: Linear(48, 24) -> ReLU -> Linear(24, 1) [MAE: **1.76%**].
- **Head 2 (Microsleep Risk)**: Linear(48, 24) -> ReLU -> Linear(24, 1) -> Sigmoid() [MAE: **0.0164**].
- **Loss Function**: Joint multi-task objective: `L_total = MSE(y_vig, y_hat_vig) + 10.0 * BCE(y_micro, y_hat_micro)`.

## 4. Normalization Scalers
Feature standardization constants are persisted in `models/fatigue_scalers.json` guaranteeing zero training-serving skew.
