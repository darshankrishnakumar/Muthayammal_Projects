# Database Schema — PROJECT-048
## Relational SQLite Storage in Write-Ahead Logging (WAL) Mode

### 1. Connection Pragma & Concurrency
The database file `source_code/data/food_freshness.db` operates strictly under:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
```

### 2. Table: `food_batches`
Tracks perishable inventory batches registered across supply chain facilities.
- `id` (INTEGER, Primary Key, Auto-increment)
- `batch_id` (VARCHAR(50), Unique, Indexed)
- `food_category` (VARCHAR(50), Indexed): MEAT_POULTRY, FRESH_PRODUCE, DAIRY, BAKERY
- `product_name` (VARCHAR(100), Indexed)
- `supplier_origin` (VARCHAR(100))
- `storage_facility` (VARCHAR(80))
- `freshness_score` (FLOAT, 0.0 - 100.0)
- `deterioration_stage` (VARCHAR(30)): STAGE_1_FRESH, STAGE_2_MARGINAL, STAGE_3_DETERIORATED
- `estimated_shelf_life_hours` (FLOAT)
- `remaining_shelf_life_days` (FLOAT)
- `browning_index` (FLOAT)
- `spoilage_area_pct` (FLOAT)
- `microbial_risk_pct` (FLOAT)
- `cold_chain_compliance_score` (FLOAT)
- `recommendation` (VARCHAR(100))
- `timestamp` (DATETIME, Default UTC)

### 3. Table: `freshness_assessments`
Records individual spatio-spectral and physicochemical inspection events.
- `id` (INTEGER, Primary Key, Auto-increment)
- `sample_id` (VARCHAR(50), Indexed)
- `batch_id` (VARCHAR(50), Indexed)
- `food_category` (VARCHAR(50))
- `product_name` (VARCHAR(100))
- `storage_temp_c` (FLOAT)
- `relative_humidity_pct` (FLOAT)
- `storage_duration_hours` (FLOAT)
- `browning_index` (FLOAT)
- `tvbn_mg_per_100g` (FLOAT)
- `ph_level` (FLOAT)
- `ethylene_concentration_ppm` (FLOAT)
- `moisture_content_pct` (FLOAT)
- `bacterial_log_cfu_g` (FLOAT)
- `reflectance_ratio_650_850` (FLOAT)
- `freshness_score` (FLOAT)
- `deterioration_stage` (VARCHAR(30))
- `estimated_shelf_life_hours` (FLOAT)
- `remaining_shelf_life_days` (FLOAT)
- `spoilage_risk_pct` (FLOAT)
- `microbial_risk_pct` (FLOAT)
- `cold_chain_compliance_score` (FLOAT)
- `advisory_recommendation` (VARCHAR(100))
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
