# Model Card — PROJECT-048
## Dual PyTorch Neural Engines

### 1. Model Details
- **Model 1: SpectralFreshnessCNN**
  - Architecture: Multi-cue Spatio-Spectral 2D Convolutional Neural Network
  - Parameter Count: 20,869 trainable parameters
  - Input: 3-channel optical reflectance tensors (3 x 64 x 64)
  - Tasks: Freshness Score (0-100), Remaining Shelf-Life (hours), Tri-tier Deterioration Stage
  - Validation Performance: Freshness MAE: 1.24 points, Stage Accuracy: 98.3%
  - Serialized Weights: `backend/models/food_freshness_cnn_weights.pt`

- **Model 2: ShelfLifeForecastRegressorNet**
  - Architecture: Deep Multi-Layer Regressor with Batch Normalization and SiLU activations
  - Parameter Count: 18,052 trainable parameters
  - Input: 10 Normalized physico-chemical and environmental telemetry features
  - Tasks: Remaining Shelf-Life (days), Spoilage Risk (%), Microbial Risk (%), Cold-Chain Compliance (%)
  - Validation Performance: Shelf-Life MAE: 0.47 days (R²: 0.978), Spoilage MAE: 2.09%, Microbial MAE: 0.81%, Cold-Chain MAE: 1.37%
  - Serialized Weights: `backend/models/food_shelflife_regressor_weights.pt`

### 2. Training Procedure
- Mini-batch DataLoader with batch_size=64 and shuffle=True.
- Optimizer: AdamW (lr=0.003 for CNN, lr=0.005 for Regressor, weight_decay=1e-4).
- Loss Functions: Multi-task weighted MSE + Cross-Entropy (CNN) and SmoothL1Loss (Regressor).
- Training Epochs: 25 epochs per engine.
