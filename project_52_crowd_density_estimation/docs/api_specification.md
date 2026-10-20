# API Specification: PROJECT-052 RESTful Microservice

## Base URL
`http://127.0.0.1:5052`

## Endpoints

### 1. System Health Check
- **Endpoint**: `GET /api/health/`
- **Description**: Returns microservice operational status, assigned port, database WAL mode status, device acceleration (MPS/CUDA), and model parameter counts.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 52 AI Crowd Density & Anomaly Analytics API",
  "project_id": "PROJECT-052",
  "port": 5052,
  "database_wal_mode": true,
  "cuda_available": false,
  "mps_available": true,
  "models": {
    "csrnet_crowd_model": "CSRNetCrowdDensityNet",
    "csrnet_parameters": 350950,
    "risk_regressor": "CrowdOpticalFlowRiskRegressorNet",
    "risk_regressor_parameters": 12648,
    "total_parameters": 363598
  }
}
```

### 2. System Analytics Summary
- **Endpoint**: `GET /api/analytics/summary`
- **Description**: Computes live aggregate statistics from the SQLite database.
- **Response**:
```json
{
  "total_monitored_scans": 6000,
  "active_anomaly_alerts": 1348,
  "mean_zonal_headcount": 218.0,
  "mean_turbulence_index": 0.45,
  "mean_risk_score": 0.38,
  "model_performance": {
    "density_mae_people": 4.8,
    "anomaly_f1_score": 0.942,
    "inference_latency_ms": 23.4,
    "baseline_mae_people": 16.2,
    "mae_reduction_pct": 70.37
  }
}
```

### 3. Scene Analysis & Ingestion
- **Endpoint**: `POST /api/crowd/analyze`
- **Request Body**:
```json
{
  "zone_name": "Central Plaza Concourse",
  "simulation_level": "high"
}
```
- **Response**: Returns event record, metrics, 16x16 spatial density map, safety directive, and SHA-256 audit block.

### 4. Cryptographic Audit Ledger
- **Endpoint**: `GET /api/crowd/audit-logs?limit=50`
- **Response**: Returns list of verified blocks and boolean `chain_valid`.
