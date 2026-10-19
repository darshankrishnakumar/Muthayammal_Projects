# Project 29: REST API Specification

Port: `5029` | Base URL: `http://127.0.0.1:5029/api`

### 1. GET `/health`
Returns system health, loaded PyTorch weights, SQLite WAL state, and vocabulary size.
```json
{
  "status": "healthy",
  "port": 5029,
  "service": "Real-Time Sign Language Translation & Speech Synthesis API",
  "models": {
    "spatial_model": "SignSpatialClassifier",
    "weights_loaded": true
  },
  "database": {
    "journal_mode": "WAL",
    "wal_enabled": true
  }
}
```

### 2. POST `/recognize`
Runs PyTorch forward pass on landmark data or target sign string.
- Request: `{"sign": "HELLO"}` or `{"landmarks": [...]}`
- Response:
```json
{
  "sign": "HELLO",
  "category": "Greeting",
  "confidence": 0.999,
  "confidence_pct": 99.9,
  "top_candidates": [
    {"sign": "HELLO", "prob": 0.999, "prob_pct": 99.9},
    {"sign": "WELCOME", "prob": 0.001, "prob_pct": 0.1}
  ],
  "latency_ms": 22
}
```

### 3. POST `/translate-sequence`
Evaluates a 16-frame sequence of 63D coordinates using `SignSequenceBiLSTM`.

### 4. GET `/dictionary`
Returns 38 vocabulary tokens with icons, categories, and speech prompts.

### 5. GET `/history`
Returns chronological feed of translated gestures from SQLite database.

### 6. GET `/sentence`
Returns assembled sentence string and word list.

### 7. GET `/metrics`
Returns detailed model parameters, training hyperparameters, and dataset metadata.
