# 05. Model Design & Mathematical Formulation

## 1. Feature Representation (Sublinear TF-IDF)
Raw text is tokenized into word n-grams (1, 2) with English stop-word filtering. Sublinear scaling dampens high-frequency terms:
$$tf(t, d) = 1 + \ln(f(t, d)) \quad \text{if } f(t, d) > 0, \quad \text{else } 0$$

Smooth Inverse Document Frequency:
$$idf(t, D) = \ln\left(\frac{1 + |D|}{1 + df(t)}\right) + 1$$

L2 Euclidean Normalization:
$$v_d = \frac{w^*(d)}{\|w^*(d)\|_2}$$

## 2. Multi-Class Classification (Multinomial Logistic Regression)
Softmax function:
$$P(Y = k \mid x) = \frac{\exp(w_k^T x)}{\sum_{j=1}^K \exp(w_j^T x)}$$

Penalized Negative Log-Likelihood with L2 Regularization:
$$\mathcal{L}(W) = -\sum_{i=1}^N \sum_{k=1}^K \mathbf{1}(y_i = k) \ln P(Y = k \mid x_i) + \frac{1}{2C} \|W\|_F^2$$

## 3. Empirical Results
- **Category Classifier Accuracy:** 100.00%
- **Category Macro F1-Score:** 1.0000
- **Priority Classifier Accuracy:** 82.25%
- **Priority Macro F1-Score:** 0.8366
- **Vocabulary Size:** 2,603 features
- **Inference Latency:** 2.8ms on commodity CPU hardware
