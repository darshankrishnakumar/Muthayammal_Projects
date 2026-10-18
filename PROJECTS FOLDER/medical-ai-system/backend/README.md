# Medical Sensor-Based Disease Prediction and Recommendation System Using CNN — Backend API

Reliable, secure, and clinical-safety-oriented JavaScript backend for medical sensor health monitoring and CNN-assisted disease prediction.

---

## 1. Architecture Overview

Built using modern **Node.js**, **Express.js**, **JavaScript ES Modules**, and **SQLite (`better-sqlite3`)**.

```
React Frontend (Vite + TypeScript)
       │
       │ HTTP / REST / Multipart Upload (Port 5000)
       ▼
Node.js + Express.js API
       │
       ├── Middleware (Helmet, CORS, Multer, Zod Validation, Centralized Error Handling)
       │
       ├── Routes & Controllers
       │     ├── /api/health          -> Biometric measurements, trends, and summary
       │     ├── /api/ecg             -> Secure ECG uploads, storage, and deletion
       │     ├── /api/predictions     -> CNN prediction gateway with 503 safety lock
       │     ├── /api/recommendations -> Reviewed illustrative health guidance
       │     ├── /api/alerts          -> Technical and data-quality alerts
       │     ├── /api/reports         -> Aggregated analytics & summaries
       │     └── /api/system          -> Verified live system & model statuses
       │
       ├── Storage & Data Layer
       │     ├── SQLite Database (`better-sqlite3` WAL mode)
       │     └── Validated Local Storage (`./storage/ecg`, `./storage/reports`)
       │
       └── Future Inference Adapter (`src/services/modelAdapter.js`)
             └── 1D CNN Model / Microservice (TensorFlow.js or HTTP service)
```

---

## 2. Medical AI Ethics & Safety Invariants

1. **No Synthetic Predictions**: This system strictly **never fabricates** synthetic disease classifications or random model confidence scores.
2. **Explicit 503 Guard**: When a validated CNN model is not connected, `POST /api/predictions` returns an explicit `503 Service Unavailable` with `MODEL_NOT_CONNECTED`.
3. **Plausibility & Data Quality**: Biometric readings are validated against physiological bounds. Plausible normal/borderline readings are stored with `data_quality_status = 'valid'`; extreme physiological values are flagged as `review_required`.
4. **Illustrative Guidance**: Predefined recommendations are marked as `illustrative`. The system explicitly clarifies it does **not** replace a healthcare professional.

---

## 3. Technology Stack

- **Runtime**: Node.js (v20+ / v22+ / v24+)
- **Framework**: Express.js 4
- **Module System**: JavaScript ES Modules (`"type": "module"`)
- **Database**: SQLite via `better-sqlite3` (with WAL mode, foreign keys, and parameterized statements)
- **Validation**: Zod
- **File Uploads**: Multer (disk storage, path traversal protection, file type filtering, size caps)
- **Security**: Helmet, CORS
- **Configuration**: dotenv
- **Testing**: Node.js Test Runner (`node --test`) + Supertest

---

## 4. Folder Structure

