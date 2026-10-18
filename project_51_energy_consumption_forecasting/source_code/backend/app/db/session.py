import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, EnergyOptimizationPlan
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(EnergyOptimizationPlan).count() == 0:
        facilities = ["Tech Campus Science Building A", "Commercial Shopping Plaza North", "Smart Residential Microgrid Complex"]
        for i, fac in enumerate(facilities):
            db.add(EnergyOptimizationPlan(
                plan_id=f"NRG-2026-{100+i}",
                building_facility=fac,
                forecasted_peak_kwh=round(random.uniform(420.0, 680.0), 1),
                optimized_peak_kwh=round(random.uniform(310.0, 480.0), 1),
                peak_shaving_reduction_pct=round(random.uniform(18.0, 26.5), 1),
                estimated_daily_savings_usd=round(random.uniform(145.0, 280.0), 2),
                co2_reduction_kg=round(random.uniform(85.0, 160.0), 1),
                recommended_load_shift_actions="Shift HVAC pre-cooling to 04:00-06:00; Schedule EV charging off-peak; Battery ESS discharge during 16:00-19:00 tariff peak.",
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
