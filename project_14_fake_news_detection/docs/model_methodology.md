# Algorithmic Methodology: Passive-Aggressive Large-Margin Learning

## 1. Core Principle
Passive-Aggressive algorithms belong to the family of online large-margin algorithms. Unlike batch optimization methods that require costly matrix inversions or stochastic gradient epochs across massive datasets, Passive-Aggressive updates incrementally whenever an example violates the margin requirement.

## 2. Mathematical Formulation
Given an example $(x_t, y_t)$ where $x_t \in \mathbb{R}^V$ is the TF-IDF feature vector and $y_t \in \{-1, +1\}$:

1. **Prediction Rule**:
$$\hat{y}_t = \text{sign}(w_t \cdot x_t + b)$$

2. **Hinge Loss**:
$$\ell_t(w) = \max(0, 1 - y_t(w_t \cdot x_t + b))$$

3. **Optimization Objective**:
$$w_{t+1} = \arg\min_w \frac{1}{2} ||w - w_t||^2 + C \xi \quad \text{s.t.} \quad \ell(w; (x_t, y_t)) \le \xi, \quad \xi \ge 0$$

4. **Closed-Form Update**:
$$w_{t+1} = w_t + \text{sign}(y_t) \tau_t x_t$$
$$\tau_t = \frac{\ell_t(w_t)}{||x_t||^2 + \frac{1}{2C}}$$

## 3. Sigmoid Probability Calibration
Because the raw score $d = w \cdot x + b$ is an uncalibrated geometric distance, we project it onto a bounded probability scale:
$$P(\text{Fake}) = \frac{1}{1 + \exp(-\text{clip}(d, -12, 12))}$$
$$P(\text{Real}) = 1.0 - P(\text{Fake})$$
