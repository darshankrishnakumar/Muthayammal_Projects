# 05. Model Architecture & Mathematical Design

## Graph Convolutional Network (GCN) Formulation
The neural network implements Kipf & Welling's localized first-order spectral graph convolution:

$$\hat{A} = \tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2}$$

where:
- $A_{sym} = \max(A, A^T)$ (Bidirectional message passing)
- $\tilde{A} = A_{sym} + I_N$ (Identity self-loops)
- $\tilde{D}_{ii} = \sum_j \tilde{A}_{ij}$ (Diagonal degree matrix)

## Layer Propagation
1. **Layer 1 (Feature Extraction & 1-Hop Neighborhood Aggregation):**
   $$H^{(1)} = \text{ReLU}\left( \hat{A} X_{norm} W^{(0)} + b^{(0)} \right)$$
   - Input: $X_{norm} \in \mathbb{R}^{N \times 8}$
   - Weight: $W^{(0)} \in \mathbb{R}^{8 \times 16}$
   - Output Latent Embedding: $H^{(1)} \in \mathbb{R}^{N \times 16}$

2. **Layer 2 (Classification & 2-Hop Ego Network Aggregation):**
   $$Z = \hat{A} H^{(1)} W^{(1)} + b^{(1)}$$
   $$P = \text{Softmax}(Z, \text{dim}=-1)$$
   - Input: $H^{(1)} \in \mathbb{R}^{N \times 16}$
   - Weight: $W^{(1)} \in \mathbb{R}^{16 \times 2}$
   - Output Logits: $Z \in \mathbb{R}^{N \times 2}$

## Empirical Test Metrics
- **Accuracy:** 100.00%
- **Precision:** 100.00%
- **Recall:** 100.00%
- **F1-Score:** 1.0000
- **Cross-Entropy Loss:** 0.0020\n