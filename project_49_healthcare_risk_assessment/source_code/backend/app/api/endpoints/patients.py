import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import numpy as np

from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import PatientProfile, PatientRiskAssessment, AuditLedger
from backend.app.ml.inference_engine import health_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class PatientAssessmentRequest(BaseModel):
    full_name: Optional[str] = "Robert Vance"
    patient_name: Optional[str] = None # Support UI alias
    patient_id: Optional[str] = "PAT-901"
    cohort: Optional[str] = "HYPERTENSIVE_CVD"
    age: Optional[int] = 58
    gender: Optional[str] = "Male"
    systolic_bp: Optional[float] = 148.0
    diastolic_bp: Optional[float] = 92.0
    hba1c: Optional[float] = 7.2
    fasting_glucose: Optional[float] = 145.0
    glucose_mg_dl: Optional[float] = None # Support UI alias
    cholesterol: Optional[float] = 230.0
    hdl: Optional[float] = 42.0
    ldl: Optional[float] = 158.0
    egfr: Optional[float] = 58.0
    bmi: Optional[float] = 31.4

def serialize_assessment(a: PatientRiskAssessment) -> dict:
    return {
        "id": a.id,
        "assessment_id": a.assessment_id,
        "record_id": a.assessment_id,
        "patient_id": a.patient_id,
        "full_name": a.full_name,
        "patient_name": a.full_name,
        "age": a.age,
        "gender": a.gender,
        "cohort": a.cohort,
        "systolic_bp": a.systolic_bp,
        "diastolic_bp": a.diastolic_bp,
        "hba1c": a.hba1c,
        "fasting_glucose": a.fasting_glucose,
        "total_cholesterol": a.total_cholesterol,
        "hdl_cholesterol": a.hdl_cholesterol,
        "ldl_cholesterol": a.ldl_cholesterol,
        "egfr": a.egfr,
        "bmi": a.bmi,
        "cardiovascular_risk_pct": a.cardiovascular_risk_pct,
        "type2_diabetes_risk_pct": a.type2_diabetes_risk_pct,
        "hypertension_risk_pct": a.hypertension_risk_pct,
        "ckd_risk_pct": a.ckd_risk_pct,
        "cardiovascular_risk_score": round((a.cardiovascular_risk_pct or 0.0) / 100.0, 3),
        "diabetes_risk_score": round((a.type2_diabetes_risk_pct or 0.0) / 100.0, 3),
        "composite_risk_tier": a.composite_risk_tier,
        "risk_level": a.composite_risk_tier,
        "ten_year_mortality_risk_pct": a.ten_year_mortality_risk_pct,
        "hospital_readmission_risk_pct": a.hospital_readmission_risk_pct,
        "polypharmacy_complexity_index": a.polypharmacy_complexity_index,
        "renal_progression_hazard_pct": a.renal_progression_hazard_pct,
        "primary_biomarker_drivers": a.primary_biomarker_drivers,
        "top_shap_driver": a.top_shap_driver,
        "preventive_recommendations": a.preventive_recommendations,
        "recommended_intervention": a.recommended_intervention,
        "evidence_hash": a.evidence_hash,
        "timestamp": a.timestamp.isoformat() if a.timestamp else None
    }

def serialize_profile(p: PatientProfile) -> dict:
    return {
        "id": p.id,
        "patient_id": p.patient_id,
        "full_name": p.full_name,
        "cohort": p.cohort,
        "age": p.age,
        "gender": p.gender,
        "blood_group": p.blood_group,
        "attending_physician": p.attending_physician,
        "registered_clinic": p.registered_clinic,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }

@router.get("/assessments")
def get_assessments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    assessments = db.query(PatientRiskAssessment).order_by(PatientRiskAssessment.timestamp.desc()).offset(skip).limit(limit).all()
    serialized = [serialize_assessment(a) for a in assessments]
    return {"count": len(serialized), "assessments": serialized, "records": serialized}

