# API Specification (OpenAPI 3.0 Standard)

Base URL: `http://localhost:5002`

---

### 1. Health & Readiness Probe
- **Endpoint**: `GET /health`
- **Description**: Verifies service liveness, database connectivity, and ML model weights availability.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "network_intrusion_detection_service",
  "version": "2.0.0",
  "models_ready": true,
  "database_connected": true
}
```

---

### 2. Preloaded Attack Presets
- **Endpoint**: `GET /api/presets`
- **Description**: Returns validated connection dictionaries for real-world attack vectors (SYN Flood, Port Sweep, Benign HTTP, SSH Brute Force, Buffer Overflow, Zero-Day Anomaly).
- **Response `200 OK`**:
```json
{
  "syn_flood_dos": {
    "name": "Neptune SYN Flood (DoS Attack)",
    "description": "Rapid succession of TCP SYN packets with no completion...",
    "data": { ... }
  },
  "port_scan_probe": { ... },
  "normal_http_session": { ... },
  "ssh_brute_force_r2l": { ... },
  "buffer_overflow_u2r": { ... },
  "zero_day_anomaly": { ... }
}
```

---

### 3. Packet Inspection & Threat Scoring
- **Endpoint**: `POST /api/inspect`
- **Description**: Evaluates packet parameters, executes ensemble and anomaly inference, logs incident to SQLite, and returns defense directives.
- **Request Body**:
```json
{
  "source_ip": "185.220.101.5",
  "destination_ip": "10.0.0.1",
  "protocol_type": "tcp",
  "service": "private",
  "flag": "S0",
  "duration": 0,
  "src_bytes": 0,
  "dst_bytes": 0,
  "count": 250,
  "srv_count": 20,
  "serror_rate": 1.0,
  "rerror_rate": 0.0
}
```
- **Response `200 OK`**:
```json
{
  "predicted_category": "DoS",
  "confidence": 0.8205,
  "threat_level": "CRITICAL_ATTACK",
  "is_anomaly": false,
  "anomaly_score_pct": 40.0,
  "isolation_score_raw": -0.0124,
  "recommended_action": "BLOCK: High-frequency denial-of-service signatures detected. Rate-limit and throttle host.",
  "class_probabilities": {
    "DoS": 0.8205,
    "Normal": 0.0,
    "Probe": 0.1795,
    "R2L": 0.0,
    "U2R": 0.0
  },
  "models_evaluated": {
    "random_forest_prediction": "DoS",
    "extra_trees_prediction": "DoS",
    "ensemble_consensus": true
  },
  "latency_ms": 55.8,
  "timestamp": 1729272800.5,
  "event_id": 14,
  "source_ip": "185.220.101.5",
  "destination_ip": "10.0.0.1"
}
```

---

### 4. Security Event Audit Logs
- **Endpoint**: `GET /api/events?limit=25`
- **Description**: Retrieves transactional incident history from SQLite store with pagination.
- **Response `200 OK`**:
```json
{
  "count": 25,
  "events": [
    {
      "id": 14,
      "timestamp": "2026-10-18T17:30:12Z",
      "source_ip": "185.220.101.5",
      "destination_ip": "10.0.0.1",
      "protocol": "tcp",
      "service": "private",
      "flag": "S0",
      "predicted_category": "DoS",
      "confidence": 0.8205,
      "threat_level": "CRITICAL_ATTACK",
      "anomaly_score": 40.0,
      "recommended_action": "BLOCK: High-frequency denial-of-service signatures detected...",
      "latency_ms": 55.8
    }
  ]
}
```

---

### 5. Threat Intelligence Analytics
- **Endpoint**: `GET /api/analytics`
- **Description**: Returns live aggregated incident statistics from database.
- **Response `200 OK`**:
```json
{
  "total_inspected_packets": 142,
  "malicious_intrusions": 84,
  "benign_packets": 58,
  "anomalies_detected": 12,
  "category_distribution": {
    "Normal": 58,
    "DoS": 52,
    "Probe": 22,
    "R2L": 8,
    "U2R": 2
  },
  "threat_levels": {
    "BENIGN": 58,
    "CRITICAL_ATTACK": 54,
    "HIGH_ALERT": 30
  },
  "avg_latency_ms": 52.4
}
```

---

### 6. Empirical Evaluation Metrics
- **Endpoint**: `GET /api/metrics`
- **Description**: Returns verified evaluation scores from held-out NSL-KDD test dataset.
