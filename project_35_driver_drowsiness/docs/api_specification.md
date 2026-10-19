# VIGILANCE-AI REST API Specification

## Base URL
`http://127.0.0.1:5035`

## Endpoints

### 1. System Health
- **Route**: `GET /api/health`
- **Description**: Returns microservice operational health, PyTorch model parameters, monitored fleet counts, and benchmarks.
- **Response**:
```json
{
  "status": "healthy",
  "service": "AI Driver Drowsiness & Fatigue Vigilance Detection System",
  "port": 5035,
  "monitored_drivers": 5,
  "telemetry_records_analyzed": 42,
  "classifier_accuracy": "97.25%",
  "vigilance_mae": "1.76%",
  "microsleep_mae": "0.0164",
  "framework": "PyTorch 2.x Deep Residual MLP & Dual-Head Regressor",
  "benchmark": "NHTSA / FMCSA Driver Vigilance Safety Benchmark"
}
```

### 2. Driver Frame Analysis (Audit Verification Contract)
- **Route**: `POST /api/analyze`
- **Description**: Evaluates driver facial telemetry and returns 4-tier fatigue classification, vigilance score, and active intervention mandates.
- **Audit Contract Payload**: `{"ear": 0.18, "mar": 0.65}`
- **Response**:
```json
{
  "id": "TEL-8E29B1A0",
  "driver_id": "DRV-801",
  "drowsiness_state": "Severely Drowsy",
  "drowsiness_score": 0.7412,
  "vigilance_score": 25.88,
  "microsleep_risk": 0.8841,
  "ear": 0.1800,
  "mar": 0.6500,
  "blink_duration_ms": 760.0,
  "blink_frequency_cpm": 28.5,
  "head_pitch_degrees": -18.2,
  "perclos_pct": 52.4,
  "alert_required": true,
  "severity": "CRITICAL",
  "alert_type": "HAPTIC_AUDITORY_PULLOVER",
  "alert_message": "⚠️ CRITICAL DROWSINESS DETECTED! IMMEDIATE EMERGENCY STOP: Audible warning siren and haptic seat vibration triggered.",
  "recommended_action": "IMMEDIATE EMERGENCY STOP: Audible warning siren and haptic seat vibration triggered. Safely exit traffic corridor."
}
```

### 3. Driver Fleet Listing
- **Route**: `GET /api/drivers`
- **Description**: Lists all monitored commercial drivers, assigned equipment, route corridors, shift classifications, and baseline biometric parameters.

### 4. Trip Sessions
- **Route**: `GET /api/trips`
- **Description**: Retrieves commercial fleet trips, distance traveled, average vigilance scores, and safety letter grades.

### 5. Safety Alerts & Interventions
- **Route**: `GET /api/alerts`
- **Description**: Returns recent active safety alerts with operator acknowledgment tracking.

### 6. Acknowledge Alert
- **Route**: `POST /api/alerts/<alert_id>/acknowledge`
- **Description**: Records driver acknowledgment of active safety intervention and updates audit ledger.

### 7. Fleet Statistics
- **Route**: `GET /api/stats`
- **Description**: Aggregates fleet-wide vigilance metrics, total analyzed frames, and fatigue distribution.

### 8. Audit Ledger
- **Route**: `GET /api/audit-logs`
- **Description**: Retrieves cryptographic SHA-256 audit log records for FMCSA compliance reviews.
