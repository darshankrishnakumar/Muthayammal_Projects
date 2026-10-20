# Database Schema — PROJECT-049
## Relational SQLite Storage in Write-Ahead Logging (WAL) Mode

### 1. Connection Pragma & Concurrency
The database file `source_code/data/healthcare.db` operates strictly under:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
```

### 2. Table: `patient_profiles`
Master patient index storing demographics and clinical provider assignments.
- `id` (INTEGER, Primary Key, Auto-increment)
- `patient_id` (VARCHAR(50), Unique, Indexed)
- `full_name` (VARCHAR(100), Indexed)
- `cohort` (VARCHAR(50)): DIABETIC_METABOLIC, HYPERTENSIVE_CVD, RENAL_CKD, NORMOTENSIVE_CONTROL
- `age` (INTEGER)
- `gender` (VARCHAR(20))
- `blood_group` (VARCHAR(10))
- `attending_physician` (VARCHAR(100))
- `registered_clinic` (VARCHAR(100))
- `created_at` (DATETIME, Default UTC)

### 3. Table: `patient_assessments`
Longitudinal risk evaluations storing biomarkers, predictions, and evidence hashes.
- `id` (INTEGER, Primary Key, Auto-increment)
- `assessment_id` (VARCHAR(50), Unique, Indexed)
- `patient_id` (VARCHAR(50), Indexed)
- `full_name` (VARCHAR(100))
- `age` (INTEGER)
- `gender` (VARCHAR(20))
- `cohort` (VARCHAR(50))
- `systolic_bp` (FLOAT)
- `diastolic_bp` (FLOAT)
- `hba1c` (FLOAT)
- `fasting_glucose` (FLOAT)
- `total_cholesterol` (FLOAT)
- `hdl_cholesterol` (FLOAT)
- `ldl_cholesterol` (FLOAT)
- `egfr` (FLOAT)
- `bmi` (FLOAT)
- `cardiovascular_risk_pct` (FLOAT)
- `type2_diabetes_risk_pct` (FLOAT)
- `hypertension_risk_pct` (FLOAT)
- `ckd_risk_pct` (FLOAT)
- `composite_risk_tier` (VARCHAR(20)): LOW, MODERATE, HIGH, CRITICAL
- `ten_year_mortality_risk_pct` (FLOAT)
- `hospital_readmission_risk_pct` (FLOAT)
- `polypharmacy_complexity_index` (FLOAT)
- `renal_progression_hazard_pct` (FLOAT)
- `primary_biomarker_drivers` (TEXT)
- `top_shap_driver` (VARCHAR(100))
- `preventive_recommendations` (TEXT)
- `recommended_intervention` (VARCHAR(150))
- `evidence_hash` (VARCHAR(64), Indexed, SHA-256)
- `timestamp` (DATETIME, Default UTC)

### 4. Table: `audit_ledger`
Cryptographic ledger with Genesis seeding and continuous SHA-256 block hash chaining.
- `id` (INTEGER, Primary Key, Auto-increment)
- `block_index` (INTEGER, Unique, Indexed)
- `previous_hash` (VARCHAR(64), Not Null)
- `block_hash` (VARCHAR(64), Unique, Not Null)
- `timestamp` (DATETIME, Default UTC)
- `event_type` (VARCHAR(50), Not Null)
- `details_json` (TEXT, Not Null, Canonical Sorted JSON)
- `evidence_hash` (VARCHAR(64), Not Null)
