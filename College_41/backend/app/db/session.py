import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, FruitItem
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
    if db.query(FruitItem).count() == 0:
        varieties = ["APPLE", "ORANGE", "MANGO", "BANANA"]
        grades = [("GRADE_A_PREMIUM", "BIN_1_EXPORT", "NONE", 0.0), ("GRADE_B_STANDARD", "BIN_2_DOMESTIC", "BRUISE", 3.5), ("GRADE_C_REJECT", "BIN_3_DISCARD", "SKIN_ROT", 18.2)]
        for i in range(12):
            g, chute, def_t, def_pct = random.choice(grades)
            var = random.choice(varieties)
            item = FruitItem(
                item_id=f"FRUIT-2026-{100+i}",
                fruit_variety=var,
                quality_grade=g,
                defect_type=def_t,
                defect_area_pct=round(def_pct + random.uniform(0.0, 2.0), 1),
                diameter_mm=round(random.uniform(65.0, 88.0), 1),
                confidence=round(random.uniform(0.92, 0.99), 3),
                sorting_chute=chute,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(2, 60))
            )
            db.add(item)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
