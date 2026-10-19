# API Documentation: DEA-RNN Cyberbullying Detection Service

Base URL: `http://127.0.0.1:5009`

## Endpoints

### 1. `GET /health`
Returns system status and active port.
**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "DEA-RNN Cyberbullying Classifier",
  "port": 5009,
  "models_loaded": true,
  "timestamp": 1792399436.709
}
```

### 2. `GET /api/stats`
Returns aggregate platform metrics.
**Response (200 OK):**
```json
{
  "total_audited_scans": 3020,
  "cyberbullying_detected": 2516,
  "safe_clean_rate_pct": 16.7,
  "accuracy_pct": 100.0,
  "roc_auc": 1.0
}
```

### 3. `GET /api/metrics`
Returns formal evaluation scores and confusion matrix.
**Response (200 OK):**
```json
{
  "model_architecture": "DEA-RNN (Bi-GRU + Attention)",
  "accuracy": 1.0,
  "f1_score": 1.0,
  "roc_auc": 1.0
}
```

### 4. `POST /api/predict`
Analyzes a single tweet for cyberbullying.
**Request Body:**
```json
{
  "text": "Women should stay in the kitchen and stop pretending they understand engineering."
}
```
**Response (200 OK):**
```json
{
  "text": "Women should stay in the kitchen...",
  "predicted_category": "gender",
  "is_cyberbullying": true,
  "confidence": 0.9984,
  "severity_score": 0.9485,
  "moderation_action": "AUTOMATIC ACCOUNT QUARANTINE",
  "probabilities": {
    "not_cyberbullying": 0.0001,
    "gender": 0.9984,
    "religion": 0.0004,
    "age": 0.0003,
    "ethnicity": 0.0005,
    "other_cyberbullying": 0.0003
  },
  "token_attentions": [
    {"token": "women", "weight": 0.2841},
    {"token": "kitchen", "weight": 0.3125}
  ],
  "latency_ms": 18.4
}
```

### 5. `GET /api/history`
Returns recent SQLite transaction records.
