# Model Card: PROJECT-053 Dual Neural Engine

## Model 1: ResUNetRailDefectSegmenter
- **Type**: Multi-Class Semantic Segmentation ResUNet
- **Parameters**: 374,342
- **Input**: Optical track imagery tensor (Batch, 3, 128, 128)
- **Architecture**: 3-stage contracting encoder with residual skips, bottleneck bridge, 2-stage expansive decoder with skip concatenations, 1x1 classifier.
- **Classes**:
  - 0: Clean Rail Head
  - 1: Surface Crack (Transverse fissures, squats)
  - 2: Missing Fastener / Clip
  - 3: Abnormal Joint (Gap degradation, batter)
  - 4: Surface Deterioration (Corrugation, spalling)
  - 5: Foreign Obstacle (Ballast rocks, metallic debris)
- **Accuracy**: mIoU 86.2% (vs 58.4% baseline, +27.8% gain)
- **Latency**: 14.8 ms on Apple Silicon MPS / CUDA GPUs

## Model 2: RailTrackGeometryAndDegradationRegressorNet
- **Type**: Deep Multi-Task Track Geometry & Mechanical Degradation Regressor
- **Parameters**: 12,582
- **Input**: 12-dimensional physical telemetry feature vector
- **Hidden Layers**: Dense(12, 128) -> BatchNorm -> Dense(128, 64) -> BatchNorm -> Dense(64, 32)
- **Heads**:
  1. `track_quality_index` (0-100 scale, MAE: 1.45)
  2. `speed_restriction_kmh` (0-160 km/h, MAE: 3.2 km/h)
  3. `derailment_risk` (0.0 - 1.0 probability, MAE: 0.016)
  4. `severity_logits` (3 classes: Minor, Moderate, Critical, F1: 0.952)
- **Combined Parameters**: 386,924 active parameters.
