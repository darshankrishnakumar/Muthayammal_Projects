"""
Career Guidance AI - Database Subsystem
========================================
Persistent SQLite storage for student career assessments, recommendations, and audit logs.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "career_guidance.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                student_name TEXT NOT NULL,
                suggested_role TEXT NOT NULL,
                model_used TEXT NOT NULL,
                confidence REAL NOT NULL,
                top_skills TEXT,
                salary_range TEXT,
                academic_avg REAL,
                coding_rating INTEGER,
                interested_area TEXT,
                input_json TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessment_time ON career_assessments(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessment_role ON career_assessments(suggested_role)")
        conn.commit()

def save_assessment(
    student_name: str,
    suggested_role: str,
    model_used: str,
    confidence: float,
    top_skills: List[str],
    salary_range: str,
    academic_avg: float,
    coding_rating: int,
    interested_area: str,
    input_data: dict
) -> int:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO career_assessments (
                timestamp, student_name, suggested_role, model_used, confidence,
                top_skills, salary_range, academic_avg, coding_rating, interested_area, input_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str,
            student_name or "Anonymous Student",
            suggested_role,
            model_used,
            confidence,
            ", ".join(top_skills) if isinstance(top_skills, list) else str(top_skills),
            salary_range,
            academic_avg,
            coding_rating,
            interested_area,
            json.dumps(input_data)
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_assessments(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, student_name, suggested_role, model_used,
                   confidence, top_skills, salary_range, academic_avg, coding_rating, interested_area, input_json
            FROM career_assessments
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "student_name": r["student_name"],
                "suggested_role": r["suggested_role"],
                "model_used": r["model_used"],
                "confidence": round(r["confidence"], 1),
                "top_skills": r["top_skills"],
                "salary_range": r["salary_range"],
                "academic_avg": round(r["academic_avg"], 1) if r["academic_avg"] else 0.0,
                "coding_rating": r["coding_rating"],
                "interested_area": r["interested_area"],
                "input_data": json.loads(r["input_json"]) if r["input_json"] else {}
            })
        return results

def delete_assessment(record_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM career_assessments WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_assessments() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM career_assessments")
        conn.commit()
        return True

def get_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM career_assessments")
        total = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT suggested_role, COUNT(*) as count 
            FROM career_assessments 
            GROUP BY suggested_role 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_roles = [dict(r) for r in cursor.fetchall()]
        return {
            "total_assessments": total,
            "top_recommended_roles": top_roles
        }
