# Database Schema Specification: SQLite WAL Engine

## Engine Configuration
- **File**: `data/career.db`
- **Journal Mode**: `WAL` (Write-Ahead Logging via `PRAGMA journal_mode=WAL`)
- **Synchronous**: `NORMAL` (`PRAGMA synchronous=NORMAL`)
- **Foreign Keys**: Enabled (`PRAGMA foreign_keys=ON`)

## Tables

### 1. `career_roles`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `role_id` VARCHAR(50) UNIQUE INDEX
- `role_title` VARCHAR(100) NOT NULL
- `required_competencies` TEXT NOT NULL
- `avg_salary_usd` INTEGER DEFAULT 120000
- `market_growth_rate` VARCHAR(20) DEFAULT 'HIGH'
- `is_active` BOOLEAN DEFAULT TRUE

### 2. `roadmaps`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `roadmap_id` VARCHAR(50) UNIQUE INDEX
- `user_name` VARCHAR(100) NOT NULL
- `target_role` VARCHAR(100) NOT NULL
- `readiness_score` FLOAT NOT NULL
- `gap_score` FLOAT NOT NULL
- `missing_skills` TEXT NOT NULL
- `recommended_courses` TEXT NOT NULL
- `recommended_projects` TEXT NOT NULL
- `estimated_weeks_to_readiness` INTEGER NOT NULL
- `salary_growth_potential` FLOAT
- `evidence_hash` VARCHAR(64)
- `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP

### 3. `audit_ledger`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `block_index` INTEGER NOT NULL
- `timestamp` VARCHAR(50) NOT NULL
- `action_type` VARCHAR(64) NOT NULL
- `details` TEXT NOT NULL
- `previous_hash` VARCHAR(64) NOT NULL
- `current_hash` VARCHAR(64) NOT NULL
