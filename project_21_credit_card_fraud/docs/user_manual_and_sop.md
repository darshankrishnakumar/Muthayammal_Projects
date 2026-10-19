# User Manual & FinTech Standard Operating Procedures (SOP)

## 1. Command Center Navigation
The VIGIL-CARD interface provides four operational modules accessible via the top navigation bar:
1. **⚡ Real-Time Telematics Stream**: Live incoming transaction ledger, dynamic Radial Risk Gauge, KPI cards, and instant fraud drill button.
2. **🔬 Forensic Inspector & SHAP Explainability**: Deep dive into individual transaction vectors, interactive preset loaders, and directional SHAP attribution waterfall.
3. **📊 Model Benchmarks & Threshold Studio**: Dynamic decision threshold slider (0.10 to 0.90), real-time confusion matrix, financial cost-benefit analysis, and ROC curve canvas.
4. **📁 Batch Evaluation & Card Sanctions**: High-volume transaction array batch runner with progress bar and active card sanctions blacklist ledger.

## 2. Operational Fraud SOP Matrix
- **CRITICAL RISK (Score >= 80%)**:
  1. Automated interlock declines checkout.
  2. Account latched in `blocked_cards` table.
  3. Real-time SMS and push notification sent to cardholder.
- **HIGH RISK (Score 50% - 79%)**:
  1. Transaction flagged for Step-Up 2FA challenge.
  2. 5-minute timeout window before auto-cancellation.
- **MEDIUM RISK (Score 25% - 49%)**:
  1. Transaction approved with tagged velocity tracking.
- **LOW RISK (Score < 25%)**:
  1. Frictionless sub-2ms approval.
