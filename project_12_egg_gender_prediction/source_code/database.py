"""
Egg Sex Prediction AI - Database Subsystem
===========================================
Persistent SQLite audit logging and history management for egg sex diagnostic records.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egg_history.db")

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS egg_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                specimen_name TEXT NOT NULL,
                predicted_sex TEXT NOT NULL,
                symbol TEXT,
                confidence REAL NOT NULL,
                female_prob REAL NOT NULL,
                male_prob REAL NOT NULL,
                shape_index REAL NOT NULL,
                elongation REAL,
                apex_sharpness REAL,
                recommendation TEXT,
                source TEXT DEFAULT 'web'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_timestamp ON egg_predictions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_sex ON egg_predictions(predicted_sex)")
        conn.commit()

def save_prediction_record(
    specimen_name: str,
    predicted_sex: str,
    symbol: str,
    confidence: float,
    female_prob: float,
    male_prob: float,
    shape_index: float,
    elongation: float,
    apex_sharpness: float,
    recommendation: str,
    source: str = "web"
) -> int:
    """Inserts a new prediction record into SQLite and returns the record ID."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO egg_predictions (
                timestamp, specimen_name, predicted_sex, symbol,
                confidence, female_prob, male_prob, shape_index,
                elongation, apex_sharpness, recommendation, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str, specimen_name, predicted_sex, symbol,
            round(float(confidence), 1), round(float(female_prob), 1), round(float(male_prob), 1),
            round(float(shape_index), 2), round(float(elongation), 3), round(float(apex_sharpness), 3),
            recommendation, source
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches the latest prediction records."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, specimen_name, predicted_sex, symbol,
                   confidence, female_prob, male_prob, shape_index,
                   elongation, apex_sharpness, recommendation, source
            FROM egg_predictions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_database_stats() -> Dict[str, Any]:
    """Computes aggregate analytics from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM egg_predictions")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM egg_predictions WHERE predicted_sex LIKE 'Female%'")
        female_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM egg_predictions WHERE predicted_sex LIKE 'Male%'")
        male_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence), AVG(shape_index) FROM egg_predictions")
        avg_row = cursor.fetchone()
        avg_conf = round(avg_row[0], 1) if avg_row[0] else 0.0
        avg_si = round(avg_row[1], 1) if avg_row[1] else 0.0

        return {
            "total_records": total,
            "female_count": female_count,
            "male_count": male_count,
            "avg_confidence": avg_conf,
            "avg_shape_index": avg_si,
            "database_file": DB_FILE,
            "status": "connected"
        }

def clear_all_history():
    """Wipes the database table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM egg_predictions")
        conn.commit()

# Self-initialize on import
init_db()

if __name__ == "__main__":
    print(f"Database initialized at: {DB_FILE}")
    stats = get_database_stats()
    print("Database Stats:", stats)
