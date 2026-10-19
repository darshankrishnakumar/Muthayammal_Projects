# REST API Specification: Customer Churn Intelligence (PROJECT-008)

## 1. Overview
The Customer Churn Intelligence Microservice exposes both human-interactive web routes and machine-readable RESTful JSON API endpoints for integration with enterprise telecommunication platforms, CRM pipelines, and dashboard aggregators.

- **Base URL**: `http://127.0.0.1:5008`
- **Default Port**: 5008
- **Data Exchange Format**: JSON (`application/json`) / Form URL-Encoded (`application/x-www-form-urlencoded`)

---

## 2. Endpoints

### 2.1 System Statistics (`/api/stats`)
- **Method**: `GET`
- **Description**: Returns live aggregated churn metrics, total audited database predictions, and active retention rates.
- **Response Format**: `200 OK`
```json
{
  "total": 24,
  "churn": 19,
  "stay": 5,
  "rate": 79.17
}
```

### 2.2 Model Performance Benchmarks (`/api/metrics`)
- **Method**: `GET`
- **Description**: Delivers offline holdout test metrics, confusion matrix counts, and feature importance rankings.
- **Response Format**: `200 OK`
```json
{
  "total_dataset_records": 7043,
  "train_records": 5634,
  "test_records": 1409,
  "test": {
    "accuracy": 0.7658,
    "precision": 0.5435,
    "recall": 0.7353,
    "f1": 0.625,
    "roc_auc": 0.8388,
    "confusion_matrix": {
      "tn": 804,
      "fp": 231,
      "fn": 99,
      "tp": 275
    }
  },
  "feature_names": ["gender", "SeniorCitizen", "Partner", "Dependents", "tenure", "..."],
  "feature_importances": [0.0141, 0.0154, 0.0148, 0.0152, 0.1799, "..."]
}
```

### 2.3 Historical Predictions Ledger (`/api/history`)
- **Method**: `GET`
- **Description**: Retrieves transactional historical records stored in the SQLite `predictions.db` audit ledger.
- **Response Format**: `200 OK`
```json
[
  {
    "id": 24,
    "customer_id": "CUST-48192",
    "prediction_date": "2026-10-19 13:59:15",
    "gender": "Female",
    "senior_citizen": 1,
    "partner": 0,
    "dependents": 0,
    "tenure": 1,
    "phone_service": 1,
    "multiple_lines": 1,
    "internet_service": "Fiber optic",
    "online_security": 0,
    "online_backup": 0,
    "device_protection": 0,
    "tech_support": 0,
    "streaming_tv": 0,
    "streaming_movies": 0,
    "contract": "Month-to-month",
    "paperless_billing": 1,
    "payment_method": "Electronic check",
    "monthly_charges": 95.50,
    "total_charges": 95.50,
    "prediction_status": "Churn",
    "churn_probability": 0.78,
    "risk_level": "High",
    "cltv": 477.50,
    "action_suggested": "Immediate outreach by Senior Retention Executive. Offer complimentary 3-month Tech Support and a 20% discount on a 1-year contract commitment."
  }
]
```

### 2.4 Interactive Inference (`/predict`)
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `gender`: `0` (Male) or `1` (Female)
  - `SeniorCitizen`: `1` if checked
  - `Partner`: `1` if checked
  - `Dependents`: `1` if checked
  - `Tenure`: Integer (1 - 72)
  - `PhoneService`: `1` if checked
  - `MultipleLines`: `1` if checked
  - `InternetService`: `0` (No), `1` (DSL), `2` (Fiber optic)
  - `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`: `1` if checked
  - `Contract`: `0` (Month-to-month), `1` (One year), `2` (Two year)
  - `PaperlessBilling`: `1` if checked
  - `PaymentMethod`: `0` (Bank transfer), `1` (Credit card), `2` (Electronic check), `3` (Mailed check)
  - `MonthlyCharges`: Numeric float (e.g., 65.00)
- **Response Format**: `200 OK` (Renders `predict.html` embedding Base64 image URIs for needle gauge, SHAP force plot, survival curve, and cumulative hazard plot).
