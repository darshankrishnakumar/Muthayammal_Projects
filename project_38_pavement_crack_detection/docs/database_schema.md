# Database Schema: Pavement Distress & Maintenance Storage

## Engine
Relational SQLite 3 configured with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).

## Schema DDL

```sql
-- 1. Pavement Crack Incidents
CREATE TABLE IF NOT EXISTS crack_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_uuid VARCHAR(64) UNIQUE NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    corridor_id VARCHAR(32) NOT NULL,
    chainage_km REAL NOT NULL,
    distress_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    crack_length_m REAL NOT NULL,
    crack_width_mm REAL NOT NULL,
    crack_depth_mm REAL NOT NULL,
    pci_score REAL NOT NULL,
    structural_failure_risk REAL NOT NULL,
    crack_coverage_pct REAL NOT NULL,
    recommended_action VARCHAR(128) NOT NULL,
    estimated_repair_cost REAL NOT NULL,
    evidence_hash VARCHAR(64) NOT NULL
);

-- 2. Maintenance Work Orders
CREATE TABLE IF NOT EXISTS maintenance_work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id VARCHAR(32) UNIQUE NOT NULL,
    incident_id INTEGER NOT NULL REFERENCES crack_incidents(id) ON DELETE CASCADE,
    corridor_id VARCHAR(32) NOT NULL,
    urgency_level VARCHAR(16) NOT NULL,
    contractor_assigned VARCHAR(64),
    scheduled_date DATE,
    estimated_budget REAL NOT NULL,
    status VARCHAR(32) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Cryptographic Audit Ledger
CREATE TABLE IF NOT EXISTS audit_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_index INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(64) NOT NULL,
    details TEXT NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL
);
```