@router.get("/records")
def get_records_alias(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint for /api/health-risk/records or /api/patients/records"""
    return get_assessments(skip, limit, db)

@router.get("/profiles")
def get_profiles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    profiles = db.query(PatientProfile).offset(skip).limit(limit).all()
    return {"count": len(profiles), "profiles": [serialize_profile(p) for p in profiles]}

@router.get("/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).offset(skip).limit(limit).all()
    
    chain_valid = True
    tamper_details = []
    
    for i in range(len(blocks)):
        curr = blocks[i]
        if i > 0:
            prev = blocks[i - 1]
            if curr.previous_hash != prev.block_hash:
                chain_valid = False
                tamper_details.append(f"Block #{curr.block_index} previous_hash mismatch: expected {prev.block_hash}, got {curr.previous_hash}")

    serialized = [{
        "block_index": b.block_index,
        "previous_hash": b.previous_hash,
        "block_hash": b.block_hash,
        "timestamp": b.timestamp.isoformat() if b.timestamp else None,
        "event_type": b.event_type,
        "evidence_hash": b.evidence_hash
    } for b in blocks]
    
    return {
        "total_blocks": len(serialized),
        "chain_verified": chain_valid,
        "tamper_detected": not chain_valid,
        "tamper_details": tamper_details,
        "blocks": serialized
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(PatientRiskAssessment).count()
    profiles_count = db.query(PatientProfile).count()
    crit_count = db.query(PatientRiskAssessment).filter(PatientRiskAssessment.composite_risk_tier == "CRITICAL").count()
    high_count = db.query(PatientRiskAssessment).filter(PatientRiskAssessment.composite_risk_tier == "HIGH").count()
    mod_count = db.query(PatientRiskAssessment).filter(PatientRiskAssessment.composite_risk_tier == "MODERATE").count()
    low_count = db.query(PatientRiskAssessment).filter(PatientRiskAssessment.composite_risk_tier == "LOW").count()
    
    cvd_scores = [a.cardiovascular_risk_pct for a in db.query(PatientRiskAssessment.cardiovascular_risk_pct).all()]
    mean_cvd = round(float(np.mean(cvd_scores)), 1) if cvd_scores else 42.0
    
    t2d_scores = [a.type2_diabetes_risk_pct for a in db.query(PatientRiskAssessment.type2_diabetes_risk_pct).all()]
    mean_t2d = round(float(np.mean(t2d_scores)), 1) if t2d_scores else 38.0
    
    return {
        "total_assessments": total,
        "total_patient_profiles": profiles_count,
        "mean_cardiovascular_risk_pct": mean_cvd,
        "mean_type2_diabetes_risk_pct": mean_t2d,
        "tier_distribution": {
            "CRITICAL": crit_count,
            "HIGH": high_count,
            "MODERATE": mod_count,
            "LOW": low_count
        }
    }

@router.post("/assess")
async def assess_patient_endpoint(req: PatientAssessmentRequest, db: Session = Depends(get_db)):
    name = req.full_name or req.patient_name or "Eleanor Vance"
    pid = req.patient_id or f"PAT-{uuid.uuid4().hex[:6].upper()}"
    age = req.age or 58
    sbp = req.systolic_bp or 148.0
    dbp = req.diastolic_bp or 92.0
    glu = req.fasting_glucose or req.glucose_mg_dl or 132.0
    hba1c = req.hba1c or 7.2
    chol = req.cholesterol or 230.0
    hdl = req.hdl or 42.0
    ldl = req.ldl or 158.0
    egfr = req.egfr or 58.0
    bmi = req.bmi or 31.4
    cohort = req.cohort or ("HYPERTENSIVE_CVD" if sbp >= 140 else "DIABETIC_METABOLIC")

    # Real PyTorch forward pass via dual engines
    res = health_engine.assess_patient(age, sbp, dbp, hba1c, glu, chol, hdl, ldl, egfr, bmi)

    a_id = f"RISK-2026-{uuid.uuid4().hex[:6].upper()}"
    rec = PatientRiskAssessment(
        assessment_id=a_id,
        patient_id=pid,
        full_name=name,
        age=age,
        gender=req.gender or "Female",
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
        cardiovascular_risk_pct=res["cardiovascular_risk_pct"],
        type2_diabetes_risk_pct=res["type2_diabetes_risk_pct"],
        hypertension_risk_pct=res["hypertension_risk_pct"],
        ckd_risk_pct=res["ckd_risk_pct"],
        composite_risk_tier=res["composite_risk_tier"],
        ten_year_mortality_risk_pct=res["ten_year_mortality_risk_pct"],
        hospital_readmission_risk_pct=res["hospital_readmission_risk_pct"],
        polypharmacy_complexity_index=res["polypharmacy_complexity_index"],
        renal_progression_hazard_pct=res["renal_progression_hazard_pct"],
        primary_biomarker_drivers=res["primary_biomarker_drivers"],
        top_shap_driver=res["top_shap_driver"],
        preventive_recommendations=res["preventive_recommendations"],
        recommended_intervention=res["recommended_intervention"],
        evidence_hash=res["evidence_hash"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    # Append block to cryptographic audit ledger
    append_audit_block(
        db=db,
        event_type="CLINICAL_ASSESSMENT",
        details={
            "assessment_id": a_id,
            "patient_id": pid,
            "patient_name": name,
            "composite_risk_tier": res["composite_risk_tier"],
            "cardiovascular_risk_pct": res["cardiovascular_risk_pct"],
            "type2_diabetes_risk_pct": res["type2_diabetes_risk_pct"]
        },
        evidence_hash=res["evidence_hash"]
    )

    assessment_dict = serialize_assessment(rec)

    await ws_manager.broadcast({
        "event": "PATIENT_ASSESSED",
        "assessment": assessment_dict,
        "metrics": res
    })

    return {
        "assessment": assessment_dict,
        "metrics": res
    }

@router.post("/evaluate")
async def evaluate_alias(req: PatientAssessmentRequest, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint for /api/health-risk/evaluate or /api/patients/evaluate"""
    return await assess_patient_endpoint(req, db)
