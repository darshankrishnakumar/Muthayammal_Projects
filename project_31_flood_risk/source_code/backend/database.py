"""
Urban Flood Risk Prediction & Early Warning System
Relational SQLite Database Layer with ACID Persistence & WAL Mode
"""

import os
import sqlite3
import json
from datetime import datetime, timezone, timedelta
import random

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "flood_risk.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS river_basins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        basin_id TEXT UNIQUE NOT NULL,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        dem_elevation_m REAL NOT NULL,
        river_threshold_m REAL NOT NULL,
        drainage_capacity TEXT NOT NULL,
        drainage_score REAL NOT NULL,
        population_density INTEGER NOT NULL,
        icon TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS hydrological_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        basin_id TEXT NOT NULL,
        rainfall_mm REAL NOT NULL,
        river_stage_m REAL NOT NULL,
        river_threshold_m REAL NOT NULL,
        soil_moisture REAL NOT NULL,
        storm_surge_m REAL NOT NULL,
        crest_exceedance_ratio REAL NOT NULL,
        recorded_at TIMESTAMP NOT NULL,
        FOREIGN KEY (basin_id) REFERENCES river_basins(basin_id)
    );

    CREATE TABLE IF NOT EXISTS flood_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        zone TEXT NOT NULL,
        zone_type TEXT NOT NULL,
        icon TEXT NOT NULL,
        elevation_m REAL NOT NULL,
        risk_score REAL NOT NULL,
        risk_pct REAL NOT NULL,
        alert_level TEXT NOT NULL,
        alert_title TEXT NOT NULL,
        emergency_protocol TEXT NOT NULL,
        color TEXT NOT NULL,
        inundation_depth_m REAL NOT NULL,
        lead_time_hours REAL NOT NULL,
        rainfall_mm REAL NOT NULL,
        river_stage_m REAL NOT NULL,
        river_threshold_m REAL NOT NULL,
        soil_saturation_pct REAL NOT NULL,
        storm_surge_m REAL NOT NULL,
        population_at_risk INTEGER NOT NULL,
        model TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS emergency_dispatches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        zone TEXT NOT NULL,
        alert_level TEXT NOT NULL,
        dispatch_team TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        status TEXT NOT NULL,
        protocol TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_pred_timestamp ON flood_predictions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_pred_zone ON flood_predictions(zone);
    CREATE INDEX IF NOT EXISTS idx_pred_level ON flood_predictions(alert_level);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """)

    conn.commit()
    conn.close()

def log_audit(event_type, details, severity="INFO"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO audit_log (timestamp, event_type, details, severity) VALUES (?, ?, ?, ?)",
            (now, event_type, details, severity)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging audit: {e}")

def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM river_basins")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    basins_data = [
        ('BASIN-01', 'Riverside Embankment District', 'River Basin', 6.5, 6.0, 'Medium', 2.0, 18500, '🌊'),
        ('BASIN-02', 'Bay Coastal Lowlands', 'Tidal Estuary', 3.2, 4.5, 'Low', 1.0, 24000, '🏖️'),
        ('BASIN-03', 'Downtown Metropolitan Core', 'Urban Concrete Basin', 14.0, 8.5, 'High', 3.0, 42000, '🏙️'),
        ('BASIN-04', 'Industrial Valley Sector', 'Alluvial Flood Plain', 11.0, 7.0, 'Medium', 2.0, 8500, '🏭'),
        ('BASIN-05', 'Upland Ridge Buffer', 'Highland Plateau', 85.0, 14.0, 'Optimal', 4.0, 5200, '⛰️')
    ]

    cursor.executemany("""
    INSERT INTO river_basins (basin_id, name, type, dem_elevation_m, river_threshold_m, drainage_capacity, drainage_score, population_density, icon)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, basins_data)

    # Seed 50 historical telemetry readings
    now = datetime.now(timezone.utc)
    readings = []
    for b in basins_data:
        bid = b[0]
        thresh = b[4]
        for h in range(10, 0, -1):
            t = (now - timedelta(hours=h * 2)).isoformat()
            rain = round(random.uniform(5.0, 120.0), 1)
            stage = round(random.uniform(thresh * 0.4, thresh * 1.1), 2)
            soil = round(random.uniform(0.35, 0.85), 3)
            surge = round(random.uniform(0.1, 1.2), 2)
            crest_ratio = round(stage / thresh, 3)
            readings.append((bid, rain, stage, thresh, soil, surge, crest_ratio, t))

    cursor.executemany("""
    INSERT INTO hydrological_readings (basin_id, rainfall_mm, river_stage_m, river_threshold_m, soil_moisture, storm_surge_m, crest_exceedance_ratio, recorded_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, readings)

    # Seed initial predictions
    seed_preds = [
        (
            (now - timedelta(minutes=45)).isoformat(),
            'Bay Coastal Lowlands', 'Tidal Estuary', '🏖️', 3.2, 0.86, 86.0,
            'CRITICAL', '🔴 RED ALERT: Severe Inundation Imminent',
            'Mandatory evacuation of ground floors. Deploy flood gates & high-capacity pumps.',
            '#ef4444', 1.45, 2.5, 215.0, 5.8, 4.5, 94.0, 2.3, 20640,
            'PyTorch Residual FloodNet + Inundation Regressor'
        ),
        (
            (now - timedelta(minutes=90)).isoformat(),
            'Riverside Embankment District', 'River Basin', '🌊', 6.5, 0.68, 68.0,
            'WARNING', '🟠 ORANGE WARNING: Flash Flood Watch',
            'Prepare emergency relief teams, move vehicles to high ground, seal storm drains.',
            '#f97316', 0.48, 5.0, 140.0, 6.4, 6.0, 82.0, 0.8, 12580,
            'PyTorch Residual FloodNet + Inundation Regressor'
        ),
        (
            (now - timedelta(minutes=130)).isoformat(),
            'Downtown Metropolitan Core', 'Urban Concrete Basin', '🏙️', 14.0, 0.42, 42.0,
            'ADVISORY', '🟡 YELLOW ADVISORY: Elevated Water Level',
            'Monitor upstream river gauges and clear municipal drainage grates.',
            '#eab308', 0.0, 11.0, 75.0, 6.8, 8.5, 65.0, 0.4, 17640,
            'PyTorch Residual FloodNet + Inundation Regressor'
        ),
        (
            (now - timedelta(minutes=180)).isoformat(),
            'Industrial Valley Sector', 'Alluvial Flood Plain', '🏭', 11.0, 0.38, 38.0,
            'ADVISORY', '🟡 YELLOW ADVISORY: Elevated Water Level',
            'Monitor upstream river gauges and clear municipal drainage grates.',
            '#eab308', 0.0, 12.5, 62.0, 5.5, 7.0, 68.0, 0.3, 3230,
            'PyTorch Residual FloodNet + Inundation Regressor'
        ),
        (
            (now - timedelta(minutes=240)).isoformat(),
            'Upland Ridge Buffer', 'Highland Plateau', '⛰️', 85.0, 0.12, 12.0,
            'NORMAL', '🟢 GREEN: Hydrological Equilibrium',
            'All reservoirs and runoff channels operating within normal safety limits.',
            '#10b981', 0.0, 22.0, 28.0, 4.2, 14.0, 38.0, 0.1, 0,
            'PyTorch Residual FloodNet + Inundation Regressor'
        )
    ]

    cursor.executemany("""
    INSERT INTO flood_predictions (
        timestamp, zone, zone_type, icon, elevation_m, risk_score, risk_pct,
        alert_level, alert_title, emergency_protocol, color, inundation_depth_m,
        lead_time_hours, rainfall_mm, river_stage_m, river_threshold_m,
        soil_saturation_pct, storm_surge_m, population_at_risk, model
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seed_preds)

    # Seed initial emergency dispatch
    cursor.execute("""
    INSERT INTO emergency_dispatches (timestamp, zone, alert_level, dispatch_team, action_taken, status, protocol)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        (now - timedelta(minutes=40)).isoformat(),
        'Bay Coastal Lowlands',
        'CRITICAL',
        'Coastal Evacuation Unit Alpha',
        'Barrier deployment and evacuation sirens triggered in sectors 1-4',
        'DEPLOYED',
        'Mandatory ground floor evacuation initiated.'
    ))

    conn.commit()
    conn.close()
    log_audit("DATABASE_INIT", "Database initialized and seeded with river basins and hydrological telemetry", "INFO")

def save_prediction(data):
    conn = get_connection()
    cursor = conn.cursor()
    tel = data.get('telemetry', {})

    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO flood_predictions (
        timestamp, zone, zone_type, icon, elevation_m, risk_score, risk_pct,
        alert_level, alert_title, emergency_protocol, color, inundation_depth_m,
        lead_time_hours, rainfall_mm, river_stage_m, river_threshold_m,
        soil_saturation_pct, storm_surge_m, population_at_risk, model
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now,
        data.get('zone'),
        data.get('zone_type'),
        data.get('icon', '🌊'),
        data.get('elevation_m', 0.0),
        data.get('risk_score', 0.0),
        data.get('risk_pct', 0.0),
        data.get('alert_level', 'NORMAL'),
        data.get('alert_title', ''),
        data.get('emergency_protocol', ''),
        data.get('color', '#10b981'),
        data.get('inundation_depth_m', 0.0),
        data.get('lead_time_hours', 24.0),
        tel.get('rainfall_mm', 0.0),
        tel.get('river_stage_m', 0.0),
        tel.get('river_threshold_m', 0.0),
        tel.get('soil_saturation_pct', 0.0),
        tel.get('storm_surge_m', 0.0),
        tel.get('population_at_risk', 0),
        data.get('model', 'PyTorch Residual FloodNet')
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(
        "PREDICTION_GENERATED",
        f"Zone: {data.get('zone')} | Level: {data.get('alert_level')} | Depth: {data.get('inundation_depth_m')}m",
        "WARNING" if data.get('alert_level') in ['WARNING', 'CRITICAL'] else "INFO"
    )
    return new_id

def get_zones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM river_basins ORDER BY dem_elevation_m ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_history(limit=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flood_predictions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d['telemetry'] = {
            'rainfall_mm': d['rainfall_mm'],
            'river_stage_m': d['river_stage_m'],
            'river_threshold_m': d['river_threshold_m'],
            'soil_saturation_pct': d['soil_saturation_pct'],
            'storm_surge_m': d['storm_surge_m'],
            'population_at_risk': d['population_at_risk']
        }
        result.append(d)
    return result

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM flood_predictions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM flood_predictions WHERE alert_level = 'CRITICAL'")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM flood_predictions WHERE alert_level = 'WARNING'")
    warning = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(population_at_risk) FROM (SELECT population_at_risk FROM flood_predictions ORDER BY id DESC LIMIT 5)")
    pop_sum = cursor.fetchone()[0] or 0

    conn.close()
    return {
        'total_assessments': total,
        'critical_zones': critical,
        'warning_zones': warning,
        'population_at_risk_sum': pop_sum,
        'system_readiness_pct': 99.4
    }

def create_dispatch(zone, alert_level, dispatch_team, action_taken, status, protocol):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO emergency_dispatches (timestamp, zone, alert_level, dispatch_team, action_taken, status, protocol)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now, zone, alert_level, dispatch_team, action_taken, status, protocol))
    did = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit("EMERGENCY_DISPATCH", f"Dispatched {dispatch_team} to {zone} for {alert_level}", "CRITICAL")
    return did

def get_dispatches(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_dispatches ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_audit_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == '__main__':
    seed_database()
    print("Database initialization & seeding complete. Total records:", get_stats())
