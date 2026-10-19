import os
import sys
import pytest

# Ensure source_code is on path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import database as db

def test_db_connection():
    conn = db.get_connection()
    assert conn is not None
    conn.close()

def test_db_init():
    db.init_db()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='egg_predictions'")
        table = cursor.fetchone()
        assert table is not None
        assert table[0] == "egg_predictions"

def test_save_and_retrieve_prediction():
    rec_id = db.save_prediction_record(
        specimen_name="Test_Egg_Unit_Specimen",
        predicted_sex="Female (Hen)",
        symbol="♀",
        confidence=89.5,
        female_prob=89.5,
        male_prob=10.5,
        shape_index=81.2,
        elongation=1.23,
        apex_sharpness=0.03,
        recommendation="Test recommendation for unit test.",
        source="test_runner"
    )
    assert rec_id > 0

    recent = db.get_recent_history(limit=5)
    assert len(recent) > 0
    matched = any(r["specimen_name"] == "Test_Egg_Unit_Specimen" for r in recent)
    assert matched is True

def test_database_stats():
    stats = db.get_database_stats()
    assert "total_records" in stats
    assert "female_count" in stats
    assert "male_count" in stats
    assert stats["total_records"] > 0
    assert stats["status"] == "connected"

def test_history_limit():
    recent_2 = db.get_recent_history(limit=2)
    assert len(recent_2) <= 2
