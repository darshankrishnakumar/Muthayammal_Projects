# API Specification: PROJECT-053 RESTful Microservice

## Base URL
`http://127.0.0.1:5053`

## Endpoints

### 1. System Health Check
- **Endpoint**: `GET /api/health/`
- **Description**: Returns microservice operational status, assigned port, database WAL mode status, device acceleration (MPS/CUDA), and model parameter counts.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 53 Intelligent Railway Track Defect Detection API",
  "project_id": "PROJECT-053",
  "port": 5053,
  "database_wal_mode": true,
  "cuda_available": false,
  "mps_available": true,
  "models": {
    "resunet_segmenter": "ResUNetRailDefectSegmenter",
    "resunet_parameters": 374342,
    "geometry_regressor": "RailTrackGeometryAndDegradationRegressorNet",
    "geometry_regressor_parameters": 12582,
    "total_parameters": 386924
  }
}
```

### 2. System Analytics Summary
- **Endpoint**: `GET /api/analytics/summary`
- **Description**: Computes live aggregate statistics from the SQLite database.
- **Response**:
```json
{
  "total_inspected_defects": 6000,
  "critical_priority_defects": 912,
  "mean_model_confidence": 0.948,
  "mean_track_quality_index": 82.5,
  "mean_derailment_risk": 0.22,
  "model_performance": {
    "mIoU_accuracy": 0.862,
    "baseline_mIoU": 0.584,
    "mIoU_gain_pct": 27.8,
    "inspection_latency_ms": 22.1,
    "f1_score": 0.952
  }
}
```

### 3. Track Inspection & Defect Inference
- **Endpoint**: `POST /api/rail/inspect`
- **Request Body**:
```json
{
  "chainage_km": "KM 144.200",
  "track_segment": "Line 1 Main Westbound",
  "simulated_condition": "crack"
}
```
- **Response**: Returns full record metadata, predicted defect type, pixel mask area, TQI, speed restriction, derailment risk, and cryptographic audit block index.

### 4. Presets
- **Endpoint**: `GET /api/rail/presets`
- **Description**: Retrieves 4 standardized corridor presets (Line 1 Main, Line 2 Freight, Metro Suburban, Mountain Pass Turnout).

### 5. Historical Defect Records
- **Endpoint**: `GET /api/rail/defects?skip=0&limit=20&track_segment=Line 1 Main Westbound&severity=Critical`
- **Description**: Paginated query of persistent SQLite defect inspection records.

### 6. Cryptographic Audit Logs
- **Endpoint**: `GET /api/rail/audit-logs?limit=50`
- **Description**: Validates the continuous SHA-256 block hash chain and returns blocks from Genesis Block #0.
