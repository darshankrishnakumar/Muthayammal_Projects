# API Specification & Endpoint Documentation

The Node.js Express Gateway operates on **Port 5016** with base prefix `/api`. The Python Inference Service operates on **Port 5017**.

## 1. Gateway Endpoints (Port 5016)

### 1.1 System & Health Checks
- `GET /health`
  - Returns gateway operational status and uptime.
  - Response: `{ "success": true, "data": { "status": "healthy", "uptime": 12.4 } }`
- `GET /api/system/status`
  - Returns multi-subsystem connectivity: database, ecgStorage, and cnnModel status.
  - Invariant: When Python model is offline, `cnnModel` reports `not_connected`.

### 1.2 Biometric Measurements
- `GET /api/health/measurements`: Lists biometric telemetry records with optional date filtering.
- `POST /api/health/measurements`: Ingests physiological vitals. Rejects invalid physiology with 422.
- `GET /api/health/summary`: Returns latest readings and 24-hour statistical aggregates.
- `GET /api/health/trends`: Returns formatted time-series data for Recharts visualization.

### 1.3 ECG Management
- `POST /api/ecg/upload`: Multipart file upload accepting `.csv`, `.json`, `.dat`, `.hea`.
  - Body: `file` (multipart/form-data)
  - Response: `{ "success": true, "data": { "recordingId": 1, "filename": "ecg_123.csv" } }`
- `GET /api/ecg/recordings`: Lists all uploaded recordings with metadata.
- `GET /api/ecg/recordings/:id`: Retrieves individual recording metadata without leaking disk paths.

### 1.4 Deep Learning Arrhythmia Predictions
- `POST /api/predictions`: Triggers 1D CNN inference on a stored recording ID.
  - Request: `{ "recordingId": 1 }`
  - Error: Returns HTTP 503 `MODEL_NOT_CONNECTED` if inference service is unreachable.
  - Success Response:
    ```json
    {
      "success": true,
      "data": {
        "predictionId": 1,
        "recordingId": 1,
        "predictedClass": "Ventricular Ectopic Beat",
        "predictedCode": "V",
        "confidenceScore": 0.7818,
        "explanation": "Analyzed 6 cardiac cycle(s). Predominant rhythm classified as Ventricular Ectopic Beat (V) with 78.2% model confidence.",
        "modelName": "Residual 1D CNN Arrhythmia Classifier",
        "modelVersion": "2.0.0"
      }
    }
    ```
- `GET /api/predictions/history`: Retrieves chronologically sorted list of genuine historical inferences.

### 1.5 Recommendations, Alerts & Reports
- `GET /api/recommendations`: Lists clinical recommendations (lifestyle, diagnostic, medication).
- `GET /api/alerts`: Lists clinical and technical alert notifications.
- `PATCH /api/alerts/:id/status`: Updates alert status to acknowledged or resolved.
- `GET /api/reports/summary`: Generates structured clinical diagnostic summary.

## 2. Python Inference Microservice Endpoints (Port 5017)

- `GET /health`: Verifies model weight initialization and AAMI class mapping readiness.
- `POST /predict`: Ingests `{ "filePath": "...", "fileFormat": "csv" }` or `{ "samples": [...] }`, applies digital filtering, and executes PyTorch forward pass.
