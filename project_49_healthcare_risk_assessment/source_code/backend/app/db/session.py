import os
import json
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, PatientProfile, PatientRiskAssessment, AuditLedger

db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(os.path.abspath(db_file_path)), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def compute_block_hash(block_index: int, previous_hash: str, timestamp_str: str, event_type: str, details_json: str, evidence_hash: str) -> str:
    payload = f"{block_index}:{previous_hash}:{timestamp_str}:{event_type}:{details_json}:{evidence_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db, event_type: str, details: dict, evidence_hash: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    new_index = (last_block.block_index + 1) if last_block else 0
    prev_hash = last_block.block_hash if last_block else "0" * 64
    now = datetime.utcnow()
    details_str = json.dumps(details, sort_keys=True)
    b_hash = compute_block_hash(new_index, prev_hash, now.isoformat(), event_type, details_str, evidence_hash)
    
    block = AuditLedger(
        block_index=new_index,
        previous_hash=prev_hash,
        block_hash=b_hash,
        timestamp=now,
        event_type=event_type,
        details_json=details_str,
        evidence_hash=evidence_hash
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Seed Genesis Block #0
    if db.query(AuditLedger).count() == 0:
        genesis_time = datetime.utcnow() - timedelta(days=14)
        genesis_details = json.dumps({"description": "PROJECT-049 Healthcare Risk Assessment Ledger Genesis Seed", "port": 5049}, sort_keys=True)
        genesis_evidence = hashlib.sha256(b"HEALTHCARE_RISK_GENESIS_SEED_PORT_5049").hexdigest()
        genesis_hash = compute_block_hash(0, "0" * 64, genesis_time.isoformat(), "GENESIS_SEED", genesis_details, genesis_evidence)
        
        genesis_block = AuditLedger(
            block_index=0,
            previous_hash="0" * 64,
            block_hash=genesis_hash,
            timestamp=genesis_time,
            event_type="GENESIS_SEED",
            details_json=genesis_details,
            evidence_hash=genesis_evidence
        )
        db.add(genesis_block)
        db.commit()
        
    # 2. Seed Baseline Profiles & Assessments
    if db.query(PatientProfile).count() == 0:
        seed_patients = [
            ("PAT-901", "Robert Vance", "HYPERTENSIVE_CVD", 58, "Male", "A+", "Dr. Sarah Caldwell, MD", 148.0, 92.0, 7.2, 145.0, 230.0, 42.0, 158.0, 58.0, 31.4, 74.2, 68.5, 82.0, 34.0, "HIGH", 42.5, 38.0, 52.0, 28.0, "Systolic BP (148 mmHg); Atherogenic LDL (158 mg/dL)", "Systolic Blood Pressure (+0.38)", "ACE Inhibitor Therapy; Statin Titration; Dietary Sodium Restriction", "Cardiovascular & Metabolic Specialist Evaluation"),
            ("PAT-902", "Linda Sterling", "NORMOTENSIVE_CONTROL", 42, "Female", "O+", "Dr. Marcus Thorne, MD", 118.0, 76.0, 5.2, 92.0, 175.0, 58.0, 98.0, 104.0, 23.2, 18.5, 12.0, 22.0, 8.5, "LOW", 6.5, 8.0, 12.0, 5.0, "Optimal Physiological Biomarkers", "Normal Physiological Biomarkers (-0.22)", "Annual Preventive Metabolic Panel; Aerobic Conditioning Maintenance", "Routine Preventive Health Maintenance"),
            ("PAT-903", "Arthur Pendelton", "RENAL_CKD", 67, "Male", "B+", "Dr. Eleanor Vance, MD", 162.0, 98.0, 7.8, 175.0, 245.0, 34.0, 168.0, 32.0, 29.5, 88.0, 81.0, 91.0, 84.0, "CRITICAL", 68.0, 62.0, 78.0, 72.0, "Renal eGFR (32 mL/min); Systolic BP (162 mmHg); HbA1c (7.8%)", "Renal eGFR Impairment (+0.44)", "Urgent Nephrology & Cardiology Consultation; SGLT2i Renal Protection Protocol", "Immediate Specialist Referral & Target Organ Protection"),
            ("PAT-904", "Jennifer Montgomery", "DIABETIC_METABOLIC", 52, "Female", "AB-", "Dr. Sarah Caldwell, MD", 136.0, 84.0, 8.9, 188.0, 220.0, 38.0, 142.0, 82.0, 34.8, 58.0, 86.0, 64.0, 26.0, "HIGH", 36.0, 44.0, 60.0, 22.0, "HbA1c (8.9%); Fasting Glucose (188 mg/dL); BMI (34.8)", "Diabetic Glycemia HbA1c (+0.41)", "GLP-1 Receptor Agonist Initiation; Medical Nutrition Therapy; Continuous Glucose Monitoring", "Pharmacotherapy Escalation & Intensive Glycemic Control")
        ]
        
        for pid, name, cohort, age, gen, bld, doc_name, sbp, dbp, hba1c, glu, chol, hdl, ldl, egfr, bmi, cvd, t2d, htn, ckd, tier, mort, readmit, poly, renal, drivers, top_shap, rec, inter in seed_patients:
            prof = PatientProfile(
                patient_id=pid,
                full_name=name,
                cohort=cohort,
                age=age,
                gender=gen,
                blood_group=bld,
                attending_physician=doc_name
            )
            db.add(prof)
            db.commit()
            
            evidence = hashlib.sha256(f"{pid}:{name}:{age}:{sbp}:{dbp}:{hba1c}:{glu}:{egfr}:{bmi}:{cvd}:{t2d}".encode("utf-8")).hexdigest()
            a_id = f"RISK-2026-{pid.replace('PAT-', '')}"
            ass = PatientRiskAssessment(
                assessment_id=a_id,
                patient_id=pid,
                full_name=name,
                age=age,
                gender=gen,
                cohort=cohort,
                systolic_bp=sbp,
                diastolic_bp=dbp,
                hba1c=hba1c,
                fasting_glucose=glu,
                total_cholesterol=chol,
                hdl_cholesterol=hdl,
                ldl_cholesterol=ldl,
                egfr=egfr,
                bmi=bmi,
                cardiovascular_risk_pct=cvd,
                type2_diabetes_risk_pct=t2d,
                hypertension_risk_pct=htn,
                ckd_risk_pct=ckd,
                composite_risk_tier=tier,
                ten_year_mortality_risk_pct=mort,
                hospital_readmission_risk_pct=readmit,
                polypharmacy_complexity_index=poly,
                renal_progression_hazard_pct=renal,
                primary_biomarker_drivers=drivers,
                top_shap_driver=top_shap,
                preventive_recommendations=rec,
                recommended_intervention=inter,
                evidence_hash=evidence,
                timestamp=datetime.utcnow() - timedelta(days=2)
            )
            db.add(ass)
            db.commit()
            
            append_audit_block(
                db=db,
                event_type="CLINICAL_ASSESSMENT",
                details={
                    "assessment_id": a_id,
                    "patient_id": pid,
                    "patient_name": name,
                    "composite_risk_tier": tier,
                    "cardiovascular_risk_pct": cvd,
                    "type2_diabetes_risk_pct": t2d
                },
                evidence_hash=evidence
            )
            
    db.close()

if __name__ == "__main__":
    init_db()
