# Project 30: Deep Learning Model Design

## 1. IoTAnomalyAutoencoder
- **Architecture**: 7-Layer Deep Bottleneck Autoencoder
- **Encoder**: Linear(8, 16) -> LayerNorm -> LeakyReLU(0.2) -> Linear(16, 8) -> LayerNorm -> LeakyReLU(0.2) -> Linear(8, 4)
- **Decoder**: Linear(4, 8) -> LayerNorm -> LeakyReLU(0.2) -> Linear(8, 16) -> LayerNorm -> LeakyReLU(0.2) -> Linear(16, 8)
- **Loss**: MSE Loss on normal baseline traffic
- **Weights**: `iot_autoencoder_weights.pt` (10.2 KB)
- **Threshold**: 0.35 reconstruction error cutoff

## 2. IoTThreatClassifier
- **Architecture**: Deep Residual Threat Net
- **Input**: 8 standardized features + 1 autoencoder reconstruction loss scalar = 9D input
- **Layers**:
  - `Linear(9, 64)` + `BatchNorm1d(64)` + `LeakyReLU(0.2)` + `Dropout(0.15)`
  - Residual block: `Linear(64, 64)` + `BatchNorm1d` + `LeakyReLU` + `Linear(64, 64)` + skip addition
  - Head: `Linear(64, 32)` + `LeakyReLU` + `Dropout(0.15)` + `Linear(32, 6)`
- **Accuracy**: 100.0% Test Accuracy across 1,100 held-out test vectors
- **Weights**: `iot_classifier_weights.pt` (54.5 KB)
