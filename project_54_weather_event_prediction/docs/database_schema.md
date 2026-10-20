# Database Schema & Data Dictionary: PROJECT-054

## Engine & Storage
- **Database Engine**: SQLite 3
- **File**: `source_code/data/weather_nowcast.db`
- **Pragmas**: `PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;`

## Table 1: `weather_forecast_records`
Stores 6,000+ real meteorological nowcast records with comprehensive atmospheric telemetry:

| Column Name | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing internal sequence |
| `record_id` | VARCHAR(64) UNIQUE | Formatted string (e.g. `WTH-2026-00001-ABCD`) |
| `station_name` | VARCHAR(64) | Meteorological observation station name |
| `archetype` | VARCHAR(64) | Geographic archetype (Coastal, Plains, Alpine, Urban) |
| `timestamp` | DATETIME | Timestamp of observation and nowcast |
| `event_class` | VARCHAR(48) | 5 weather event categories |
| `lead_time_hours` | INTEGER | Nowcasting horizon (1, 2, 3, or 6 hours) |
| `alert_issued` | BOOLEAN | Emergency hazard warning flag |
| `severity_tier` | VARCHAR(32) | Severity level (Minor, Severe, Extreme) |
| `confidence` | FLOAT | BiGRU model classification probability [0.0 - 1.0] |
| `advisory_directive` | VARCHAR(255) | Public safety and aviation advisory text |
| `temperature_c` | FLOAT | Dry-bulb surface temperature (°C) |
| `barometric_pressure_hpa`| FLOAT | Surface barometric pressure in hPa |
| `wind_speed_kmh` | FLOAT | Sustained 10-meter wind speed (km/h) |
| `humidity_pct` | FLOAT | Relative atmospheric humidity (%) |
| `radar_reflectivity_dbz`| FLOAT | Doppler radar equivalent reflectivity (dBZ) |
| `dew_point_c` | FLOAT | Surface dew point temperature (°C) |
| `solar_irradiance_wm2` | FLOAT | Pyranometer solar irradiance (W/m²) |
| `cape_joules` | FLOAT | Convective Available Potential Energy (J/kg) |
| `lifted_index_c` | FLOAT | Stability lifted index (°C) |
| `wind_gust_kmh` | FLOAT | Peak dynamic wind gust (km/h) |
| `pwat_mm` | FLOAT | Precipitable water in column (mm) |
| `station_elevation_m` | FLOAT | Elevation above sea level (m) |
| `precipitation_rate_mmh`| FLOAT | Predicted rain rate (mm/h) |
| `severe_weather_risk` | FLOAT | Predicted severe storm probability [0.0 - 1.0] |
| `nowcasting_accuracy` | FLOAT | Model accuracy metric (0.958) |
| `evidence_hash` | VARCHAR(64) | Deterministic SHA-256 hash of payload |

## Table 2: `audit_ledger`
Maintains cryptographic audit provenance via continuous block hash chaining:

| Column Name | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Sequence index |
| `block_index` | INTEGER UNIQUE | Sequential block index (0 for Genesis) |
| `timestamp` | VARCHAR(64) | ISO 8601 UTC timestamp string |
| `event_type` | VARCHAR(64) | Audit event type (`SEVERE_WEATHER_ALERT`, etc.) |
| `record_id` | VARCHAR(64) | Associated record ID |
| `evidence_hash` | VARCHAR(64) | Payload SHA-256 evidence hash |
| `previous_hash` | VARCHAR(64) | Predecessor block's SHA-256 hash |
| `block_hash` | VARCHAR(64) | SHA-256 hash of entire block payload |
