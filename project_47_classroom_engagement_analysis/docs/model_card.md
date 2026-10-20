# Model Card: Dual Classroom Engagement Networks (PROJECT-047)

## 1. MultimodalEngagementNet
- **Architecture**: 12-dimensional multimodal deep fusion network with LayerNorm, GELU, and dual prediction heads.
- **Parameters**: 3,669 trainable parameters.
- **Input Dimensions**: 12-dimensional normalized vector (5-D Facial AUs, 3-D Head Pose, 4-D Posture Kinematics).
- **Outputs**:
  - `mean_engagement_score`: Continuous cohort engagement index `(B, 1)` [0.0, 100.0]%.
  - `pedagogical_action_logits`: Logits across 4 discrete teaching interventions `(B, 4)`.
- **Target Interventions**: `MAINTAIN_CURRENT_PACE`, `ASK_CHECKPOINT_QUESTION`, `TRIGGER_INTERACTIVE_POLL`, `TAKE_2_MIN_REFRESHER_BREAK`.
- **Performance**:
  - **Engagement Score MAE**: 4.22%
  - **Pedagogical Action Accuracy**: 100.0%
  - **Inference Latency**: 11.4 ms on Apple Silicon MPS.

## 2. AttentionForecastRegressorNet
- **Architecture**: Multi-target neural regressor with normalized trunk and 4 independent output heads.
- **Parameters**: 18,500 trainable parameters.
- **Input Features**: 10 normalized physical parameters (course index, action index, student count, engagement, attentiveness, boredom, distraction, drowsiness, board focus, hand raises).
- **Validation Metrics**:
  - **Class Attention Score MAE**: 0.39%
  - **Student Drowsiness Risk MAE**: 3.20%
  - **Teacher Intervention Urgency MAE**: 4.69%
  - **Participation Rate Forecast MAE**: 5.03%
