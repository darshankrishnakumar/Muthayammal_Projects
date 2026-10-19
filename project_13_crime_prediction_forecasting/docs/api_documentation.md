# API Documentation & Endpoint Reference

## Base URL
`http://127.0.0.1:5013/`

## Endpoints

### 1. Health & Status
- **Route**: `GET /health`
- **Description**: Verifies service operational status, database connectivity, and loaded model architectures.
- **Response**:
```json
{
  "status": "healthy",
  "service": "Urban Crime Prediction & Deep Learning Forecasting Subsystem",
  "port": 5013,
  "database": {
    "status": "connected",
    "file": ".../crime_incident.db",
    "total_incidents": 5040
  },
  "models": {
    "risk_dnn": "CrimeRiskDNN (PyTorch 11-128-64-32-4)",
    "type_classifier": "RandomForestClassifier (150 trees)",
    "classes": ["CRITICAL", "HIGH", "LOW", "MODERATE"]
  },
  "timestamp": 1792402374.9
}
```

### 2. Police Districts
- **Route**: `GET /api/districts`
- **Description**: Returns list of all 8 municipal police districts with geographical coordinates and baseline risk indices.

### 3. Predict Crime Risk & Incident Type
- **Route**: `POST /api/predict_risk`
- **Body**:
```json
{
  "hour": 23,
  "day_of_week": 5,
  "month": 10,
  "is_weekend": 1,
  "district": "Central Downtown",
  "location_type": "Nightclub / Bar",
  "historical_density": 8.5,
  "ambient_light": 2,
  "patrol_score": 2,
  "latitude": 41.8825,
  "longitude": -87.6285
}
```
- **Response**:
```json
{
  "success": true,
  "incident_id": "CR-LIVE-102941",
  "timestamp": "2026-10-19 15:00:00",
  "district": "Central Downtown",
  "location_type": "Nightclub / Bar",
  "predicted_risk": "CRITICAL",
  "risk_confidence": 88.4,
  "predicted_crime_type": "ROBBERY",
  "type_confidence": 62.5,
  "risk_probabilities": {
    "CRITICAL": 62.5,
    "HIGH": 25.0,
    "MODERATE": 10.0,
    "LOW": 2.5
  },
  "recommendation": "URGENT - CODE 3: Dispatch Immediate High-Visibility Tactical Patrol Unit",
  "patrol_dispatched": true,
  "inference_latency_ms": 4.2
}
```

### 4. 24-Hour Temporal Curve Forecast
- **Route**: `POST /api/forecast_hourly`
- **Body**:
```json
{
  "district": "Central Downtown",
  "day_of_week": 5,
  "month": 10,
  "location_type": "Street / Sidewalk"
}
```
- **Response**:
```json
{
  "success": true,
  "district": "Central Downtown",
  "day_of_week": 5,
  "hourly_forecast": [
    { "hour": 0, "hour_label": "00:00", "risk_category": "CRITICAL", "spike_probability": 82.5, "is_night": true }
  ],
  "peak_hour": "23:00",
  "computation_time_ms": 18.5
}
```

### 5. Dispatch Patrol Unit
- **Route**: `POST /api/dispatch_unit`
- **Body**:
```json
{
  "unit_callsign": "ALPHA-12",
  "assigned_district": "Central Downtown",
  "priority_level": "URGENT - CODE 3",
  "incident_type": "ROBBERY",
  "eta_minutes": 4
}
```
