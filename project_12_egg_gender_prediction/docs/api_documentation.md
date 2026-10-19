# API Documentation & Endpoint Reference

## Base URL
`http://127.0.0.1:5012/`

## Endpoints

### 1. Health & Status Check
- **Route**: `GET /api/health`
- **Description**: Verifies server responsiveness, neural engine readiness, and database connectivity.
- **Response**:
```json
{
  "status": "healthy",
  "service": "Egg Sex Prediction Neural Network",
  "engine": "Neural Network (MLP) + Shape Index Morphology",
  "database": {
    "status": "operational",
    "file": "/.../egg_history.db",
    "total_records": 50
  },
  "timestamp": 1792401555.998
}
```

### 2. Sample Specimen Listing
- **Route**: `GET /api/samples`
- **Description**: Retrieves list of reference calibration egg specimens.
- **Response**:
```json
{
  "samples": [
    {
      "id": "F01_standard_female.png",
      "filename": "F01_standard_female.png",
      "title": "F01 standard female",
      "expected_sex": "Female",
      "url": "/sample_image/F01_standard_female.png"
    }
  ]
}
```

### 3. Predict Single Specimen
- **Route**: `POST /api/predict`
- **Headers**: `Content-Type: application/x-www-form-urlencoded` or `multipart/form-data`
- **Parameters**:
  - `sample_id` (string, optional): ID of sample in calibration folder.
  - `file` (binary, optional): Uploaded egg photo.
- **Response**:
```json
{
  "success": true,
  "database_logged": true,
  "record_id": 51,
  "result": {
    "prediction": "Female (Hen)",
    "code": "FEMALE",
    "symbol": "♀",
    "color": "#ec4899",
    "confidence_pct": 65.7,
    "female_probability": 65.7,
    "male_probability": 34.3,
    "morphology": {
      "shape_index": 80.44,
      "elongation": 1.243,
      "apex_sharpness": 0.031,
      "asymmetry_index": 1.032,
      "roundness": 0.608
    },
    "recommendation": "Recommended for Egg Laying / Pullet flock development."
  }
}
```

### 4. Batch Dataset Evaluation
- **Route**: `POST /api/submit_all` (or `GET /api/evaluate_dataset`)
- **Description**: Evaluates all calibration eggs, computing confusion matrix and metrics.
- **Response**:
```json
{
  "success": true,
  "total_samples": 10,
  "correct_predictions": 10,
  "accuracy_pct": 100.0,
  "precision_pct": 100.0,
  "recall_pct": 100.0,
  "f1_score": 100.0,
  "confusion_matrix": {
    "true_female": 5,
    "true_male": 5,
    "false_female": 0,
    "false_male": 0
  }
}
```

### 5. Historical Audit Logs
- **Route**: `GET /api/history?limit=30`
- **Description**: Returns recent diagnostic history records from SQLite database.
