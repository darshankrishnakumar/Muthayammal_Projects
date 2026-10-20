import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, FireIncident, HazardZone, AuditLedger

db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def compute_block_hash(action: str, details: str, timestamp: str, prev_hash: str) -> str:
    payload = f"{action}|{details}|{timestamp}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db: Session, action_type: str, details: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    ts = datetime.utcnow().isoformat() + "Z"
    if last_block is None:
        idx = 0
        prev_hash = "0" * 64
    else:
        idx = last_block.block_index + 1
        prev_hash = last_block.current_hash
    cur_hash = compute_block_hash(action_type, details, ts, prev_hash)
    entry = AuditLedger(
        block_index=idx,
        timestamp=ts,
        action_type=action_type,
        details=details,
        previous_hash=prev_hash,
        current_hash=cur_hash
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "Industrial Fire & Smoke Vision Surveillance Microservice initialized on Port 5040 with SQLite WAL mode"
        )

    # Hazard Zones
    if db.query(HazardZone).count() == 0:
        zones = [
            HazardZone(zone_id="ZN-01", zone_name="Industrial Plant Boiler Room", facility_type="Thermal Energy Plant", camera_count=4, sprinkler_armed=True, suppression_system="High-Pressure Water Mist / CO2 Deluge"),
            HazardZone(zone_id="ZN-02", zone_name="Warehouse Sector B Chemical Storage", facility_type="Hazmat Chemical Depot", camera_count=6, sprinkler_armed=True, suppression_system="Dry Chemical / FM-200 Clean Agent"),
            HazardZone(zone_id="ZN-03", zone_name="Commercial Mall Kitchen", facility_type="Commercial Dining Facility", camera_count=4, sprinkler_armed=True, suppression_system="Wet Chemical K-Class Suppressant"),
            HazardZone(zone_id="ZN-04", zone_name="Underground Parking Bay 4", facility_type="Subterranean Transport Facility", camera_count=8, sprinkler_armed=True, suppression_system="Pre-Action Foam-Water Sprinkler"),
            HazardZone(zone_id="ZN-05", zone_name="Data Center Server Hall 3", facility_type="Critical Telecommunications", camera_count=6, sprinkler_armed=True, suppression_system="Inergen IG-541 Clean Agent")
        ]
        db.add_all(zones)
        db.commit()
        append_audit_block(db, "FACILITY_ZONES_CONFIGURED", "Registered 5 mission-critical industrial hazard surveillance zones")

    # Initial verified fire incidents
    if db.query(FireIncident).count() == 0:
        samples = [
            ("Industrial Plant Boiler Room", "CCTV-BOI-01", "FLAME_DETECTED", "TIER_2_ACTIVE", 0.985, 12.5, 1.8, 485.0, 78.5, 165.0, "DISPATCHED"),
            ("Warehouse Sector B Chemical Storage", "CCTV-CHE-02", "DUAL_FIRE_SMOKE_HAZARD", "TIER_3_CRITICAL", 0.994, 15.8, 5.2, 745.0, 96.0, 580.0, "DISPATCHED"),
            ("Commercial Mall Kitchen", "CCTV-KIT-01", "SMOKE_DETECTED", "TIER_1_EARLY", 0.942, 3.2, 2.8, 42.0, 45.0, 110.0, "RESOLVED"),
            ("Underground Parking Bay 4", "CCTV-PRK-03", "SMOKE_DETECTED", "TIER_1_EARLY", 0.915, 2.5, 1.9, 36.5, 40.0, 85.0, "RESOLVED"),
            ("Data Center Server Hall 3", "CCTV-SRV-02", "FLAME_DETECTED", "TIER_2_ACTIVE", 0.978, 14.0, 1.5, 520.0, 82.0, 195.0, "SUPPRESSED"),
            ("Warehouse Sector B Chemical Storage", "CCTV-CHE-04", "DUAL_FIRE_SMOKE_HAZARD", "TIER_3_CRITICAL", 0.998, 16.5, 6.4, 810.0, 98.5, 640.0, "DISPATCHED")
        ]
        for i, (z, c, ht, st, conf, flk, plm, temp, urg, co, disp) in enumerate(samples):
            ev_hash = hashlib.sha256(f"{z}|{c}|{ht}|{st}|{conf}|{temp}|{urg}".encode()).hexdigest()
            inc = FireIncident(
                incident_id=f"FIRE-2026-{100+i:04d}",
                zone_name=z,
                camera_id=c,
                hazard_type=ht,
                severity_tier=st,
                confidence=conf,
                flicker_frequency_hz=flk,
                plume_expansion_rate=plm,
                flame_temp_c=temp,
                evacuation_urgency=urg,
                co_ppm=co,
                evidence_hash=ev_hash,
                dispatch_status=disp,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
            )
            db.add(inc)
        db.commit()
        append_audit_block(db, "BENCHMARK_INCIDENTS_LOADED", "Seeded 6 verified industrial fire telemetry records")

    db.close()

if __name__ == "__main__":
    init_db()
