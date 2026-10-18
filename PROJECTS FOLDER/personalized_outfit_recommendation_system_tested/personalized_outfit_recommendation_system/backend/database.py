"""SQLite Database Schema and Connection Management for User Profiles and History.

Rules:
- Explicit separation of manual vs image-derived measurements.
- Cascade deletion when profile is deleted.
- No storage of raw images in the database.
- Graceful error handling and transaction rollback.
"""

import os
import sqlite3
from typing import Optional
import config


def get_db_connection(db_path: str = config.DB_PATH) -> sqlite3.Connection:
    """Creates a connection to the SQLite database with row factory enabled."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = config.DB_PATH) -> None:
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        # 1. USER_PROFILE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USER_PROFILE (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. BODY_MEASUREMENTS
        cursor.execute("""
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
        """)

        # 3. USER_PREFERENCES
        cursor.execute("""
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
        """)

        # 4. RECOMMENDATION_HISTORY
        cursor.execute("""
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
        """)

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
