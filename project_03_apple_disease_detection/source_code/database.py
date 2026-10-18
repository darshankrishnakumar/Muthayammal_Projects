"""
Apple Health Intelligence AI - Database Subsystem
=================================================
Manages persistent SQLite connection and audit logging for diagnostic inferences.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_FILE = Path("apple_diagnostics.db")

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnostic_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                specimen_type TEXT NOT NULL,
                predicted_class TEXT NOT NULL,
                display_name TEXT,
                confidence REAL NOT NULL,
                model_used TEXT NOT NULL,
                severity TEXT,
                is_uncertain INTEGER DEFAULT 0,
                uncertainty_reason TEXT,
                source TEXT DEFAULT 'web'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_timestamp ON diagnostic_records(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_specimen ON diagnostic_records(specimen_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_class ON diagnostic_records(predicted_class)")
        conn.commit()

def save_diagnosis(
    specimen_type: str,
    predicted_class: str,
    display_name: str,
    confidence: float,
    model_used: str,
    severity: str = "N/A",
    is_uncertain: bool = False,
    uncertainty_reason: str = None,
    source: str = "web"
) -> int:
    """Inserts a new diagnosis record and returns the assigned ID."""
    now_str = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diagnostic_records (
                timestamp, specimen_type, predicted_class, display_name,
                confidence, model_used, severity, is_uncertain,
                uncertainty_reason, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str,
            specimen_type,
            predicted_class,
            display_name,
            round(float(confidence), 2),
            model_used,
            severity,
            1 if is_uncertain else 0,
            uncertainty_reason,
            source
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_diagnoses(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves recent diagnostic records sorted by timestamp descending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, specimen_type, predicted_class, display_name,
                   confidence, model_used, severity, is_uncertain, uncertainty_reason, source
            FROM diagnostic_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_db_stats() -> Dict[str, Any]:
    """Returns database connection status and statistics."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM diagnostic_records")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT specimen_type, COUNT(*) FROM diagnostic_records GROUP BY specimen_type")
            specimen_counts = dict(cursor.fetchall())
            
            return {
                "connected": True,
                "database_file": str(DB_FILE.resolve()),
                "total_records": total_count,
                "specimen_breakdown": specimen_counts
            }
    except Exception as e:
        return {
            "connected": False,
            "database_file": str(DB_FILE.resolve()),
            "error": str(e),
            "total_records": 0
        }

# Auto-initialize database on import
init_db()
