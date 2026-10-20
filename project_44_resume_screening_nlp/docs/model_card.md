# Model Card: TransformerSemanticMatcherNet & CandidateCompetencyRegressorNet

## Model Overview
- **Project**: PROJECT-044 (Intelligent Resume Screening & Job Matching)
- **Framework**: PyTorch 2.x
- **Hardware Acceleration**: Apple Silicon MPS (Metal Performance Shaders) / CUDA

## Model 1: TransformerSemanticMatcherNet
- **Architecture**: 128-dimensional contextual SBERT projection trunk with differential fusion matching head
- **Parameters**: 58,241 trainable parameters
- **File Size**: 238,041 bytes (`experiments/phase2_model.pt`)
- **Forward Pass**:
  - `c_proj = LayerNorm(ReLU(Linear(128, 128)(cand_emb)))`
  - `j_proj = LayerNorm(ReLU(Linear(128, 128)(job_emb)))`
  - `fused = cat([c_proj, j_proj, abs(c_proj - j_proj)], dim=-1)` (384-D)
  - `match_score = Sigmoid(Linear(64, 1)(ReLU(Linear(384, 64)(fused))))`
- **Validation Metric**: 16.26% match score MAE

## Model 2: CandidateCompetencyRegressorNet
- **Architecture**: 10-feature normalized trunk with GELU activations and 4 dedicated regression heads
- **Parameters**: 18,500 trainable parameters
- **File Size**: 83,709 bytes (`backend/models/candidate_competency_regressor_weights.pt`)
- **Regression Heads & Test Performance**:
  - `overall_match_head`: Sigmoid * 100.0 (MAE: 0.44%)
  - `skill_overlap_head`: Sigmoid (MAE: 0.029)
  - `experience_fit_head`: Sigmoid * 10.0 (MAE: 0.08 pts)
  - `seniority_head`: Sigmoid * 100.0 (MAE: 5.83%)
