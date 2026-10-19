# Relational Database Architecture & Schema Specification

## 1. Database Overview
VIGIL-8 persists all security incidents, camera configurations, taxonomy definitions, and audit events into a transactional SQLite database:
- **Database File**: `weapon_detection.db`
- **Location**: `project_20_weapon_detection/source_code/backend/weapon_detection.db`
- **ACID Compliance**: Full transaction atomicity with automated schema provisioning on launch.

## 2. Entity-Relationship Schemas

### Table: `incidents`
```sql
CREATE TABLE incidents (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    threat_level TEXT NOT NULL,
    weapon_detected INTEGER NOT NULL,
    weapon_class TEXT,
    confidence REAL,
    status TEXT NOT NULL,
    notes TEXT,
    detections_json TEXT,
    image_metrics_json TEXT
);
```

### Table: `cctv_cameras`
```sql
CREATE TABLE cctv_cameras (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    zone TEXT NOT NULL,
    resolution TEXT NOT NULL,
    status TEXT NOT NULL,
    type TEXT NOT NULL
);
```

### Table: `threat_definitions`
```sql
CREATE TABLE threat_definitions (
    weapon_class TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    threat_level TEXT NOT NULL,
    color_code TEXT NOT NULL,
    response_protocol TEXT NOT NULL
);
```

### Table: `system_audit`
```sql
CREATE TABLE system_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT DEFAULT 'SEC-OPERATOR',
    details TEXT
);
```
