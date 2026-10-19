# Relational Database Architecture & Schema Specification

## 1. Database Overview
VIGIL-CARD implements an ACID-compliant SQLite relational database:
- **Database File**: `credit_card_fraud.db`
- **Location**: `project_21_credit_card_fraud/source_code/backend/credit_card_fraud.db`
- **Integrity**: Transactional commit with zero data loss under simulated power failures.

## 2. Entity-Relationship Schemas

### Table: `transactions`
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    card_id TEXT NOT NULL,
    merchant TEXT NOT NULL,
    amount REAL NOT NULL,
    risk_score REAL NOT NULL,
    fraud_probability REAL NOT NULL,
    is_fraud INTEGER NOT NULL,
    decision TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    features_json TEXT,
    attributions_json TEXT
);
```

### Table: `blocked_cards`
```sql
CREATE TABLE blocked_cards (
    card_id TEXT PRIMARY KEY,
    blocked_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    operator TEXT DEFAULT 'FRAUD-GUARD'
);
```

### Table: `system_audit`
```sql
CREATE TABLE system_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT
);
```

### Table: `model_benchmarks`
```sql
CREATE TABLE model_benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    accuracy REAL NOT NULL,
    precision REAL NOT NULL,
    recall REAL NOT NULL,
    f1_score REAL NOT NULL,
    auc_roc REAL NOT NULL,
    latency_ms REAL NOT NULL
);
```
