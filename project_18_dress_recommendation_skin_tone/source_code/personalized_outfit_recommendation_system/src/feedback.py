"""SQLite interaction and feedback manager for Stage 8/11."""

import os
import sqlite3
from typing import Dict, Any, List, Optional
import config


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_feedback_tables():
    """Initializes feedback tables in user_data.db."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER_FEEDBACK (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL, -- 'like', 'dislike', 'save', 'skip'
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def record_user_feedback(user_id: str, item_id: str, feedback_type: str, comment: str = None) -> bool:
    try:
        init_feedback_tables()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO USER_FEEDBACK (user_id, item_id, feedback_type, comment)
            VALUES (?, ?, ?, ?)
        """, (user_id, item_id, feedback_type, comment))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_user_feedback(user_id: str) -> List[Dict[str, Any]]:
    try:
        init_feedback_tables()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USER_FEEDBACK WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []
