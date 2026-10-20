# Database Schema: PROJECT-050 Relational Storage

## Database Configuration
- **Engine**: SQLite 3 (WAL Mode Enabled)
- **Database File**: `source_code/data/idp.db`
- **Pragmas**:
  - `PRAGMA journal_mode=WAL;`
  - `PRAGMA synchronous=NORMAL;`

## Tables

### 1. `processed_documents`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing identifier |
| `doc_id` | VARCHAR(50) UNIQUE | Unique document identifier (e.g., DOC-2026-0001) |
| `document_type` | VARCHAR(50) | Form archetype category |
| `patient_or_client_name` | VARCHAR(100) | Extracted name entity |
| `primary_diagnosis_or_purpose` | VARCHAR(100) | Extracted diagnostic or purpose field |
| `date_field` | VARCHAR(30) | Date string (YYYY-MM-DD) |
| `id_number` | VARCHAR(50) | Form reference number |
| `total_amount` | VARCHAR(30) | Currency value |
| `contrast_ratio` | REAL | Optical contrast ratio [0.0 - 1.0] |
| `stroke_variance` | REAL | Pen stroke width variance |
| `background_snr` | REAL | Background signal-to-noise ratio in dB |
| `quality_score` | REAL | Predicted document quality score [0 - 100] |
| `lexical_confidence` | REAL | Lexical confidence probability [0.0 - 1.0] |
| `character_error_rate` | REAL | Character Error Rate (CER) |
| `word_error_rate` | REAL | Word Error Rate (WER) |
| `signature_verified` | BOOLEAN | Signature authenticity verification flag |
| `human_review_required` | BOOLEAN | Escalation flag for human review |
| `evidence_hash` | VARCHAR(64) | 64-character SHA-256 evidence digest |
| `extracted_json_payload` | TEXT | Serialized full extraction payload |
| `timestamp` | DATETIME | Ingestion timestamp |

### 2. `audit_ledger`
| Column | Type | Description |
|---|---|---|
| `block_index` | INTEGER PRIMARY KEY | Chronological block sequence index (0 = Genesis) |
| `timestamp` | TEXT | ISO 8601 UTC timestamp |
| `event_type` | TEXT | Event classification (GENESIS_BLOCK, DOCUMENT_OCR_TRANSCRIBED, HUMAN_REVIEW_FLAGGED) |
| `doc_id` | TEXT | Target document identifier |
| `evidence_hash` | TEXT | SHA-256 hash of document payload |
| `previous_hash` | TEXT | Hash of block index N-1 |
| `block_hash` | TEXT | SHA-256 hash of block contents |
