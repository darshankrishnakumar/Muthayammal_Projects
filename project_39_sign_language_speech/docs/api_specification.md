# API Specification: Sign Language & Speech Microservice (Port 5039)

## Base URL
`http://127.0.0.1:5039/`

## Endpoints

### 1. Health & Telemetry Liveness
- **Route**: `GET /api/health/` and `GET /api/health`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 39 Sign Language Recognition & Speech API",
  "port": 5039,
  "cuda_available": false,
  "mps_available": true,
  "device": "mps",
  "models": {
    "gesture_classifier": "BiLSTMSignAttentionNet (700,107 params)",
    "prosody_regressor": "SpeechProsodyAcousticRegressorNet (83 KB)"
  },
  "database": "sign_speech.db (SQLite WAL Mode)"
}
```

### 2. Gesture Translation & Speech Prediction
- **Route**: `POST /api/translation/predict`
- **Request**:
```json
{
  "gesture_index": 0,
  "session_id": "LIVE-SESSION-1"
}
```
- **Response**:
```json
{
  "gloss": "HELLO",
  "spoken_sentence": "Hello, how can I assist you today?",
  "confidence": 1.0,
  "class_id": 0,
  "latency_ms": 18.4,
  "prosody": {
    "pitch_f0_hz": 182.5,
    "duration_seconds": 1.76,
    "energy_db": 62.7,
    "prosody_quality_score": 48.5
  },
  "evidence_hash": "c85821b8..."
}
```

### 3. Translation History Logs
- **Route**: `GET /api/translation/logs?limit=10`
- **Response**: Array of translation logs with timestamps, acoustic prosody, and SHA-256 evidence hashes.

### 4. Standard Vocabulary
- **Route**: `GET /api/translation/vocabulary`
- **Response**: Array of 10 standard sign classes with movement descriptions.

### 5. Cryptographic Audit Ledger
- **Route**: `GET /api/translation/audit-logs?limit=10`
- **Response**: Array of chained audit blocks with SHA-256 digests.

### 6. Analytics Summary
- **Route**: `GET /api/analytics/summary`
- **Response**: Total translations count, average confidence, and model accuracy KPIs.
