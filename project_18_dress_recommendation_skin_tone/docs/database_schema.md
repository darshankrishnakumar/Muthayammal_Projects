# Database Schema & Persistence Specification

PROJECT-018 maintains an ACID-compliant SQLite3 database at `data/user_data.db`.

## Schema Definitions

```sql
CREATE TABLE IF NOT EXISTS USER_PROFILE (
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS BODY_MEASUREMENTS (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    height_cm REAL,
    shoulder_cm REAL,
    chest_cm REAL,
    waist_cm REAL,
    hip_cm REAL,
    measurement_source TEXT NOT NULL CHECK(measurement_source IN ('manual', 'image_estimate')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER_PROFILE (user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    preferred_styles TEXT,
    preferred_colours TEXT,
    preferred_occasions TEXT,
    preferred_categories TEXT,
    budget_min REAL DEFAULT 0,
    budget_max REAL DEFAULT 10000,
    preferred_season TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER_PROFILE (user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RECOMMENDATION_HISTORY (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    outfit_id TEXT NOT NULL,
    outfit_name TEXT,
    category TEXT,
    match_score REAL,
    recommendation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER_PROFILE (user_id) ON DELETE CASCADE
);
```
