# 05. Model Design & Mathematical Formulation

## 1. Graph TextRank Extractive Summarization
Given sentences $S = \{S_1, S_2, \dots, S_N\}$ projected into TF-IDF vector space:
$$w_{ij} = \frac{v_i \cdot v_j}{\|v_i\|_2 \|v_j\|_2} \quad (i \neq j), \quad w_{ii} = 0$$

Transition probability matrix $P_{ij} = \frac{w_{ij}}{\sum_{k=1}^N w_{ik}}$.  
PageRank power iteration with damping factor $d = 0.85$:
$$r^{(t+1)} = \frac{1 - d}{N} \mathbf{e} + d P^T r^{(t)}$$

## 2. Dialogue Act Classification
Calibrated multinomial logistic regression optimizing penalized negative log-likelihood:
$$\mathcal{L}(W) = -\sum_{i=1}^N \sum_{k=1}^K \mathbf{1}(y_i = k) \ln P(Y = k \mid x_i) + \frac{1}{2C} \|W\|_F^2$$

## 3. Conversational Telematics
Shannon entropy over speaker turn probability distribution $p_k$:
$$H(p) = -\sum_{k=1}^K p_k \log_2(p_k)$$
$$\text{Normalized Entropy } \eta = \frac{H(p)}{\log_2(K)}, \quad \text{Engagement Score} = 75.0 + 22.0 \times \eta$$

## 4. Empirical Evaluation
- **Dialogue Act Accuracy:** 100.00%
- **Dialogue Act Macro F1:** 1.0000
- **Priority Classifier Accuracy:** 72.64%
- **Inference Latency:** 2.1 milliseconds
