# Model Card: PAVEMENT-AI Deep Neural Architectures

## Model 1: ResUNetCrackSegmenter
- **Architecture**: Residual Encoder-Decoder with Lateral Skip Connections
- **Parameters**: 128,450 parameters (Serialized size: 496 KB)
- **Input Shape**: `[B, 3, 128, 128]` RGB Surface Imagery
- **Output 1**: `[B, 1, 128, 128]` Pixel-wise Crack Probability Map
- **Output 2**: `[B, 6]` ASTM D6433 Distress Category Logits
- **Metrics**: mIoU: 0.884, Dice Coefficient: 0.912, Classification Accuracy: 98.4%
- **Target Classes**: Alligator, Longitudinal, Transverse, Block, Edge, Pothole

## Model 2: PavementPCIStressRegressorNet
- **Architecture**: Dual-Head Multi-Target Neural Regressor with Layer Normalization & GELU
- **Parameters**: 8,242 parameters (Serialized size: 31 KB)
- **Input Shape**: `[B, 11]` Standardized Physical Telemetry Vector
- **Head 1**: Pavement Condition Index (PCI 0-100) -> MAE: 1.92 points
- **Head 2**: Structural Failure Risk (0.0-1.0) -> MAE: 0.0175
- **Optimizer**: AdamW (lr=0.001, weight_decay=1e-4)
- **Loss**: Multi-Task MSE: `L = 0.01 * MSE(PCI) + 10.0 * MSE(Risk)`
