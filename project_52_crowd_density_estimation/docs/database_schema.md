# Database Schema: PROJECT-052 Relational Storage

## Database Configuration
- **Engine**: SQLite 3 (WAL Mode Enabled)
- **Database File**: `source_code/data/crowd_analytics.db`
- **Pragmas**:
  - `PRAGMA journal_mode=WAL;`
  - `PRAGMA synchronous=NORMAL;`

## Tables

### 1. `crowd_monitoring_events`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing identifier |
| `event_id` | VARCHAR(32) UNIQUE | Unique scan identifier (e.g., CRW-2026-00001) |
| `zone_name` | VARCHAR(64) | Monitored CCTV zone identifier |
| `archetype` | VARCHAR(50) | Venue zone archetype category |
| `timestamp` | DATETIME | Surveillance timestamp |
| `estimated_headcount` | INTEGER | CSRNet estimated headcount |
| `density_level` | VARCHAR(24) | Categorical density level (Low, Moderate, High, Critical) |
| `anomaly_detected` | BOOLEAN | Safety anomaly trigger flag |
| `anomaly_type` | VARCHAR(32) | Classification (Normal, Congestion, Dispersal, Intrusion, Stampede) |
| `risk_score` | REAL | Predicted composite risk score [0.0 - 1.0] |
| `optical_flow_turbulence` | REAL | Normalized optical flow turbulence index [0.0 - 1.0] |
| `flow_velocity_mps` | REAL | Mean crowd velocity in m/s |
| `spatial_divergence` | REAL | Velocity spatial divergence div(V) |
| `kinetic_energy_entropy` | REAL | Kinetic energy spatial entropy |
| `density_ratio_sqm` | REAL | Localized density ratio in persons/m² |
| `bottleneck_pressure_psi` | REAL | Compressive physical pressure |
| `directional_coherence` | REAL | Directional coherence [0.0 - 1.0] |
| `velocity_variance` | REAL | Velocity variance |
| `occlusion_ratio` | REAL | Visual pedestrian occlusion ratio |
| `ambient_lighting_lux` | REAL | Scene illumination in lux |
| `panic_index` | REAL | Composite panic index [0.0 - 1.0] |
| `evidence_hash` | VARCHAR(64) | 64-character SHA-256 evidence digest |

### 2. `audit_ledger`
| Column | Type | Description |
|---|---|---|
| `block_index` | INTEGER PRIMARY KEY | Chronological block sequence index (0 = Genesis) |
| `timestamp` | TEXT | ISO 8601 UTC timestamp |
| `event_type` | TEXT | Event classification (GENESIS_BLOCK, CROWD_MONITORING_SCAN, CROWD_ANOMALY_ALERT) |
| `event_id` | TEXT | Target event identifier |
| `evidence_hash` | TEXT | SHA-256 hash of event payload |
| `previous_hash` | TEXT | Hash of block index N-1 |
| `block_hash` | TEXT | SHA-256 hash of block contents |
