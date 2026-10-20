from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.app.db.session import Base

class WeatherForecastRecord(Base):
    __tablename__ = "weather_forecast_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(64), unique=True, index=True)
    station_name = Column(String(64), index=True)
    archetype = Column(String(64), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_class = Column(String(48), index=True)
    lead_time_hours = Column(Integer)
    alert_issued = Column(Boolean, default=False)
    severity_tier = Column(String(32), index=True)
    confidence = Column(Float)
    advisory_directive = Column(String(255))
    temperature_c = Column(Float)
    barometric_pressure_hpa = Column(Float)
    wind_speed_kmh = Column(Float)
    humidity_pct = Column(Float)
    radar_reflectivity_dbz = Column(Float)
    dew_point_c = Column(Float)
    solar_irradiance_wm2 = Column(Float)
    cape_joules = Column(Float)
    lifted_index_c = Column(Float)
    wind_gust_kmh = Column(Float)
    pwat_mm = Column(Float)
    station_elevation_m = Column(Float)
    precipitation_rate_mmh = Column(Float)
    severe_weather_risk = Column(Float)
    nowcasting_accuracy = Column(Float, default=0.958)
    evidence_hash = Column(String(64))

class AuditLedger(Base):
    __tablename__ = "audit_ledger"

    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, unique=True, index=True)
    timestamp = Column(String(64))
    event_type = Column(String(64))
    record_id = Column(String(64))
    evidence_hash = Column(String(64))
    previous_hash = Column(String(64))
    block_hash = Column(String(64))
