# 06. REST API Specification

The backend exposes RESTful endpoints on `http://127.0.0.1:5025`:

### 1. Health Status
- **Endpoint:** `GET /api/health`
- **Response:**
```json
{
  "architecture": "1D-CNN + Bi-LSTM with Self-Attention Pooling (DeepSERNet)",
  "database_backend": "SQLite ACID Relational DB (speech_emotion.db)",
  "status": "healthy",
  "supported_emotions": 7,
  "total_audios_processed": 12
}
```

### 2. Emotion Recognition
- **Endpoint:** `POST /api/recognize`
- **Payload:**
```json
{
  "audio_info": {
    "language": "English",
    "preset_emotion": "happy",
    "duration": 3.8
  },
  "note": "Customer service feedback"
}
```
*(Also supports flat payload: `{"language": "en", "preset_emotion": "happy"}`)*
- **Response:** Returns classified emotion, icon, color, confidence percentage, Valence, Arousal, 40-dim features, and 7-class distribution.

### 3. Classification History
- **Endpoint:** `GET /api/history`
- **Response:** Array of recent audio session records from SQLite.

### 4. Language Statistics
- **Endpoint:** `GET /api/languages`
- **Response:** Array of supported languages with country flags.

### 5. Aggregate Statistics
- **Endpoint:** `GET /api/stats`
- **Response:** Total samples, emotion counts, average confidence percentage, and benchmark profiles.\n