# REST API Specification: Manufacturing Defect Platform (Port 5046)

## System Health
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
  ```json
  {
    "status": "HEALTHY",
    "service": "Project 46 Product Defect Detection API",
    "port": 5046,
    "database": "SQLite (WAL Mode Enabled)",
    "hardware_device": "mps",
    "models": {
      "fpn_defect_segmenter": "DeepFPNDefectNet (Loaded)",
      "defect_risk_regressor": "ManufacturingDefectRiskRegressorNet (Loaded)"
    }
  }
  ```

## Parts & Templates Inspection
- **Route**: `GET /api/inspection/parts?skip=0&limit=50`
- **Route**: `GET /api/inspection/templates`
- **Route**: `GET /api/inspection/audit-logs?limit=50`
- **Route**: `GET /api/inspection/stats`
- **Route**: `GET /api/analytics/summary`

## Synchronous Optical Scan
- **Route**: `POST /api/inspection/scan`
- **Request Body**:
  ```json
  {
    "assembly_line": "Line-1 SMT PCB Assembly",
    "part_type": "PCB_BOARD",
    "simulate_defect": "NONE"
  }
  ```
- **Response Body**:
  ```json
  {
    "status": "SUCCESS",
    "part": {
      "part_id": "PART-2026-A1B2C3",
      "inspection_verdict": "PASS",
      "defect_type": "NONE",
      "severity_score": 1.8,
      "defect_area_pct": 0.05,
      "actuator_action": "ROUTE_CONVEYOR",
      "evidence_hash": "..."
    },
    "metrics": { ... },
    "audit_block_index": 3
  }
  ```
