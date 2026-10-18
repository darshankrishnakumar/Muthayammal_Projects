import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, PatientRiskAssessment
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
    if db.query(PatientRiskAssessment).count() == 0:
        samples = [
            ("PAT-901", "Robert Vance", 58, "Male", 74.2, 68.5, 82.0, 34.0, "HIGH", "Systolic BP (148), HbA1c (7.2%), LDL (158)", "Prescribe ACE Inhibitor, Dietary sodium restriction, Statin therapy"),
            ("PAT-902", "Linda Sterling", 42, "Female", 22.0, 18.5, 24.0, 12.0, "LOW", "Normal Vitals, Optimal eGFR", "Maintain annual checkup, Regular aerobic exercise"),
            ("PAT-903", "Arthur Pendelton", 67, "Male", 88.0, 81.0, 91.0, 62.0, "CRITICAL", "eGFR (<45), Fasting Glucose (175), BP (162/98)", "Immediate Nephrology & Cardiology consult, Renal protective protocol")
        ]
        for pid, name, age, gen, cvd, t2d, htn, ckd, tier, drivers, rec in samples:
            db.add(PatientRiskAssessment(
                assessment_id=f"RISK-2026-{random.randint(100, 999)}",
                patient_id=pid,
                full_name=name,
                age=age,
                gender=gen,
                cardiovascular_risk_pct=cvd,
                type2_diabetes_risk_pct=t2d,
                hypertension_risk_pct=htn,
                ckd_risk_pct=ckd,
                composite_risk_tier=tier,
                primary_biomarker_drivers=drivers,
                preventive_recommendations=rec,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
