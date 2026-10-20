# Database Schema: Biometric Attendance & Audit Ledger (SQLite WAL)

## Connection & Operational Pragmas
- Engine: SQLite 3.x
- Journal Mode: `PRAGMA journal_mode=WAL;`
- Synchronous Mode: `PRAGMA synchronous=NORMAL;`
- Foreign Key Constraints: `PRAGMA foreign_keys=ON;`

## Tables

### 1. `students`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Internal row index |
| `student_id` | VARCHAR(50) | UNIQUE, INDEX | Institutional ID (e.g., STU-101) |
| `full_name` | VARCHAR(100) | NOT NULL | Student legal name |
| `department` | VARCHAR(50) | NOT NULL | Academic department |
| `year` | INTEGER | DEFAULT 3 | Current matriculation year |
| `face_enrolled` | BOOLEAN | DEFAULT TRUE | Biometric enrollment flag |
| `rfid_tag` | VARCHAR(32) | DEFAULT 'RFID-8821' | Encrypted smartcard fallback |

### 2. `attendance_records`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Internal record counter |
| `record_id` | VARCHAR(50) | UNIQUE, INDEX | Unique access code (e.g., ATT-2026-XXXXXX) |
| `student_id` | VARCHAR(50) | INDEX | Foreign reference to student |
| `full_name` | VARCHAR(100) | NULLABLE | Cached full name |
| `course_code` | VARCHAR(30) | DEFAULT 'CS-401' | Course code |
| `classroom_id` | VARCHAR(30) | DEFAULT 'HALL-A1' | Physical turnstile gate |
| `liveness_status` | VARCHAR(30) | NOT NULL | REAL vs SPOOF_DETECTED |
| `attack_type` | VARCHAR(50) | DEFAULT 'NONE' | NONE, PRINT_ATTACK_2D, SCREEN, MASK |
| `anti_spoof_confidence` | FLOAT | NOT NULL | 0.0 to 1.0 confidence score |
| `face_match_confidence` | FLOAT | NOT NULL | 0.0 to 1.0 cosine match |
| `spoof_risk_pct` | FLOAT | NOT NULL | Regressed attack probability (0-100%) |
| `micro_tremor_score` | FLOAT | NOT NULL | Regressed biological tremor (0-1.0) |
| `illumination_entropy` | FLOAT | NOT NULL | Regressed surface uniformity (0-10.0) |
| `attendance_score` | FLOAT | NOT NULL | Composite quality score (0-100%) |
| `status` | VARCHAR(30) | DEFAULT 'PRESENT' | PRESENT, REJECTED_SPOOF, LATE |
| `evidence_hash` | VARCHAR(64) | NOT NULL | SHA-256 biometric fingerprint hash |
| `timestamp` | DATETIME | DEFAULT UTC | UTC access timestamp |

### 3. `audit_ledger`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Internal ledger index |
| `block_index` | INTEGER | NOT NULL | Sequential block height (0 = Genesis) |
| `timestamp` | VARCHAR(50) | NOT NULL | ISO-8601 UTC timestamp |
| `action_type` | VARCHAR(64) | NOT NULL | Action descriptor |
| `details` | TEXT | NOT NULL | Human and machine readable audit payload |
| `previous_hash` | VARCHAR(64) | NOT NULL | SHA-256 hash of previous block (or '0'*64) |
| `current_hash` | VARCHAR(64) | NOT NULL | SHA-256(Action || Details || Ts || PrevHash) |
