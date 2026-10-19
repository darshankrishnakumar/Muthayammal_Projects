# API Documentation & Endpoint Reference

## Base URL
`http://127.0.0.1:5014/`

## 1. System Health Check
- **Endpoint**: `/api/health`
- **Method**: `GET`
- **Description**: Returns operational health, port number, model metadata, vocabulary dimension, and database connectivity.
- **Sample Response**:
```json
{
  "database": {
    "status": "connected",
    "total_verifications": 42
  },
  "model": {
    "classifier": "PassiveAggressiveClassifier (TF-IDF Vectorizer)",
    "source_watermark_filter": true,
    "vocabulary_size": 146627
  },
  "port": 5014,
  "service": "Fake News Detection & Explainable Stylometry Subsystem",
  "status": "healthy"
}
```

## 2. Text Verification & XAI Prediction
- **Endpoint**: `/api/predict`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Payload**:
```json
{
  "news": "Secret government plan revealed to control weather with cell towers",
  "pure_language_mode": false
}
```
- **Response**:
```json
{
  "is_fake": true,
  "verdict_title": "Looking Fake News 📰",
  "confidence": 88.5,
  "fake_pct": 88.5,
  "real_pct": 11.5,
  "decision_score": 2.04,
  "sensational_score": 60,
  "sensationalism_level": "High Sensationalism / Clickbait",
  "tone_description": "Sensational Alert / Alarmist",
  "annotated_words": [
    {"token": "Secret", "clean": "secret", "direction": "fake", "impact": 0.438, "weight": 1.52},
    {"token": "plan", "clean": "plan", "direction": "fake", "impact": 0.125, "weight": 0.43}
  ]
}
```

## 3. Verification History Log
- **Endpoint**: `/api/history`
- **Method**: `GET`
- **Query Parameters**: `limit` (optional integer, default=25)
- **Response**: Array of recent verification records with headline, scores, and timestamps.

## 4. Aggregate Analytics
- **Endpoint**: `/api/stats`
- **Method**: `GET`
- **Response**: Aggregate metrics including total verifications, fake count, real count, and average sensationalism score.
