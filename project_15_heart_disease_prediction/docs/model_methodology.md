# Algorithmic Methodology: Random Forest Ensemble Learning

## 1. Ensemble Architecture
The CardioPredict classification engine uses Breiman's Random Forest, an ensemble of $B=100$ bagged decision trees.

## 2. Mathematical Splitting Rule
Each decision tree node split evaluates a random subset of $m = \lfloor \sqrt{11} \rfloor \approx 3$ candidate features to maximize Gini gain:
$$\Delta \text{Gini} = \text{Gini}(D) - \left( \frac{|D_L|}{|D|} \text{Gini}(D_L) + \frac{|D_R|}{|D|} \text{Gini}(D_R) \right)$$
Where the Gini impurity of node dataset $D$ is:
$$\text{Gini}(D) = 1 - \sum_{k=1}^2 p_k^2$$

## 3. Soft Probability Calibration
The ensemble aggregates predictions through unweighted tree probability averaging:
$$P(\text{Disease} \mid x) = \frac{1}{B} \sum_{b=1}^B P_b(\text{Disease} \mid x)$$
$$P(\text{Healthy} \mid x) = 1.0 - P(\text{Disease} \mid x)$$

## 4. Risk Stratification Mapping
- **Low Risk**: $P(\text{Disease}) < 25.0\%$
- **Moderate Risk**: $25.0\% \le P(\text{Disease}) < 50.0\%$
- **Elevated Risk**: $50.0\% \le P(\text{Disease}) < 75.0\%$
- **High Risk**: $P(\text{Disease}) \ge 75.0\%$
