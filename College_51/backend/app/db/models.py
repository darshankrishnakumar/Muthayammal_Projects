from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class EnergyOptimizationPlan(Base):
    __tablename__ = "energy_plans"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, index=True)
    building_facility = Column(String(100))
    forecasted_peak_kwh = Column(Float)
    optimized_peak_kwh = Column(Float)
    peak_shaving_reduction_pct = Column(Float)
    estimated_daily_savings_usd = Column(Float)
    co2_reduction_kg = Column(Float)
    recommended_load_shift_actions = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
