# Database Schema & ACID Persistence: SQLite WAL Mode

## Overview
Database file: `source_code/data/fire_smoke.db`
Engine: SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`)

## Schema Definition (DDL)

```sql
-- 1. Fire Incidents Register
CREATE TABLE IF NOT EXISTS fire_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id VARCHAR(50) UNIQUE NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    camera_id VARCHAR(50) NOT NULL,
    hazard_type VARCHAR(50) NOT NULL,
    severity_tier VARCHAR(30) NOT NULL,
    confidence REAL NOT NULL,
    flicker_frequency_hz REAL NOT NULL,
    plume_expansion_rate REAL NOT NULL,
    flame_temp_c REAL,
    evacuation_urgency REAL,
    co_ppm REAL,
    evidence_hash VARCHAR(64),
    dispatch_status VARCHAR(30) DEFAULT 'DISPATCHED',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mission-Critical Hazard Zones
CREATE TABLE IF NOT EXISTS hazard_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id VARCHAR(32) UNIQUE NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    facility_type VARCHAR(64) NOT NULL,
    camera_count INTEGER DEFAULT 4,
    sprinkler_armed BOOLEAN DEFAULT 1,
    suppression_system VARCHAR(64) DEFAULT 'Dry Chemical / FM-200 Clean Agent'
);

-- 3. Cryptographic Audit Ledger
CREATE TABLE IF NOT EXISTS audit_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_index INTEGER NOT NULL,
    timestamp VARCHAR(50) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    details TEXT NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL
);
```
