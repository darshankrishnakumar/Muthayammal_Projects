import os
import sqlite3
import json
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "source_code", "backend", "road_damage.db")

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
    CREATE TABLE IF NOT EXISTS road_sectors (
        sector_id TEXT PRIMARY KEY,
        sector_name TEXT NOT NULL,
        speed_limit_kmh INTEGER NOT NULL,
        surface_type TEXT NOT NULL,
        traffic_vpd_k REAL NOT NULL,
        heavy_truck_pct REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS damage_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector_id TEXT NOT NULL,
        sector_name TEXT NOT NULL,
        pci_score REAL NOT NULL,
        pci_rating TEXT NOT NULL,
        status_color TEXT NOT NULL,
        iri_roughness_m_km REAL NOT NULL,
        defects_found_count INTEGER NOT NULL,
        total_repair_cost_usd INTEGER NOT NULL,
        total_area_sqm REAL NOT NULL,
        model_name TEXT NOT NULL,
        inspected_at TEXT NOT NULL,
        FOREIGN KEY (sector_id) REFERENCES road_sectors(sector_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pavement_defects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspection_id INTEGER,
        sector_id TEXT NOT NULL,
        damage_code TEXT NOT NULL,
        damage_name TEXT NOT NULL,
        severity TEXT NOT NULL,
        confidence REAL NOT NULL,
        area_sqm REAL NOT NULL,
        estimated_cost_usd INTEGER NOT NULL,
        bbox_json TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        FOREIGN KEY (inspection_id) REFERENCES damage_inspections(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS municipal_work_orders (
        order_id TEXT PRIMARY KEY,
        sector_id TEXT NOT NULL,
        sector_name TEXT NOT NULL,
        priority TEXT NOT NULL,
        remediation_scope TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_contractor TEXT NOT NULL,
        budget_allocated_usd INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (sector_id) REFERENCES road_sectors(sector_id)
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

    # Seed sectors if empty
    cursor.execute("SELECT COUNT(*) FROM road_sectors;")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    sectors = [
        ('SEC-NORTH-01', 'Highway Sector A4 (Expressway Corridor)', 110, 'Dense Asphalt Concrete (DAC)', 45.0, 28.0, now_str),
        ('SEC-URBAN-02', 'Urban Arterial Road 12 (Downtown Junction)', 60, 'Stone Mastic Asphalt (SMA)', 55.0, 14.0, now_str),
        ('SEC-IND-03', 'Industrial Ring Road (Heavy Cargo Freight)', 80, 'Reinforced Bituminous Concrete', 32.0, 38.0, now_str),
        ('SEC-RES-04', 'Residential Boulevard (Suburban Sector 8)', 40, 'Standard Flexible Pavement', 8.5, 6.0, now_str),
        ('SEC-MTN-05', 'Mountain Pass Highway (High Incline Zone)', 70, 'Polymer Modified Asphalt (PMA)', 12.0, 22.0, now_str)
    ]

    cursor.executemany("""
    INSERT INTO road_sectors (sector_id, sector_name, speed_limit_kmh, surface_type, traffic_vpd_k, heavy_truck_pct, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, sectors)

    # Seed baseline inspections
    inspections = [
        ('SEC-NORTH-01', 'Highway Sector A4 (Expressway Corridor)', 78.5, 'GOOD (STRUCTURALLY SOUND)', '#10b981', 2.34, 1, 190, 1.35, 'YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)', (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()),
        ('SEC-URBAN-02', 'Urban Arterial Road 12 (Downtown Junction)', 54.2, 'FAIR (MAINTENANCE REQUIRED)', '#f59e0b', 3.82, 3, 580, 4.80, 'YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)', (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()),
        ('SEC-IND-03', 'Industrial Ring Road (Heavy Cargo Freight)', 34.0, 'POOR (CRITICAL RESURFACING)', '#ef4444', 5.65, 4, 1450, 9.20, 'YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)', (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
        ('SEC-RES-04', 'Residential Boulevard (Suburban Sector 8)', 88.0, 'GOOD (STRUCTURALLY SOUND)', '#10b981', 1.85, 1, 95, 0.90, 'YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)', (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()),
        ('SEC-MTN-05', 'Mountain Pass Highway (High Incline Zone)', 62.1, 'FAIR (MAINTENANCE REQUIRED)', '#f59e0b', 3.40, 2, 340, 2.70, 'YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)', (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat())
    ]

    cursor.executemany("""
    INSERT INTO damage_inspections (sector_id, sector_name, pci_score, pci_rating, status_color, iri_roughness_m_km, defects_found_count, total_repair_cost_usd, total_area_sqm, model_name, inspected_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, inspections)

    # Seed work orders
    work_orders = [
        ('MWO-2026-401', 'SEC-IND-03', 'Industrial Ring Road (Heavy Cargo Freight)', 'CRITICAL', 'Emergency deep asphalt milling and cold patch repair for severe D40 pothole cluster.', 'CREW_DISPATCHED', 'Apex Pavement Contractors LLC', 8500, (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(), None),
        ('MWO-2026-388', 'SEC-URBAN-02', 'Urban Arterial Road 12 (Downtown Junction)', 'HIGH', 'Rubberized bitumen crack sealing on intersection alligator cracking zones.', 'SCHEDULED', 'Metro Infrastructure Engineering', 4200, (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), None),
        ('MWO-2026-340', 'SEC-NORTH-01', 'Highway Sector A4 (Expressway Corridor)', 'NORMAL', 'Preventative micro-surfacing on lane 2 longitudinal expansion joints.', 'COMPLETED', 'State Highway Maintenance Division', 12000, (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(), (datetime.now(timezone.utc) - timedelta(days=4)).isoformat())
    ]

    cursor.executemany("""
    INSERT INTO municipal_work_orders (order_id, sector_id, sector_name, priority, remediation_scope, status, assigned_contractor, budget_allocated_usd, created_at, completed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, work_orders)

    cursor.execute("""
    INSERT INTO audit_log (action, entity, entity_id, details, performed_by, timestamp)
    VALUES ('SYSTEM_INITIALIZED', 'DATABASE', 'ROAD_DAMAGE_DB', 'Initialized SQLite WAL schema and seeded sectors, inspections, and municipal work orders', 'System Bootstrapper', ?);
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
