# Database Schema & Persistence Specification

PROJECT-017 utilizes an ACID-compliant SQLite3 database located at `source_code/phishing_scans.db`.

## `email_scans` Table Definition

```sql
CREATE TABLE IF NOT EXISTS email_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    from_hdr TEXT,
    reply_to_hdr TEXT,
    spf_dkim_hdr TEXT,
    subject_hdr TEXT,
    body_snippet TEXT,
    selected_model TEXT,
    is_phishing INTEGER,
    phishing_probability REAL,
    threat_level TEXT,
    risk_class TEXT,
    header_risk REAL,
    body_risk REAL,
    consensus_phish_votes INTEGER,
    latency_ms REAL
);
```

## Schema Field Descriptions
- `id`: Auto-incrementing primary key for audit trail indexing.
- `timestamp`: UTC ISO 8601 execution timestamp.
- `from_hdr`: Envelope sender address.
- `reply_to_hdr`: Return path address.
- `spf_dkim_hdr`: Verification result (`pass`, `fail`, `softfail`, `none`).
- `subject_hdr`: Incoming email subject line.
- `body_snippet`: First 300 characters of email body content.
- `selected_model`: Model utilized (`rcnn_attn`, `ensemble`, `bilstm`, etc.).
- `is_phishing`: 1 for malicious phishing, 0 for legitimate email.
- `phishing_probability`: Confidence score from 0.0 to 100.0%.
- `threat_level`: Human-readable classification (`CRITICAL / PHISHING CONFIRMED`, `LEGITIMATE / AUTHENTICATED`, etc.).
- `consensus_phish_votes`: Number of parallel models voting phishing (out of 9).
- `latency_ms`: Total wall-clock inference duration in milliseconds.
