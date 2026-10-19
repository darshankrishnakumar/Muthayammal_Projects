# Project 32: Model Design & Training Dynamics

## 1. Neural Network Topologies
- **MachineHealthClassifierNet**: Residual multi-layer perceptron with skip connections, batch normalization, and dropout. Trained with AdamW ($lr=0.003$) and CrossEntropyLoss over 25 epochs, reaching **96.83%** validation accuracy.
- **RULRegressorNet**: Deep dense MLP utilizing LayerNorm and GELU activations. The output heads utilize Sigmoid scaling (0-100 health score) and Softplus activation (+24h minimum RUL) to enforce strict physical degradation boundaries.

## 2. Training Trajectory
- Classification Loss: 0.2840 -> 0.0884 (Epoch 25).
- Validation Accuracy: 96.83% on 1,200 held-out test records.
- Weights saved on disk: `pdm_classifier_weights.pt` (56.7 KB) and `pdm_rul_weights.pt` (33.4 KB).
