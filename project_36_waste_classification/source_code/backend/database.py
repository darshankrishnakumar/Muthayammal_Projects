import os
import sqlite3
import json
import hashlib
from datetime import datetime, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "waste_sorting.db"))

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
    CREATE TABLE IF NOT EXISTS waste_categories (
        category_id TEXT PRIMARY KEY,
        category_name TEXT NOT NULL,
        bin_color TEXT NOT NULL,
        sort_mechanism TEXT NOT NULL,
        avg_market_value_usd_per_ton REAL NOT NULL,
        carbon_offset_ratio REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sorting_conveyors (
        conveyor_id TEXT PRIMARY KEY,
        conveyor_name TEXT NOT NULL,
        line_speed_m_s REAL NOT NULL,
        optical_sensor_model TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPERATIONAL',
        facility_zone TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS classified_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT UNIQUE NOT NULL,
        conveyor_id TEXT NOT NULL,
        item_type TEXT NOT NULL,
        category TEXT NOT NULL,
        confidence_pct REAL NOT NULL,
        density_g_cm3 REAL NOT NULL,
        spectral_reflectance_nir REAL NOT NULL,
        opacity_pct REAL NOT NULL,
        surface_roughness_um REAL NOT NULL,
        moisture_content_pct REAL NOT NULL,
        rigidity_modulus_gpa REAL NOT NULL,
        magnetic_susceptibility REAL NOT NULL,
        carbon_footprint_kg_co2 REAL NOT NULL,
        recyclability_score REAL NOT NULL,
        contamination_risk REAL NOT NULL,
        diversion_bin TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (conveyor_id) REFERENCES sorting_conveyors(conveyor_id)
    );

    CREATE TABLE IF NOT EXISTS recycling_batches (
        batch_id TEXT PRIMARY KEY,
        conveyor_id TEXT NOT NULL,
        material_type TEXT NOT NULL,
        item_count INTEGER NOT NULL,
        total_weight_kg REAL NOT NULL,
        avg_recyclability REAL NOT NULL,
        contamination_grade TEXT NOT NULL,
        dispatched_to TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (conveyor_id) REFERENCES sorting_conveyors(conveyor_id)
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

    # Seed baseline categories if empty
    cursor.execute("SELECT COUNT(*) FROM waste_categories")
    if cursor.fetchone()[0] == 0:
        cats = [
            ("CAT-PLASTIC", "Plastic", "#06b6d4", "PNEUMATIC_AIR_JET", 420.0, 2.3),
            ("CAT-GLASS", "Glass", "#3b82f6", "MECHANICAL_FLIPPER", 85.0, 0.4),
            ("CAT-METAL", "Metal", "#f59e0b", "EDDY_CURRENT_SEPARATOR", 1250.0, 8.5),
            ("CAT-PAPER", "Paper", "#10b981", "OPTICAL_SUCTION_PICKER", 140.0, 1.2),
            ("CAT-CARDBOARD", "Cardboard", "#d97706", "ROTARY_STAR_SCREEN", 165.0, 1.6),
            ("CAT-ORGANIC", "Organic", "#84cc16", "GRAVITY_DROP_COMPOST", 45.0, 0.8)
        ]
        cursor.executemany("""
            INSERT INTO waste_categories (category_id, category_name, bin_color, sort_mechanism, avg_market_value_usd_per_ton, carbon_offset_ratio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, cats)

        conveyors = [
            ("CONV-A1", "Municipal Container Line A1 (PET/HDPE & Glass)", 1.2, "SpectraCam Hyperspectral NIR-850", "OPERATIONAL", "Zone 1 - Primary Sort"),
            ("CONV-B2", "Commercial Fiber Line B2 (OCC & Deinked Paper)", 1.8, "OptoGrip Dual-Spectrum RGB-NIR", "OPERATIONAL", "Zone 2 - Fiber Recovery"),
            ("CONV-C3", "Mixed Organic & Rigid Line C3 (Biomass & Met)", 1.0, "MultiSensor Vision + Eddy Array", "OPERATIONAL", "Zone 3 - Residual Separation")
        ]
        cursor.executemany("""
            INSERT INTO sorting_conveyors (conveyor_id, conveyor_name, line_speed_m_s, optical_sensor_model, status, facility_zone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, conveyors)

        batches = [
            ("BATCH-2026-01", "CONV-A1", "Plastic", 1420, 385.5, 84.5, "Grade A", "EcoCycle Polymer Reclamation Corp", "2026-10-19T14:30:00Z"),
            ("BATCH-2026-02", "CONV-B2", "Cardboard", 2850, 1240.0, 93.2, "Grade A+", "International Paper Mill #4", "2026-10-19T16:00:00Z"),
            ("BATCH-2026-03", "CONV-A1", "Glass", 940, 680.0, 96.0, "Grade A+", "Owens-Illinois Cullet Processing", "2026-10-19T17:15:00Z"),
            ("BATCH-2026-04", "CONV-C3", "Metal", 620, 215.0, 97.4, "Grade A+", "Alcoa Aluminum Recycling Works", "2026-10-19T18:45:00Z"),
            ("BATCH-2026-05", "CONV-C3", "Organic", 3100, 1850.0, 18.2, "Compost Grade", "Municipal Anaerobic Digestion Facility", "2026-10-19T20:00:00Z")
        ]
        cursor.executemany("""
            INSERT INTO recycling_batches (batch_id, conveyor_id, material_type, item_count, total_weight_kg, avg_recyclability, contamination_grade, dispatched_to, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batches)

        conn.commit()
        record_audit_log(cursor, "SYSTEM_INIT", "SYSTEM", {"message": "Initialized autonomous waste sorting database in WAL mode with categories, conveyors, and batches."})
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
    print("Initialized waste_sorting.db successfully at", DB_PATH)
