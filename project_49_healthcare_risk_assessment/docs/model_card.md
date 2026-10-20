# Model Card — PROJECT-049
## Dual PyTorch Clinical Risk & Prognostic Engines

### 1. Model Details
- **Model 1: LongitudinalHealthRiskNet**
  - Architecture: Multi-Condition Deep Neural Encoder Network
  - Parameter Count: 3,044 trainable parameters
  - Inputs: 10 Standardized biomarkers
  - Task Heads: CVD Risk %, T2D Risk %, HTN Risk %, CKD Risk %
  - Validation Performance: CVD MAE: 1.27% | T2D MAE: 1.87% | HTN MAE: 1.11% | CKD MAE: 2.53% | R²: 0.993
  - Serialized Weights: `backend/models/healthcare_risk_net_weights.pt`

- **Model 2: ClinicalComorbidityForecastNet**
  - Architecture: Deep Multi-Layer Regressor with Batch Normalization and SiLU activations
  - Parameter Count: 18,308 trainable parameters
  - Inputs: 14 Features (10 normalized vitals + 4 condition risk probabilities)
  - Tasks: 10-Year Mortality %, 30-Day Readmission %, Polypharmacy %, Renal Hazard %
  - Validation Performance: Mortality MAE: 1.16% | Readmission MAE: 1.02% | Polypharmacy MAE: 0.86% | Renal Hazard MAE: 0.94% | R²: 0.997
  - Serialized Weights: `backend/models/comorbidity_regressor_weights.pt`

### 2. Training Procedure
- Mini-batch DataLoader with batch_size=64 and shuffle=True.
- Optimizer: AdamW (lr=0.005, weight_decay=1e-4).
- Loss Function: SmoothL1Loss.
- Training Epochs: 25 epochs per engine.
