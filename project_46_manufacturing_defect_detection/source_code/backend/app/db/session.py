import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, InspectedPart, InspectionTemplate, AuditLedger

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

    # 1. Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "Project 46 Automated Product Defect Detection Platform initialized on Port 5046 with SQLite WAL mode and FPN Defect Localization"
        )

    # 2. Seed Inspection Templates
    if db.query(InspectionTemplate).count() == 0:
        templates = [
            InspectionTemplate(
                template_id="TEMPL-PCB",
                part_type="PCB_BOARD",
                assembly_line="Line-1 SMT PCB Assembly",
                camera_resolution="4096x3072 120fps High-Res Telecentric",
                max_acceptable_roughness=1.5,
                max_acceptable_defect_area=0.5,
                ejection_air_pressure_bar=6.2,
                is_active=True
            ),
            InspectionTemplate(
                template_id="TEMPL-GEAR",
                part_type="MACHINED_GEAR",
                assembly_line="Line-2 CNC Gear Milling",
                camera_resolution="2560x1920 90fps Laser Profilometer",
                max_acceptable_roughness=2.0,
                max_acceptable_defect_area=1.0,
                ejection_air_pressure_bar=7.5,
                is_active=True
            ),
            InspectionTemplate(
                template_id="TEMPL-CASING",
                part_type="METALLIC_CASING",
                assembly_line="Line-3 Casing Foundry",
                camera_resolution="3840x2160 60fps Multi-Illumination Array",
                max_acceptable_roughness=3.0,
                max_acceptable_defect_area=1.5,
                ejection_air_pressure_bar=8.0,
                is_active=True
            ),
            InspectionTemplate(
                template_id="TEMPL-BLADE",
                part_type="TURBINE_BLADE",
                assembly_line="Line-4 Precision Aerospace",
                camera_resolution="5120x3840 45fps Micro-CT & Laser Interferometer",
                max_acceptable_roughness=0.8,
                max_acceptable_defect_area=0.2,
                ejection_air_pressure_bar=9.0,
                is_active=True
            )
        ]
        db.add_all(templates)
        db.commit()
        append_audit_block(db, "SEEDED_TEMPLATES", "Seeded 4 industrial inspection station optical templates")

    # 3. Seed Inspected Parts
    if db.query(InspectedPart).count() == 0:
        seed_parts = [
            ("PART-2026-00101", "Line-1 SMT PCB Assembly", "PCB_BOARD", "PASS", "NONE", 2.1, 0.05, 0.85, 2.5, 11.2, "ROUTE_CONVEYOR"),
            ("PART-2026-00102", "Line-1 SMT PCB Assembly", "PCB_BOARD", "REJECT", "SCRATCH", 78.4, 6.80, 4.20, 94.6, 12.1, "TRIGGER_PNEUMATIC_EJECT"),
            ("PART-2026-00103", "Line-2 CNC Gear Milling", "MACHINED_GEAR", "PASS", "NONE", 1.5, 0.02, 1.10, 1.8, 10.8, "ROUTE_CONVEYOR"),
            ("PART-2026-00104", "Line-2 CNC Gear Milling", "MACHINED_GEAR", "REJECT", "CRACK", 91.2, 12.40, 6.85, 98.7, 13.5, "TRIGGER_PNEUMATIC_EJECT"),
            ("PART-2026-00105", "Line-3 Casing Foundry", "METALLIC_CASING", "PASS", "NONE", 3.4, 0.10, 1.45, 3.2, 11.5, "ROUTE_CONVEYOR"),
            ("PART-2026-00106", "Line-3 Casing Foundry", "METALLIC_CASING", "REJECT", "DENT", 68.9, 8.15, 5.10, 91.4, 11.9, "TRIGGER_PNEUMATIC_EJECT"),
            ("PART-2026-00107", "Line-4 Precision Aerospace", "TURBINE_BLADE", "PASS", "NONE", 0.8, 0.01, 0.55, 1.1, 14.0, "ROUTE_CONVEYOR"),
            ("PART-2026-00108", "Line-4 Precision Aerospace", "TURBINE_BLADE", "REJECT", "MISSING_COMPONENT", 96.5, 18.90, 7.60, 99.5, 14.8, "TRIGGER_PNEUMATIC_EJECT"),
        ]

        for p_id, line, p_type, verdict, dtype, sev, area, rough, eject, ctime, act in seed_parts:
            ev_hash = hashlib.sha256(f"{p_id}:{verdict}:{dtype}:{sev}:{area}:{rough}".encode("utf-8")).hexdigest()
            db.add(InspectedPart(
                part_id=p_id,
                assembly_line=line,
                part_type=p_type,
                inspection_verdict=verdict,
                defect_type=dtype,
                severity_score=sev,
                defect_area_pct=area,
                surface_roughness_ra=rough,
                pneumatic_ejection_confidence=eject,
                inspection_cycle_time_ms=ctime,
                actuator_action=act,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 120))
            ))
        db.commit()
        append_audit_block(db, "SEEDED_INSPECTIONS", "Seeded 8 optical inspection calibration parts with SHA-256 evidence hashes")

    db.close()

if __name__ == "__main__":
    init_db()
