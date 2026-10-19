# Project 32: Relational Database Schema & WAL Configuration

### Engine: SQLite3 in Write-Ahead Logging (WAL) Mode
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA foreign_keys=ON;`

### Database Tables:
1. `machines`: Equipment master inventory (ID, name, type, nominal RPM, baseline temp, vibration, oil, AE, criticality).
2. `sensor_telemetry`: High-frequency multi-modal telemetry streams.
3. `diagnostic_inspections`: Model forward-pass inference logs, health scores, fault modes, and 8-band FFT spectra.
4. `maintenance_work_orders`: Official corrective work orders, assigned technicians, and resolution statuses.
5. `audit_log`: Chronological system lifecycle and operational events.
