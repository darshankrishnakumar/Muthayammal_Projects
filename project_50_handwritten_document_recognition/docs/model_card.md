# Model Card: Dual Neural Engines for PROJECT-050

## Model 1: DeepCRNNTextRecognizer
- **Type**: Spatio-Temporal Convolutional Recurrent Network with Connectionist Temporal Classification
- **Parameters**: 326,569
- **Input**: 3-channel normalized image patch (Batch, 3, 32, 128)
- **Convolutional Backbone**: Two Conv2d-BatchNorm-ReLU-MaxPool blocks yielding (64, 4, 16)
- **Recurrent Context**: 2-layer Bidirectional GRU (hidden_dim=128)
- **Classification Head**: Linear projection to 37 vocabulary logits
- **Loss Function**: PyTorch `nn.CTCLoss(blank=0, zero_infinity=True)`
- **CER**: 0.042 (vs 0.245 baseline, 82.8% reduction)
- **WER**: 0.078 (vs 0.384 baseline, 79.7% reduction)

## Model 2: DocumentQualityAndLexicalScorerNet
- **Type**: Deep Multi-Task Degradation Regressor & Classifier
- **Parameters**: 12,580
- **Input**: 12-dimensional continuous physical degradation feature vector
- **Hidden Layers**: Dense(12, 128) -> LayerNorm -> Dense(128, 64) -> LayerNorm -> Dense(64, 32)
- **Heads**:
  1. `quality_score` (0 - 100 scale, MAE: 1.69)
  2. `lexical_confidence` (0.0 - 1.0 scale, MAE: 0.0156)
  3. `review_risk` (BCE, 99.1% classification accuracy)
  4. `signature_integrity` (0 - 100 scale, MAE: 1.82)
- **Latency**: 16.5 ms inference time on Apple Silicon MPS / CUDA.
