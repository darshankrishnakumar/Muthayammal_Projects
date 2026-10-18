import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, FoodBatch
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
    if db.query(FoodBatch).count() == 0:
        samples = [
            ("MEAT_POULTRY", "Prime Ribeye Beef Cut", 92.4, "STAGE_1_FRESH", 120.0, 1.2, 0.0, "IMMEDIATE_RETAIL_SALE"),
            ("FRESH_PRODUCE", "Organic Spinach Batch #4", 62.0, "STAGE_2_MARGINAL", 24.0, 8.4, 4.2, "PRIORITY_DISCOUNT_SALE"),
            ("BAKERY", "Artisan Sourdough Loaves", 41.5, "STAGE_3_DETERIORATED", 0.0, 18.2, 12.0, "DISCARD_COMPOSTING"),
            ("DAIRY", "Farm Cheddar Cheese Block", 88.0, "STAGE_1_FRESH", 360.0, 0.8, 0.0, "COLD_STORAGE_INVENTORY"),
        ]
        for cat, name, score, stage, hours, brown, spoil, rec in samples:
            db.add(FoodBatch(
                batch_id=f"FOOD-2026-{random.randint(100, 999)}",
                food_category=cat,
                product_name=name,
                freshness_score=score,
                deterioration_stage=stage,
                estimated_shelf_life_hours=hours,
                browning_index=brown,
                spoilage_area_pct=spoil,
                recommendation=rec,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 36))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
