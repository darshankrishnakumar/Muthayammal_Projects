from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import JobOpening, CandidateMatch, AuditLedger
from backend.app.ml.inference_engine import screening_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CandidateScreenRequest(BaseModel):
    candidate_name: str = "Elena Rostova"
    candidate_skills: str = "Python, PyTorch, Transformers, FastAPI, Docker"
    experience_years: float = Field(default=4.5, ge=0.0, le=40.0)
    job_id: str = "JOB-AI-LEAD"
    certification_count: int = Field(default=2, ge=0, le=20)
    education_level: int = Field(default=3, ge=1, le=5)
    github_contributions: int = Field(default=45, ge=0, le=500)
    soft_skills_score: float = Field(default=8.5, ge=0.0, le=10.0)
    anonymize_bias: bool = False

@router.api_route("/jobs", methods=["GET"])
@router.api_route("/jobs/", methods=["GET"])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobOpening).all()
    return {"count": len(jobs), "jobs": jobs}

@router.api_route("/matches", methods=["GET"])
@router.api_route("/matches/", methods=["GET"])
def get_matches(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    matches = db.query(CandidateMatch).order_by(CandidateMatch.id.desc()).offset(skip).limit(limit).all()
    total = db.query(CandidateMatch).count()
    return {"count": total, "matches": matches}

@router.api_route("/audit-logs", methods=["GET"])
@router.api_route("/audit-logs/", methods=["GET"])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    total = db.query(AuditLedger).count()
    return {"count": total, "blocks": logs}

@router.api_route("/stats", methods=["GET"])
@router.api_route("/stats/", methods=["GET"])
def get_stats(db: Session = Depends(get_db)):
    total = db.query(CandidateMatch).count()
    shortlisted = db.query(CandidateMatch).filter(CandidateMatch.screening_decision == "SHORTLISTED").count()
    review = db.query(CandidateMatch).filter(CandidateMatch.screening_decision == "REVIEW").count()
    rejected = db.query(CandidateMatch).filter(CandidateMatch.screening_decision == "REJECTED").count()
    avg_score = db.query(func.avg(CandidateMatch.overall_match_score)).scalar() or 0.0
    blocks_count = db.query(AuditLedger).count()
    return {
        "total_screened_candidates": total,
        "shortlisted_count": shortlisted,
        "review_count": review,
        "rejected_count": rejected,
        "shortlist_ratio_pct": round((shortlisted / max(1, total)) * 100.0, 1),
        "average_match_score": round(float(avg_score), 1),
        "audit_ledger_blocks": blocks_count
    }

@router.api_route("/match", methods=["POST"])
@router.api_route("/match/", methods=["POST"])
async def match_resume(req: CandidateScreenRequest, db: Session = Depends(get_db)):
    job = db.query(JobOpening).filter(JobOpening.job_id == req.job_id).first()
    if not job:
        job = db.query(JobOpening).first()
    
    if not job:
        job_skills = ["PyTorch", "Transformers", "Python", "FastAPI", "Docker"]
        job_min_exp = 4.0
        job_title = "Senior AI / ML Research Engineer"
    else:
        job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
        job_min_exp = job.min_years_experience
        job_title = job.title

    c_skills = [s.strip() for s in req.candidate_skills.split(",") if s.strip()]
    metrics = screening_engine.evaluate_fit(
        candidate_skills=c_skills,
        job_skills=job_skills,
        candidate_exp_years=req.experience_years,
        job_min_exp=job_min_exp,
        certification_count=req.certification_count,
        education_level=req.education_level,
        github_contributions=req.github_contributions,
        soft_skills_score=req.soft_skills_score
    )

    c_name = f"Candidate #ANON-{uuid.uuid4().hex[:4].upper()}" if req.anonymize_bias else req.candidate_name
    match_id = f"MAT-2026-{uuid.uuid4().hex[:6].upper()}"

    rec = CandidateMatch(
        match_id=match_id,
        job_id=job.job_id if job else req.job_id,
        candidate_name=c_name,
        overall_match_score=metrics["overall_match_score"],
        semantic_similarity=metrics["semantic_similarity"],
        skill_coverage_pct=metrics["skill_coverage_pct"],
        experience_fit_score=metrics["experience_fit_score"],
        seniority_compatibility=metrics["seniority_compatibility"],
        matched_skills=metrics["matched_skills"],
        missing_skills=metrics["missing_skills"],
        screening_decision=metrics["screening_decision"],
        evidence_hash=metrics["evidence_hash"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    # Append to cryptographic audit ledger
    audit_detail = (
        f"Match {match_id} for '{c_name}' on role '{job_title}': "
        f"Score {metrics['overall_match_score']}%, Decision {metrics['screening_decision']}, "
        f"Hash {metrics['evidence_hash'][:16]}..."
    )
    append_audit_block(db, "CANDIDATE_MATCH_EVALUATED", audit_detail)

    # WebSocket broadcast
    try:
        await ws_manager.broadcast({
            "event": "CANDIDATE_SCREENED",
            "match_id": match_id,
            "candidate_name": c_name,
            "job_title": job_title,
            "data": metrics
        })
    except Exception:
        pass

    return {
        "status": "SUCCESS",
        "match": {
            "id": rec.id,
            "match_id": rec.match_id,
            "job_id": rec.job_id,
            "candidate_name": rec.candidate_name,
            "overall_match_score": rec.overall_match_score,
            "semantic_similarity": rec.semantic_similarity,
            "skill_coverage_pct": rec.skill_coverage_pct,
            "experience_fit_score": rec.experience_fit_score,
            "seniority_compatibility": rec.seniority_compatibility,
            "matched_skills": rec.matched_skills,
            "missing_skills": rec.missing_skills,
            "screening_decision": rec.screening_decision,
            "evidence_hash": rec.evidence_hash,
            "timestamp": rec.timestamp.isoformat() if rec.timestamp else ""
        },
        "metrics": metrics
    }

# Backward compatibility routes
@router.api_route("/candidates", methods=["GET"])
def get_candidates_alias(db: Session = Depends(get_db)):
    matches = db.query(CandidateMatch).order_by(CandidateMatch.id.desc()).limit(20).all()
    formatted = [
        {
            "candidate_id": m.match_id,
            "name": m.candidate_name,
            "job_role": m.job_id,
            "score": m.overall_match_score / 100.0,
            "verified_skills": m.matched_skills
        }
        for m in matches
    ]
    return {"count": len(formatted), "candidates": formatted}
