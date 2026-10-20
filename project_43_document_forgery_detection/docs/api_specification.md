# API Specification: Document Forgery Detection Microservice (Port 5043)

## Base URL
`http://127.0.0.1:5043/`

## Core Endpoints

### 1. System Health Check
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 43 | AI-Based Document Forgery Detection Microservice",
  "port": 5043,
  "device": "mps",
  "cuda_available": false,
  "database_wal_active": true,
  "models": {
    "dual_domain_forgery_cnn": true,
    "forensic_regressor_weights": true
  },
  "telemetry_dataset_ready": true,
  "architecture": "DualDomainForgeryNet (Spatial ELA + DCT Frequency) + DocumentForensicRiskRegressorNet"
}
```

### 2. Historical Document Audits
- **Route**: `GET /api/forensics/audits?skip=0&limit=50`
- **Response**: Returns count and list of audited document records.

### 3. Forensic Document Examination
- **Route**: `POST /api/forensics/analyze`
- **Request Body**:
```json
{
  "document_title": "Commercial Tax Invoice #9841",
  "document_type": "INVOICE",
  "simulate_forgery": true,
  "forgery_type": "SPLICING"
}
```
- **Response**:
```json
{
  "audit": {
    "audit_id": "AUD-2026-F981AA",
    "document_title": "Commercial Tax Invoice #9841",
    "document_type": "INVOICE",
    "forgery_verdict": "FORGED",
    "forgery_type": "SPLICING",
    "forgery_probability": 0.965,
    "tampered_area_pct": 24.8,
    "ela_anomaly_score": 9.12,
    "evidence_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "metrics": {
    "forgery_verdict": "FORGED",
    "forgery_type": "SPLICING",
    "forgery_probability": 0.965,
    "tampered_area_pct": 24.8,
    "ela_anomaly_score": 9.12,
    "spectral_dct_noise": 0.742,
    "latency_ms": 18.2
  }
}
```

### 4. Forensic Inspection Templates
- **Route**: `GET /api/forensics/templates`
- **Response**: List of configured document templates and tolerances.

### 5. Immutable Cryptographic Audit Ledger
- **Route**: `GET /api/forensics/audit-logs?skip=0&limit=50`
- **Response**: Sequential blockchain blocks with index, action, and SHA-256 hashes.
