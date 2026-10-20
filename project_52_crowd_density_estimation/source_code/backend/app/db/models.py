from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from datetime import datetime
from backend.app.db.session import Base

class CrowdMonitoringEvent(Base):
    __tablename__ = "crowd_monitoring_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(32), unique=True, index=True)
    zone_name = Column(String(64), index=True)
    archetype = Column(String(50), default="PUBLIC_CONCOURSE")
    timestamp = Column(DateTime, default=datetime.utcnow)
    estimated_headcount = Column(Integer)
    density_level = Column(String(24))
    anomaly_detected = Column(Boolean, default=False)
    anomaly_type = Column(String(32))
    risk_score = Column(Float)
    optical_flow_turbulence = Column(Float)
    flow_velocity_mps = Column(Float, default=1.0)
    spatial_divergence = Column(Float, default=0.0)
    kinetic_energy_entropy = Column(Float, default=2.5)
    density_ratio_sqm = Column(Float, default=1.5)
    bottleneck_pressure_psi = Column(Float, default=20.0)
    directional_coherence = Column(Float, default=0.8)
    velocity_variance = Column(Float, default=0.2)
    occlusion_ratio = Column(Float, default=0.2)
    ambient_lighting_lux = Column(Float, default=500.0)
    panic_index = Column(Float, default=0.1)
    evidence_hash = Column(String(64), nullable=False)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"

    block_index = Column(Integer, primary_key=True)
    timestamp = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    event_id = Column(Text, nullable=False)
    evidence_hash = Column(Text, nullable=False)
    previous_hash = Column(Text, nullable=False)
    block_hash = Column(Text, nullable=False)
