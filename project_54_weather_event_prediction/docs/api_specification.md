# API Specification: PROJECT-054 RESTful Microservice

## Base URL
`http://127.0.0.1:5054`

## Endpoints

### 1. System Health Check
- **Endpoint**: `GET /api/health/`
- **Description**: Returns microservice operational status, assigned port, database WAL mode status, device acceleration (MPS/CUDA), and model parameter counts.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 54 AI Weather Event Nowcasting & Prediction API",
  "project_id": "PROJECT-054",
  "port": 5054,
  "database_wal_mode": true,
  "cuda_available": false,
  "mps_available": true,
  "models": {
    "bigru_weather_model": "BiGRUWeatherNowcastingNet",
    "bigru_parameters": 115270,
    "radar_precip_regressor": "RadarPrecipitationAndExtremeWeatherRegressorNet",
    "radar_regressor_parameters": 12615,
    "total_parameters": 127885
  }
}
```

### 2. System Analytics Summary
- **Endpoint**: `GET /api/analytics/summary`
- **Description**: Computes live aggregate statistics from the SQLite database.
- **Response**:
```json
{
  "total_nowcast_runs": 6000,
  "severe_weather_warnings": 1500,
  "mean_event_confidence": 0.958,
  "mean_cape_joules": 1650.0,
  "mean_severe_weather_risk": 0.35,
  "model_performance": {
    "nowcasting_accuracy": 0.958,
    "f1_score": 0.952,
    "precip_mae_mmh": 2.8,
    "inference_latency_ms": 11.4
  }
}
```

### 3. Mesoscale Nowcasting & Hazard Inference
- **Endpoint**: `POST /api/weather/nowcast`
- **Request Body**:
```json
{
  "station_name": "Plains Supercell Radar Station 02",
  "lead_time_hours": 2,
  "simulated_condition": "severe_storm"
}
```
- **Response**: Returns full record metadata, predicted event class, CAPE, precipitation rate, wind gusts, severe storm risk, temporal attention weights, and cryptographic audit block index.

### 4. Presets
- **Endpoint**: `GET /api/weather/presets`
- **Description**: Retrieves 4 standardized station presets (Coastal Maritime, Plains Supercell, Mountain Alpine Pass, Urban Convective Basin).

### 5. Historical Forecast Records
- **Endpoint**: `GET /api/weather/forecasts?skip=0&limit=20&station_name=Coastal Maritime Radar Station 01`
- **Description**: Paginated query of persistent SQLite weather nowcast records.

### 6. Cryptographic Audit Logs
- **Endpoint**: `GET /api/weather/audit-logs?limit=50`
- **Description**: Validates the continuous SHA-256 block hash chain and returns blocks from Genesis Block #0.
