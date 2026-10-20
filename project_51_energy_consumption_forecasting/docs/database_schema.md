# Database Schema: PROJECT-051 Relational Storage

## Database Configuration
- **Engine**: SQLite 3 (WAL Mode Enabled)
- **Database File**: `source_code/data/energy.db`
- **Pragmas**:
  - `PRAGMA journal_mode=WAL;`
  - `PRAGMA synchronous=NORMAL;`

## Tables

### 1. `energy_plans`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing identifier |
| `plan_id` | VARCHAR(50) UNIQUE | Unique dispatch plan identifier (e.g., PLAN-2026-0001) |
| `facility_name` | VARCHAR(100) | Facility identifier |
| `archetype` | VARCHAR(50) | Facility archetype category |
| `timestamp` | DATETIME | Plan generation timestamp |
| `nominal_base_load` | REAL | Facility base power draw in kW |
| `ambient_temperature` | REAL | Ambient temperature in °C |
| `tou_tariff_rate` | REAL | Time-of-use tariff rate in ¢/kWh |
| `renewable_penetration` | REAL | Grid renewable energy percentage [0-100] |
| `forecast_peak_kwh` | REAL | Predicted peak load under uncontrolled operation |
| `optimized_peak_kwh` | REAL | Predicted peak load after dynamic load shifting |
| `peak_reduction_pct` | REAL | Achieved peak reduction percentage |
| `daily_cost_savings_usd` | REAL | Daily electricity cost savings in USD |
| `co2_avoided_kg` | REAL | Estimated avoided marginal CO2 emissions in kg |
| `grid_stress_index` | REAL | Grid congestion / stress score [0-100] |
| `recommendations` | TEXT | Actionable operational dispatch steps |
| `evidence_hash` | VARCHAR(64) | 64-character SHA-256 evidence digest |
| `baseline_24h` | TEXT | Serialized JSON array of 24-hour baseline values |
| `optimized_24h` | TEXT | Serialized JSON array of 24-hour optimized values |

### 2. `audit_ledger`
| Column | Type | Description |
|---|---|---|
| `block_index` | INTEGER PRIMARY KEY | Chronological block sequence index (0 = Genesis) |
| `timestamp` | TEXT | ISO 8601 UTC timestamp |
| `event_type` | TEXT | Event classification (GENESIS_BLOCK, FORECAST_DISPATCHED, PEAK_SHAVING_APPLIED) |
| `plan_id` | TEXT | Target plan identifier |
| `evidence_hash` | TEXT | SHA-256 hash of energy plan payload |
| `previous_hash` | TEXT | Hash of block index N-1 |
| `block_hash` | TEXT | SHA-256 hash of block contents |
