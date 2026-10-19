# Model Card: AERO-RUL PyTorch Dual Architecture

## 1. AviationAirworthinessClassifierNet
- **Architecture**: Deep Residual Multi-Layer Perceptron.
- **Layers**: Linear(8, 64) -> BatchNorm1d -> GELU -> 2x ResidualBlocks(Linear(64,64), BatchNorm, GELU, Dropout(0.15)) -> Linear(64, 32) -> GELU -> Linear(32, 3).
- **Optimizer**: AdamW (lr=0.003, weight_decay=1e-4).
- **Scheduler**: CosineAnnealingLR (T_max=25).
- **Validation Accuracy**: 98.08% on holdout test set.
- **Classes**:
  - `AIRWORTHY / OPTIMAL` (Health >= 60%)
  - `MAINTENANCE DUE SOON` (30% <= Health < 60%)
  - `GROUNDED / MANDATORY SHOP VISIT` (Health < 30%)

## 2. TurbofanRULRegressorNet
- **Architecture**: Dual-Head LayerNorm Multi-Layer Perceptron.
- **Backbone**: Linear(8, 64) -> LayerNorm -> GELU -> Linear(64, 64) -> LayerNorm -> GELU -> Linear(64, 32) -> GELU.
- **Dual Heads**:
  - Health Head: Linear(32, 1) -> Sigmoid() * 100.0 (Health Score 0-100%).
  - RUL Head: Linear(32, 1) -> Softplus() * 4500.0 (RUL Cycles >= 0).
- **Optimizer**: AdamW (lr=0.004, weight_decay=1e-4).
- **Scheduler**: CosineAnnealingLR (T_max=30).
- **Validation Error**:
  - Health MAE: 0.82%
  - RUL MAE: 51.5 flight cycles (under 0.86% error across design lifespan).

## 3. Weight Artifacts
- `source_code/backend/models/aviation_classifier_weights.pt` (94 KB)
- `source_code/backend/models/turbofan_rul_weights.pt` (33 KB)
- `source_code/backend/models/aviation_scalers.json` (Min-max scaling parameters)
- `source_code/backend/models/model_metadata.json` (Comprehensive model cards)
