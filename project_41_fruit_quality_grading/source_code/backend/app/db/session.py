import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, FruitItem, SortingLane, AuditLedger

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
            "Autonomous Fruit Quality Grading & Defect Microservice initialized on Port 5041 with SQLite WAL mode"
        )

    # 2. Sorting Lanes
    if db.query(SortingLane).count() == 0:
        lanes = [
            SortingLane(lane_id="LN-01", lane_number=1, lane_name="Lane 1: High-Speed Apple Optical Sorter", camera_id="OPTICAL-CAM-01", target_fruit="APPLE", belt_speed_m_s=1.2, ejector_status="ARMED", throughput_per_min=140),
            SortingLane(lane_id="LN-02", lane_number=2, lane_name="Lane 2: Citrus / Orange Surface Defect Sorter", camera_id="OPTICAL-CAM-02", target_fruit="ORANGE", belt_speed_m_s=1.0, ejector_status="ARMED", throughput_per_min=120),
            SortingLane(lane_id="LN-03", lane_number=3, lane_name="Lane 3: Tropical Banana Ripeness & Curvature Belt", camera_id="OPTICAL-CAM-03", target_fruit="BANANA", belt_speed_m_s=0.9, ejector_status="ARMED", throughput_per_min=100),
            SortingLane(lane_id="LN-04", lane_number=4, lane_name="Lane 4: Premium Mango Export Inspection Line", camera_id="OPTICAL-CAM-04", target_fruit="MANGO", belt_speed_m_s=0.8, ejector_status="ARMED", throughput_per_min=90)
        ]
        db.add_all(lanes)
        db.commit()
        append_audit_block(db, "CONVEYOR_LANES_CONFIGURED", "Initialized 4 high-speed multi-lane fruit inspection conveyors")

    # 3. Baseline Verified Fruit Items
    if db.query(FruitItem).count() == 0:
        samples = [
            ("APPLE", "GRADE_A_PREMIUM", "NONE", 0.0, 78.5, 210.0, 84.5, 16.5, 24.0, 96.5, "BIN_1_EXPORT", 0.992, 1),
            ("APPLE", "GRADE_B_STANDARD", "BRUISE", 3.8, 76.0, 195.0, 58.0, 13.5, 11.5, 76.0, "BIN_2_DOMESTIC", 0.965, 1),
            ("ORANGE", "GRADE_A_PREMIUM", "NONE", 0.0, 82.0, 230.0, 78.0, 14.8, 22.0, 94.0, "BIN_1_EXPORT", 0.988, 2),
            ("ORANGE", "GRADE_C_REJECT", "SKIN_ROT", 16.5, 79.0, 215.0, 28.0, 9.2, 2.5, 25.0, "BIN_3_DISCARD", 0.995, 2),
            ("BANANA", "GRADE_A_PREMIUM", "NONE", 0.0, 60.0, 145.0, 68.0, 18.2, 16.0, 91.0, "BIN_1_EXPORT", 0.979, 3),
            ("BANANA", "GRADE_B_STANDARD", "SCAB", 4.2, 58.0, 138.0, 48.0, 14.0, 8.5, 68.0, "BIN_2_DOMESTIC", 0.952, 3),
            ("MANGO", "GRADE_A_PREMIUM", "NONE", 0.0, 92.0, 310.0, 88.0, 19.5, 20.0, 98.0, "BIN_1_EXPORT", 0.996, 4),
            ("MANGO", "GRADE_C_REJECT", "FUNGAL_SPOT", 18.2, 88.0, 280.0, 22.0, 8.5, 1.5, 18.0, "BIN_3_DISCARD", 0.991, 4)
        ]
        for i, (var, g, d, def_pct, dia, wt, firm, brix, shelf, econ, chute, conf, lane) in enumerate(samples):
            ev_hash = hashlib.sha256(f"{var}|{g}|{d}|{firm}|{brix}|{shelf}|{econ}".encode()).hexdigest()
            item = FruitItem(
                item_id=f"FRUIT-2026-{100+i:04d}",
                conveyor_lane=lane,
                fruit_variety=var,
                quality_grade=g,
                defect_type=d,
                defect_area_pct=def_pct,
                diameter_mm=dia,
                weight_grams=wt,
                firmness_n=firm,
                sugar_brix=brix,
                shelf_life_days=shelf,
                batch_economic_index=econ,
                confidence=conf,
                sorting_chute=chute,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=(8 - i) * 12)
            )
            db.add(item)
        db.commit()
        append_audit_block(db, "BASELINE_BATCH_GRADED", "Logged 8 initial verified optical fruit grading inspections")

    db.close()

if __name__ == "__main__":
    init_db()
