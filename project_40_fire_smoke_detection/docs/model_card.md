# Model Card: INDUSTRIAL FIRE-VISION AI Deep Neural Networks

## Model 1: DualStreamFireSmokeNet
- **Architecture**: Dual-Stream Spatio-Temporal Convolutional Network
- **Serialized Weights**: `source_code/experiments/phase2_model.pt` (672 KB)
- **Input Stream 1**: `[Batch, 3, 64, 64]` Normalized optical frame
- **Input Stream 2**: `[Batch, 8]` Normalized temporal flicker FFT power spectrum
- **Fusion Output**: `[Batch, 4]` Logits across 4 hazard classes
- **Classes**: NORMAL (0), SMOKE_DETECTED (1), FLAME_DETECTED (2), DUAL_FIRE_SMOKE_HAZARD (3)
- **Validation Accuracy**: 100.00% on 1,200 held-out test records

## Model 2: FirePropagationThermalRiskRegressorNet
- **Architecture**: Multi-Target Continuous Regressor with Layer Normalization & GELU
- **Serialized Weights**: `source_code/backend/models/thermal_risk_regressor_weights.pt` (83 KB)
- **Input Shape**: `[Batch, 10]` Continuous physical telemetry features
- **Head 1**: Flame Core Temperature [150.0, 950.0] C -> Test MAE: 60.93 C
- **Head 2**: Plume Expansion Velocity [0.2, 8.5] m/s -> Test MAE: 0.109 m/s
- **Head 3**: Evacuation Urgency Index [0, 100] -> Test MAE: 5.74 points
- **Head 4**: Carbon Monoxide Concentration [10, 800] ppm -> Test MAE: 5.50 ppm
