# Database Schema & Data Dictionary: PROJECT-053

## Engine & Storage
- **Database Engine**: SQLite 3
- **File**: `source_code/data/rail_defects.db`
- **Pragmas**: `PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;`

## Table 1: `railway_defect_records`
Stores 6,000+ real track inspection records with comprehensive physical geometry telemetry:

| Column Name | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing internal sequence |
| `record_id` | VARCHAR(64) UNIQUE | Formatted string (e.g. `RAL-2026-A1B2C3`) |
| `chainage_km` | VARCHAR(32) | Formatted corridor chainage marker (e.g. `KM 144.200`) |
| `chainage_numeric_km` | FLOAT | Numeric kilometer value for indexing and sorting |
| `track_segment` | VARCHAR(64) | Name of corridor segment |
| `archetype` | VARCHAR(64) | Track archetype (High-Speed, Heavy Freight, Metro, Mountain) |
| `timestamp` | DATETIME | Timestamp of inspection record |
| `defect_type` | VARCHAR(64) | 6 defect categories (Clean Rail, Surface Crack, etc.) |
| `severity` | VARCHAR(32) | Severity tier (None, Minor, Moderate, Critical) |
| `confidence` | FLOAT | ResUNet model classification certainty [0.0 - 1.0] |
| `affected_area_px` | INTEGER | Surface defect pixel count from segmented mask |
| `status` | VARCHAR(32) | Remediation status (Nominal, Scheduled, Urgent) |
| `recommended_action` | VARCHAR(255) | Engineering action recommendation |
| `cant_deficiency_mm` | FLOAT | Lateral cant shortfall in millimeters |
| `gauge_deviation_mm` | FLOAT | Deviation from standard 1435mm gauge |
| `vertical_profile_roughness`| FLOAT | Longitudinal unevenness (mm) |
| `alignment_deviation_mm` | FLOAT | Horizontal alignment offset (mm) |
| `sleeper_ballast_void_depth`| FLOAT | Under-tie ballast void depth (mm) |
| `rail_temperature_c` | FLOAT | Steel rail temperature in Celsius |
| `fastener_torque_loss_pct` | FLOAT | Percentage clamping torque loss |
| `vibration_acceleration_g` | FLOAT | Dynamic axle-box vibration in g |
| `axle_load_tons` | FLOAT | Static/dynamic wheelset axle load |
| `acoustic_emission_db` | FLOAT | High-frequency acoustic crack noise |
| `track_curvature_rad` | FLOAT | Track curve radius in radians |
| `track_quality_index` | FLOAT | Overall Track Quality Index [0 - 100] |
| `speed_restriction_kmh` | FLOAT | Dynamic speed restriction [0 - 160 km/h] |
| `derailment_risk` | FLOAT | Predicted derailment probability [0.0 - 1.0] |
| `evidence_hash` | VARCHAR(64) | Deterministic SHA-256 hash of payload |

## Table 2: `audit_ledger`
Maintains cryptographic audit provenance via continuous block hash chaining:

| Column Name | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Sequence index |
| `block_index` | INTEGER UNIQUE | Sequential block index (0 for Genesis) |
| `timestamp` | VARCHAR(64) | ISO 8601 UTC timestamp string |
| `event_type` | VARCHAR(64) | Audit event type (`RAIL_DEFECT_DETECTED`, etc.) |
| `record_id` | VARCHAR(64) | Associated record ID |
| `evidence_hash` | VARCHAR(64) | Payload SHA-256 evidence hash |
| `previous_hash` | VARCHAR(64) | Predecessor block's SHA-256 hash |
| `block_hash` | VARCHAR(64) | SHA-256 hash of entire block payload |
