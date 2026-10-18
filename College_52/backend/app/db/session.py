from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///./crowd_analytics.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.db.models import CrowdMonitoringEvent
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(CrowdMonitoringEvent).count() == 0:
        samples = [
            CrowdMonitoringEvent(
                event_id="CRW-2026-001",
                zone_name="Central Plaza Concourse",
                estimated_headcount=342,
                density_level="High",
                anomaly_detected=True,
                anomaly_type="Dangerous Congestion",
                risk_score=0.82,
                optical_flow_turbulence=0.74
            ),
            CrowdMonitoringEvent(
                event_id="CRW-2026-002",
                zone_name="North Gate Turnstiles",
                estimated_headcount=88,
                density_level="Low",
                anomaly_detected=False,
                anomaly_type="Normal Flow",
                risk_score=0.18,
                optical_flow_turbulence=0.15
            ),
            CrowdMonitoringEvent(
                event_id="CRW-2026-003",
                zone_name="Transit Station Platform 2",
                estimated_headcount=265,
                density_level="Moderate",
                anomaly_detected=True,
                anomaly_type="Sudden Dispersal",
                risk_score=0.76,
                optical_flow_turbulence=0.88
            )
        ]
        db.add_all(samples)
        db.commit()
    db.close()
