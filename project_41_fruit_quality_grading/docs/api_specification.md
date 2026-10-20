# API Specification: Fruit Quality Grading Microservice (Port 5041)

## Base URL
`http://127.0.0.1:5041/`

## Endpoints

### 1. Health & Telemetry Liveness
- **Route**: `GET /api/health/` and `GET /api/health`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 41 Fruit Quality Grading & Defect Platform API",
  "port": 5041,
  "cuda_available": false,
  "mps_available": true,
  "device": "mps",
  "models": {
    "multitask_cnn": "MultiTaskFruitNet (Phase 2 SOTA, 391 KB)",
    "freshness_regressor": "FruitFreshnessShelfLifeRegressorNet (83 KB)"
  },
  "database": "fruit_grading.db (SQLite WAL Mode)"
}
```

### 2. Optical Fruit Inspection & Grading
- **Route**: `POST /api/grading/inspect`
- **Request**:
```json
{
  "conveyor_lane": 1,
  "variety": "APPLE",
  "defect_sim": "NONE"
}
```
- **Response**:
```json
{
  "item": {
    "item_id": "FRUIT-2026-F1A2B3",
    "fruit_variety": "APPLE",
    "quality_grade": "GRADE_A_PREMIUM",
    "defect_type": "NONE",
    "sorting_chute": "BIN_1_EXPORT",
    "firmness_n": 84.5,
    "sugar_brix": 16.5,
    "shelf_life_days": 24.0,
    "batch_economic_index": 96.5,
    "confidence": 0.992
  },
  "metrics": {
    "variety": "APPLE",
    "grade": "GRADE_A_PREMIUM",
    "sorting_chute": "BIN_1_EXPORT",
    "latency_ms": 14.8,
    "evidence_hash": "e3b0c442..."
  }
}
```

### 3. Inspected Items History
- **Route**: `GET /api/grading/items?limit=20`

### 4. Sorting Lanes Configuration
- **Route**: `GET /api/grading/lanes`

### 5. Cryptographic Audit Ledger
- **Route**: `GET /api/grading/audit-logs?limit=20`

### 6. Packhouse Sorting Statistics
- **Route**: `GET /api/grading/stats`
