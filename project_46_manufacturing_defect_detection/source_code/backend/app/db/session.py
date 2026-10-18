import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, InspectedPart
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(InspectedPart).count() == 0:
        lines = ["Line-1 SMT PCB Assembly", "Line-2 CNC Gear Milling", "Line-3 Chassis Enclosure"]
        parts = ["PCB_BOARD", "MACHINED_GEAR", "METALLIC_CASING"]
        for i in range(12):
            is_def = random.random() < 0.35
            v = "REJECT" if is_def else "PASS"
            dtype = random.choice(["SCRATCH", "CRACK", "DENT", "MISSING_COMPONENT"]) if is_def else "NONE"
            sev = round(random.uniform(55.0, 95.0), 1) if is_def else 0.0
            act = "TRIGGER_PNEUMATIC_EJECT" if is_def else "ROUTE_CONVEYOR"
            db.add(InspectedPart(
                part_id=f"PART-2026-{1000+i}",
                assembly_line=random.choice(lines),
                part_type=random.choice(parts),
                inspection_verdict=v,
                defect_type=dtype,
                severity_score=sev,
                defect_area_pct=round(random.uniform(2.5, 14.2), 1) if is_def else 0.0,
                actuator_action=act,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(2, 60))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
