from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class EnergyOptimizationPlan(Base):
    __tablename__ = "energy_plans"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, index=True)
    facility_archetype = Column(String(50))
    building_facility = Column(String(100))
    ambient_temp_c = Column(Float)
    relative_humidity_pct = Column(Float)
    base_load_kw = Column(Float)
    ev_charging_load_kw = Column(Float)
    tou_tariff_cents_kwh = Column(Float)
    renewable_penetration_pct = Column(Float)
    forecasted_peak_kwh = Column(Float)
    optimized_peak_kwh = Column(Float)
    peak_shaving_reduction_pct = Column(Float)
    estimated_daily_savings_usd = Column(Float)
    co2_reduction_kg = Column(Float)
    grid_stress_index = Column(Float)
    carbon_intensity_gco2 = Column(Float)
    curtailment_risk_prob = Column(Float)
    recommended_load_shift_actions = Column(Text)
    evidence_hash = Column(String(64))
    extracted_json_payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    block_index = Column(Integer, primary_key=True)
    timestamp = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    plan_id = Column(String(50), nullable=False)
    evidence_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), nullable=False)
