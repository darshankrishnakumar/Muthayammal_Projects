# Project 31: Relational Database Schema & WAL Configuration

### Engine: SQLite3 in Write-Ahead Logging (WAL) Mode
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA foreign_keys=ON;`

### Database Tables:
1. `river_basins`: Static topographic catchment attributes (ID, name, type, DEM, crest threshold, drainage score, population).
2. `hydrological_readings`: Raw sensor telemetry readings over time.
3. `flood_predictions`: Model forward-pass prediction records with full telemetry snapshots.
4. `emergency_dispatches`: Dispatch commands, teams, protocols, and deployment status.
5. `audit_log`: Chronological system lifecycle and operational events.
