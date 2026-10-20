# Database Schema: Sign Language Translation & Audio Storage

## Engine
Relational SQLite 3 configured with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).

## Schema DDL

```sql
-- 1. Translation Logs
CREATE TABLE IF NOT EXISTS translation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(50) NOT NULL,
    gloss_sequence VARCHAR(100) NOT NULL,
    spoken_sentence TEXT NOT NULL,
    confidence REAL NOT NULL,
    latency_ms REAL NOT NULL,
    pitch_hz REAL,
    duration_s REAL,
    energy_db REAL,
    evidence_hash VARCHAR(64),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Standard Gesture Vocabulary
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sign_label VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    description VARCHAR(200) NOT NULL
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
