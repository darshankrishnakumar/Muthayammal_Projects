# 05 — API Reference & Endpoints

## Base URL
`http://127.0.0.1:5055/api`

## Core Endpoints
### 1. Health Diagnostics
- **Method**: `GET`
- **Route**: `/api/health/`
- **Response**:
  ```json
  {
    "status": "HEALTHY",
    "project_id": "PROJECT-055",
    "port": 5055,
    "journal_mode": "WAL",
    "database_counts": { "cameras": 4, "incidents": 6000, "dispatches": 1195, "audit_blocks": 6001 },
    "models": {
      "temporal_fusion_model": { "parameters": 185990 },
      "crash_severity_regressor": { "parameters": 12648 },
      "total_parameters": 198638
    }
  }
  ```

### 2. Preset Scenarios
- **Method**: `GET`
- **Route**: `/api/incidents/presets`
- **Response**: 4 preset demonstration scenarios with complete kinematic vectors.

### 3. Dual-Model Inference & Live Analysis
- **Method**: `POST`
- **Route**: `/api/incidents/analyze`
- **Request Body**:
  ```json
  {
    "camera_id": "CAM-HWY-101-NORTH",
    "deceleration_g": 4.8,
    "orientation_yaw_deg": 180.0,
    "trajectory_deviation_m": 14.5,
    "impact_force_kn": 340.0,
    "delta_v_kph": 82.0,
    "post_impact_immobility_sec": 45.0,
    "actual_speed_kph": 118.0,
    "speed_limit_kph": 110.0,
    "vehicles_involved": 2,
    "road_friction_coeff": 0.72,
    "visibility_m": 850.0,
    "ambient_lux": 420.0,
    "rollover_detected": true
  }
  ```
- **Response**: Full classification, severity score, delta-V, dynamic cue weights, CAD dispatch payload, and chained block hash.

### 4. Cryptographic Audit Ledger
- **Method**: `GET`
- **Route**: `/api/incidents/audit-ledger?limit=50&offset=0`
- **Response**: Paginated blockchain records, total block count (6,001+), and chain integrity verification status (`VALID`).

### 5. Roadside Cameras
- **Method**: `GET`
- **Route**: `/api/streams/cameras`
- **Response**: Monitored corridors, geospatial coordinates, and video stream endpoints.
