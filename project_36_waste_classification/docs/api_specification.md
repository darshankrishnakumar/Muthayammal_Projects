# SORT-AI REST API Specification

## Base URL
`http://127.0.0.1:5036`

## Endpoints

### 1. System Health
- **Route**: `GET /api/health`
- **Description**: Returns microservice operational health, PyTorch model parameters, monitored conveyor counts, and benchmarks.
- **Response**:
```json
{
  "status": "healthy",
  "service": "AI Waste Classification & Autonomous Sorting API",
  "port": 5036,
  "monitored_conveyors": 3,
  "total_items_classified": 24,
  "classifier_accuracy": "98.83%",
  "recyclability_mae": "4.76%",
  "contamination_mae": "0.0546",
  "framework": "PyTorch 2.x Deep Residual MLP & Dual-Head Regressor",
  "benchmark": "EPA / ASTM D5231 Solid Waste Sorting Benchmark"
}
```

### 2. Waste Item Classification (Audit Verification Contract)
- **Route**: `POST /api/classify`
- **Description**: Evaluates waste item physical parameters and returns 6-class material prediction, recyclability score, and actuator diversion routing.
- **Audit Contract Payload**: `{"item_type": "plastic_bottle"}`
- **Response**:
```json
{
  "item_id": "ITM-9F40A1C2",
  "conveyor_id": "CONV-A1",
  "item_type": "plastic_bottle",
  "category": "Plastic",
  "confidence_pct": 98.80,
  "density_g_cm3": 0.95,
  "spectral_reflectance_nir": 0.720,
  "opacity_pct": 35.0,
  "surface_roughness_um": 2.2,
  "moisture_content_pct": 2.5,
  "rigidity_modulus_gpa": 2.1,
  "magnetic_susceptibility": 0.01,
  "carbon_footprint_kg_co2": 2.8,
  "recyclability_score": 82.0,
  "contamination_risk": 0.120,
  "diversion_bin": "BIN-A (Blue - Optical Air Jet #1)",
  "actuator_action": "ACTUATE: Pneumatically route to BIN-A (Blue - Optical Air Jet #1)",
  "timestamp": "2026-10-20T00:30:00Z",
  "model": "PyTorch Residual Material Classifier & Dual-Head Recyclability Regressor"
}
```

### 3. Waste Categories Listing
- **Route**: `GET /api/categories`
- **Description**: Returns all 6 supported waste categories, bin colors, market values ($/ton), and sorting mechanisms.

### 4. Conveyor Lines Listing
- **Route**: `GET /api/conveyors`
- **Description**: Lists active industrial conveyor lines (`CONV-A1`, `CONV-B2`, `CONV-C3`), operating speeds, and sensor models.

### 5. Dispatched Recycling Batches
- **Route**: `GET /api/batches`
- **Description**: Retrieves commercial batches of sorted commodities dispatched to downstream mills.

### 6. Facility Statistics
- **Route**: `GET /api/stats`
- **Description**: Aggregates total classified items, average recyclability index, category breakdown, and embodied carbon offsets.

### 7. Historical Item Ledger
- **Route**: `GET /api/history`
- **Description**: Returns recent 50 sorting events with timestamps, confidence scores, and diversion bin assignments.

### 8. Cryptographic Audit Ledger
- **Route**: `GET /api/audit-logs`
- **Description**: Retrieves immutable SHA-256 sealed audit logs for municipal EPA compliance verification.
