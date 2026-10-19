# API Documentation: MesoInception-4 Deepfake Detection Service

Base URL: `http://127.0.0.1:5010`

## Endpoints

### 1. `GET /health`
Returns system health and active port.
**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Deepfake Vision Forensics Microservice",
  "port": 5010,
  "models_loaded": true,
  "timestamp": 1792400192.920
}
```

### 2. `GET /api/stats`
Returns executive forensic telemetry.
**Response (200 OK):**
```json
{
  "total_audited_scans": 1020,
  "deepfakes_intercepted": 511,
  "authentic_rate_pct": 49.9,
  "model_accuracy_pct": 99.5,
  "roc_auc": 0.999
}
```

### 3. `GET /api/samples`
Returns list of available benchmark facial presets.
**Response (200 OK):**
```json
[
  "deepfake_diffusion_01.jpg",
  "deepfake_faceswap_01.jpg",
  "deepfake_stylegan_01.jpg",
  "real_person_01.jpg",
  "real_person_02.jpg"
]
```

### 4. `POST /api/analyze`
Executes deep neural and frequency analysis on a specified sample.
**Request Body:**
```json
{
  "sample_name": "deepfake_faceswap_01.jpg"
}
```
**Response (200 OK):**
```json
{
  "filename": "deepfake_faceswap_01.jpg",
  "prediction": "DEEPFAKE",
  "is_deepfake": true,
  "confidence": 0.985,
  "probability_deepfake": 0.985,
  "probability_real": 0.015,
  "moderation_verdict": "CRITICAL SYNTHETIC FRAUD - QUARANTINED",
  "forensic_indicators": {
    "fft_anomaly_score": 0.4850,
    "boundary_discontinuity": 0.8240,
    "color_chroma_variance": 28.5,
    "laplacian_sharpness": 190.4,
    "eye_asymmetry_index": 0.1520
  },
  "latency_ms": 21.4
}
```

### 5. `GET /api/history`
Returns recent SQLite transactional forensic logs.
