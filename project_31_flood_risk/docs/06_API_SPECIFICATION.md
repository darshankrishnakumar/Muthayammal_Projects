# Project 31: REST API Specification

### Base URL: `http://127.0.0.1:5031/`

#### 1. Liveness & Health
- `GET /api/health`
- Response: Status, Port 5031, Monitored Basins, Active Models, Storage Mode.

#### 2. Risk Evaluation & Inundation Prediction
- `POST /api/predict`
- Body:
```json
{
  "zone": "Bay Coastal Lowlands",
  "features": {
    "rainfall_mm": 180.0,
    "river_level_m": 6.2,
    "soil_moisture": 0.90,
    "storm_surge_m": 1.5
  }
}
```
- Response: `alert_level`, `alert_title`, `color`, `risk_pct`, `inundation_depth_m`, `lead_time_hours`, `emergency_protocol`, `telemetry`.

#### 3. Catchment Basins
- `GET /api/zones`
- Returns array of 5 monitored river catchments with DEM elevations and crest thresholds.

#### 4. Historical Ledger & Audit Logs
- `GET /api/history?limit=30`: Historical broadcast assessments.
- `GET /api/stats`: Situational awareness metrics.
- `GET /api/audit-logs`: System audit trail.
- `POST /api/dispatch`: Log emergency response team deployment.
