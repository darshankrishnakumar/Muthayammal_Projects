# 03 — Dual PyTorch Model Specifications

## Summary Table
| Model Metric | Model 1: MultiCueTemporalFusionModel | Model 2: CrashSeverityAndDispatchNeuralNet | Combined System |
| :--- | :--- | :--- | :--- |
| **Model Role** | Visual-Kinematic Accident Detection | Multi-Task Severity & Dispatch Regressor | End-to-End Early Warning |
| **Input Shape** | Video (B, 16, 3, 64, 64) + Kinematics (B, 5) | Telemetry Vector (B, 12) | Multimodal Telemetry |
| **Trainable Params**| **185,990 parameters** | **12,648 parameters** | **198,638 parameters** |
| **Disk Checkpoint** | `backend/models/temporal_fusion_weights.pt` | `backend/models/crash_severity_weights.pt` | Serialized PyTorch Weights |
| **Primary Metric** | 100.0% Accuracy / 0.0% False Alarm Rate | MAE: 2.1 (Severity) / MAE: 1.8 km/h (Delta-V) | Sub-Second MTTD (1.15s) |
| **Inference Time** | 6.8 ms (Apple Silicon MPS) | 0.9 ms (CPU/MPS) | 11.2 ms Total Latency |

## Model 1 Architecture Details
- **Spatial Encoder**:
  - `Conv2d(3, 32, k=3, s=2, p=1)` -> `BatchNorm2d` -> `ReLU` -> `MaxPool2d(2, 2)`
  - `Conv2d(32, 64, k=3, s=2, p=1)` -> `BatchNorm2d` -> `ReLU` -> `MaxPool2d(2, 2)`
  - `Conv2d(64, 128, k=3, s=2, p=1)` -> `BatchNorm2d` -> `ReLU` -> `AdaptiveAvgPool2d((1, 1))`
  - `Linear(128, 128)`
- **Temporal Bidirectional GRU**:
  - `GRU(input_size=128, hidden_size=32, bidirectional=True, batch_first=True)`
- **Multi-Head Cross-Attention**:
  - `MultiheadAttention(embed_dim=64, num_heads=4, batch_first=True)`
- **Cue Attribution Gate**:
  - `Linear(5, 32)` -> `ReLU` -> `Linear(32, 5)` -> `Sigmoid`

## Model 2 Architecture Details
- **Multi-Task Trunk**:
  - `Linear(12, 128)` -> `BatchNorm1d` -> `ReLU` -> `Dropout(0.15)`
  - `Linear(128, 64)` -> `BatchNorm1d` -> `ReLU` -> `Dropout(0.10)`
  - `Linear(64, 32)` -> `ReLU`
- **Heads**:
  - Severity: `Linear(32, 1)` -> `Sigmoid` (x 100.0)
  - Delta-V: `Linear(32, 1)` -> `Sigmoid` (x 120.0 km/h)
  - Casualty Risk: `Linear(32, 1)` -> `Sigmoid`
  - EMS Units: `Linear(32, 1)` -> `Sigmoid` (x 10.0)
  - Priority Logits: `Linear(32, 4)` (P1, P2, P3, P4)
