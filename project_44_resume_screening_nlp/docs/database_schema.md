# Database Schema Specification: SQLite WAL Engine

## Engine Configuration
- **File**: `data/resume_matching.db`
- **Journal Mode**: `WAL` (Write-Ahead Logging via `PRAGMA journal_mode=WAL`)
- **Synchronous**: `NORMAL` (`PRAGMA synchronous=NORMAL`)
- **Foreign Keys**: Enabled (`PRAGMA foreign_keys=ON`)

## Tables

### 1. `job_openings`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `job_id` VARCHAR(50) UNIQUE INDEX
- `title` VARCHAR(100) NOT NULL
- `department` VARCHAR(50) NOT NULL
- `required_skills` TEXT NOT NULL
- `min_years_experience` FLOAT DEFAULT 2.0
- `description` TEXT NOT NULL
- `is_active` BOOLEAN DEFAULT TRUE

### 2. `candidate_matches`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `match_id` VARCHAR(50) UNIQUE INDEX
- `job_id` VARCHAR(50) INDEX
- `candidate_name` VARCHAR(100) NOT NULL
- `overall_match_score` FLOAT NOT NULL
- `semantic_similarity` FLOAT NOT NULL
- `skill_coverage_pct` FLOAT NOT NULL
- `experience_fit_score` FLOAT NOT NULL
- `seniority_compatibility` FLOAT
- `matched_skills` TEXT NOT NULL
- `missing_skills` TEXT NOT NULL
- `screening_decision` VARCHAR(30) NOT NULL
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
