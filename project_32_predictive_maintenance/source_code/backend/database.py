"""
Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data and Deep Learning
Relational SQLite Database Layer with ACID Persistence & WAL Mode
"""

import os
import sqlite3
import json
from datetime import datetime, timezone, timedelta
import random

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "predictive_maintenance.db"))

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
    CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        nominal_rpm INTEGER NOT NULL,
        nominal_temp REAL NOT NULL,
        nominal_vib REAL NOT NULL,
        nominal_press REAL NOT NULL,
        nominal_oil REAL NOT NULL,
        nominal_ae REAL NOT NULL,
        icon TEXT NOT NULL,
        criticality TEXT NOT NULL,
        operational_status TEXT DEFAULT 'ONLINE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sensor_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_name TEXT NOT NULL,
        temperature_c REAL NOT NULL,
        vibration_mm_s REAL NOT NULL,
        pressure_bar REAL NOT NULL,
        rpm REAL NOT NULL,
        oil_viscosity_cst REAL NOT NULL,
        acoustic_emission_db REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        FOREIGN KEY (machine_name) REFERENCES machines(name)
    );

    CREATE TABLE IF NOT EXISTS diagnostic_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        machine TEXT NOT NULL,
        machine_type TEXT NOT NULL,
        criticality TEXT NOT NULL,
        icon TEXT NOT NULL,
        health_score REAL NOT NULL,
        fault_mode TEXT NOT NULL,
        urgency TEXT NOT NULL,
        action_required TEXT NOT NULL,
        color TEXT NOT NULL,
        rul_hours REAL NOT NULL,
        rul_days REAL NOT NULL,
        temperature_c REAL NOT NULL,
        vibration_mm_s REAL NOT NULL,
        pressure_bar REAL NOT NULL,
        rpm REAL NOT NULL,
        oil_viscosity_cst REAL NOT NULL,
        acoustic_emission_db REAL NOT NULL,
        fft_harmonics_json TEXT NOT NULL,
        model TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS maintenance_work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        machine TEXT NOT NULL,
        fault_mode TEXT NOT NULL,
        urgency TEXT NOT NULL,
        work_order_code TEXT UNIQUE NOT NULL,
        technician TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        status TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_diag_timestamp ON diagnostic_inspections(timestamp);
    CREATE INDEX IF NOT EXISTS idx_diag_machine ON diagnostic_inspections(machine);
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

    cursor.execute("SELECT COUNT(*) FROM machines")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    machines_data = [
        ('Screw Compressor A-101', 'Rotary Screw Compressor', 2980, 72.0, 1.1, 8.5, 55.0, 62.0, '⚙️', 'High', 'ONLINE'),
        ('Centrifugal Pump B-204', 'Slurry Circulation Pump', 1480, 64.0, 0.8, 14.2, 48.0, 58.0, '🔄', 'Critical', 'ONLINE'),
        ('Induction Motor C-302', '3-Phase 350kW Motor', 1780, 68.0, 0.6, 1.0, 45.0, 54.0, '⚡', 'Medium', 'ONLINE'),
        ('Gas Turbine Generator D-401', 'Co-Gen Gas Turbine', 5400, 118.0, 1.4, 22.0, 65.0, 78.0, '🔥', 'Critical', 'ONLINE'),
        ('Conveyor Drive Unit E-505', 'Heavy Ore Conveyor Drive', 720, 52.0, 1.8, 3.5, 68.0, 60.0, '🏗️', 'Low', 'ONLINE')
    ]

    cursor.executemany("""
    INSERT INTO machines (name, type, nominal_rpm, nominal_temp, nominal_vib, nominal_press, nominal_oil, nominal_ae, icon, criticality, operational_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, machines_data)

    now = datetime.now(timezone.utc)

    # Seed 50 historical sensor telemetry points
    telemetry_records = []
    for m in machines_data:
        m_name = m[0]
        nom_rpm = m[2]
        nom_temp = m[3]
        nom_vib = m[4]
        nom_press = m[5]
        nom_oil = m[6]
        nom_ae = m[7]

        for h in range(10, 0, -1):
            t = (now - timedelta(hours=h * 2)).isoformat()
            telemetry_records.append((
                m_name,
                round(nom_temp * random.uniform(0.96, 1.05), 1),
                round(nom_vib * random.uniform(0.92, 1.08), 2),
                round(nom_press * random.uniform(0.98, 1.02), 1),
                int(nom_rpm + random.uniform(-15, 15)),
                round(nom_oil * random.uniform(0.95, 1.05), 1),
                round(nom_ae * random.uniform(0.95, 1.05), 1),
                t
            ))

    cursor.executemany("""
    INSERT INTO sensor_telemetry (machine_name, temperature_c, vibration_mm_s, pressure_bar, rpm, oil_viscosity_cst, acoustic_emission_db, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, telemetry_records)

    # Seed initial inspections
    seed_inspections = [
        (
            (now - timedelta(minutes=30)).isoformat(),
            'Gas Turbine Generator D-401', 'Co-Gen Gas Turbine', 'Critical', '🔥',
            34.2, 'Outer Race Bearing Spall', 'IMMEDIATE',
            'Replace DE spherical roller bearing & align shaft', '#ef4444',
            96.0, 4.0, 142.5, 5.8, 21.4, 5320, 48.0, 102.5,
            json.dumps([1.2, 3.8, 1.5, 4.2, 0.8, 0.4, 0.2, 0.1]),
            'PyTorch Residual Health Classifier + RUL Regressor'
        ),
        (
            (now - timedelta(minutes=75)).isoformat(),
            'Centrifugal Pump B-204', 'Slurry Circulation Pump', 'Critical', '🔄',
            52.0, 'Hydraulic Cavitation Wear', 'SCHEDULED',
            'Inspect impeller vanes and suction pressure net positive head', '#f59e0b',
            240.0, 10.0, 78.4, 2.6, 10.8, 1420, 42.0, 92.0,
            json.dumps([0.6, 1.2, 0.8, 0.4, 1.8, 0.3, 0.2, 0.1]),
            'PyTorch Residual Health Classifier + RUL Regressor'
        ),
        (
            (now - timedelta(minutes=120)).isoformat(),
            'Screw Compressor A-101', 'Rotary Screw Compressor', 'High', '⚙️',
            58.5, 'Rotor Dynamic Imbalance', 'URGENT',
            'Dynamic 2-plane balancing & check balance weights', '#f97316',
            320.0, 13.3, 84.2, 3.9, 8.8, 2920, 52.0, 74.0,
            json.dumps([1.8, 2.4, 0.6, 0.2, 0.1, 0.1, 0.05, 0.05]),
            'PyTorch Residual Health Classifier + RUL Regressor'
        ),
        (
            (now - timedelta(minutes=160)).isoformat(),
            'Induction Motor C-302', '3-Phase 350kW Motor', 'Medium', '⚡',
            94.8, 'Normal Baseline', 'NONE',
            'Routine monthly lubrication', '#10b981',
            2800.0, 116.7, 69.2, 0.62, 1.02, 1782, 45.2, 54.1,
            json.dumps([0.2, 0.06, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]),
            'PyTorch Residual Health Classifier + RUL Regressor'
        ),
        (
            (now - timedelta(minutes=210)).isoformat(),
            'Conveyor Drive Unit E-505', 'Heavy Ore Conveyor Drive', 'Low', '🏗️',
            96.2, 'Normal Baseline', 'NONE',
            'Routine monthly lubrication', '#10b981',
            3200.0, 133.3, 52.4, 1.78, 3.48, 719, 67.5, 60.2,
            json.dumps([0.4, 0.1, 0.05, 0.02, 0.01, 0.01, 0.01, 0.01]),
            'PyTorch Residual Health Classifier + RUL Regressor'
        )
    ]

    cursor.executemany("""
    INSERT INTO diagnostic_inspections (
        timestamp, machine, machine_type, criticality, icon, health_score,
        fault_mode, urgency, action_required, color, rul_hours, rul_days,
        temperature_c, vibration_mm_s, pressure_bar, rpm, oil_viscosity_cst,
        acoustic_emission_db, fft_harmonics_json, model
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seed_inspections)

    # Seed initial work order
    cursor.execute("""
    INSERT INTO maintenance_work_orders (timestamp, machine, fault_mode, urgency, work_order_code, technician, action_taken, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        (now - timedelta(minutes=25)).isoformat(),
        'Gas Turbine Generator D-401',
        'Outer Race Bearing Spall',
        'IMMEDIATE',
        'WO-TURB-2026-041',
        'Senior Vibration Analyst Marcus Vance',
        'Mobilized emergency bearing replacement kit & laser alignment rig',
        'IN_PROGRESS'
    ))

    conn.commit()
    conn.close()
    log_audit("DATABASE_INIT", "Predictive maintenance database initialized and seeded with machine fleet", "INFO")

def save_inspection(data):
    conn = get_connection()
    cursor = conn.cursor()
    tel = data.get('telemetry', {})

    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO diagnostic_inspections (
        timestamp, machine, machine_type, criticality, icon, health_score,
        fault_mode, urgency, action_required, color, rul_hours, rul_days,
        temperature_c, vibration_mm_s, pressure_bar, rpm, oil_viscosity_cst,
        acoustic_emission_db, fft_harmonics_json, model
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now,
        data.get('machine'),
        data.get('machine_type'),
        data.get('criticality', 'Medium'),
        data.get('icon', '⚙️'),
        data.get('health_score', 100.0),
        data.get('fault_mode', 'Normal Baseline'),
        data.get('urgency', 'NONE'),
        data.get('action_required', ''),
        data.get('color', '#10b981'),
        data.get('rul_hours', 2000.0),
        data.get('rul_days', 83.3),
        tel.get('temperature_c', 0.0),
        tel.get('vibration_mm_s', 0.0),
        tel.get('pressure_bar', 0.0),
        tel.get('rpm', 0.0),
        tel.get('oil_viscosity_cst', 0.0),
        tel.get('acoustic_emission_db', 0.0),
        json.dumps(data.get('fft_harmonics', [])),
        data.get('model', 'PyTorch Residual Health Classifier + RUL Regressor')
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(
        "INSPECTION_RECORDED",
        f"Machine: {data.get('machine')} | Fault: {data.get('fault_mode')} | Health: {data.get('health_score')}%",
        "WARNING" if data.get('urgency') in ['URGENT', 'IMMEDIATE'] else "INFO"
    )
    return new_id

def get_machines():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_history(limit=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diagnostic_inspections ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d['telemetry'] = {
            'temperature_c': d['temperature_c'],
            'vibration_mm_s': d['vibration_mm_s'],
            'pressure_bar': d['pressure_bar'],
            'rpm': d['rpm'],
            'oil_viscosity_cst': d['oil_viscosity_cst'],
            'acoustic_emission_db': d['acoustic_emission_db']
        }
        try:
            d['fft_harmonics'] = json.loads(d['fft_harmonics_json'])
        except Exception:
            d['fft_harmonics'] = []
        result.append(d)
    return result

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM diagnostic_inspections")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnostic_inspections WHERE urgency = 'IMMEDIATE'")
    crit = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(health_score) FROM (SELECT health_score FROM diagnostic_inspections ORDER BY id DESC LIMIT 10)")
    avg_h = round(cursor.fetchone()[0] or 85.0, 1)

    cursor.execute("SELECT COUNT(*) FROM machines")
    assets = cursor.fetchone()[0]

    conn.close()
    return {
        'total_inspections': total,
        'critical_urgencies': crit,
        'avg_fleet_health_score': avg_h,
        'connected_assets': assets,
        'uptime_slas': '99.92%'
    }

def create_work_order(machine, fault_mode, urgency, work_order_code, technician, action_taken, status):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO maintenance_work_orders (timestamp, machine, fault_mode, urgency, work_order_code, technician, action_taken, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, machine, fault_mode, urgency, work_order_code, technician, action_taken, status))
    wo_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit("WORK_ORDER_DISPATCHED", f"Work order {work_order_code} issued for {machine} ({fault_mode})", "WARNING")
    return wo_id

def get_work_orders(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_work_orders ORDER BY id DESC LIMIT ?", (limit,))
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
    print("Database initialization & seeding complete:", get_stats())
