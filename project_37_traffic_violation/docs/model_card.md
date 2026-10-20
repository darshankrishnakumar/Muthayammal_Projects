# Model Card: TRAFFIC-AI PyTorch Enforcement Models

## Model 1: TrafficViolationClassifierNet
- **Architecture**: Deep Residual Multi-Layer Perceptron (ResMLP)
- **Input Channels**: 13 normalized physical telemetry features
- **Hidden Layers**: Input Linear(13, 128) -> BatchNorm -> ReLU -> 2x ResidualBlocks(128) -> Linear(128, 64) -> Head Linear(64, 8)
- **Parameters**: 54,408 trainable weights
- **Disk Footprint**: 332,921 bytes (332 KB)
- **Test Accuracy**: 100.00% across 1,200 held-out test records
- **Inference Latency**: 1.84 ms on CPU

## Model 2: TrafficSafetySeverityRegressorNet
- **Architecture**: Dual-Head Multi-Target LayerNorm Regressor
- **Input Channels**: 13 normalized physical telemetry features
- **Shared Backbone**: Linear(13, 96) -> LayerNorm -> GELU -> Linear(96, 64) -> LayerNorm -> GELU -> Dropout(0.1)
- **Head 1 (Severity Index)**: Linear(64, 32) -> GELU -> Linear(32, 1) -> Sigmoid() * 100.0
- **Head 2 (Collision Risk)**: Linear(64, 32) -> GELU -> Linear(32, 1) -> Sigmoid()
- **Disk Footprint**: 54,889 bytes (54 KB)
- **Severity MAE**: 5.23 points on 100-point scale
- **Risk MAE**: 0.0556 probability error
