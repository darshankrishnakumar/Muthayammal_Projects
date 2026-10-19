# 06. REST API Specification (PROJECT-028)

The application exposes a RESTful HTTP service on assigned Port 5028:

### 1. `GET /api/health`
Returns system status, active port, model architectures, and database records count.

### 2. `POST /api/forecast`
Generates 24-hour hourly and 7-day daily forecasts for a selected city.
```json
// Request
{ "city": "Delhi", "days": 7 }

// Response
{
  "city": "Delhi",
  "country": "India",
  "current": { "aqi": 235, "hazard_class": "Very Unhealthy", "confidence": 0.899 },
  "daily_forecast": [ ... ],
  "hourly_trend": [ ... ],
  "meteorology": { "temperature_c": 31.5, "humidity_pct": 64.0, "wind_speed_kmh": 6.2 },
  "health_advisories": [ ... ],
  "inference_latency_ms": 1.96,
  "forecast_id": 4
}
```

### 3. `POST /api/predict/custom`
Instantaneous 6-class hazard classification over arbitrary custom pollutant vectors.

### 4. `GET /api/cities`
Returns metadata for all 10 monitored stations.

### 5. `GET /api/stats`
Returns database record counts, min/max/average AQI, and average latency.

### 6. `GET /api/history`
Returns historical forecast executions and linked hourly prediction summaries.
