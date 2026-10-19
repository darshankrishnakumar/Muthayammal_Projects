# REST API Reference & Endpoint Specification

Host Address: `http://127.0.0.1:5020`

## 1. System Health & Metadata
- **`GET /api/health`**
  - **Returns**: `status`, `service`, `model`, `yolo_loaded`, `device`, `classes`, `cameras_online`, `server_time`.

## 2. Weapon Detection
- **`POST /api/detect`**
  - **Payload**: `{"image": "<base64_string>", "camera_id": "CAM-01", "confidence_threshold": 0.45, "iou_threshold": 0.45}`
  - **Returns**: `success`, `incident_id`, `detections`, `weapon_detected`, `alert_level`, `message`, `recommended_action`, `inference_time_ms`, `forensics`, `lockdown_active`.

## 3. Sample Evaluation Catalog
- **`GET /api/samples`**
  - **Returns**: List of curated test surveillance scenarios (handgun, knife, rifle, suspicious package, civilian safe).
- **`POST /api/samples/test/<sample_id>`**
  - **Returns**: Full detection inference and forensic metrics evaluated on disk sample.

## 4. Security Incident Management
- **`GET /api/incidents`**: Returns all recorded incidents from SQLite.
- **`GET /api/detections/history`**: Returns recent detections with optional `?limit=`, `?severity=`, `?class=` filters.
- **`PATCH /api/incidents/<incident_id>/status`**: Updates incident status (`UNDER_REVIEW`, `SECURITY_DISPATCHED`, `RESOLVED`) and tactical notes.

## 5. Security Configuration & Telemetry
- **`GET /api/cctv/cameras`**: Returns camera node metadata from `cctv_cameras`.
- **`GET /api/threats`**: Returns 5-tier threat taxonomy and protocols.
- **`GET /api/audit`**: Returns system audit event ledger.
- **`GET /api/stats`**: Returns real-time security dashboard analytics.
- **`GET /api/model/metrics`**: Returns neural architecture specs and confusion matrix.
- **`POST /api/emergency/lockdown`**: Toggles site-wide automated lockdown.
- **`GET /api/export/report`**: Exports comprehensive forensic JSON audit report.
