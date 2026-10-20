from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FruitItem(Base):
    __tablename__ = "fruit_items"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), unique=True, index=True)
    conveyor_lane = Column(Integer, default=1)
    fruit_variety = Column(String(50))   # APPLE, ORANGE, BANANA, MANGO
    quality_grade = Column(String(30))   # GRADE_A_PREMIUM, GRADE_B_STANDARD, GRADE_C_REJECT
    defect_type = Column(String(50))     # NONE, BRUISE, SKIN_ROT, FUNGAL_SPOT, SCAB
    defect_area_pct = Column(Float)
    diameter_mm = Column(Float)
    weight_grams = Column(Float, nullable=True)
    firmness_n = Column(Float, nullable=True)
    sugar_brix = Column(Float, nullable=True)
    shelf_life_days = Column(Float, nullable=True)
    batch_economic_index = Column(Float, nullable=True)
    confidence = Column(Float)
    sorting_chute = Column(String(30))   # BIN_1_EXPORT, BIN_2_DOMESTIC, BIN_3_DISCARD
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SortingLane(Base):
    __tablename__ = "sorting_lanes"
    id = Column(Integer, primary_key=True, index=True)
    lane_id = Column(String(32), unique=True, index=True)
    lane_number = Column(Integer, nullable=False)
    lane_name = Column(String(100), nullable=False)
    camera_id = Column(String(50), default="OPTICAL-CAM-01")
    target_fruit = Column(String(50), default="APPLE")
    belt_speed_m_s = Column(Float, default=1.2)
    ejector_status = Column(String(30), default="ARMED")
    throughput_per_min = Column(Integer, default=120)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
