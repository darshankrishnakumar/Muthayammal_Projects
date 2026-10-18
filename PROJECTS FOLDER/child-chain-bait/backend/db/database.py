"""
Database connection and schema initialization for Child Gait Prediction.
Manages the `gait_records` table in SQLite.
Kept strictly separate from the ML model layer.
"""

import os
import sqlite3
from typing import Generator

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "gait_database.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection with dict-like row access."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema and creates `gait_records` table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gait_records (
        id TEXT PRIMARY KEY,
        child_id TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        heel_pressure REAL NOT NULL,
        toe_pressure REAL NOT NULL,
        tilt_angle REAL NOT NULL,
        step_duration REAL NOT NULL,
        stride_length REAL NOT NULL,
        walking_speed REAL NOT NULL,
        gait_class TEXT NOT NULL,
        confidence REAL,
        data_source TEXT DEFAULT 'real',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Safe migration in case table was created earlier without data_source
    try:
        cursor.execute("ALTER TABLE gait_records ADD COLUMN data_source TEXT DEFAULT 'real';")
    except Exception:
        pass # Column already exists

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gait_child_id ON gait_records(child_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gait_created_at ON gait_records(created_at);")

    conn.commit()
    conn.close()
