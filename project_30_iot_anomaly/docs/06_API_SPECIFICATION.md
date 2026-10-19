# Project 30: REST API Specification

Port: `5030` | Base URL: `http://127.0.0.1:5030/api`

### 1. GET `/health`
Returns system status, loaded PyTorch models, SQLite WAL status, and device fleet count.

### 2. POST `/analyze`
Runs Autoencoder + Threat Classifier on device telemetry.
- Request: `{"device": "Smart IP Camera", "scenario": "attack"}`
- Response:
```json
{
  "device": "Smart IP Camera",
  "attack_type": "Mirai Botnet C&C",
  "is_anomaly": true,
  "severity": "CRITICAL",
  "anomaly_score": 84,
  "reconstruction_error": 0.842,
  "action_taken": "Quarantine MAC & Terminate Port 23/Telnet",
  "quarantine_status": "ISOLATED",
  "latency_ms": 12
}
```

### 3. GET `/devices`
Returns connected IoT devices with IP, protocol, and online/quarantined status.

### 4. POST `/device/quarantine`
Manual override to isolate or restore a device.
- Request: `{"device": "Smart TV 4K", "status": "ISOLATED"}`

### 5. GET `/stats`
Returns security metrics and System Security Index (0-100).

### 6. GET `/loss-curve`
Returns timeline points of reconstruction loss vs the 0.35 threshold.
