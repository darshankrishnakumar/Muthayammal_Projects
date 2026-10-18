from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import JobOpening, CandidateMatch
from backend.app.ml.inference_engine import screening_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CandidateScreenRequest(BaseModel):
    candidate_name: str = "Elena Rostova"
    candidate_skills: str = "Python, PyTorch, Transformers, FastAPI, Docker"
    experience_years: float = 4.5
    job_id: str = "JOB-AI-LEAD"
    anonymize_bias: bool = False

@router.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobOpening).all()
    return {"count": len(jobs), "jobs": jobs}

@router.get("/matches")
def get_matches(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    matches = db.query(CandidateMatch).order_by(CandidateMatch.overall_match_score.desc()).offset(skip).limit(limit).all()
    return {"count": len(matches), "matches": matches}

@router.post("/match")
async def match_resume(req: CandidateScreenRequest, db: Session = Depends(get_db)):
    job = db.query(JobOpening).filter(JobOpening.job_id == req.job_id).first()
    if not job:
        job_skills = ["PyTorch", "Transformers", "Python", "FastAPI", "Docker"]
        job_min_exp = 4.0
    else:
        job_skills = [s.strip() for s in job.required_skills.split(",")]
        job_min_exp = job.min_years_experience

    c_skills = [s.strip() for s in req.candidate_skills.split(",")]
    metrics = screening_engine.evaluate_fit(c_skills, job_skills, req.experience_years, job_min_exp)

    c_name = "Candidate #ANON-77" if req.anonymize_bias else req.candidate_name

    rec = CandidateMatch(
        match_id=f"MAT-2026-{uuid.uuid4().hex[:6].upper()}",
        job_id=req.job_id,
        candidate_name=c_name,
        overall_match_score=metrics["overall_match_score"],
        semantic_similarity=metrics["semantic_similarity"],
        skill_coverage_pct=metrics["skill_coverage_pct"],
        experience_fit_score=metrics["experience_fit_score"],
        matched_skills=metrics["matched_skills"],
        missing_skills=metrics["missing_skills"],
        screening_decision=metrics["screening_decision"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    await ws_manager.broadcast({"event": "CANDIDATE_SCREENED", "data": metrics})
    return {"match": rec, "metrics": metrics}
