# API Documentation & Endpoint Reference

## Base URL
`http://127.0.0.1:5015/`

## 1. System Health Check
- **Endpoint**: `/api/health` (also `/health`)
- **Method**: `GET`
- **Description**: Returns operational status, port 5015, model architecture, feature names, and database statistics.
- **Sample Response**:
```json
{
  "database": {
    "status": "connected",
    "total_assessments": 31
  },
  "model": {
    "classifier": "RandomForestClassifier (100 Trees)",
    "feature_names": [
      "Age", "Sex", "ChestPainType", "RestingBP", "Cholesterol",
      "FastingBS", "RestingECG", "MaxHR", "ExerciseAngina", "Oldpeak", "ST_Slope"
    ],
    "features_count": 11
  },
  "port": 5015,
  "service": "CardioPredict Heart Disease Diagnostic System",
  "status": "healthy"
}
```

## 2. Patient Risk Assessment
- **Endpoint**: `/api/predict`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Payload**:
```json
{
  "Age": 62,
  "Sex": 1,
  "ChestPainType": 0,
  "RestingBP": 155,
  "Cholesterol": 290,
  "FastingBS": 1,
  "RestingECG": 2,
  "MaxHR": 110,
  "ExerciseAngina": 1,
  "Oldpeak": 3.5,
  "ST_Slope": 2
}
```
- **Response**:
```json
{
  "assessment_id": 32,
  "disease_probability": 88.0,
  "features": [62, 1, 0, 155, 290, 1, 2, 110, 1, 3.5, 2],
  "healthy_probability": 12.0,
  "prediction": 1,
  "probability": 88.0,
  "result_text": "🚨 Heart Disease Detected!",
  "risk_tier": "High"
}
```

## 3. Clinical PDF Report Download
- **Endpoint**: `/api/download-report`
- **Method**: `POST`
- **Payload**:
```json
{
  "prediction_result": "🚨 Heart Disease Detected!",
  "input_data": [62, 1, 0, 155, 290, 1, 2, 110, 1, 3.5, 2]
}
```
- **Response**: Binary stream of MIME type `application/pdf` with attachment filename `Heart_Disease_Report_YYYYMMDD_HHMMSS.pdf`.

## 4. Assessment History
- **Endpoint**: `/api/history`
- **Method**: `GET`
- **Query Parameters**: `limit` (optional integer, default=25)
- **Response**: List of recent patient assessment records from SQLite.

## 5. Aggregate Analytics
- **Endpoint**: `/api/stats`
- **Method**: `GET`
- **Response**: Summary counts, disease percentages, and average biomarker values across all historical consultations.
