import sqlite3
import os
import hashlib
import json
from datetime import datetime, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "traffic_enforcement.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_intersections (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        zone TEXT NOT NULL,
        speed_limit REAL NOT NULL,
        active_cameras INTEGER NOT NULL,
        status TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS surveillance_cameras (
        camera_id TEXT PRIMARY KEY,
        intersection_id TEXT NOT NULL,
        orientation TEXT NOT NULL,
        resolution TEXT NOT NULL,
        optical_mode TEXT NOT NULL,
        last_calibration TEXT NOT NULL,
        FOREIGN KEY (intersection_id) REFERENCES traffic_intersections(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS detected_vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT NOT NULL,
        license_plate TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        intersection_id TEXT NOT NULL,
        camera_id TEXT NOT NULL,
        speed_kmh REAL NOT NULL,
        speed_limit REAL NOT NULL,
        traffic_light_state INTEGER NOT NULL,
        distance_to_stop_line_m REAL NOT NULL,
        lane_offset_m REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (intersection_id) REFERENCES traffic_intersections(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT NOT NULL,
        license_plate TEXT NOT NULL,
        violation_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        severity_index REAL NOT NULL,
        collision_risk REAL NOT NULL,
        fine_inr INTEGER NOT NULL,
        location TEXT NOT NULL,
        camera_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ISSUED'
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS e_challan_records (
        challan_id TEXT PRIMARY KEY,
        violation_id INTEGER NOT NULL,
        license_plate TEXT NOT NULL,
        violation_type TEXT NOT NULL,
        fine_amount INTEGER NOT NULL,
        mva_section TEXT NOT NULL,
        issue_timestamp TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'PENDING',
        evidence_hash TEXT NOT NULL,
        FOREIGN KEY (violation_id) REFERENCES traffic_violations(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        record_hash TEXT NOT NULL
    );
    """)

    # Populate default intersections if empty
    cur.execute("SELECT COUNT(*) FROM traffic_intersections")
    if cur.fetchone()[0] == 0:
        intersections = [
            ("INT-01", "Central Plaza Junction", "Urban Commercial", 50.0, 4, "ACTIVE"),
            ("INT-02", "North Highway Corridor", "Arterial Highway", 80.0, 4, "ACTIVE"),
            ("INT-03", "Ring Road Flyover", "Express Ring Road", 60.0, 4, "ACTIVE"),
            ("INT-04", "Tech Park Junction", "IT Corridor Boulevard", 50.0, 4, "ACTIVE")
        ]
        cur.executemany("INSERT INTO traffic_intersections VALUES (?, ?, ?, ?, ?, ?)", intersections)

        cameras = [
            ("CAM-101", "INT-01", "Northbound Entry", "4K UltraHD / 60 FPS", "Day/Night Auto IR", datetime.utcnow().isoformat()),
            ("CAM-102", "INT-01", "Southbound Exit", "4K UltraHD / 60 FPS", "Day/Night Auto IR", datetime.utcnow().isoformat()),
            ("CAM-103", "INT-02", "Highway Eastbound Lane 1-2", "4K High Speed ANPR", "Starlight Optical", datetime.utcnow().isoformat()),
            ("CAM-104", "INT-02", "Highway Westbound Lane 3-4", "4K High Speed ANPR", "Starlight Optical", datetime.utcnow().isoformat()),
            ("CAM-105", "INT-03", "Flyover Ramp Merge", "1080p PTZ Radar-Linked", "Infrared Thermal", datetime.utcnow().isoformat()),
            ("CAM-106", "INT-04", "Boulevard Pedestrian Crossing", "4K UltraHD / 60 FPS", "Day/Night Auto IR", datetime.utcnow().isoformat())
        ]
        cur.executemany("INSERT INTO surveillance_cameras VALUES (?, ?, ?, ?, ?, ?)", cameras)

        # Seed Genesis Block in audit ledger
        genesis_prev = "0" * 64
        genesis_str = f"GENESIS|SYSTEM_INIT|{datetime.utcnow().isoformat()}|{genesis_prev}"
        genesis_hash = hashlib.sha256(genesis_str.encode("utf-8")).hexdigest()
        cur.execute(
            "INSERT INTO audit_ledger (timestamp, action, details, prev_hash, record_hash) VALUES (?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), "GENESIS_INITIALIZATION", "Traffic safety enforcement database initialized in WAL mode", genesis_prev, genesis_hash)
        )

    conn.commit()
    conn.close()

def log_audit_entry(action, details):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT record_hash FROM audit_ledger ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    prev_hash = row["record_hash"] if row else "0" * 64

    ts = datetime.now(timezone.utc).isoformat()
    raw_str = f"{action}|{details}|{ts}|{prev_hash}"
    record_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    cur.execute(
        "INSERT INTO audit_ledger (timestamp, action, details, prev_hash, record_hash) VALUES (?, ?, ?, ?, ?)",
        (ts, action, details, prev_hash, record_hash)
    )
    conn.commit()
    conn.close()
    return record_hash

if __name__ == "__main__":
    init_db()
    print("Traffic enforcement database initialized successfully.")
