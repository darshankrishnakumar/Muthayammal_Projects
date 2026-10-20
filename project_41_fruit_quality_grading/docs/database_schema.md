# Database Schema & ACID Persistence: SQLite WAL Mode

## Overview
Database file: `source_code/data/fruit_grading.db`
Engine: SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`)

## Schema Definition (DDL)

```sql
-- 1. Fruit Items Register
CREATE TABLE IF NOT EXISTS fruit_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id VARCHAR(50) UNIQUE NOT NULL,
    conveyor_lane INTEGER DEFAULT 1,
    fruit_variety VARCHAR(50) NOT NULL,
    quality_grade VARCHAR(30) NOT NULL,
    defect_type VARCHAR(50) NOT NULL,
    defect_area_pct REAL NOT NULL,
    diameter_mm REAL NOT NULL,
    weight_grams REAL,
    firmness_n REAL,
    sugar_brix REAL,
    shelf_life_days REAL,
    batch_economic_index REAL,
    confidence REAL NOT NULL,
    sorting_chute VARCHAR(30) NOT NULL,
    evidence_hash VARCHAR(64),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Conveyor Sorting Lanes
CREATE TABLE IF NOT EXISTS sorting_lanes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lane_id VARCHAR(32) UNIQUE NOT NULL,
    lane_number INTEGER NOT NULL,
    lane_name VARCHAR(100) NOT NULL,
    camera_id VARCHAR(50) DEFAULT 'OPTICAL-CAM-01',
    target_fruit VARCHAR(50) DEFAULT 'APPLE',
    belt_speed_m_s REAL DEFAULT 1.2,
    ejector_status VARCHAR(30) DEFAULT 'ARMED',
    throughput_per_min INTEGER DEFAULT 120
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
