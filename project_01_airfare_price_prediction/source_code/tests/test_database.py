import os
import sys
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.database import init_db, log_prediction, get_recent_predictions, get_analytics

def test_database_initialization_and_logging():
    init_db()
    rec_id = log_prediction(
        airline="SpiceJet",
        source="Kolkata",
        destination="Banglore",
        journey_date="2026-12-01",
        dep_time="07:00",
        arrival_time="09:40",
        duration_mins=160,
        total_stops=0,
        predicted_price_lstm=3450.0,
        predicted_price_rf=3600.0,
        recommended_fare=3510.0,
        confidence_score=0.91
    )
    assert rec_id > 0, "Record ID should be auto-incremented positive integer"

def test_database_query_recent():
    records = get_recent_predictions(limit=10)
    assert isinstance(records, list)
    assert len(records) > 0
    first = records[0]
    assert "airline" in first
    assert "recommended_fare" in first

def test_database_analytics():
    stats = get_analytics()
    assert "total_predictions" in stats
    assert stats["total_predictions"] >= 1
    assert "airline_statistics" in stats
    assert len(stats["airline_statistics"]) >= 1