```
backend/
├── src/
│   ├── config/
│   │   ├── env.js                 # Environment configuration & path resolvers
│   │   └── database.js            # SQLite schema initialization and pragmas
│   ├── controllers/
│   │   ├── healthController.js    # Biometrics & summary logic
│   │   ├── ecgController.js       # ECG upload & record management
│   │   ├── predictionController.js# Prediction dispatch & history
│   │   ├── recommendationController.js # Guidelines retrieval
│   │   ├── alertController.js     # Health and technical alerts
│   │   ├── reportController.js    # Aggregate operational reports
│   │   └── systemController.js    # Live verified readiness status
│   ├── routes/
│   │   ├── healthRoutes.js
│   │   ├── ecgRoutes.js
│   │   ├── predictionRoutes.js
│   │   ├── recommendationRoutes.js
│   │   ├── alertRoutes.js
│   │   ├── reportRoutes.js
│   │   └── systemRoutes.js
│   ├── repositories/
│   │   ├── measurementRepository.js   # Prepared statements for measurements
│   │   ├── ecgRepository.js           # Prepared statements for ECG recordings
│   │   ├── predictionRepository.js    # Prepared statements for genuine inference
│   │   ├── recommendationRepository.js # Prepared statements for guidelines
│   │   ├── alertRepository.js         # Prepared statements for alerts
│   │   ├── systemEventRepository.js   # Event logging operations
│   │   └── dashboardRepository.js     # Dashboard vitals and metrics queries
│   ├── services/
│   │   ├── healthService.js       # Biometric business logic & Recharts transforms
│   │   ├── ecgService.js          # File storage & metadata persistence
│   │   ├── predictionService.js   # CNN workflow with safety guard
│   │   ├── recommendationService.js # Reviewed guidance repository
│   │   ├── alertService.js        # Alert query & status updates
│   │   ├── reportService.js       # Metrics & summary aggregation
│   │   └── modelAdapter.js        # Extensible CNN model interface
│   ├── middleware/
│   │   ├── errorHandler.js        # Centralized error handler
│   │   ├── validateRequest.js     # Zod schema validation middleware
│   │   ├── uploadMiddleware.js    # Secure Multer configuration
│   │   └── notFoundHandler.js     # 404 handler
│   ├── schemas/
│   │   ├── healthSchemas.js       # Physiological plausibility schemas
│   │   ├── ecgSchemas.js          # ECG parameters & query schemas
│   │   └── predictionSchemas.js   # Prediction payload schemas
│   ├── utils/
│   │   ├── response.js            # Unified JSON response envelope
│   │   └── logger.js              # Privacy-safe logger (scrubs raw ECG/vitals)
│   ├── app.js                     # Express app setup & route assembly
│   └── server.js                  # HTTP server & graceful shutdown
├── storage/
│   ├── ecg/                       # Stored ECG files (non-public directory)
│   └── reports/                   # Exported report files
├── tests/
│   ├── health.test.js             # Biometrics & validation tests
│   ├── ecg.test.js                # Upload, extension, & storage tests
│   ├── predictions.test.js        # Safety invariant & 503 guard tests
│   └── recommendations.test.js    # Alerts, reports, & guidance tests
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

---

## 5. Installation & Setup

### Prerequisites
- Node.js (v20 or newer recommended)
- npm

### 1. Clone & Enter Directory
```bash
cd backend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configuration parameters:
```ini
PORT=5000
NODE_ENV=development
FRONTEND_URL=http://localhost:5173,http://localhost:8080
DATABASE_PATH=./storage/medical.db
ECG_STORAGE_PATH=./storage/ecg
REPORTS_STORAGE_PATH=./storage/reports
MAX_UPLOAD_SIZE_MB=10

# Leave empty until a validated model microservice is active:
MODEL_SERVICE_URL=
```

---

## 6. Running the Backend

### Start Server in Production/Standard Mode
```bash
npm start
```

### Start Server in Development Mode (Live Watch)
```bash
npm run dev
```

The API will be available at:
👉 `http://localhost:5000`

---

## 7. Running Automated Tests

Run the full automated test suite with the built-in Node test runner:
```bash
npm test
```

All 28 tests run against an isolated in-memory SQLite database (`:memory:`) without touching persistent storage:
- Server startup and health checks
- Biometric measurement creation and physiological plausibility validation
- Rejection of invalid vitals (negative HR, invalid BP, SpO2 > 100%)
- Time-series trend formatting for Recharts
- Multipart ECG upload validation and unsupported format rejection (415)
- Non-existent resource handling (404)
- **CNN safety invariant verification (returns 503 without storing fake records)**
- Reviewed recommendation and alert retrieval

---

## 8. API Endpoint Reference

### Response Envelope Standards

#### Success (`200` / `201`)
```json
{
  "success": true,
  "message": "Request completed successfully",
  "data": {}
}
```

#### Error (`400`, `404`, `413`, `415`, `500`, `503`)
```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "The submitted data is invalid.",
  "details": []
}
```

---

### System Status
- `GET /api/system/status` — Live status of backend, SQLite database, ECG storage, and CNN model adapter.

---

