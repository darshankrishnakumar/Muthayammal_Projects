from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.app.db.session import Base

class WeatherForecastRecord(Base):
    __tablename__ = "weather_forecast_records"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(String(32), unique=True, index=True)
    location_station = Column(String(64), index=True)
    event_class = Column(String(48), index=True)
    event_probability = Column(Float)
    lead_time_hours = Column(Integer)
    temperature_c = Column(Float)
    barometric_pressure_hpa = Column(Float)
    wind_speed_kmh = Column(Float)
    humidity_pct = Column(Float)
    radar_reflectivity_dbz = Column(Float)
    alert_issued = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
