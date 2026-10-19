import os
import sqlite3
import json
from datetime import datetime, timedelta, timezone
import random

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "source_code", "backend", "aviation_maintenance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aircraft_components (
        component_id TEXT PRIMARY KEY,
        component_name TEXT NOT NULL,
        engine_model TEXT NOT NULL,
        max_design_cycles INTEGER NOT NULL,
        nominal_temp_r REAL NOT NULL,
        nominal_pres_psia REAL NOT NULL,
        nominal_core_rpm REAL NOT NULL,
        nominal_fan_rpm REAL NOT NULL,
        nominal_fuel_ratio REAL NOT NULL,
        icon TEXT NOT NULL,
        failure_mode TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_id TEXT NOT NULL,
        cycle_number INTEGER NOT NULL,
        flight_hours REAL NOT NULL,
        cycle_ratio REAL NOT NULL,
        t50_lpt_outlet_temp_r REAL NOT NULL,
        p30_hpc_pressure_psia REAL NOT NULL,
        nc_core_speed_rpm REAL NOT NULL,
        nf_fan_speed_rpm REAL NOT NULL,
        fuel_flow_ratio_pps_psi REAL NOT NULL,
        egt_margin_deg_c REAL NOT NULL,
        vibration_broadband_g REAL NOT NULL,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY (component_id) REFERENCES aircraft_components(component_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rul_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_id TEXT NOT NULL,
        component_name TEXT NOT NULL,
        engine_model TEXT NOT NULL,
        flight_cycles_completed INTEGER NOT NULL,
        flight_hours_completed REAL NOT NULL,
        health_score REAL NOT NULL,
        rul_cycles INTEGER NOT NULL,
        rul_flight_hours REAL NOT NULL,
        airworthiness_status TEXT NOT NULL,
        action_required TEXT NOT NULL,
        color TEXT NOT NULL,
        model_name TEXT NOT NULL,
        predicted_at TEXT NOT NULL,
        FOREIGN KEY (component_id) REFERENCES aircraft_components(component_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_shop_orders (
        order_id TEXT PRIMARY KEY,
        component_id TEXT NOT NULL,
        component_name TEXT NOT NULL,
        priority TEXT NOT NULL,
        defect_summary TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_technician TEXT NOT NULL,
        estimated_downtime_hrs REAL NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (component_id) REFERENCES aircraft_components(component_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        details TEXT NOT NULL,
        performed_by TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()

    # Seed baseline components if empty
    cursor.execute("SELECT COUNT(*) FROM aircraft_components;")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    components = [
        ('COMP-TURB-01', 'High-Pressure Turbine (HPT) Blades', 'CFM56-7B / LEAP-1B', 4200, 1580, 550, 9450, 2500, 0.0265, '🔥', 'Thermal Creep & Oxidation Erosion', now_str),
        ('COMP-HPC-02', 'High-Pressure Compressor (HPC) Rotor', 'GE90-115B', 6000, 1120, 480, 9200, 2350, 0.0245, '🌀', 'High-Cycle Fatigue (HCF) Micro-Cracking', now_str),
        ('COMP-BRG-03', 'Mainshaft Roller Bearings (#4 Bearing)', 'Trent 1000', 5500, 460, 45, 9100, 2400, 0.0230, '⚙️', 'Spallation & Subsurface Shear Fatigue', now_str),
        ('COMP-FMU-04', 'Fuel Metering Unit (FMU)', 'PW1100G-JM', 8500, 320, 1200, 9300, 2480, 0.0280, '⛽', 'Servo Valve Sticking & Orifice Wear', now_str),
        ('COMP-LPT-05', 'Low-Pressure Turbine (LPT) Stator', 'CF34-8E', 7200, 1340, 180, 9050, 2320, 0.0250, '🛩️', 'Thermal Barrier Coating (TBC) Delamination', now_str)
    ]

    cursor.executemany("""
    INSERT INTO aircraft_components (
        component_id, component_name, engine_model, max_design_cycles,
        nominal_temp_r, nominal_pres_psia, nominal_core_rpm, nominal_fan_rpm,
        nominal_fuel_ratio, icon, failure_mode, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, components)

    # Seed initial telemetry samples
    for comp in components:
        cid = comp[0]
        max_c = comp[3]
        for step in range(5):
            c_num = int((step + 1) * 0.18 * max_c)
            c_ratio = round(c_num / max_c, 4)
            deg = c_ratio ** 1.8
            t50 = round(comp[4] * (1.0 + deg * 0.11), 1)
            p30 = round(comp[5] * (1.0 - deg * 0.075), 1)
            nc = round(comp[6] + deg * 420.0, 1)
            nf = round(comp[7] + (step * 2), 1)
            fuel = round(comp[8] + deg * 0.005, 5)
            egt = round(85.0 - deg * 90.0, 1)
            vib = round(0.35 + (deg ** 1.6) * 3.0, 3)
            rec_time = (datetime.now(timezone.utc) - timedelta(days=20-step*4)).isoformat()

            cursor.execute("""
            INSERT INTO flight_telemetry (
                component_id, cycle_number, flight_hours, cycle_ratio,
                t50_lpt_outlet_temp_r, p30_hpc_pressure_psia, nc_core_speed_rpm,
                nf_fan_speed_rpm, fuel_flow_ratio_pps_psi, egt_margin_deg_c,
                vibration_broadband_g, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (cid, c_num, round(c_num * 2.8, 1), c_ratio, t50, p30, nc, nf, fuel, egt, vib, rec_time))

    # Seed initial predictions
    predictions = [
        ('COMP-TURB-01', 'High-Pressure Turbine (HPT) Blades', 'CFM56-7B / LEAP-1B', 3150, 8820.0, 42.4, 1050, 2940.0, 'MAINTENANCE DUE SOON', 'Schedule borescope inspection within next 75 flight cycles. Monitor EGT margin.', '#f59e0b', 'PyTorch Dual Residual RUL Net', (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()),
        ('COMP-HPC-02', 'High-Pressure Compressor (HPC) Rotor', 'GE90-115B', 2400, 6720.0, 78.5, 3600, 10080.0, 'AIRWORTHY / OPTIMAL', 'Normal on-wing operation. Proceed to standard A-check interval.', '#10b981', 'PyTorch Dual Residual RUL Net', (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()),
        ('COMP-BRG-03', 'Mainshaft Roller Bearings (#4 Bearing)', 'Trent 1000', 4950, 13860.0, 22.1, 550, 1540.0, 'GROUNDED / MANDATORY SHOP VISIT', 'AOG Alert: Immediate engine teardown and non-destructive eddy-current inspection.', '#ef4444', 'PyTorch Dual Residual RUL Net', (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
        ('COMP-FMU-04', 'Fuel Metering Unit (FMU)', 'PW1100G-JM', 3400, 9520.0, 72.8, 5100, 14280.0, 'AIRWORTHY / OPTIMAL', 'Normal on-wing operation. Proceed to standard A-check interval.', '#10b981', 'PyTorch Dual Residual RUL Net', (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()),
        ('COMP-LPT-05', 'Low-Pressure Turbine (LPT) Stator', 'CF34-8E', 4680, 13104.0, 48.9, 2520, 7056.0, 'MAINTENANCE DUE SOON', 'Schedule borescope inspection within next 75 flight cycles. Monitor EGT margin.', '#f59e0b', 'PyTorch Dual Residual RUL Net', (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat())
    ]

    cursor.executemany("""
    INSERT INTO rul_predictions (
        component_id, component_name, engine_model, flight_cycles_completed,
        flight_hours_completed, health_score, rul_cycles, rul_flight_hours,
        airworthiness_status, action_required, color, model_name, predicted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, predictions)

    # Seed maintenance shop orders
    shop_orders = [
        ('MSO-2026-081', 'COMP-BRG-03', 'Mainshaft Roller Bearings (#4 Bearing)', 'CRITICAL', 'Vibration exceedance 3.42g RMS detected during cruise climb. Suspected outer race spallation.', 'PENDING_SHOP_VISIT', 'Senior Lead Inspector H. Vance', 48.0, (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(), None),
        ('MSO-2026-079', 'COMP-TURB-01', 'High-Pressure Turbine (HPT) Blades', 'HIGH', 'Borescope inspection requested due to EGT margin degradation to 14.2°C.', 'IN_INSPECTION', 'Turbine Specialist M. Chen', 18.0, (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), None),
        ('MSO-2026-065', 'COMP-FMU-04', 'Fuel Metering Unit (FMU)', 'NORMAL', 'Scheduled periodic calibration of servo-valve torque motor during C-Check.', 'OVERHAULED', 'Avionics Eng. S. Patel', 12.0, (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(), (datetime.now(timezone.utc) - timedelta(days=3)).isoformat())
    ]

    cursor.executemany("""
    INSERT INTO maintenance_shop_orders (
        order_id, component_id, component_name, priority, defect_summary,
        status, assigned_technician, estimated_downtime_hrs, created_at, completed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, shop_orders)

    # Audit log
    cursor.execute("""
    INSERT INTO audit_log (action, entity, entity_id, details, performed_by, timestamp)
    VALUES ('SYSTEM_INITIALIZED', 'DATABASE', 'AIRCRAFT_RUL_DB', 'Initialized SQLite WAL schema and seeded components, telemetry, and MSO orders', 'System Bootstrapper', ?);
    """, (now_str,))

    conn.commit()

def log_audit(action, entity, entity_id, details, performed_by="System"):
    try:
        conn = get_db_connection()
        conn.execute("""
        INSERT INTO audit_log (action, entity, entity_id, details, performed_by, timestamp)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (action, entity, entity_id, details, performed_by, datetime.now(timezone.utc).isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging audit: {e}")

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
