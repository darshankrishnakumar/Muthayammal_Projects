from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class InspectedPart(Base):
    __tablename__ = "inspected_parts"
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(String(50), unique=True, index=True)
    assembly_line = Column(String(50))
    part_type = Column(String(50)) # PCB_BOARD, MACHINED_GEAR, METALLIC_CASING
    inspection_verdict = Column(String(20)) # PASS, REJECT
    defect_type = Column(String(50)) # NONE, SCRATCH, CRACK, DENT, MISSING_COMPONENT
    severity_score = Column(Float) # 0 to 100
    defect_area_pct = Column(Float)
    actuator_action = Column(String(30)) # ROUTE_CONVEYOR, TRIGGER_PNEUMATIC_EJECT
    timestamp = Column(DateTime, default=datetime.utcnow)
