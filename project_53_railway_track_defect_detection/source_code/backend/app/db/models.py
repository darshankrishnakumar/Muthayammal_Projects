from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from backend.app.db.session import Base

class RailwayDefectRecord(Base):
    __tablename__ = "railway_defect_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(32), unique=True, index=True)
    chainage_km = Column(String(32), index=True)
    chainage_numeric_km = Column(Float, default=140.0)
    track_segment = Column(String(64))
    archetype = Column(String(50), default="HIGH_SPEED_PASSENGER")
    timestamp = Column(DateTime, default=datetime.utcnow)
    defect_type = Column(String(48), index=True)
    severity = Column(String(24), index=True)
    confidence = Column(Float)
    affected_area_px = Column(Integer)
    status = Column(String(32), default="Pending Remediation")
    recommended_action = Column(Text)
    cant_deficiency_mm = Column(Float, default=2.0)
    gauge_deviation_mm = Column(Float, default=1.0)
    vertical_profile_roughness = Column(Float, default=1.5)
    alignment_deviation_mm = Column(Float, default=1.0)
    sleeper_ballast_void_depth = Column(Float, default=0.5)
    rail_temperature_c = Column(Float, default=25.0)
    fastener_torque_loss_pct = Column(Float, default=10.0)
    vibration_acceleration_g = Column(Float, default=0.2)
    axle_load_tons = Column(Float, default=22.0)
    acoustic_emission_db = Column(Float, default=70.0)
    track_curvature_rad = Column(Float, default=0.005)
    track_quality_index = Column(Float, default=85.0)
    speed_restriction_kmh = Column(Float, default=160.0)
    derailment_risk = Column(Float, default=0.05)
    evidence_hash = Column(String(64), nullable=False)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"

    block_index = Column(Integer, primary_key=True)
    timestamp = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    record_id = Column(Text, nullable=False)
    evidence_hash = Column(Text, nullable=False)
    previous_hash = Column(Text, nullable=False)
    block_hash = Column(Text, nullable=False)
