import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import database as db

def test_db_connection():
    conn = db.get_connection()
    assert conn is not None
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    assert cursor.fetchone()[0] == 1
    conn.close()

def test_db_init():
    db.init_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patient_assessments'")
    assert cursor.fetchone() is not None
    conn.close()

def test_log_assessment_and_retrieve():
    rec_id = db.log_assessment(
        age=52, sex=1, chest_pain_type=0, resting_bp=135, cholesterol=240,
        fasting_bs=0, resting_ecg=1, max_hr=145, exercise_angina=1, oldpeak=1.8,
        st_slope=1, prediction=1, risk_probability=78.2, risk_tier="Elevated"
    )
    assert rec_id is not None
    assert rec_id > 0

    records = db.get_recent_assessments(limit=5)
    assert len(records) > 0
    latest = records[0]
    assert latest["age"] == 52
    assert latest["prediction"] == 1
    assert latest["risk_tier"] == "Elevated"

def test_database_stats():
    stats = db.get_stats()
    assert stats["status"] == "connected"
    assert stats["total_assessments"] >= 25
    assert stats["average_patient_age"] > 0
    assert stats["average_cholesterol"] > 0

def test_history_limit_slicing():
    records_3 = db.get_recent_assessments(limit=3)
    assert len(records_3) == 3
