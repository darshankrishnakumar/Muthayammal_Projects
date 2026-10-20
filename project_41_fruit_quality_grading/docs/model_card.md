# Model Card: AUTONOMOUS FRUIT-GRADING AI Deep Neural Networks

## Model 1: MultiTaskFruitNet
- **Architecture**: Multi-Task 3-Stage Convolutional Neural Network
- **Serialized Weights**: `source_code/experiments/phase2_model.pt` (391 KB)
- **Input Shape**: `[Batch, 3, 64, 64]` Normalized RGB optical imagery
- **Head 1 (Variety)**: `[Batch, 4]` -> Apple, Orange, Banana, Mango (90.0% Validation Acc)
- **Head 2 (Grade)**: `[Batch, 3]` -> Grade A Premium, Grade B Standard, Grade C Reject (100.0% Validation Acc)
- **Head 3 (Defect)**: `[Batch, 5]` -> None, Bruise, Skin Rot, Fungal Spot, Scab

## Model 2: FruitFreshnessShelfLifeRegressorNet
- **Architecture**: Multi-Target Continuous Regressor with Layer Normalization & GELU
- **Serialized Weights**: `source_code/backend/models/fruit_freshness_regressor_weights.pt` (83 KB)
- **Input Shape**: `[Batch, 10]` Physical telemetry features
- **Head 1**: Flesh Firmness [10.0, 95.0] N -> Test MAE: 6.39 N
- **Head 2**: Sugar Content [7.0, 22.0] Brix % -> Test MAE: 1.23 Brix %
- **Head 3**: Marketable Shelf Life [0.5, 30.0] Days -> Test MAE: 2.11 Days
- **Head 4**: Batch Economic Quality Index [0, 100] Points -> Test MAE: 6.12 Points
