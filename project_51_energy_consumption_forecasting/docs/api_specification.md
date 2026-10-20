# API Specification: PROJECT-051 RESTful Microservice

## Base URL
`http://127.0.0.1:5051`

## Endpoints

### 1. System Health Check
- **Endpoint**: `GET /api/health/`
- **Description**: Returns microservice operational status, assigned port, database WAL mode status, device acceleration (MPS/CUDA), and model parameter counts.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 51 Smart Energy Forecasting & Peak Shaving API",
  "project_id": "PROJECT-051",
  "port": 5051,
  "database_wal_mode": true,
  "cuda_available": false,
  "mps_available": true,
  "models": {
    "multi_horizon_lstm": "MultiHorizonEnergyLSTM",
    "lstm_parameters": 145496,
    "grid_regressor": "GridPeakAndCarbonEmissionRegressorNet",
    "grid_regressor_parameters": 12613,
    "total_parameters": 158109
  }
}
```

### 2. System Analytics Summary
- **Endpoint**: `GET /api/analytics/summary`
- **Description**: Computes live aggregate statistics from the SQLite database.
- **Response**:
```json
{
  "total_plans": 6000,
  "mean_peak_shaving_pct": 22.0,
  "total_daily_cost_savings": 745200.0,
  "forecast_horizon_hours": 24,
  "forecasting_accuracy": {
    "mape_percentage": 3.42,
    "rmse_kwh": 12.8,
    "latency_ms": 13.5
  }
}
```

### 3. Optimization & Dispatch
- **Endpoint**: `POST /api/energy/optimize`
- **Request Body**:
```json
{
  "facility_name": "Tech Campus Science Complex A",
  "archetype": "COMMERCIAL_OFFICE_CAMPUS",
  "nominal_base_load": 480.0,
  "ambient_temperature": 26.5,
  "tou_tariff_rate": 18.5,
  "renewable_penetration": 35.0,
  "target_shave_pct": 22.4
}
```
- **Response**: Returns optimized energy plan, 24-hour hourly load curves, daily cost savings, avoided carbon emissions, and SHA-256 audit block.

### 4. Cryptographic Audit Ledger
- **Endpoint**: `GET /api/energy/audit-logs?limit=50`
- **Response**: Returns list of verified blocks and boolean `chain_valid`.
