from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CrackIncident(Base):
    __tablename__ = "crack_incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True)
    road_name = Column(String(100))
    chainage_km = Column(Float)
    crack_type = Column(String(50))  # ALLIGATOR, LONGITUDINAL, TRANSVERSE, BLOCK
    severity_level = Column(String(20)) # LOW, MEDIUM, HIGH
    mean_width_mm = Column(Float)
    total_length_cm = Column(Float)
    density_percentage = Column(Float)
    pci_score = Column(Float) # Pavement Condition Index (0 - 100)
    recommendation = Column(String(100)) # ROUTINE_MONITOR, SEALING, MILL_AND_FILL, RECONSTRUCT
    timestamp = Column(DateTime, default=datetime.utcnow)
