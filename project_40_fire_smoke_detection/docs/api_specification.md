# API Specification: Industrial Fire & Smoke Surveillance Microservice (Port 5040)

## Base URL
`http://127.0.0.1:5040/`

## Endpoints

### 1. Health & Microservice Telemetry
- **Route**: `GET /api/health/` and `GET /api/health`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 40 Industrial Fire & Smoke Vision Surveillance API",
  "port": 5040,
  "cuda_available": false,
  "mps_available": true,
  "device": "mps",
  "models": {
    "dual_stream_convnet": "DualStreamFireSmokeNet (Phase 2 SOTA, 672 KB)",
    "thermal_risk_regressor": "FirePropagationThermalRiskRegressorNet (83 KB)"
  },
  "database": "fire_smoke.db (SQLite WAL Mode)"
}
```

### 2. Surveillance Stream Analysis
- **Route**: `POST /api/incidents/analyze`
- **Request**:
```json
{
  "zone_name": "Warehouse Sector B Chemical Storage",
  "camera_id": "CCTV-CHE-02",
  "simulate_flame": true,
  "simulate_smoke": true
}
```
- **Response**:
```json
{
  "hazard_type": "DUAL_FIRE_SMOKE_HAZARD",
  "severity_tier": "TIER_3_CRITICAL",
  "confidence": 0.994,
  "is_emergency": true,
  "flicker_hz": 15.8,
  "suppression_directive": "AUTOMATIC SUPPRESSION DELUGE DISPATCHED: EVACUATE ZONE IMMEDIATELY",
  "thermal_risk": {
    "flame_temp_c": 745.0,
    "plume_expansion_m_s": 5.2,
    "evacuation_urgency_index": 96.0,
    "co_concentration_ppm": 580.0
  },
  "latency_ms": 16.4,
  "evidence_hash": "e3b0c442...",
  "incident_id": "FIRE-2026-A1B2C3"
}
```

### 3. Hazard Zones Listing
- **Route**: `GET /api/incidents/zones`
- **Response**:
```json
{
  "count": 5,
  "zones": [
    {
      "zone_id": "ZN-01",
      "zone_name": "Industrial Plant Boiler Room",
      "facility_type": "Thermal Energy Plant",
      "camera_count": 4,
      "sprinkler_armed": true,
      "suppression_system": "High-Pressure Water Mist / CO2 Deluge"
    }
  ]
}
```

### 4. Incident Logs
- **Route**: `GET /api/incidents/?limit=20`

### 5. Cryptographic Audit Ledger
- **Route**: `GET /api/incidents/audit-logs?limit=20`

### 6. Incident Operator Actions
- **Route**: `POST /api/incidents/acknowledge/{incident_id}`
- **Route**: `POST /api/incidents/dispatch-suppression/{incident_id}`
