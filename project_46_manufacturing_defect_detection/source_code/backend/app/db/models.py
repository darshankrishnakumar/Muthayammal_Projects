from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class InspectedPart(Base):
    __tablename__ = "inspected_parts"
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(String(50), unique=True, index=True)
    assembly_line = Column(String(100), nullable=False)
    part_type = Column(String(50), nullable=False) # PCB_BOARD, MACHINED_GEAR, METALLIC_CASING, TURBINE_BLADE
    inspection_verdict = Column(String(20), nullable=False) # PASS, REJECT
    defect_type = Column(String(50), nullable=False) # NONE, SCRATCH, CRACK, DENT, MISSING_COMPONENT
    severity_score = Column(Float, nullable=False) # 0.0 to 100.0%
    defect_area_pct = Column(Float, nullable=False) # 0.0 to 100.0%
    surface_roughness_ra = Column(Float, default=1.0) # um
    pneumatic_ejection_confidence = Column(Float, default=0.0) # 0.0 to 100.0%
    inspection_cycle_time_ms = Column(Float, default=11.2)
    actuator_action = Column(String(50), nullable=False) # ROUTE_CONVEYOR, TRIGGER_PNEUMATIC_EJECT
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class InspectionTemplate(Base):
    __tablename__ = "inspection_templates"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(50), unique=True, index=True)
    part_type = Column(String(50), nullable=False)
    assembly_line = Column(String(100), nullable=False)
    camera_resolution = Column(String(100), default="4096x3072 120fps")
    max_acceptable_roughness = Column(Float, default=1.5)
    max_acceptable_defect_area = Column(Float, default=0.5)
    ejection_air_pressure_bar = Column(Float, default=6.5)
    is_active = Column(Boolean, default=True)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
