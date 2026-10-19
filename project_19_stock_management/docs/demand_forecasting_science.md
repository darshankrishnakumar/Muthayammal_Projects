# Demand Forecasting Science & Operations Research

## 1. Mathematical Problem Formulation
In continuous inventory management under stochastic consumption, two critical decision variables govern the replenishment cycle:
1. **Reorder Point (ROP)**: When to issue a replenishment purchase order.
2. **Economic Order Quantity (EOQ)**: How many units to order to balance inventory holding costs against order placement costs.

### Analytical Formulations
- **Safety Stock ($SS$)**:
  $$SS = Z 	imes \sqrt{L} 	imes \sigma_d$$
  Where $Z = 1.96$ corresponding to a 98.5% enterprise service level target, $L$ is supplier replenishment lead time in days, and $\sigma_d$ is the standard deviation of daily SKU demand.

- **Reorder Point ($ROP$)**:
  $$ROP = (d_{\text{daily}} 	imes L) + SS$$
  Where $d_{\text{daily}}$ represents the mean daily consumption rate over the historical lookback period.

- **Economic Order Quantity ($EOQ$)**:
  $$EOQ = \sqrt{\frac{2 \times D \times S}{H}}$$
  Where $D$ is annual projected unit demand, $S = \text{INR } 650$ is fixed administrative ordering setup cost, and $H = 0.18 \times \text{unit\_cost}$ is annual per-unit holding cost (18% carrying rate).

- **Stockout Risk Metric**:
  $$\text{Risk}\% = \max\left(0.5, \min\left(99.0, \left(1 - \frac{\text{CurrentStock}}{ROP}\right) \times 100\right)\right)$$

## 2. Multi-Horizon Demand Forecasting
The system forecasts daily demand seven days into the future:
$$Y_{\text{ensemble}} = 0.40 \cdot Y_{\text{LSTM}} + 0.30 \cdot Y_{\text{RF}} + 0.30 \cdot Y_{\text{GBM}}$$

95% Statistical Confidence Intervals:
$$\text{Upper} = Y_{\text{ensemble}} + 1.96 \cdot \sigma_{\text{recent}}$$
$$\text{Lower} = \max(0, Y_{\text{ensemble}} - 1.96 \cdot \sigma_{\text{recent}})$$
