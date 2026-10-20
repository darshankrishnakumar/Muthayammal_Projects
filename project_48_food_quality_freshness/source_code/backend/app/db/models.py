from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FoodBatch(Base):
    """
    Perishable food inventory batch registered for quality monitoring
    """
    __tablename__ = "food_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), unique=True, index=True)
    food_category = Column(String(50), index=True) # MEAT_POULTRY, FRESH_PRODUCE, DAIRY, BAKERY
    product_name = Column(String(100), index=True)
    supplier_origin = Column(String(100), default="Pacific Northwest Agro Hub")
    storage_facility = Column(String(80), default="Cold Storage Cell #4")
    freshness_score = Column(Float, default=90.0) # 0 to 100
    deterioration_stage = Column(String(30), default="STAGE_1_FRESH") # STAGE_1_FRESH, STAGE_2_MARGINAL, STAGE_3_DETERIORATED
    estimated_shelf_life_hours = Column(Float, default=120.0)
    remaining_shelf_life_days = Column(Float, default=5.0)
    browning_index = Column(Float, default=1.0)
    spoilage_area_pct = Column(Float, default=0.0)
    microbial_risk_pct = Column(Float, default=5.0)
    cold_chain_compliance_score = Column(Float, default=98.0)
    recommendation = Column(String(100), default="OPTIMAL_RETAIL_SALE")
    timestamp = Column(DateTime, default=datetime.utcnow)

class FreshnessAssessment(Base):
    """
    Individual spatio-spectral & physicochemical freshness assessment
    """
    __tablename__ = "freshness_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(50), index=True)
    batch_id = Column(String(50), index=True)
    food_category = Column(String(50))
    product_name = Column(String(100))
    
    # 10 Telemetry inputs
    storage_temp_c = Column(Float)
    relative_humidity_pct = Column(Float)
    storage_duration_hours = Column(Float)
    browning_index = Column(Float)
    tvbn_mg_per_100g = Column(Float)
    ph_level = Column(Float)
    ethylene_concentration_ppm = Column(Float)
    moisture_content_pct = Column(Float)
    bacterial_log_cfu_g = Column(Float)
    reflectance_ratio_650_850 = Column(Float)
    
    # Dual Model Predictions
    freshness_score = Column(Float)
    deterioration_stage = Column(String(30))
    estimated_shelf_life_hours = Column(Float)
    remaining_shelf_life_days = Column(Float)
    spoilage_risk_pct = Column(Float)
    microbial_risk_pct = Column(Float)
    cold_chain_compliance_score = Column(Float)
    advisory_recommendation = Column(String(100))
    evidence_hash = Column(String(64), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLedger(Base):
    """
    Cryptographic Audit Ledger with Genesis Seeding & Continuous SHA-256 Hash Chaining
    """
    __tablename__ = "audit_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, unique=True, index=True)
    previous_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50), nullable=False) # GENESIS_SEED, QUALITY_EVALUATION, BATCH_DISPATCH, COLD_CHAIN_AUDIT
    details_json = Column(Text, nullable=False)
    evidence_hash = Column(String(64), nullable=False)
