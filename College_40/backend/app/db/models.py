from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FireIncident(Base):
    __tablename__ = "fire_incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True)
    zone_name = Column(String(100))
    camera_id = Column(String(50))
    hazard_type = Column(String(50)) # FLAME, SMOKE, DUAL_HAZARD, FALSE_ALARM
    severity_tier = Column(String(20)) # TIER_1_EARLY, TIER_2_ACTIVE, TIER_3_CRITICAL
    confidence = Column(Float)
    flicker_frequency_hz = Column(Float)
    plume_expansion_rate = Column(Float)
    dispatch_status = Column(String(30), default="DISPATCHED") # DISPATCHED, RESOLVED, SUPPRESSED
    timestamp = Column(DateTime, default=datetime.utcnow)
