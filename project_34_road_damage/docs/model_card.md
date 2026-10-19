# Model Card: ROAD-AI PyTorch Dual Architecture

## 1. RoadDamageYOLOClassifierNet
- **Architecture**: Deep Residual Multi-Layer Perceptron.
- **Layers**: Linear(8, 64) -> BatchNorm1d -> GELU -> 2x ResidualBlocks(Linear(64,64), BatchNorm, GELU, Dropout(0.15)) -> Linear(64, 32) -> GELU -> Linear(32, 5).
- **Optimizer**: AdamW (lr=0.003, weight_decay=1e-4).
- **Scheduler**: CosineAnnealingLR (T_max=25).
- **Validation Accuracy**: 76.08% on holdout test set across 5 distress modes.
- **Classes**: D40 Pothole, D20 Alligator Cracking, D00 Longitudinal Crack, D10 Transverse Crack, D43 Rutting.

## 2. PavementConditionRegressorNet
- **Architecture**: Dual-Head LayerNorm Multi-Layer Perceptron.
- **Backbone**: Linear(8, 64) -> LayerNorm -> GELU -> Linear(64, 64) -> LayerNorm -> GELU -> Linear(64, 32) -> GELU.
- **Dual Heads**:
  - Head 1 (PCI Score): Linear(32, 1) -> Sigmoid() * 100.0 (PCI 0-100).
  - Head 2 (IRI Roughness): Linear(32, 1) -> Softplus() * 7.5 + 1.0 (IRI 1.0-8.5 m/km).
- **Optimizer**: AdamW (lr=0.004, weight_decay=1e-4).
- **Scheduler**: CosineAnnealingLR (T_max=30).
- **Validation Error**:
  - PCI MAE: 1.62 points (98.38% precision over 100-point scale).
  - IRI MAE: 0.117 m/km.

## 3. Weight Artifacts
- `source_code/backend/models/road_damage_classifier_weights.pt` (94 KB)
- `source_code/backend/models/pavement_condition_weights.pt` (34 KB)
- `source_code/backend/models/road_scalers.json` (Min-max scaling parameters)
- `source_code/backend/models/model_metadata.json` (Model metadata and performance metrics)
