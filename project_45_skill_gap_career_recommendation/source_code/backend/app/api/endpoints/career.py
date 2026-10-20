from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import CareerRole, UpskillingRoadmap, AuditLedger
from backend.app.ml.inference_engine import career_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CareerAnalyzeRequest(BaseModel):
    user_name: str = "Jordan Bell"
    current_skills: str = "Python, PyTorch, Deep Learning, Docker"
    target_role_id: str = "ROLE-AI"
    years_experience: float = Field(default=3.5, ge=0.0, le=40.0)
    certifications_count: int = Field(default=2, ge=0, le=20)
    completed_projects: int = Field(default=4, ge=0, le=50)
    weekly_hours: int = Field(default=12, ge=1, le=80)
    learning_budget: float = Field(default=1200.0, ge=0.0, le=20000.0)

@router.api_route("/roles", methods=["GET"])
@router.api_route("/roles/", methods=["GET"])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(CareerRole).all()
    return {"count": len(roles), "roles": roles}

@router.api_route("/roadmaps", methods=["GET"])
@router.api_route("/roadmaps/", methods=["GET"])
def get_roadmaps(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    roadmaps = db.query(UpskillingRoadmap).order_by(UpskillingRoadmap.id.desc()).offset(skip).limit(limit).all()
    total = db.query(UpskillingRoadmap).count()
    return {"count": total, "roadmaps": roadmaps}

@router.api_route("/audit-logs", methods=["GET"])
@router.api_route("/audit-logs/", methods=["GET"])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    total = db.query(AuditLedger).count()
    return {"count": total, "blocks": logs}

@router.api_route("/stats", methods=["GET"])
@router.api_route("/stats/", methods=["GET"])
def get_stats(db: Session = Depends(get_db)):
    total = db.query(UpskillingRoadmap).count()
    avg_readiness = db.query(func.avg(UpskillingRoadmap.readiness_score)).scalar() or 0.0
    avg_weeks = db.query(func.avg(UpskillingRoadmap.estimated_weeks_to_readiness)).scalar() or 0.0
    ready_count = db.query(UpskillingRoadmap).filter(UpskillingRoadmap.readiness_score >= 80.0).count()
    blocks_count = db.query(AuditLedger).count()
    roles_count = db.query(CareerRole).count()

    return {
        "total_roadmaps_generated": total,
        "ready_candidates_count": ready_count,
        "ready_ratio_pct": round((ready_count / max(1, total)) * 100.0, 1),
        "average_readiness_score": round(float(avg_readiness), 1),
        "average_weeks_to_readiness": round(float(avg_weeks), 1),
        "total_active_roles": roles_count,
        "audit_ledger_blocks": blocks_count
    }

@router.api_route("/analyze", methods=["POST"])
@router.api_route("/analyze/", methods=["POST"])
async def analyze_gap(req: CareerAnalyzeRequest, db: Session = Depends(get_db)):
    role = db.query(CareerRole).filter(CareerRole.role_id == req.target_role_id).first()
    if not role:
        role = db.query(CareerRole).first()

    if not role:
        role_skills = ["Python", "PyTorch", "Deep Learning", "MLOps", "Transformers", "Kubernetes"]
        role_title = "AI / ML Research & Platform Engineer"
    else:
        role_skills = [s.strip() for s in role.required_competencies.split(",") if s.strip()]
        role_title = role.role_title

    u_skills = [s.strip() for s in req.current_skills.split(",") if s.strip()]
    res = career_engine.analyze_skill_gap(
        user_skills=u_skills,
        role_skills=role_skills,
        target_role_id=role.role_id if role else req.target_role_id,
        years_experience=req.years_experience,
        certifications_count=req.certifications_count,
        completed_projects=req.completed_projects,
        weekly_hours=req.weekly_hours,
        learning_budget=req.learning_budget
    )

    roadmap_id = f"RMAP-2026-{uuid.uuid4().hex[:6].upper()}"

    roadmap = UpskillingRoadmap(
        roadmap_id=roadmap_id,
        user_name=req.user_name,
        target_role=role_title,
        readiness_score=res["readiness_score"],
        gap_score=res["gap_score"],
        missing_skills=", ".join(res["missing_skills"]) if res["missing_skills"] else "None",
        recommended_courses=", ".join(res["recommended_courses"]),
        recommended_projects=", ".join(res["recommended_projects"]),
        estimated_weeks_to_readiness=res["estimated_weeks"],
        salary_growth_potential=res["salary_growth_potential_pct"],
        evidence_hash=res["evidence_hash"]
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    # Cryptographic Audit Block
    audit_detail = (
        f"Roadmap {roadmap_id} for '{req.user_name}' -> '{role_title}': "
        f"Readiness {res['readiness_score']}%, Gap {res['gap_score']}%, "
        f"Est. {res['estimated_weeks']} weeks, Hash {res['evidence_hash'][:16]}..."
    )
    append_audit_block(db, "CAREER_ROADMAP_GENERATED", audit_detail)

    # WebSocket broadcast
    try:
        await ws_manager.broadcast({
            "event": "ROADMAP_GENERATED",
            "roadmap_id": roadmap_id,
            "user_name": req.user_name,
            "target_role": role_title,
            "data": res
        })
    except Exception:
        pass

    return {
        "status": "SUCCESS",
        "roadmap": {
            "id": roadmap.id,
            "roadmap_id": roadmap.roadmap_id,
            "user_name": roadmap.user_name,
            "target_role": roadmap.target_role,
            "readiness_score": roadmap.readiness_score,
            "gap_score": roadmap.gap_score,
            "missing_skills": roadmap.missing_skills,
            "recommended_courses": roadmap.recommended_courses,
            "recommended_projects": roadmap.recommended_projects,
            "estimated_weeks_to_readiness": roadmap.estimated_weeks_to_readiness,
            "salary_growth_potential": roadmap.salary_growth_potential,
            "evidence_hash": roadmap.evidence_hash,
            "timestamp": roadmap.timestamp.isoformat() if roadmap.timestamp else ""
        },
        "metrics": res
    }
