# Fraud Detection Data Science & Ensemble Modeling

## 1. Problem Formulation & Extreme Class Skew
Credit card fraud detection is characterized by extreme class imbalance ($< 0.25\%$ positive class). In standard empirical risk minimization, classifiers optimize accuracy by ignoring the minority class. To resolve this:
- **Balanced Class Weights**: Cost-sensitive weighting assigns penalty weights $w_c = \frac{N}{2 \times N_c}$ during tree construction.
- **Objective Metric**: Evaluation prioritizes Area Under the Precision-Recall Curve (PR-AUC) and Area Under the ROC Curve (AUC-ROC) over raw accuracy.

## 2. Mathematical Formulations

### Balanced Random Forest
Each tree $T_b$ is trained on a balanced bootstrap resample of the training set. At each node split, a subset of $m = \sqrt{30} \approx 5$ candidate features is evaluated. Splitting maximizes Gini impurity reduction:
$$\Delta I_G = I_G(t) - \frac{N_L}{N} I_G(t_L) - \frac{N_R}{N} I_G(t_R)$$

### Gradient Boosting Regressor
Sequential additive modeling minimizes binomial log-likelihood loss:
$$L(y, F(x)) = \log(1 + \exp(-2 y F(x)))$$
With shrinkage learning rate $\eta = 0.10$ scaling each decision tree contribution:
$$F_m(x) = F_{m-1}(x) + \eta \cdot h_m(x)$$

### Weighted Ensemble Voting
The unified transaction risk probability combines model outputs:
$$P_{\text{ensemble}}(x) = 0.70 \cdot P_{\text{RF}}(x) + 0.30 \cdot P_{\text{GBM}}(x)$$

## 3. Directional SHAP Attribution Mechanics
Feature impact scores approximate local Shapley values:
$$\phi_i(x) = \text{Sign}(x_i - \mu_i) \cdot w_i \cdot \left|\frac{x_i - \mu_i}{\sigma_i}\right|$$
Isolating whether individual PCA components drive risk toward 'CRITICAL' (risk-increasing) or ground it toward 'LOW' (risk-reducing).
