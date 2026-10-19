import sqlite3
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "heart_patients.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            sex INTEGER NOT NULL,
            chest_pain_type INTEGER NOT NULL,
            resting_bp INTEGER NOT NULL,
            cholesterol INTEGER NOT NULL,
            fasting_bs INTEGER NOT NULL,
            resting_ecg INTEGER NOT NULL,
            max_hr INTEGER NOT NULL,
            exercise_angina INTEGER NOT NULL,
            oldpeak REAL NOT NULL,
            st_slope INTEGER NOT NULL,
            prediction INTEGER NOT NULL,
            risk_probability REAL NOT NULL,
            risk_tier TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_heart_timestamp ON patient_assessments (timestamp DESC)
    """)
    conn.commit()

    # Seed if empty
    cursor.execute("SELECT COUNT(*) FROM patient_assessments")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_data = [
            (54, 1, 3, 150, 195, 0, 0, 122, 0, 0.0, 1, 0, 18.5, "Low", "2026-10-18T08:15:00Z"),
            (62, 1, 0, 140, 268, 0, 2, 160, 0, 3.6, 2, 1, 88.2, "High", "2026-10-18T08:45:00Z"),
            (48, 0, 2, 130, 275, 0, 0, 139, 0, 0.2, 1, 0, 22.1, "Low", "2026-10-18T09:12:00Z"),
            (58, 1, 0, 150, 270, 0, 2, 111, 1, 0.8, 1, 1, 74.6, "Elevated", "2026-10-18T09:30:00Z"),
            (45, 0, 1, 128, 204, 0, 0, 172, 0, 0.0, 0, 0, 12.4, "Low", "2026-10-18T10:05:00Z"),
            (60, 1, 0, 130, 206, 0, 2, 132, 1, 2.4, 1, 1, 81.3, "High", "2026-10-18T10:45:00Z"),
            (52, 1, 2, 172, 199, 1, 0, 162, 0, 0.5, 0, 0, 35.8, "Moderate", "2026-10-18T11:10:00Z"),
            (65, 0, 0, 155, 269, 0, 0, 148, 0, 0.8, 1, 0, 31.0, "Moderate", "2026-10-18T11:40:00Z"),
            (56, 1, 1, 120, 236, 0, 0, 178, 0, 0.8, 0, 0, 15.2, "Low", "2026-10-18T12:15:00Z"),
            (59, 1, 0, 140, 221, 0, 0, 164, 1, 0.0, 1, 1, 68.7, "Elevated", "2026-10-18T13:00:00Z"),
            (42, 1, 1, 120, 295, 0, 0, 162, 0, 0.0, 0, 0, 14.1, "Low", "2026-10-18T13:30:00Z"),
            (67, 1, 0, 120, 229, 0, 2, 129, 1, 2.6, 1, 1, 89.5, "High", "2026-10-18T14:10:00Z"),
            (57, 0, 3, 140, 241, 0, 0, 123, 1, 0.2, 1, 1, 55.4, "Moderate", "2026-10-18T14:45:00Z"),
            (51, 1, 2, 110, 175, 0, 0, 123, 0, 0.6, 1, 0, 25.0, "Low", "2026-10-18T15:20:00Z"),
            (63, 0, 0, 150, 407, 0, 2, 154, 0, 4.0, 1, 1, 92.4, "High", "2026-10-18T15:55:00Z"),
            (49, 1, 1, 130, 266, 0, 0, 171, 0, 0.6, 0, 0, 18.0, "Low", "2026-10-18T16:30:00Z"),
            (55, 1, 0, 140, 217, 0, 0, 111, 1, 5.6, 2, 1, 96.1, "High", "2026-10-18T17:05:00Z"),
            (43, 1, 0, 120, 177, 0, 2, 120, 1, 2.5, 1, 1, 78.9, "Elevated", "2026-10-18T17:40:00Z"),
            (58, 0, 0, 100, 248, 0, 2, 122, 0, 1.0, 1, 0, 32.5, "Moderate", "2026-10-18T18:15:00Z"),
            (61, 1, 0, 138, 166, 0, 2, 125, 1, 3.6, 1, 1, 87.3, "High", "2026-10-18T18:50:00Z"),
            (50, 1, 2, 140, 233, 0, 0, 163, 0, 0.6, 1, 0, 21.8, "Low", "2026-10-18T19:20:00Z"),
            (64, 1, 0, 128, 263, 0, 0, 105, 1, 0.2, 1, 1, 71.4, "Elevated", "2026-10-18T19:55:00Z"),
            (41, 0, 1, 126, 306, 0, 0, 163, 0, 0.0, 0, 0, 9.8, "Low", "2026-10-18T20:25:00Z"),
            (66, 0, 2, 146, 278, 0, 2, 152, 0, 0.0, 1, 0, 28.3, "Low", "2026-10-18T21:00:00Z"),
            (57, 1, 0, 130, 131, 0, 0, 115, 1, 1.2, 1, 1, 77.0, "Elevated", "2026-10-18T21:30:00Z")
        ]
        cursor.executemany("""
            INSERT INTO patient_assessments 
            (age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, prediction, risk_probability, risk_tier, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_data)
        conn.commit()
    conn.close()

def log_assessment(age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, prediction, risk_probability, risk_tier):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    now_utc = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO patient_assessments 
        (age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, prediction, risk_probability, risk_tier, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (age, sex, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, max_hr, exercise_angina, oldpeak, st_slope, prediction, risk_probability, risk_tier, now_utc))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_recent_assessments(limit=25):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM patient_assessments ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_stats():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patient_assessments")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patient_assessments WHERE prediction = 1")
    disease_cases = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patient_assessments WHERE prediction = 0")
    healthy_cases = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(risk_probability), AVG(age), AVG(cholesterol), AVG(resting_bp) FROM patient_assessments")
    row = cursor.fetchone()
    avg_risk = round(row[0] or 0.0, 1)
    avg_age = round(row[1] or 0.0, 1)
    avg_chol = round(row[2] or 0.0, 1)
    avg_bp = round(row[3] or 0.0, 1)

    conn.close()
    return {
        "status": "connected",
        "total_assessments": total,
        "disease_cases": disease_cases,
        "healthy_cases": healthy_cases,
        "disease_percentage": round((disease_cases / total * 100) if total > 0 else 0.0, 1),
        "average_risk_probability": avg_risk,
        "average_patient_age": avg_age,
        "average_cholesterol": avg_chol,
        "average_resting_bp": avg_bp
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print("Stats:", get_stats())
