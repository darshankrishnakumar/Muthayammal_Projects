# API Documentation: Inception-RNN Parkinson's Telemonitoring Service

Base URL: `http://127.0.0.1:5011`

## Endpoints

### 1. `GET /health`
Returns system health and active port.
**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Inception-RNN Parkinson's Telemonitoring API",
  "port": 5011,
  "models_loaded": true,
  "timestamp": 1792400824.503
}
```

### 2. `GET /api/stats`
Returns executive clinical telemetry.
**Response (200 OK):**
```json
{
  "total_patients_screened": 215,
  "parkinsons_detected": 157,
  "healthy_controls_rate_pct": 27.0,
  "model_accuracy_pct": 100.0,
  "roc_auc": 1.0
}
```

### 3. `GET /api/presets`
Returns list of available benchmark clinical presets.
**Response (200 OK):**
```json
[
  "patient_healthy_control.json",
  "patient_parkinsons_advanced.json",
  "patient_parkinsons_early_stage.json"
]
```

### 4. `POST /api/diagnose`
Executes deep neural and acoustic evaluation for a patient.
**Request Body:**
```json
{
  "patient_id": "PD-3041",
  "features": {
    "MDVP:Fo(Hz)": 152.845,
    "MDVP:Fhi(Hz)": 163.305,
    "MDVP:Flo(Hz)": 129.443,
    "MDVP:Jitter(%)": 0.00582,
    "MDVP:Shimmer": 0.02850,
    "NHR": 0.02140,
    "HNR": 21.430,
    "RPDE": 0.5120,
    "DFA": 0.7240,
    "spread1": -5.620,
    "spread2": 0.2240,
    "PPE": 0.1980
  }
}
```
**Response (200 OK):**
```json
{
  "patient_id": "PD-3041",
  "diagnosis": "PARKINSONS_DIAGNOSED",
  "is_parkinsons": true,
  "confidence": 0.9620,
  "probability_parkinsons": 0.9620,
  "probability_healthy": 0.0380,
  "predicted_updrs_score": 24.5,
  "disease_staging": "Hoehn & Yahr Stage 1-2 (Early Mild)",
  "clinical_recommendation": "EARLY STAGE PD - INITIATE NEUROLOGY REFERRAL & SPEECH THERAPY",
  "biomarker_radar": {
    "vocal_frequency_hz": 152.845,
    "vocal_jitter_pct": 0.00582,
    "vocal_shimmer": 0.02850,
    "harmonics_noise_ratio": 21.43,
    "pitch_period_entropy": 0.198,
    "recurrent_period_entropy": 0.512
  },
  "latency_ms": 18.5
}
```

### 5. `GET /api/history`
Returns recent SQLite clinical diagnostic logs.
