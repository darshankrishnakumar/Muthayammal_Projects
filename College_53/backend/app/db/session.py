from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///./rail_defects.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.db.models import RailwayDefectRecord
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(RailwayDefectRecord).count() == 0:
        samples = [
            RailwayDefectRecord(
                record_id="RAL-2026-001",
                chainage_km="KM 142.350",
                track_segment="Line 1 Westbound",
                defect_type="Surface Crack",
                severity="Critical",
                confidence=0.96,
                affected_area_px=1480,
                status="Pending Remediation"
            ),
            RailwayDefectRecord(
                record_id="RAL-2026-002",
                chainage_km="KM 142.820",
                track_segment="Line 1 Westbound",
                defect_type="Missing Fastener",
                severity="Moderate",
                confidence=0.92,
                affected_area_px=520,
                status="Scheduled"
            ),
            RailwayDefectRecord(
                record_id="RAL-2026-003",
                chainage_km="KM 143.110",
                track_segment="Line 1 Eastbound",
                defect_type="Track Surface Deterioration",
                severity="Minor",
                confidence=0.88,
                affected_area_px=240,
                status="Monitored"
            )
        ]
        db.add_all(samples)
        db.commit()
    db.close()
