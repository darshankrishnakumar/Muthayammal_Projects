from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import PatientRiskAssessment
from backend.app.ml.inference_engine import health_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class PatientAssessmentRequest(BaseModel):
    full_name: str = "Robert Vance"
    patient_id: str = "PAT-901"
    age: int = 58
    gender: str = "Male"
    systolic_bp: float = 148.0
    diastolic_bp: float = 92.0
    hba1c: float = 7.2
    fasting_glucose: float = 145.0
    cholesterol: float = 230.0
    hdl: float = 42.0
    ldl: float = 158.0
    egfr: float = 58.0
    bmi: float = 31.4

@router.get("/assessments")
def get_assessments(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    assessments = db.query(PatientRiskAssessment).order_by(PatientRiskAssessment.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(assessments), "assessments": assessments}

@router.post("/assess")
async def assess_patient(req: PatientAssessmentRequest, db: Session = Depends(get_db)):
    res = health_engine.assess_patient(
        req.age, req.systolic_bp, req.diastolic_bp, req.hba1c, req.fasting_glucose,
        req.cholesterol, req.hdl, req.ldl, req.egfr, req.bmi
    )

    rec = PatientRiskAssessment(
        assessment_id=f"RISK-2026-{uuid.uuid4().hex[:6].upper()}",
        patient_id=req.patient_id,
        full_name=req.full_name,
        age=req.age,
        gender=req.gender,
        cardiovascular_risk_pct=res["cardiovascular_risk_pct"],
        type2_diabetes_risk_pct=res["type2_diabetes_risk_pct"],
        hypertension_risk_pct=res["hypertension_risk_pct"],
        ckd_risk_pct=res["ckd_risk_pct"],
        composite_risk_tier=res["composite_risk_tier"],
        primary_biomarker_drivers=res["primary_biomarker_drivers"],
        preventive_recommendations=res["preventive_recommendations"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    await ws_manager.broadcast({"event": "PATIENT_ASSESSED", "data": res})
    return {"assessment": rec, "metrics": res}
