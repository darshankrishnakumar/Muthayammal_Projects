# Database Schema Specification: manufacturing.db (PROJECT-046)

## Overview
SQLite relational database operating with Write-Ahead Logging (`PRAGMA journal_mode=WAL`) on Port 5046.

### 1. `inspected_parts` Table
Stores full telemetry, optical verdicts, continuous metrics, and cryptographic evidence hashes.
- `id` (INTEGER, PK): Primary key index.
- `part_id` (VARCHAR(50), UNIQUE, INDEX): Unique serial (e.g., `PART-2026-00101`).
- `assembly_line` (VARCHAR(100)): Production line identifier.
- `part_type` (VARCHAR(50)): `PCB_BOARD`, `MACHINED_GEAR`, `METALLIC_CASING`, `TURBINE_BLADE`.
- `inspection_verdict` (VARCHAR(20)): `PASS`, `REJECT`.
- `defect_type` (VARCHAR(50)): `NONE`, `SCRATCH`, `CRACK`, `DENT`, `MISSING_COMPONENT`.
- `severity_score` (FLOAT): Predicted severity percentage (0.0 to 100.0%).
- `defect_area_pct` (FLOAT): Spatial defect area coverage percentage.
- `surface_roughness_ra` (FLOAT): Continuous roughness metric in um (ISO 4287).
- `pneumatic_ejection_confidence` (FLOAT): Solenoid actuator confidence (0.0 to 100.0%).
- `inspection_cycle_time_ms` (FLOAT): End-to-end edge inference latency in milliseconds.
- `actuator_action` (VARCHAR(50)): `ROUTE_CONVEYOR` or `TRIGGER_PNEUMATIC_EJECT`.
- `evidence_hash` (VARCHAR(64)): Deterministic SHA-256 evidence fingerprint.
- `timestamp` (DATETIME): UTC timestamp of inspection event.

### 2. `inspection_templates` Table
Stores pre-calibrated optical station configurations and tolerance thresholds.
- `template_id` (VARCHAR(50), UNIQUE, INDEX): E.g., `TEMPL-PCB`, `TEMPL-GEAR`.
- `part_type` (VARCHAR(50)): Target component classification.
- `assembly_line` (VARCHAR(100)): Designated assembly line.
- `camera_resolution` (VARCHAR(100)): Sensor optics and frame rate.
- `max_acceptable_roughness` (FLOAT): Upper tolerance threshold for Ra.
- `max_acceptable_defect_area` (FLOAT): Upper tolerance threshold for defect area.
- `ejection_air_pressure_bar` (FLOAT): Solenoid pneumatic line pressure.
- `is_active` (BOOLEAN): Active operational status.

### 3. `audit_ledger` Table
Stores the continuous cryptographic SHA-256 block hash chain.
- `id` (INTEGER, PK): Internal record key.
- `block_index` (INTEGER): Sequential block number starting at Genesis Block #0.
- `timestamp` (VARCHAR(50)): ISO 8601 UTC timestamp string.
- `action_type` (VARCHAR(64)): Event type (`SYSTEM_INIT`, `INSPECTION_SCAN`, etc.).
- `details` (TEXT): Audit event narrative and telemetry parameters.
- `previous_hash` (VARCHAR(64)): Hash of preceding block (Block #0 = 64 zeros).
- `current_hash` (VARCHAR(64)): SHA-256 hash of `action|details|timestamp|previous_hash`.
