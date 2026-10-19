# RESTful API Specification: AERO-RUL (Port 5033)

## Base URL
`http://127.0.0.1:5033/api`

## Endpoints

### 1. GET `/health`
Returns microservice operational status, model weights verification, and monitored engine count.
**Response (200 OK):**
```json
{
  "classifier_accuracy": "98.08%",
  "dataset_benchmark": "NASA Turbofan C-MAPSS Engine Degradation (FD001-FD004)",
  "model_framework": "PyTorch 2.x Deep Residual MLP & Dual-Head Regressor",
  "monitored_components": 5,
  "port": 5033,
  "service": "Aircraft Component RUL & Telemetry Prediction API",
  "status": "healthy"
}
```

### 2. POST `/predict`
Executes forward tensor evaluation through both PyTorch models.
**Request Body:**
```json
{
  "component_id": "COMP-TURB-01",
  "cycles": 2150,
  "scenario": "auto"
}
```
*Note: Accepts either `component_id` or `component`, and either `cycles` or `operating_hours`.*

**Response (200 OK):**
```json
{
  "action_required": "Schedule borescope inspection within next 75 flight cycles. Monitor EGT margin.",
  "airworthiness_status": "MAINTENANCE DUE SOON",
  "cmapss_sensors": {
    "egt_margin_deg_c": 38.2,
    "nc_core_speed_rpm": 9320.4,
    "p30_hpc_pressure_psia": 532.1,
    "t50_lpt_outlet_temp_r": 1612.4
  },
  "color": "#f59e0b",
  "component_id": "COMP-TURB-01",
  "component_name": "High-Pressure Turbine (HPT) Blades",
  "degradation_curve": [100.0, 97.4, 94.2, 88.5, 78.1, 62.4, 48.2, 35.1, 22.4, 12.0, 0.0],
  "engine_model": "CFM56-7B / LEAP-1B",
  "health_score": 58.4,
  "rul_cycles": 1050,
  "rul_flight_hours": 2940.0,
  "status_probabilities": {
    "airworthy_optimal": 0.0312,
    "maintenance_due_soon": 0.9542,
    "grounded_mandatory": 0.0146
  }
}
```

### 3. GET `/components`
Returns metadata and operational limits for all 5 registered aircraft engine components.

### 4. GET `/stats`
Returns aggregated fleet metrics: total assessments, grounded units, maintenance due soon, and average health score.

### 5. GET & POST `/shop-orders`
Retrieves or creates Maintenance Shop Orders (MSO) for engine teardown and overhaul.

### 6. GET `/audit-logs`
Returns the immutable FAA/EASA regulatory audit trail.

### 7. GET `/model/info`
Returns deep learning parameters, PyTorch architecture details, and loss convergence values.
