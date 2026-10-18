from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PatientRiskAssessment(Base):
    __tablename__ = "patient_assessments"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, index=True)
    patient_id = Column(String(50), index=True)
    full_name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    cardiovascular_risk_pct = Column(Float)
    type2_diabetes_risk_pct = Column(Float)
    hypertension_risk_pct = Column(Float)
    ckd_risk_pct = Column(Float)
    composite_risk_tier = Column(String(20)) # LOW, MODERATE, HIGH, CRITICAL
    primary_biomarker_drivers = Column(Text)
    preventive_recommendations = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
