import os
import sys
import pytest

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
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_verifications'")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "news_verifications"

def test_log_verification_and_retrieve():
    rec_id = db.log_verification(
        headline_preview="Test Headline for Automated Unit Test Verification",
        classification="REAL",
        confidence=92.5,
        decision_score=1.85,
        sensationalism_score=5.0,
        speculative_score=10.0,
        objective_score=85.0,
        source_watermark_detected=False,
        pure_language_mode=True
    )
    assert rec_id > 0

    recent = db.get_recent_verifications(limit=5)
    assert len(recent) > 0
    matched = any("Test Headline for Automated Unit Test" in r["headline_preview"] for r in recent)
    assert matched is True

def test_database_stats():
    stats = db.get_stats()
    assert "total_verifications" in stats
    assert "real_news_count" in stats
    assert "fake_news_count" in stats
    assert stats["total_verifications"] > 0
    assert stats["status"] == "connected"

def test_history_limit_slicing():
    recent_3 = db.get_recent_verifications(limit=3)
    assert len(recent_3) <= 3
