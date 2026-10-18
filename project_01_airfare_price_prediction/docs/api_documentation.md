# API Specification (OpenAPI 3.0 Standard)

Base URL: `http://localhost:5001`

---

### 1. Health & Readiness Probe
- **Endpoint**: `GET /health`
- **Description**: Verifies service liveness, database connectivity, and ML model weights availability.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "airfare_prediction_service",
  "version": "1.0.0",
  "models_loaded": {
    "lstm": true,
    "random_forest": true,
    "preprocessor": true
  },
  "database_connected": true
}
```

---

### 2. Form Parameter Options
- **Endpoint**: `GET /api/options`
- **Description**: Returns validated enumerations for supported airlines, source cities, destinations, and additional services.
- **Response `200 OK`**:
```json
{
  "airlines": ["IndiGo", "Air India", "Jet Airways", "SpiceJet", "Multiple carriers", "GoAir", "Vistara", "Air Asia"],
  "sources": ["Banglore", "Kolkata", "Delhi", "Chennai", "Mumbai"],
  "destinations": ["New Delhi", "Banglore", "Cochin", "Kolkata", "Delhi", "Hyderabad"],
  "additional_info": ["No info", "In-flight meal not included", "No check-in baggage included", "1 Short layover", "1 Long layover", "Change airports", "Business class", "2 Long layover"]
}
```

---

### 3. Flight Fare Valuation
- **Endpoint**: `POST /api/predict`
- **Description**: Evaluates requested flight parameters and returns fare estimates with confidence intervals.
- **Request Body**:
```json
{
  "airline": "IndiGo",
  "source": "Delhi",
  "destination": "Cochin",
  "dep_date": "2026-11-15",
  "dep_time": "10:30",
  "arr_time": "13:45",
  "duration_hours": 3,
  "duration_mins": 15,
  "total_stops": 0,
  "additional_info": "No info"
}
```
- **Response `200 OK`**:
```json
{
  "status": "success",
  "prediction_id": "PRED-1729272300-8421",
  "predicted_price_inr": 5420.50,
  "confidence_interval": {
    "lower_inr": 4350.00,
    "upper_inr": 6490.00,
    "confidence_level": 0.95
  },
  "benchmark_rf_inr": 5280.00,
  "execution_time_ms": 14.8,
  "model_used": "PyTorch BiLSTM (2-Layer)"
}
```
- **Error Response `422 Unprocessable Entity`**: Returned when required parameters are missing or values fall outside legal ranges.

---

### 4. Query History & Logs
- **Endpoint**: `GET /api/history?limit=10`
- **Description**: Fetches persistent transaction history of logged predictions from SQLite database.
- **Response `200 OK`**:
```json
{
  "total_records": 152,
  "history": [
    {
      "id": 152,
      "timestamp": "2026-10-18T17:03:12Z",
      "airline": "IndiGo",
      "source": "Delhi",
      "destination": "Cochin",
      "total_stops": 0,
      "predicted_price": 5420.50,
      "latency_ms": 14.8
    }
  ]
}
```

---

### 5. Benchmark Performance Metrics
- **Endpoint**: `GET /api/metrics`
- **Description**: Exposes empirical test split performance metrics for both LSTM and Random Forest models.
- **Response `200 OK`**:
```json
{
  "lstm": {
    "r2_score": 0.7566,
    "mae": 1362.47,
    "rmse": 2275.89
  },
  "random_forest": {
    "r2_score": 0.8321,
    "mae": 1136.58,
    "rmse": 1890.12
  },
  "test_dataset_size": 2137
}
```

---

### 6. Aggregate Analytics
- **Endpoint**: `GET /api/analytics`
- **Description**: Computes high-level statistics across all queries (average fare by carrier, volume by route).
