# Project 31: Model Design & Training Dynamics

## 1. Neural Network Topologies
- **FloodRiskClassifierNet**: Residual multi-layer perceptron with skip connections and batch normalization. Trained with AdamW ($lr=0.003$) and CrossEntropyLoss over 25 epochs, reaching 92.16% validation accuracy.
- **InundationDepthRegressorNet**: Dense MLP utilizing LayerNorm and GELU activations. The output heads utilize Softplus activation functions to strictly enforce non-negative standing inundation water depths and a minimum 1.0-hour evacuation lead time.

## 2. Model Convergence
- Classification Loss: 0.4210 -> 0.2345 (Epoch 25).
- Regression MSE: 5.820 -> 2.9750 (Epoch 25).
- Weights saved on disk: `flood_risk_classifier_weights.pt` (56.7 KB) and `inundation_regressor_weights.pt` (33.7 KB).
