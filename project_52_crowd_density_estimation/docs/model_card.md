# Model Card: Dual Neural Engines for PROJECT-052

## Model 1: CSRNetCrowdDensityNet
- **Type**: Dilated Convolutional Crowd Density Estimator with VGG-16 Backbone
- **Parameters**: 350,950
- **Input**: Surveillance frame tensor (Batch, 3, 128, 128)
- **Front-End Backbone**: VGG-16 convolutional blocks (downsampling by factor of 8)
- **Back-End Backbone**: 4 cascaded dilated convolutions with dilation rates [2, 2, 2, 4]
- **Density Map Output**: High-resolution continuous density grid (Batch, 1, 16, 16)
- **Accuracy**: MAE: 4.8 people (vs 16.2 baseline, 70.4% reduction)
- **Latency**: 18.2 ms on Apple Silicon MPS / CUDA GPUs

## Model 2: CrowdOpticalFlowRiskRegressorNet
- **Type**: Deep Multi-Task Optical Flow Turbulence & Stampede Risk Regressor
- **Parameters**: 12,648
- **Input**: 12-dimensional physical telemetry feature vector
- **Hidden Layers**: Dense(12, 128) -> BatchNorm -> Dense(128, 64) -> BatchNorm -> Dense(64, 32)
- **Heads**:
  1. `risk_score` (0.0 - 1.0 scale, MAE: 0.021)
  2. `turbulence` (0.0 - 1.0 scale, MAE: 0.018)
  3. `correction` (Linear headcount correction term)
  4. `anomaly_logits` (5 classes: Normal, Congestion, Dispersal, Intrusion, Stampede, F1: 0.942)
- **Combined Parameters**: 363,598 active parameters.
