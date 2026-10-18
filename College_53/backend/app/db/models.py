from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.app.db.session import Base

class RailwayDefectRecord(Base):
    __tablename__ = "railway_defect_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(32), unique=True, index=True)
    chainage_km = Column(String(32), index=True)
    track_segment = Column(String(64))
    defect_type = Column(String(48), index=True)
    severity = Column(String(24), index=True) # Minor, Moderate, Critical
    confidence = Column(Float)
    affected_area_px = Column(Integer)
    status = Column(String(32), default="Pending Remediation")
    timestamp = Column(DateTime, default=datetime.utcnow)
