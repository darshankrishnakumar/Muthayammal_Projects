import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, FireIncident
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
    if db.query(FireIncident).count() == 0:
        zones = ["Industrial Plant Boiler Room", "Warehouse Sector B Chemical Storage", "Commercial Mall Kitchen", "Underground Parking Bay 4"]
        for i in range(8):
            ht = random.choice(["FLAME", "SMOKE", "DUAL_HAZARD"])
            st = "TIER_3_CRITICAL" if ht == "DUAL_HAZARD" else ("TIER_2_ACTIVE" if ht == "FLAME" else "TIER_1_EARLY")
            inc = FireIncident(
                incident_id=f"FIRE-2026-{200+i}",
                zone_name=random.choice(zones),
                camera_id=f"CCTV-ZONE-0{random.randint(1,4)}",
                hazard_type=ht,
                severity_tier=st,
                confidence=round(random.uniform(0.88, 0.99), 3),
                flicker_frequency_hz=round(random.uniform(7.5, 16.2), 1) if ht != "SMOKE" else 0.0,
                plume_expansion_rate=round(random.uniform(1.2, 4.8), 2) if ht != "FLAME" else 0.5,
                dispatch_status=random.choice(["DISPATCHED", "RESOLVED"]),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.add(inc)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
