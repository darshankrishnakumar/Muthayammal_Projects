# Walkthrough Video Timestamps: Customer Churn Intelligence (PROJECT-008)

**Total Duration**: 03:00 (180.0 Seconds)  
**Video File**: `walkthrough/walkthrough_video.mp4`  
**Application Port**: `http://127.0.0.1:5008`  

| Timestamp Range | Duration | Demonstration Phase | Core UI / System Action Observed |
|---|---|---|---|
| `00:00 - 00:25` | 25s | **Executive Dashboard & KPIs** | Overview on `/`: 7,043 customers, 26.5% churn rate, retention donut chart, recent logs |
| `00:25 - 00:55` | 30s | **Prediction Form & Intake** | Navigate to `/predict`: Demographics, Services, Fiber Optic, Month-to-Month inputs |
| `00:55 - 01:25` | 30s | **Random Forest Churn Assessment**| Submit prediction: 78.4% high risk needle gauge, CLTV calculation, tailored retention action |
| `01:25 - 01:50` | 25s | **Survival & Hazard Curves** | Scroll down to Cox model plots: 72-month survival decay curve and cumulative hazard spike |
| `01:50 - 02:15` | 25s | **SHAP Explainability Breakdown** | Scroll down to SHAP force waterfall plot: local feature impact on churn log-odds |
| `02:15 - 02:35` | 20s | **Model Benchmarks & Metrics** | Navigate to `/model-performance`: ROC-AUC 0.844, Confusion Matrix, feature importances |
| `02:35 - 02:50` | 15s | **SQLite Audit Ledger Table** | Navigate to `/history`: Transactional audit table with search, timestamps, and customer IDs |
| `02:50 - 03:00` | 10s | **Conclusion & Capstone Sign-Off**| Return to `/`: Summary of 23 passing tests, model verification, and submission sign-off |
