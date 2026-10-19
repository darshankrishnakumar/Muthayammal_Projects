# Explainable AI (XAI) & Attention Visualizations

## Interpretability Rationale
In enterprise security operations centers (SOC), autonomous threat mitigation requires high transparency. Black-box classifications cannot be audited or acted upon with confidence.

## Mathematical Formulation of Attention Weights
Given the RCNN hidden representations $y_t \in \mathbb{R}^{d}$, the attention module computes a normalized weight $\alpha_t$ for each token:

$$u_t = \tanh(W_w y_t + b_w)$$
$$\alpha_t = \frac{\exp(u_t^T u_w)}{\sum_{j=1}^L \exp(u_j^T u_w)}$$

Where:
- $u_w$ is a trainable query vector.
- $\alpha_t$ satisfies $\sum_{t=1}^L \alpha_t = 1.0$.

## Visual Representation in Web Dashboard
Tokens are dynamically tagged and styled based on their relative energy percentage:
- **Red Highlight (Threat Token)**: High attention weight on urgency or credential harvest words (`urgent`, `verify`, `account`, `suspension`, `login`, `credentials`).
- **Amber Highlight (Elevated Signal)**: Medium attention tokens providing contextual coercion.
- **Slate Text (Neutral Token)**: Benign syntactic tokens (`at`, `the`, `is`, `for`).
