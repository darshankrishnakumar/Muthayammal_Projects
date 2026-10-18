from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///./weather_nowcast.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.db.models import WeatherForecastRecord
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(WeatherForecastRecord).count() == 0:
        samples = [
            WeatherForecastRecord(
                forecast_id="WTH-2026-001",
                location_station="Met Station Bay Alpha",
                event_class="Severe Thunderstorm",
                event_probability=0.91,
                lead_time_hours=2,
                temperature_c=29.4,
                barometric_pressure_hpa=992.1,
                wind_speed_kmh=68.5,
                humidity_pct=88.0,
                radar_reflectivity_dbz=54.2,
                alert_issued=True
            ),
            WeatherForecastRecord(
                forecast_id="WTH-2026-002",
                location_station="Met Station Highland Ridge",
                event_class="Heavy Rainfall",
                event_probability=0.86,
                lead_time_hours=4,
                temperature_c=22.1,
                barometric_pressure_hpa=1004.5,
                wind_speed_kmh=34.0,
                humidity_pct=94.5,
                radar_reflectivity_dbz=46.8,
                alert_issued=True
            ),
            WeatherForecastRecord(
                forecast_id="WTH-2026-003",
                location_station="Met Station Valley Central",
                event_class="Normal Transition",
                event_probability=0.12,
                lead_time_hours=6,
                temperature_c=25.0,
                barometric_pressure_hpa=1013.2,
                wind_speed_kmh=12.5,
                humidity_pct=52.0,
                radar_reflectivity_dbz=14.0,
                alert_issued=False
            )
        ]
        db.add_all(samples)
        db.commit()
    db.close()
