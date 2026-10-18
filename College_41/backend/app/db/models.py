from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FruitItem(Base):
    __tablename__ = "fruit_items"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), unique=True, index=True)
    fruit_variety = Column(String(50)) # APPLE, ORANGE, MANGO, BANANA
    quality_grade = Column(String(20)) # GRADE_A_PREMIUM, GRADE_B_STANDARD, GRADE_C_REJECT
    defect_type = Column(String(50)) # NONE, BRUISE, SKIN_ROT, FUNGAL_SPOT, SCAB
    defect_area_pct = Column(Float)
    diameter_mm = Column(Float)
    confidence = Column(Float)
    sorting_chute = Column(String(20)) # BIN_1_EXPORT, BIN_2_DOMESTIC, BIN_3_DISCARD
    timestamp = Column(DateTime, default=datetime.utcnow)
