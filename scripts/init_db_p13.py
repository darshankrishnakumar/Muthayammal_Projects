import os
import sqlite3
import random
from datetime import datetime, timedelta

def init_db():
    base_dir = "/Users/eash/Documents/antigravity/excited-borg/project_13_crime_prediction_forecasting/source_code/data"
    os.makedirs(base_dir, exist_ok=True)
    db_path = os.path.join(base_dir, "crime_incident.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS crime_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            district TEXT NOT NULL,
            location_type TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            historical_density REAL NOT NULL,
            risk_score REAL NOT NULL,
            risk_category TEXT NOT NULL,
            primary_type TEXT NOT NULL,
            arrest_made INTEGER NOT NULL,
            patrol_dispatched INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patrol_dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispatch_id TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            unit_callsign TEXT NOT NULL,
            assigned_district TEXT NOT NULL,
            priority_level TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            eta_minutes INTEGER NOT NULL,
            status TEXT DEFAULT 'EN_ROUTE'
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_incident_time ON crime_incidents(timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incident_district ON crime_incidents(district)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_incident_risk ON crime_incidents(risk_category)")

    # Seed 30 recent historical incidents
    districts = ["Central Downtown", "North Waterfront", "South Industrial", "Westside Residential", "East Commercial", "Uptown Arts", "Harbor District", "Tech Corridor"]
    location_types = ["Street / Sidewalk", "Commercial Store / Mall", "Residential Apartment", "Transit Hub / Station", "Parking Garage", "Nightclub / Bar"]
    crimes = ["THEFT", "BATTERY", "BURGLARY", "ROBBERY", "NARCOTICS", "ASSAULT", "VANDALISM", "WEAPONS_VIOLATION"]
    risk_cats = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    base_time = datetime.now() - timedelta(days=3)
    for i in range(30):
        t_str = (base_time + timedelta(hours=i*2, minutes=random.randint(0, 45))).strftime("%Y-%m-%d %H:%M:%S")
        inc_id = f"CR-DISP-2026-{1001+i}"
        dist = random.choice(districts)
        loc = random.choice(location_types)
        risk = random.choice(risk_cats)
        score = random.uniform(0.75, 0.96) if risk == "CRITICAL" else (random.uniform(0.50, 0.74) if risk == "HIGH" else random.uniform(0.15, 0.49))
        crime = random.choice(crimes)
        arr = 1 if random.random() > 0.55 else 0
        disp = 1 if risk in ["HIGH", "CRITICAL"] else 0

        cur.execute("""
            INSERT OR IGNORE INTO crime_incidents (
                incident_id, timestamp, district, location_type, latitude, longitude,
                historical_density, risk_score, risk_category, primary_type, arrest_made, patrol_dispatched
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc_id, t_str, dist, loc,
            round(41.8781 + random.gauss(0, 0.03), 5),
            round(-87.6298 + random.gauss(0, 0.03), 5),
            round(random.uniform(2.5, 9.5), 1),
            round(score, 4), risk, crime, arr, disp
        ))

    # Seed 10 patrol dispatches
    units = ["ALPHA-12", "BRAVO-04", "CHARLIE-09", "DELTA-15", "ECHO-02", "FOXTROT-07", "SIERRA-11", "TANGO-05", "VICTOR-08", "ZULU-01"]
    for i in range(10):
        disp_id = f"DISP-UNIT-{5001+i}"
        t_str = (datetime.now() - timedelta(hours=i*3, minutes=random.randint(5, 40))).strftime("%Y-%m-%d %H:%M:%S")
        unit = units[i]
        dist = random.choice(districts)
        prio = random.choice(["URGENT - CODE 3", "HIGH - CODE 2", "ROUTINE PATROL"])
        crime = random.choice(crimes)
        eta = random.randint(2, 9)
        stat = random.choice(["COMPLETED", "ON_SCENE", "EN_ROUTE"])

        cur.execute("""
            INSERT OR IGNORE INTO patrol_dispatches (
                dispatch_id, timestamp, unit_callsign, assigned_district, priority_level, incident_type, eta_minutes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            disp_id, t_str, unit, dist, prio, crime, eta, stat
        ))

    conn.commit()
    conn.close()
    print(f"Database initialized and seeded at: {db_path}")

if __name__ == "__main__":
    init_db()
