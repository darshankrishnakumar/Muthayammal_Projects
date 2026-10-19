import os
import sqlite3
import json
import hashlib
from datetime import datetime, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "driver_safety.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS driver_profiles (
        driver_id TEXT PRIMARY KEY,
        driver_name TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        route_corridor TEXT NOT NULL,
        shift_type TEXT NOT NULL,
        license_no TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        baseline_ear REAL NOT NULL DEFAULT 0.35,
        baseline_mar REAL NOT NULL DEFAULT 0.18,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS fatigue_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telemetry_id TEXT UNIQUE NOT NULL,
        driver_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        ear REAL NOT NULL,
        mar REAL NOT NULL,
        blink_duration_ms REAL NOT NULL,
        blink_frequency_cpm REAL NOT NULL,
        head_pitch_deg REAL NOT NULL,
        head_yaw_deg REAL NOT NULL,
        head_roll_deg REAL NOT NULL,
        perclos_pct REAL NOT NULL,
        drowsiness_state TEXT NOT NULL,
        vigilance_score REAL NOT NULL,
        microsleep_risk REAL NOT NULL,
        FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id)
    );

    CREATE TABLE IF NOT EXISTS drowsiness_alerts (
        alert_id TEXT PRIMARY KEY,
        driver_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        severity TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        ear REAL NOT NULL,
        mar REAL NOT NULL,
        vigilance_score REAL NOT NULL,
        recommended_action TEXT NOT NULL,
        driver_acknowledged INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id)
    );

    CREATE TABLE IF NOT EXISTS trip_sessions (
        trip_id TEXT PRIMARY KEY,
        driver_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        duration_minutes REAL NOT NULL,
        distance_km REAL NOT NULL,
        avg_vigilance REAL NOT NULL,
        alert_count INTEGER NOT NULL,
        safety_grade TEXT NOT NULL,
        FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id)
    );

    CREATE TABLE IF NOT EXISTS audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        details_json TEXT NOT NULL,
        verification_hash TEXT NOT NULL
    );
    """)

    # Seed baseline drivers if empty
    cursor.execute("SELECT COUNT(*) FROM driver_profiles")
    if cursor.fetchone()[0] == 0:
        drivers = [
            ("DRV-801", "Marcus Vance", "Freightliner Cascadia (Class 8 Semi)", "I-80 Interstate Cross-Country", "Nocturnal Long-Haul", "CDL-A-882194", "ACTIVE", 0.36, 0.16, datetime.now(timezone.utc).isoformat()),
            ("DRV-802", "Elena Rostova", "New Flyer Xcelsior (Transit Bus)", "Metro Route 44 Express", "Morning Commuter Peak", "CDL-B-440129", "ACTIVE", 0.35, 0.17, datetime.now(timezone.utc).isoformat()),
            ("DRV-803", "Devon Miller", "Toyota Camry Hybrid", "Metropolitan Rideshare Corridor", "Evening Congestion", "DL-C-993810", "ACTIVE", 0.34, 0.18, datetime.now(timezone.utc).isoformat()),
            ("DRV-804", "Kavita Rao", "Peterbilt 579 Cryogenic Tanker", "Gulf Coast Chemical Transit", "Graveyard Hazardous Cargo", "CDL-A-HAZ-771", "ACTIVE", 0.36, 0.15, datetime.now(timezone.utc).isoformat()),
            ("DRV-805", "Lucas Silva", "Mercedes-Benz Sprinter Cargo", "Urban Last-Mile Logistics", "Afternoon Multidrop", "DL-C-239011", "ACTIVE", 0.35, 0.18, datetime.now(timezone.utc).isoformat())
        ]
        cursor.executemany("""
            INSERT INTO driver_profiles (driver_id, driver_name, vehicle_type, route_corridor, shift_type, license_no, status, baseline_ear, baseline_mar, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, drivers)

        # Seed initial trips
        trips = [
            ("TRIP-101", "DRV-801", "2026-10-19T18:00:00Z", 240.0, 310.5, 88.5, 1, "A"),
            ("TRIP-102", "DRV-802", "2026-10-19T06:00:00Z", 180.0, 85.0, 92.4, 0, "A+"),
            ("TRIP-103", "DRV-803", "2026-10-19T17:30:00Z", 210.0, 140.2, 79.1, 3, "B"),
            ("TRIP-104", "DRV-804", "2026-10-19T22:00:00Z", 300.0, 380.0, 94.0, 0, "A+"),
            ("TRIP-105", "DRV-805", "2026-10-19T12:00:00Z", 195.0, 95.8, 83.2, 2, "B+")
        ]
        cursor.executemany("""
            INSERT INTO trip_sessions (trip_id, driver_id, start_time, duration_minutes, distance_km, avg_vigilance, alert_count, safety_grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, trips)

        conn.commit()
        record_audit_log(cursor, "SYSTEM_INIT", "SYSTEM", {"message": "Initialized driver safety database with 5 profiles and baseline trips."})
        conn.commit()

    conn.close()

def record_audit_log(cursor, action, actor, details_dict):
    now_str = datetime.now(timezone.utc).isoformat()
    raw_json = json.dumps(details_dict, sort_keys=True)
    hash_payload = f"{now_str}:{action}:{actor}:{raw_json}".encode("utf-8")
    sha256 = hashlib.sha256(hash_payload).hexdigest()
    cursor.execute("""
        INSERT INTO audit_ledger (timestamp, action, actor, details_json, verification_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (now_str, action, actor, raw_json, sha256))

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