### Biometric Measurements
- `GET /api/health/measurements` — Retrieve measurements (filters: `measurementType`, `startDate`, `endDate`, `limit`, `offset`).
- `GET /api/health/measurements/:id` — Retrieve a single measurement.
- `POST /api/health/measurements` — Create a measurement record. Supports both single metric entries and multi-metric sensor bundles.
  
  *Example (Single Metric):*
  ```json
  {
    "measurementType": "heart_rate",
    "value": 78,
    "unit": "bpm",
    "source": "manual",
    "measuredAt": "2026-10-09T10:00:00Z"
  }
  ```

  *Example (Blood Pressure):*
  ```json
  {
    "measurementType": "blood_pressure",
    "systolic": 120,
    "diastolic": 80,
    "unit": "mmHg",
    "source": "manual"
  }
  ```

- `GET /api/health/summary` — Latest readings and summary aggregates (count, min, max, average).
- `GET /api/health/trends` — Formatted time-series vitals for Recharts (`[{ timestamp, heartRate, systolic, diastolic, spo2, temperature }]`).

---

### ECG File Management
- `POST /api/ecg/upload` — Upload ECG recording (`multipart/form-data`, field name `file`).
  - Allowed extensions: `.csv`, `.txt`, `.dat`, `.json`, `.edf`.
  - Max size: `10MB` (configurable via `MAX_UPLOAD_SIZE_MB`).
  - Stored outside web root with unique cryptographically random filenames.
- `GET /api/ecg/recordings` — List recordings with metadata.
- `GET /api/ecg/recordings/:id` — Retrieve recording metadata (internal filesystem paths are kept private).
- `DELETE /api/ecg/recordings/:id` — Safely deletes recording file and database record.

---

### CNN Predictions (Safety Protected)
- `POST /api/predictions` — Request prediction analysis for an ECG recording.
  ```json
  {
    "ecgRecordingId": 1
  }
  ```
  *When model is not connected (Current Status):*
  **HTTP 503 Service Unavailable**
  ```json
  {
    "success": false,
    "code": "MODEL_NOT_CONNECTED",
    "message": "The CNN model has not been connected."
  }
  ```
- `GET /api/predictions` — List prediction records.
- `GET /api/predictions/history` — Returns prediction history structured for frontend `PredictionResult` interface.
- `GET /api/predictions/:id` — Single prediction record.

---

### Health Recommendations & Alerts
- `GET /api/recommendations` — List reviewed guidance (filters: `category`).
- `GET /api/recommendations/:id` — Single recommendation.
- `GET /api/alerts` — List health and system alerts (filters: `status`, `severity`, `alertType`).
- `PATCH /api/alerts/:id/status` — Update alert status (`acknowledged`, `dismissed`, `resolved`).

---

### Reports
- `GET /api/reports/summary` — Aggregated operational statistics (counts by measurement type, quality breakdown, predictions, and alerts).
- `GET /api/reports/measurements` — Detailed measurement export with date range filtering.

---

## 9. Frontend Integration

In the existing React frontend (`pixel-perfect-pixels`):

1. Set `.env` or `.env.local`:
   ```ini
   VITE_API_BASE_URL=http://localhost:5000/api
   ```
2. Start the Vite development server:
   ```bash
   cd pixel-perfect-pixels
   npm run dev
   ```
3. The frontend's `apiClient.ts` will connect to `http://localhost:5000` with full CORS support.

---

## 10. Future CNN Model Adapter Integration

To connect a trained 1D CNN model in future phases:
1. Export model weights and architecture (e.g. from Keras/PyTorch) to TensorFlow.js (`model.json` + `.bin`) or serve via a dedicated microservice.
2. In `backend/.env`, set `MODEL_SERVICE_URL=http://localhost:8000`.
3. In `src/services/modelAdapter.js`, implement standardized signal preprocessing:
   - Resample signal to benchmark frequency (e.g. 360 Hz).
   - Normalize amplitude (z-score or min-max).
   - Feed windowed sample into `model.predict()`.
4. When `modelAdapter.isModelConnected()` returns `true`, the `503` guard lifts automatically and stores genuine model outputs with valid confidence probabilities.
