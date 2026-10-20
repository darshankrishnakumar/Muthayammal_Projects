# Database Schema: Document Forgery Detection (SQLite WAL)

## Connection & Operational Pragmas
- Engine: SQLite 3.x
- Journal Mode: `PRAGMA journal_mode=WAL;`
- Synchronous Mode: `PRAGMA synchronous=NORMAL;`
- Foreign Key Constraints: `PRAGMA foreign_keys=ON;`

## Tables

### 1. `document_audits`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Internal row counter |
| `audit_id` | VARCHAR(50) | UNIQUE, INDEX | Unique audit identifier (e.g., AUD-2026-XXXXXX) |
| `document_title` | VARCHAR(120) | NOT NULL | Title of questioned document |
| `document_type` | VARCHAR(50) | NOT NULL | INVOICE, IDENTITY_CARD, ACADEMIC_CERTIFICATE, CONTRACT |
| `forgery_verdict` | VARCHAR(20) | NOT NULL | AUTHENTIC, SUSPICIOUS, FORGED |
| `forgery_type` | VARCHAR(50) | NOT NULL | NONE, COPY_MOVE, SPLICING, TEXT_ERASURE |
| `forgery_probability` | FLOAT | NOT NULL | Forgery confidence (0.0 to 1.0) |
| `tampered_area_pct` | FLOAT | NOT NULL | Compromised surface area (0.0 to 50.0%) |
| `ela_anomaly_score` | FLOAT | NOT NULL | Compression discrepancy index (0.0 to 10.0) |
| `spectral_dct_noise` | FLOAT | NULLABLE | Frequency noise energy (0.0 to 1.0) |
| `evidence_hash` | VARCHAR(64) | NOT NULL | SHA-256 evidence fingerprint |
| `timestamp` | DATETIME | DEFAULT UTC | UTC audit timestamp |

### 2. `inspection_templates`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Primary key |
| `template_code` | VARCHAR(32) | UNIQUE, INDEX | e.g. TMPL-INV-01, TMPL-ID-02 |
| `template_name` | VARCHAR(100) | NOT NULL | Human readable template name |
| `document_category` | VARCHAR(50) | NOT NULL | Category code |
| `allowed_compression_variance` | FLOAT | DEFAULT 0.08 | ELA residual tolerance |
| `baseline_dpi` | INTEGER | DEFAULT 300 | Scanning resolution standard |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active flag |

### 3. `audit_ledger`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Internal index |
| `block_index` | INTEGER | NOT NULL | Sequential height (0 = Genesis) |
| `timestamp` | VARCHAR(50) | NOT NULL | ISO-8601 UTC timestamp |
| `action_type` | VARCHAR(64) | NOT NULL | Action descriptor |
| `details` | TEXT | NOT NULL | Human and machine readable audit payload |
| `previous_hash` | VARCHAR(64) | NOT NULL | SHA-256 hash of previous block (or '0'*64) |
| `current_hash` | VARCHAR(64) | NOT NULL | SHA-256(Action || Details || Ts || PrevHash) |
