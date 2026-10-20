# API Specification: AI Traffic Violation Detection Microservice (Port 5037)

## Base URL
`http://127.0.0.1:5037/`

## Endpoints

### 1. Health & Telemetry Liveness
- **Method**: `GET`
- **Route**: `/api/health`
- **Response**: `200 OK`
```json
{
  "active_cameras": 6,
  "classifier_accuracy": "100.00%",
  "framework": "PyTorch 2.x Deep Residual MLP & Dual-Head Multi-Target Regressor",
  "intersections_monitored": 4,
  "port": 5037,
  "service": "AI Traffic Violation Detection & ANPR Safety Enforcement API",
  "severity_mae": "5.23 points",
  "status": "healthy",
  "timestamp": "2026-10-20T00:16:03.282415+00:00",
  "total_violations_logged": 51
}
```

### 2. Vehicle Violation Analysis
- **Method**: `POST`
- **Route**: `/api/analyze`
- **Payload** (Single Vehicle or Multi-Vehicle Scene):
```json
{
  "vehicle_type": "Car",
  "speed_kmh": 98.0,
  "speed_limit": 60.0
}
```
- **Response**: `200 OK`
```json
{
  "camera_id": "CAM-101",
  "location": "INT-01 Central Plaza",
  "vehicles_detected": 1,
  "violations_found": 1,
  "total_fine_amount": 2000,
  "detections": [
    {
      "vehicle_id": 1,
      "vehicle_type": "Car",
      "license_plate": "TN62A7092",
      "speed_kmph": 98.0,
      "speed_limit": 60.0,
      "violation_detected": true,
      "violation_type": "Speeding",
      "confidence": 1.0,
      "severity_index": 73.2,
      "collision_risk": 0.7402,
      "fine_amount": 2000,
      "mva_section": "MVA Sec 183(1) - Dangerous Speed Violation"
    }
  ]
}
```

### 3. Intersections Topology
- **Method**: `GET`
- **Route**: `/api/intersections`
- **Response**: List of registered corridors (`INT-01`, `INT-02`, `INT-03`, `INT-04`).

### 4. Surveillance Cameras
- **Method**: `GET`
- **Route**: `/api/cameras`
- **Response**: List of configured optical/radar cameras (`CAM-101` through `CAM-106`).

### 5. E-Challan History
- **Method**: `GET`
- **Route**: `/api/challans?limit=30`
- **Response**: List of issued e-challans with evidence hashes.

### 6. Aggregated Stats
- **Method**: `GET`
- **Route**: `/api/stats`
- **Response**: Scanned vehicles, violation counts, revenue, and compliance rate.

### 7. Cryptographic Audit Ledger
- **Method**: `GET`
- **Route**: `/api/audit-logs?limit=25`
- **Response**: Block hash chain entries with SHA-256 tamper-evident hashes.
