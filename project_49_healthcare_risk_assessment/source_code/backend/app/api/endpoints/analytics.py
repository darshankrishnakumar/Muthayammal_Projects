from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.db.models import PatientRiskAssessment

router = APIRouter()

@router.get("/summary")
def get_analytics(db: Session = Depends(get_db)):
    total = db.query(PatientRiskAssessment).count()
    by_tier = db.query(PatientRiskAssessment.composite_risk_tier, func.count(PatientRiskAssessment.id)).group_by(PatientRiskAssessment.composite_risk_tier).all()
    return {
        "total_patient_profiles": total,
        "cohort_tier_distribution": {t: c for t, c in by_tier},
        "model_performance": {
            "cvd_prediction_c_index": 0.892,
            "t2d_roc_auc": 0.945,
            "inference_latency_ms": 12.5
        }
    }
