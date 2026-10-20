# Model Card: Dual Industrial Defect Detection Networks (PROJECT-046)

## 1. DeepFPNDefectNet (Feature Pyramid Network)
- **Architecture**: Multi-scale convolutional Feature Pyramid Network with lateral connections and dual segmentation/classification heads.
- **Parameters**: 585,919 trainable parameters.
- **Input Dimensions**: RGB optical tensor `(B, 3, 64, 64)`.
- **Outputs**:
  - `seg_mask`: Continuous spatial defect probability map `(B, 1, 16, 16)`.
  - `defect_logits`: Multi-class anomaly logits across 5 classes `(B, 5)`.
- **Target Classes**: `NONE`, `SCRATCH`, `CRACK`, `DENT`, `MISSING_COMPONENT`.
- **Performance**:
  - **F1-Score**: 0.968
  - **Mean IoU**: 0.935
  - **Inference Latency**: 11.2 ms on Apple Silicon MPS.

## 2. ManufacturingDefectRiskRegressorNet
- **Architecture**: Multi-target neural regressor with normalized trunk and 4 independent output heads.
- **Parameters**: 18,500 trainable parameters.
- **Input Features**: 10 normalized physical parameters (component index, anomaly index, reject flag, raw metrics, cycle time, optical confidence).
- **Validation Metrics**:
  - **Severity Score MAE**: 0.48%
  - **Defect Area Percentage MAE**: 0.17%
  - **Surface Roughness Ra MAE**: 0.13 um
  - **Pneumatic Ejection Confidence MAE**: 0.30%
