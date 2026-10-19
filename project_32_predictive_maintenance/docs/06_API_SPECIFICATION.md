# Project 32: REST API Specification

### Base URL: `http://127.0.0.1:5032/`

#### 1. Liveness & Health
- `GET /api/health`
- Response: Status, Port 5032, Monitored Assets, Active Models, Storage Mode.

#### 2. Diagnostic Analysis & RUL Forecasting
- `POST /api/analyze`
- Body:
```json
{
  "machine": "Gas Turbine Generator D-401",
  "scenario": "fault",
  "features": {
    "temperature_c": 135.0,
    "vibration_mm_s": 5.2,
    "pressure_bar": 21.0
  }
}
```
- Response: `fault_mode`, `health_score`, `urgency`, `action_required`, `color`, `rul_hours`, `rul_days`, `fft_harmonics`, `telemetry`.

#### 3. Equipment Inventory & Work Orders
- `GET /api/machines`: Lists all 5 monitored equipment assets with nominal parameters.
- `GET /api/history?limit=30`: Queries historical diagnostic inspections.
- `GET /api/stats`: Fleet-wide reliability KPIs.
- `POST /api/work-order`: Automatically dispatch corrective maintenance crews.
- `GET /api/work-orders`: Returns dispatched maintenance work orders.
- `GET /api/audit-logs`: System audit trail.
