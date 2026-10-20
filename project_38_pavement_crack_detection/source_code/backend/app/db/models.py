from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class CrackIncident(Base):
    __tablename__ = "crack_incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True)
    road_name = Column(String(100))
    chainage_km = Column(Float)
    crack_type = Column(String(50))  # ALLIGATOR, LONGITUDINAL, TRANSVERSE, BLOCK, EDGE_CRACKING, POTHOLE_DISTRESS
    severity_level = Column(String(20)) # LOW, MEDIUM, HIGH
    mean_width_mm = Column(Float)
    total_length_cm = Column(Float)
    density_percentage = Column(Float)
    pci_score = Column(Float) # Pavement Condition Index (0 - 100)
    recommendation = Column(String(100)) # ROUTINE_MONITOR, SEALING, MILL_AND_FILL, RECONSTRUCT
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True)
    incident_id = Column(String(50), index=True)
    road_name = Column(String(100))
    chainage_km = Column(Float)
    treatment_type = Column(String(100))
    estimated_cost_usd = Column(Float)
    priority_tier = Column(String(20)) # URGENT, SCHEDULED, MONITOR
    status = Column(String(20), default="DISPATCHED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    prev_hash = Column(String(64), nullable=False)
    record_hash = Column(String(64), nullable=False)
