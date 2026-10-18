from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.app.db.session import Base

class CrowdMonitoringEvent(Base):
    __tablename__ = "crowd_monitoring_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(32), unique=True, index=True)
    zone_name = Column(String(64), index=True)
    estimated_headcount = Column(Integer)
    density_level = Column(String(24))
    anomaly_detected = Column(Boolean, default=False)
    anomaly_type = Column(String(32))
    risk_score = Column(Float)
    optical_flow_turbulence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
