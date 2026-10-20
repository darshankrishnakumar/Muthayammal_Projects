# API Specification: Pavement Crack Detection Microservice (Port 5038)

## Base URL
`http://127.0.0.1:5038/`

## Endpoints

### 1. Health & Liveness
- **Route**: `GET /api/health/` and `GET /api/health`
- **Response**:
```json
{
  "status": "healthy",
  "port": 5038,
  "system": "PAVEMENT-AI Pavement Crack Detection & PCI Assessment",
  "version": "2.0.0",
  "device": "mps",
  "models": {
    "segmenter": "ResUNetCrackSegmenter (496 KB)",
    "regressor": "PavementPCIStressRegressorNet (31 KB)"
  },
  "database": "pavement_crack.db (WAL Mode Enabled)"
}
```

### 2. Multi-Modal Pavement Analysis
- **Route**: `POST /api/cracks/analyze`
- **Request**:
```json
{
  "image_path": "sample_crack_01.png",
  "crack_length_m": 3.4,
  "crack_width_mm": 8.2,
  "crack_depth_mm": 14.5,
  "surface_roughness_iri": 2.8,
  "traffic_volume_aadt": 28000,
  "temperature_c": 32.5,
  "moisture_pct": 14.2,
  "pavement_age_years": 4.5,
  "asphalt_binder_ratio": 5.4,
  "aggregate_size_mm": 19.0,
  "deflection_microns": 280.0
}
```
- **Response**:
```json
{
  "incident_id": 104,
  "distress_type": "Alligator Cracking",
  "severity": "High",
  "pci_score": 42.8,
  "structural_failure_risk": 0.742,
  "crack_coverage_pct": 18.4,
  "remediation_action": "Full-Depth Asphalt Patching",
  "estimated_cost_usd": 2450.0,
  "work_order_generated": true,
  "audit_hash": "a4f8c9e..."
}
```

### 3. Municipal Work Orders
- **Route**: `GET /api/cracks/work-orders`
- **Response**: Array of scheduled municipal maintenance work orders.

### 4. Cryptographic Audit Ledger
- **Route**: `GET /api/cracks/audit-logs`
- **Response**: Array of chained audit blocks with SHA-256 signatures.

### 5. Corridor Analytics Summary
- **Route**: `GET /api/analytics/summary`
- **Response**: Corridor statistics, average PCI, total active work orders.

### 6. Model Metadata
- **Route**: `GET /api/model/info`
- **Response**: Layer definitions, parameters, and training metrics.
