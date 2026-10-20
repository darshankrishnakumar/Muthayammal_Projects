# API Specification: Biometric Face Attendance Microservice (Port 5042)

## Base URL
`http://127.0.0.1:5042/`

## Core Endpoints

### 1. System Health Check
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 42 | AI-Driven Face Attendance & Anti-Spoofing Microservice",
  "port": 5042,
  "device": "mps",
  "cuda_available": false,
  "database_wal_active": true,
  "models": {
    "arcface_antispoof_weights": true,
    "biometric_regressor_weights": true
  },
  "telemetry_dataset_ready": true,
  "architecture": "DeepAntiSpoofFaceNet + BiometricLivenessQualityRegressorNet"
}
```

### 2. Enrolled Student Roster
- **Route**: `GET /api/attendance/students`
- **Response**: Array of enrolled students (STU-101 through STU-105).

### 3. Biometric Verification & Liveness Audit
- **Route**: `POST /api/attendance/verify`
- **Request Body**:
```json
{
  "student_index": 0,
  "simulate_spoof_attack": false,
  "attack_type": "PRINT_ATTACK_2D",
  "course_code": "CS-401",
  "classroom_id": "HALL-A1"
}
```
- **Response**:
```json
{
  "record": {
    "record_id": "ATT-2026-F981AA",
    "student_id": "STU-101",
    "full_name": "Alex Chen",
    "status": "PRESENT",
    "evidence_hash": "9d9ab8e5053b14c165137d6d5a0254c8138f6f2c9cbeb51264886c90246438b8"
  },
  "metrics": {
    "anti_spoof_confidence": 0.985,
    "face_match_confidence": 0.965,
    "spoof_risk_pct": 2.53,
    "micro_tremor_score": 0.817,
    "illumination_entropy": 8.00,
    "attendance_score": 95.83,
    "latency_ms": 14.8
  }
}
```

### 4. Verified Attendance Logs
- **Route**: `GET /api/attendance/logs?skip=0&limit=50`
- **Response**: Paginated list of recent transactional attendance events.

### 5. Immutable Cryptographic Audit Ledger
- **Route**: `GET /api/attendance/audit-logs?skip=0&limit=50`
- **Response**: Sequentially ordered blocks with block index, action type, SHA-256 current hash, and previous hash.
