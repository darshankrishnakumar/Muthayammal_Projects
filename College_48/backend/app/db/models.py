from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FoodBatch(Base):
    __tablename__ = "food_batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), unique=True, index=True)
    food_category = Column(String(50)) # MEAT_POULTRY, FRESH_PRODUCE, BAKERY, DAIRY
    product_name = Column(String(100))
    freshness_score = Column(Float) # 0 to 100
    deterioration_stage = Column(String(30)) # STAGE_1_FRESH, STAGE_2_MARGINAL, STAGE_3_DETERIORATED
    estimated_shelf_life_hours = Column(Float)
    browning_index = Column(Float)
    spoilage_area_pct = Column(Float)
    recommendation = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
