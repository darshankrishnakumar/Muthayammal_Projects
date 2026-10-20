from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PatientProfile(Base):
    """
    Electronic Health Record (EHR) Patient Master Index
    """
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True)
    full_name = Column(String(100), index=True)
    cohort = Column(String(50), default="DIABETIC_METABOLIC")
    age = Column(Integer)
    gender = Column(String(20))
    blood_group = Column(String(10), default="O+")
    attending_physician = Column(String(100), default="Dr. Sarah Caldwell, MD (Endocrinology)")
    registered_clinic = Column(String(100), default="Metropolitan Chronic Care Institute")
    created_at = Column(DateTime, default=datetime.utcnow)

class PatientRiskAssessment(Base):
    """
    Multi-Target Clinical Risk Assessment & Comorbidity Prognosis Record
    """
    __tablename__ = "patient_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, index=True)
    patient_id = Column(String(50), index=True)
    full_name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    cohort = Column(String(50), default="DIABETIC_METABOLIC")
    
    # 10 Biomarker Inputs
    systolic_bp = Column(Float)
    diastolic_bp = Column(Float)
    hba1c = Column(Float)
    fasting_glucose = Column(Float)
    total_cholesterol = Column(Float)
    hdl_cholesterol = Column(Float)
    ldl_cholesterol = Column(Float)
    egfr = Column(Float)
    bmi = Column(Float)
    
    # 4 Disease Risks (LongitudinalHealthRiskNet)
    cardiovascular_risk_pct = Column(Float)
    type2_diabetes_risk_pct = Column(Float)
    hypertension_risk_pct = Column(Float)
    ckd_risk_pct = Column(Float)
    composite_risk_tier = Column(String(20)) # LOW, MODERATE, HIGH, CRITICAL
    
    # 4 Prognostic Comorbidity Forecasts (ClinicalComorbidityForecastNet)
    ten_year_mortality_risk_pct = Column(Float)
    hospital_readmission_risk_pct = Column(Float)
    polypharmacy_complexity_index = Column(Float)
    renal_progression_hazard_pct = Column(Float)
    
    primary_biomarker_drivers = Column(Text)
    top_shap_driver = Column(String(100))
    preventive_recommendations = Column(Text)
    recommended_intervention = Column(String(150))
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
    event_type = Column(String(50), nullable=False) # GENESIS_SEED, CLINICAL_ASSESSMENT, CARE_PLAN_UPDATE, AUDIT_INSPECTION
    details_json = Column(Text, nullable=False)
    evidence_hash = Column(String(64), nullable=False)
