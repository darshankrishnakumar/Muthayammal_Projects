"""
Database Engine, Session Management, and Seed Setup for Project 55.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, Camera

# Create database parent dir if necessary
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
if db_path.startswith("./"):
    db_path = db_path[2:]
db_dir = os.path.dirname(db_path)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Seed default enterprise roadside cameras if empty
        if db.query(Camera).count() == 0:
            cams = [
                Camera(
                    camera_id="CAM-HWY-101-N",
                    name="Highway 101 North - Mile Marker 42",
                    roadway="Highway 101 Corridor",
                    latitude=37.7749,
                    longitude=-122.4194,
                    zone="Lane 1 & 2 (Northbound)",
                    status="ONLINE",
                    stream_url="data/sample_videos/high_speed_collision.mp4"
                ),
                Camera(
                    camera_id="CAM-I80-BAY",
                    name="I-80 Bay Bridge Approach",
                    roadway="Interstate 80 Corridor",
                    latitude=37.7983,
                    longitude=-122.3778,
                    zone="Westbound Deck",
                    status="ONLINE",
                    stream_url="data/sample_videos/rollover_spinout.mp4"
                ),
                Camera(
                    camera_id="CAM-HWY-280-S",
                    name="Highway 280 South - Silicon Valley Express",
                    roadway="I-280 Corridor",
                    latitude=37.3382,
                    longitude=-121.8863,
                    zone="Express Lanes",
                    status="ONLINE",
                    stream_url="data/sample_videos/sudden_brake_normal.mp4"
                ),
                Camera(
                    camera_id="CAM-HWY-99-CENTRAL",
                    name="Highway 99 Central Valley Junction",
                    roadway="State Route 99",
                    latitude=36.7468,
                    longitude=-119.7726,
                    zone="Junction 14B",
                    status="ONLINE",
                    stream_url="data/sample_videos/adverse_weather_accident.mp4"
                ),
                Camera(
                    camera_id="CAM-CITY-MAIN",
                    name="Downtown Metro Arterial & 4th Ave",
                    roadway="Market Street Transit Corridor",
                    latitude=37.7850,
                    longitude=-122.4070,
                    zone="Intersection Grid",
                    status="ONLINE",
                    stream_url="data/sample_videos/normal_traffic.mp4"
                )
            ]
            db.add_all(cams)
            db.commit()
            print(f"Database initialized with {len(cams)} seeded roadside cameras.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
