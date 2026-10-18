from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import CareerRole, UpskillingRoadmap
from backend.app.ml.inference_engine import career_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CareerAnalyzeRequest(BaseModel):
    user_name: str = "Jordan Bell"
    current_skills: str = "Python, PyTorch, Deep Learning, Docker"
    target_role_id: str = "ROLE-AI"

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(CareerRole).all()
    return {"count": len(roles), "roles": roles}

@router.get("/roadmaps")
def get_roadmaps(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    roadmaps = db.query(UpskillingRoadmap).order_by(UpskillingRoadmap.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(roadmaps), "roadmaps": roadmaps}

@router.post("/analyze")
async def analyze_gap(req: CareerAnalyzeRequest, db: Session = Depends(get_db)):
    role = db.query(CareerRole).filter(CareerRole.role_id == req.target_role_id).first()
    if not role:
        role_skills = ["Python", "PyTorch", "Deep Learning", "MLOps", "Transformers"]
        role_title = "AI / ML Engineer"
    else:
        role_skills = [s.strip() for s in role.required_competencies.split(",")]
        role_title = role.role_title

    u_skills = [s.strip() for s in req.current_skills.split(",")]
    res = career_engine.analyze_skill_gap(u_skills, role_skills)

    roadmap = UpskillingRoadmap(
        roadmap_id=f"RMAP-2026-{uuid.uuid4().hex[:6].upper()}",
        user_name=req.user_name,
        target_role=role_title,
        readiness_score=res["readiness_score"],
        gap_score=res["gap_score"],
        missing_skills=", ".join(res["missing_skills"]),
        recommended_courses=", ".join(res["recommended_courses"]),
        recommended_projects=", ".join(res["recommended_projects"]),
        estimated_weeks_to_readiness=res["estimated_weeks"]
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    await ws_manager.broadcast({"event": "ROADMAP_GENERATED", "data": res})
    return {"roadmap": roadmap, "metrics": res}
