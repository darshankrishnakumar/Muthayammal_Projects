# Database Schema & Data Dictionary

## SQLite Database
File: `source_code/fake_news.db` (and fallback `data/fake_news.db`).

## Table: `verifications`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique verification record ID |
| `headline` | TEXT | NOT NULL | News headline or article body |
| `is_fake` | INTEGER | NOT NULL (0 or 1) | Binary classification verdict |
| `fake_pct` | REAL | NOT NULL | Calibrated fake probability (0-100) |
| `real_pct` | REAL | NOT NULL | Calibrated real credibility (0-100) |
| `decision_score` | REAL | NOT NULL | Raw hyperplane margin distance ($w \cdot x + b$) |
| `sensational_score`| INTEGER | NOT NULL | Sensationalism index (0-100) |
| `pure_language_mode`| INTEGER | NOT NULL | 1 if watermarks stripped, 0 otherwise |
| `timestamp` | TEXT | NOT NULL | ISO 8601 UTC timestamp |

## Indexes
- `idx_verif_timestamp`: B-tree index on `timestamp DESC` for rapid pagination and timeline queries.
