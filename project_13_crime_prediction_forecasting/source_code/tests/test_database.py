import os
import sys
import sqlite3
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import get_db, DB_PATH

def test_database_file_exists():
    assert os.path.exists(DB_PATH)

def test_database_tables():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        assert "crime_incidents" in tables
        assert "patrol_dispatches" in tables

def test_insert_and_query_incident():
    with get_db() as conn:
        cur = conn.cursor()
        test_id = f"TEST-INC-{os.getpid()}"
        cur.execute("""
            INSERT INTO crime_incidents (
                incident_id, timestamp, district, location_type, latitude, longitude,
                historical_density, risk_score, risk_category, primary_type, arrest_made, patrol_dispatched
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_id, "2026-10-19 12:00:00", "Central Downtown", "Street / Sidewalk",
            41.88, -87.63, 7.5, 0.85, "HIGH", "THEFT", 0, 1
        ))
        conn.commit()

        cur.execute("SELECT incident_id, risk_category FROM crime_incidents WHERE incident_id = ?", (test_id,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == test_id
        assert row[1] == "HIGH"

def test_insert_and_query_dispatch():
    with get_db() as conn:
        cur = conn.cursor()
        test_disp_id = f"TEST-DISP-{os.getpid()}"
        cur.execute("""
            INSERT INTO patrol_dispatches (
                dispatch_id, timestamp, unit_callsign, assigned_district, priority_level, incident_type, eta_minutes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_disp_id, "2026-10-19 12:05:00", "UNIT-TEST", "Harbor District", "CODE 2", "BURGLARY", 4, "EN_ROUTE"
        ))
        conn.commit()

        cur.execute("SELECT dispatch_id, unit_callsign FROM patrol_dispatches WHERE dispatch_id = ?", (test_disp_id,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == test_disp_id
        assert row[1] == "UNIT-TEST"

def test_database_indexes():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [r[0] for r in cur.fetchall()]
        assert any("incident" in idx for idx in indexes)
