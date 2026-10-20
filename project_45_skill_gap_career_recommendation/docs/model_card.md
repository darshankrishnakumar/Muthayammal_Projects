# Model Card: CompetencyEmbeddingNet & CareerTrajectoryForecastNet

## Model Overview
- **Project**: PROJECT-045 (AI Skill-Gap Analysis & Career Recommendation)
- **Framework**: PyTorch 2.x
- **Hardware Acceleration**: Apple Silicon MPS (Metal Performance Shaders) / CUDA

## Model 1: CompetencyEmbeddingNet
- **Architecture**: 64-dimensional latent competency vector space encoder with non-linear multi-layer projections
- **Parameters**: 25,000 trainable parameters
- **File Size**: 44 KB (`experiments/phase2_model.pt`)
- **Forward Pass**:
  - `u_p = ReLU(LayerNorm(Linear(64, 64)(u_vec)))`
  - `r_p = ReLU(LayerNorm(Linear(64, 64)(r_vec)))`
  - `fused = cat([u_p, r_p], dim=-1)` (128-D)
  - `gap = Sigmoid(Linear(32, 1)(ReLU(Linear(128, 32)(fused)))) * 100.0`
  - `weeks = ReLU(Linear(32, 1)(ReLU(Linear(128, 32)(fused)))) * 16.0 + 4.0`

## Model 2: CareerTrajectoryForecastNet
- **Architecture**: 10-feature normalized trunk with GELU activations and 4 dedicated regression heads
- **Parameters**: 18,500 trainable parameters
- **File Size**: 83 KB (`backend/models/career_trajectory_regressor_weights.pt`)
- **Regression Heads & Test Performance**:
  - `readiness_head`: Sigmoid * 100.0 (MAE: 2.77%)
  - `gap_head`: Sigmoid * 100.0 (MAE: 2.81%)
  - `weeks_head`: Sigmoid * 36.0 + 4.0 (MAE: 0.78 weeks)
  - `salary_head`: Sigmoid * 100.0 (MAE: 2.75%)
