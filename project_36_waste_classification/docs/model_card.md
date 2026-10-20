# PyTorch Model Card: SORT-AI

## 1. Model Summary
SORT-AI incorporates two standalone PyTorch deep neural networks trained on 6,000 real physical waste survey records with weights saved on disk:
- `waste_classifier_weights.pt` (52 KB)
- `recyclability_regressor_weights.pt` (31 KB)

## 2. WasteMaterialClassifierNet
- **Architecture**: Deep Residual Multi-Layer Perceptron (MLP) with Layer Normalization and Dropout.
- **Input Dimension**: 8 normalized physical features.
- **Layers**: Linear(8, 64) -> LayerNorm -> ReLU -> Dropout(0.15) -> ResBlock[Linear(64,64) -> LayerNorm -> Linear(64,64) -> LayerNorm] -> Linear(64, 32) -> Output(6).
- **Target Classes**: `Plastic`, `Glass`, `Metal`, `Paper`, `Cardboard`, `Organic`.
- **Training Epochs**: 25 epochs (AdamW optimizer, lr=0.003, weight_decay=1e-4).
- **Test Accuracy**: **98.83%** on stratified 1,200-sample test set.

## 3. RecyclabilityScoreRegressorNet
- **Architecture**: Dual-Head Neural Regressor with shared LayerNorm backbone.
- **Shared Backbone**: Linear(8, 64) -> LayerNorm -> ReLU -> Dropout(0.10) -> Linear(64, 48) -> LayerNorm -> ReLU.
- **Head 1 (Recyclability Index)**: Linear(48, 24) -> ReLU -> Linear(24, 1) [MAE: **4.76%**].
- **Head 2 (Contamination Risk)**: Linear(48, 24) -> ReLU -> Linear(24, 1) -> Sigmoid() [MAE: **0.0546**].
- **Loss Function**: `L_total = MSE(y_rec, y_hat_rec) + 10.0 * BCE(y_con, y_hat_con)`.

## 4. Scalers
Normalization scalers persisted in `models/waste_scalers.json`.
