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
    hazard_type = Column(String(50))  # NORMAL, SMOKE_DETECTED, FLAME_DETECTED, DUAL_FIRE_SMOKE_HAZARD
    severity_tier = Column(String(30))  # NONE, TIER_1_EARLY, TIER_2_ACTIVE, TIER_3_CRITICAL
    confidence = Column(Float)
    flicker_frequency_hz = Column(Float)
    plume_expansion_rate = Column(Float)
    flame_temp_c = Column(Float, nullable=True)
    evacuation_urgency = Column(Float, nullable=True)
    co_ppm = Column(Float, nullable=True)
    evidence_hash = Column(String(64), nullable=True)
    dispatch_status = Column(String(30), default="DISPATCHED")  # NOMINAL, DISPATCHED, SUPPRESSED, RESOLVED
    timestamp = Column(DateTime, default=datetime.utcnow)

class HazardZone(Base):
    __tablename__ = "hazard_zones"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String(32), unique=True, index=True)
    zone_name = Column(String(100), nullable=False)
    facility_type = Column(String(64), nullable=False)
    camera_count = Column(Integer, default=4)
    sprinkler_armed = Column(Boolean, default=True)
    suppression_system = Column(String(64), default="Dry Chemical / FM-200 Clean Agent")

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
