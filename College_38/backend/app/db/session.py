import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, CrackIncident
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
    if db.query(CrackIncident).count() == 0:
        roads = ["Interstate 80 Westbound", "State Route 17 Mile 22", "Broadway Boulevard", "El Camino Real Sector 4"]
        types = ["ALLIGATOR", "LONGITUDINAL", "TRANSVERSE", "BLOCK"]
        sevs = [("LOW", 85.0, "ROUTINE_MONITOR"), ("MEDIUM", 62.0, "SEALING"), ("HIGH", 38.0, "MILL_AND_FILL")]
        for i in range(10):
            sev_lvl, pci_base, rec = random.choice(sevs)
            inc = CrackIncident(
                incident_id=f"CRK-2026-{100+i}",
                road_name=random.choice(roads),
                chainage_km=round(random.uniform(5.0, 85.0), 2),
                crack_type=random.choice(types),
                severity_level=sev_lvl,
                mean_width_mm=round(random.uniform(1.2, 8.5) if sev_lvl != "LOW" else random.uniform(0.5, 1.8), 2),
                total_length_cm=round(random.uniform(15.0, 180.0), 1),
                density_percentage=round(random.uniform(2.5, 24.0), 1),
                pci_score=round(pci_base + random.uniform(-5.0, 5.0), 1),
                recommendation=rec,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(inc)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
