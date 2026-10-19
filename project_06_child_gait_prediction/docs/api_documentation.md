# REST API Documentation - Child Gait Prediction System

The Child Gait Prediction microservice provides asynchronous REST endpoints running on `http://127.0.0.1:5006`.

---

## 1. System Health & Metadata

### `GET /api`
Returns service description, status, database status, record count, and medical disclaimers.

**Response (200 OK):**
```json
{
  "service": "Child Gait Prediction System API",
  "status": "online",
  "database": "SQLite (gait_records)",
  "total_records": 34,
  "disclaimer": "This application is a college-level machine learning prototype intended for educational and decision-support purposes..."
}
```

### `GET /api/health`
Returns continuous heartbeat monitoring.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Child Gait Prediction AI",
  "database": "connected",
  "table": "gait_records",
  "total_records": 34,
  "port": 5006
}
```

---

## 2. Predictive Biomechanical Inference

### `POST /api/predict`
Evaluates pediatric gait kinematics, returns diagnostic classification with confidence and clinical recommendations, and persists the record into SQLite.

**Request Payload:**
```json
{
  "child_id": "C-101",
  "age": 7,
  "gender": "Male",
  "heel_pressure": 115.0,
  "toe_pressure": 220.0,
  "tilt_angle": 14.5,
  "step_duration": 0.78,
  "stride_length": 52.0,
  "walking_speed": 0.65
}
```

**Response (200 OK):**
```json
{
  "prediction": "Diplegic",
  "confidence": 0.92,
  "assessmentId": "gait-3c72e29381",
  "recommendations": [
    "Bilateral spasticity or crouch gait features detected across lower limbs.",
    "Recommend pediatric physical therapy evaluation for lower limb motor tone.",
    "Assess sagittal joint kinematics (hip flexion, knee extension, ankle equinus).",
    "Consider gait laboratory biomechanical evaluation and AFO orthotic suitability."
  ],
  "record": {
    "id": "gait-3c72e29381",
    "child_id": "C-101",
    "age": 7,
    "gender": "Male",
    "heel_pressure": 115.0,
    "toe_pressure": 220.0,
    "tilt_angle": 14.5,
    "step_duration": 0.78,
    "stride_length": 52.0,
    "walking_speed": 0.65,
    "gait_class": "Diplegic",
    "confidence": 0.92,
    "data_source": "real",
    "created_at": "2026-10-19T13:24:31.074010"
  },
  "disclaimer": "This application is a college-level machine learning prototype intended for educational and decision-support purposes."
}
```

---

## 3. Historical Record Management

### `GET /api/records`
Retrieves all historical assessment records, with optional filtering by Child ID.

**Query Parameters:**
- `childId` (optional string): Filter records by specific child ID (e.g. `?childId=C-101`).

### `GET /api/records/{id}`
Retrieves a specific assessment record by primary key UUID.

### `DELETE /api/records/{id}`
Deletes an assessment record from `gait_records`.

**Response (200 OK):**
```json
{
  "status": "deleted",
  "id": "gait-3c72e29381"
}
```

---

## 4. Administrative Data Ingestion

### `POST /api/import-csv`
Imports batch gait records from a CSV file into SQLite.
